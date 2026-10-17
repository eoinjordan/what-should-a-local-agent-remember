"""AI Agents with MongoDB - the course's main.py, running on the RUBIK Pi.

Same structure as the course (lessons 2 to 6): init_mongodb, two tools, GraphState,
agent node, tool node, route_tools, init_graph with a MongoDBSaver checkpointer,
execute_graph with a thread_id. Three things are swapped so it runs on a Pi with a
self-managed MongoDB and no paid APIs:

  * vector search   - $vectorSearch when the deployment has search attached; otherwise
                      an exact cosine scan over the 107 chunks (same top-5, no index);
  * embeddings      - embeddings.py: Voyage if VOYAGE_API_KEY is set, else a local model;
  * the LLM         - OpenAI gpt-4o if OPENAI_API_KEY is set, any OpenAI-compatible server
                      if LLM_BASE_URL is set, else a scripted stand-in that issues the tool
                      calls the course's two test queries would produce. The stand-in exists
                      so the graph, the tools and the checkpointer can be exercised and
                      inspected on the Pi without a key; it is not a language model.
"""
import math
import key_param
from pymongo import MongoClient
from langchain.agents import tool
from typing import List, Annotated
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import ToolMessage, AIMessage, HumanMessage
from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.mongodb import MongoDBSaver
from embeddings import embed


def init_mongodb():
    """Initialize MongoDB client and collections (identical to the course)."""
    mongodb_client = MongoClient(key_param.mongodb_uri)
    DB_NAME = "ai_agents"
    vs_collection = mongodb_client[DB_NAME]["chunked_docs"]
    full_collection = mongodb_client[DB_NAME]["full_docs"]
    return mongodb_client, vs_collection, full_collection


class GraphState(TypedDict):
    messages: Annotated[list, add_messages]


def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a piece of text (course: voyage-3-lite; here: embeddings.py)."""
    return embed(text, input_type="query")


def _has_search(collection) -> bool:
    try:
        return any(ix.get("name") == "vector_index" for ix in collection.list_search_indexes())
    except Exception:
        return False


@tool
def get_information_for_question_answering(user_query: str) -> str:
    """
    Retrieve relevant documents for a user query using vector search.

    Args:
        user_query (str): The user's query.

    Returns:
        str: The retrieved documents as a string.
    """
    query_embedding = generate_embedding(user_query)
    vs_collection = init_mongodb()[1]

    if _has_search(vs_collection):
        pipeline = [
            {"$vectorSearch": {"index": "vector_index", "path": "embedding", "queryVector": query_embedding,
                               "numCandidates": 150, "limit": 5}},
            {"$project": {"_id": 0, "body": 1, "score": {"$meta": "vectorSearchScore"}}},
        ]
        results = list(vs_collection.aggregate(pipeline))
    else:
        # Exact cosine similarity over every chunk. Fine for 107 vectors; this is what
        # the index does approximately for millions.
        qn = math.sqrt(sum(x * x for x in query_embedding))
        scored = []
        for doc in vs_collection.find({}, {"_id": 0, "body": 1, "embedding": 1}):
            e = doc["embedding"]
            score = sum(a * b for a, b in zip(query_embedding, e)) / (qn * math.sqrt(sum(x * x for x in e)) or 1)
            scored.append((score, doc["body"]))
        scored.sort(reverse=True)
        results = [{"body": b, "score": s} for s, b in scored[:5]]

    return "\n\n".join(doc.get("body") for doc in results)


@tool
def get_page_content_for_summarization(user_query: str) -> str:
    """
    Retrieve the content of a documentation page for summarization.

    Args:
        user_query (str): The user's query (title of the documentation page).

    Returns:
        str: The content of the documentation page.
    """
    full_collection = init_mongodb()[2]
    document = full_collection.find_one({"title": user_query}, {"_id": 0, "body": 1})
    return document["body"] if document else "Document not found"


def agent(state: GraphState, llm_with_tools) -> GraphState:
    """Agent node: the LLM decides to answer or to call a tool."""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


def tool_node(state: GraphState, tools_by_name) -> GraphState:
    """Tool node: run every tool call the agent asked for."""
    result = []
    for tool_call in state["messages"][-1].tool_calls:
        observation = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


def route_tools(state: GraphState):
    """Conditional edge: tools if the last message has tool calls, else END."""
    messages = state.get("messages", [])
    if not messages:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    ai_message = messages[-1]
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


def init_graph(llm_with_tools, tools_by_name, mongodb_client):
    """Build the cyclical graph and give it a MongoDB checkpointer (lesson 6)."""
    graph = StateGraph(GraphState)
    graph.add_node("agent", lambda state: agent(state, llm_with_tools))
    graph.add_node("tools", lambda state: tool_node(state, tools_by_name))
    graph.add_edge(START, "agent")
    graph.add_edge("tools", "agent")
    graph.add_conditional_edges("agent", route_tools, {"tools": "tools", END: END})
    checkpointer = MongoDBSaver(mongodb_client)
    return graph.compile(checkpointer=checkpointer)


def execute_graph(app, thread_id: str, user_input: str) -> None:
    """Stream the graph for one user turn on one thread."""
    input = {"messages": [("user", user_input)]}
    config = {"configurable": {"thread_id": thread_id}}
    for output in app.stream(input, config):
        for key, value in output.items():
            print(f"Node {key}:")
            for m in value["messages"]:
                kind = type(m).__name__
                body = m.content if isinstance(m.content, str) else str(m.content)
                calls = getattr(m, "tool_calls", None)
                print(f"  {kind}: {body[:160]!r}" + (f"  tool_calls={[(c['name'], c['args']) for c in calls]}" if calls else ""))
    print("---FINAL ANSWER---")
    print(value["messages"][-1].content)


# ---------------------------------------------------------------------------
# LLM selection. The course hard-codes ChatOpenAI(model="gpt-4o").
# ---------------------------------------------------------------------------
class ScriptedLLM:
    """Stand-in used only when no LLM is configured. It replays the decisions the course
    shows for its two test queries: a tool call first, then an answer built from the tool
    result; and for 'What did I just ask?' it reads the earlier HumanMessage back from the
    checkpointed history, which is the memory behaviour lesson 6 demonstrates."""

    def __init__(self, tools):
        self.tools = {t.name: t for t in tools}

    def bind_tools(self, tools):
        from langchain_core.runnables import RunnableLambda
        return RunnableLambda(self.invoke)          # so `prompt | llm.bind_tools(tools)` composes like ChatOpenAI

    def invoke(self, messages, config=None):
        if hasattr(messages, "to_messages"):
            messages = messages.to_messages()
        last = messages[-1]
        if isinstance(last, ToolMessage):
            return AIMessage(content=f"(scripted) Based on the retrieved documentation:\n{str(last.content)[:600]}")
        humans = [m for m in messages if isinstance(m, HumanMessage)]
        q = humans[-1].content.strip()
        if "just ask" in q.lower() and len(humans) > 1:
            return AIMessage(content=f"(scripted, from checkpointed history) You asked: {humans[-2].content!r}")
        if q.lower().startswith("summarize"):
            title = q[len("summarize"):].strip().rstrip(".").removeprefix("the ").removesuffix(" page").strip()
            return AIMessage(content="", tool_calls=[{"name": "get_page_content_for_summarization", "args": {"user_query": title}, "id": "call_1"}])
        return AIMessage(content="", tool_calls=[{"name": "get_information_for_question_answering", "args": {"user_query": q}, "id": "call_1"}])


def make_llm(tools):
    if key_param.openai_api_key:
        print("LLM: OpenAI gpt-4o (as in the course)")
        return ChatOpenAI(openai_api_key=key_param.openai_api_key, temperature=0, model="gpt-4o")
    if key_param.openai_base_url:
        print(f"LLM: OpenAI-compatible server at {key_param.openai_base_url}")
        return ChatOpenAI(openai_api_key="local", base_url=key_param.openai_base_url, temperature=0, model="local")
    print("LLM: none configured - using the scripted stand-in (set OPENAI_API_KEY or LLM_BASE_URL for a real model)")
    return ScriptedLLM(tools)


def main():
    mongodb_client, vs_collection, full_collection = init_mongodb()
    tools = [get_information_for_question_answering, get_page_content_for_summarization]
    llm = make_llm(tools)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a helpful AI assistant."
         " You are provided with tools to answer questions and summarize technical documentation related to MongoDB."
         " Think step-by-step and use these tools to get the information required to answer the user query."
         " Do not re-run tools unless absolutely necessary."
         " If you are not able to get enough information using the tools, reply with I DON'T KNOW."
         " You have access to the following tools: {tool_names}."),
        MessagesPlaceholder(variable_name="messages"),
    ]).partial(tool_names=", ".join(t.name for t in tools))

    llm_with_tools = prompt | llm.bind_tools(tools)
    tools_by_name = {t.name: t for t in tools}
    app = init_graph(llm_with_tools, tools_by_name, mongodb_client)

    import sys, uuid
    thread_id = sys.argv[1] if len(sys.argv) > 1 else str(uuid.uuid4())[:8]
    print(f"thread_id = {thread_id}")
    execute_graph(app, thread_id, "What are some best practices for data backups in MongoDB?")
    execute_graph(app, thread_id, "What did I just ask?")
    execute_graph(app, thread_id, "Summarize the View Database Access History page")


if __name__ == "__main__":
    main()
