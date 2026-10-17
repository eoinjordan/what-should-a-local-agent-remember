# Study sheet: AI Agents with MongoDB (skill badge)

One page on the MongoDB University course [AI Agents with MongoDB](https://learn.mongodb.com/courses/ai-agents-with-mongodb), written in my own words from the four lessons, for revision before the skill check and for lining the course's vocabulary up with the talk. 1.25 hours nominal, free, Credly badge on passing the skill check. The course code is in [mongodb-university/curriculum](https://github.com/mongodb-university/curriculum/tree/main/AI-Agents-with-MongoDB/01-Building-AI-Agents-with-MongoDB) and runs on the Pi from `course-on-pi/`.

## Unit 1: what an agent is

- An agent is software that perceives, decides and acts toward a goal. The course names three capabilities and will test them: **reasoning**, **tool use**, **memory**.
- When to use one: tasks without a fixed workflow, tolerance for latency, non-deterministic problems with several valid answers, personalisation over time. When not to: anything a plain algorithm or classic ML model handles. Agents add complexity.
- The worked contrast is a code-completion tool (not an agent) versus a coding assistant that knows the project and remembers feedback (an agent).
- MongoDB plays two roles for an agent: **knowledge base** (what it reads to answer) and **memory** (what it remembers across interactions). The model has no persistent store of its own.
- The project: an agent that answers MongoDB questions and summarises documentation pages, with two tools. Vector search over chunked docs for questions, a `find` by title over full pages for summaries. The agent picks the tool from the query.
- Why not plain RAG: it would work here, but the agent is the foundation for memory and human-in-the-loop later.

## Unit 2: environment and data

- Plan before code: tasks, data (type, sources, processing), decision logic.
- Two collections in database `ai_agents`. `chunked_docs` holds pieces of pages with a `body` and an `embedding`; chunking gives the model targeted context. `full_docs` holds whole pages, no embeddings, because a summary needs the whole page.
- Vector index on `embedding`: model `voyage-3-lite`, **512 dimensions**, **cosine** similarity. Expect a question on dimensions or similarity function.
- Dependency roles, each one a likely question: LangChain is the framework; langchain-openai connects the model; **LangGraph** gives workflows and decision-making; **langgraph-checkpoint-mongodb** saves agent state to MongoDB for memory; PyMongo is the driver; VoyageAI makes the embeddings.
- `init_mongodb()` returns the client and the two collections. `main()` creates the model with `temperature=0`.

## Unit 3: tools

- A tool is a function that extends the model past its training data: real-time data, private data, actions. The agent's loop is decide whether a tool is needed and which, format the input, call it, fold the result into its reasoning.
- LangChain's `@tool` decorator registers a Python function with its name, description and parameter schema. **Names, descriptions and schemas drive tool selection**; the course says this twice.
- Tool one, `get_information_for_question_answering`: embed the query (`input_type="query"`), run `$vectorSearch` with `index`, `path`, `queryVector`, `numCandidates` 150, `limit` 5, then `$project` the body and `vectorSearchScore`. Join the five bodies into one context string.
- Tool two, `get_page_content_for_summarization`: `find_one({"title": ...})` with a projection to `body`. Exact match only, so titles must be unique.
- Giving the model tools: a `ChatPromptTemplate` with a system message listing `{tool_names}` and a `MessagesPlaceholder`, then `llm.bind_tools(tools)`, composed as `prompt | bind_tools`. Invoking it returns a message whose `tool_calls` field says which tool and with what arguments.

## Unit 4: the graph and memory

- Why a graph: relationships, conditional paths, cycles, flexibility, visual clarity. LangGraph builds a **cyclical graph**.
- **State** is the current snapshot flowing through the graph. **Memory** is storage that persists state within a session or across sessions. Distinguish them.
- `GraphState` is a `TypedDict` with one field, `messages: Annotated[list, add_messages]`. The `add_messages` reducer appends instead of overwriting; without a reducer a key is replaced.
- Nodes: the **agent node** calls the model and appends its reply (an answer or tool calls). The **tool node** runs each pending tool call and appends a `ToolMessage` per call with the `tool_call_id`.
- Edges: `START` to agent, tools back to agent, and a **conditional edge** from agent through `route_tools`, which returns `"tools"` if the last message has tool calls and `END` otherwise. That router is what makes the graph cyclical.
- `execute_graph` streams the compiled graph; each item is a dict of node name to state update.
- Memory types: **short-term** keeps context within a session (follow-up questions). **Long-term** persists across sessions (preferences, summaries, past actions). The course implements short-term only.
- Implementation: `MongoDBSaver(mongodb_client)` as the `checkpointer` passed to `graph.compile`. A checkpointer captures state at each node step. Every run needs `config = {"configurable": {"thread_id": ...}}`; the thread id is the session key, and a session id is the natural choice in an app.
- What lands in MongoDB: database `checkpointing_db`, collections `checkpoints` and `checkpoint_writes`, documents keyed by `thread_id`. LangGraph creates them.
- The proof: ask about backups, then "What did I just ask you?" on the same thread.

## Likely skill-check angles

1. Which capability is which: reasoning, tools, memory.
2. Which collection serves which tool, and why chunk one but not the other.
3. Index facts: 512 dimensions, cosine, field `embedding`.
4. What `@tool` contributes to tool selection.
5. What `bind_tools` does versus what the tool node does.
6. The role of `add_messages`.
7. What `route_tools` returns and when.
8. State versus memory; short-term versus long-term.
9. What `MongoDBSaver` needs (the client) and what `thread_id` identifies.
10. Where checkpoints are stored.

## Vocabulary to line up with the deck

| Course says | Deck says | Where |
|---|---|---|
| state and checkpointer | workflow state, resume by `thread_id` | slides 14, 25 |
| short-term vs long-term memory | keep / expire / review, session context | slides 15, 16, 25 |
| knowledge base | structured and semantic retrieval over the same documents | slide 17 |
| tool node runs the tool | the governor decides before the actuator fires | slide 18 |
| LangChain `@tool` | MCP tools and skills | slides 4, 5, 28 |

**MCP tool versus LangChain tool**, since the panel will know the second: identical to the model (name, description, JSON schema in, text out). A `@tool` is a function inside the agent's process, usable only by that framework in that language. An MCP tool is served by a separate process over a standard protocol, so any client can discover and call it, and LangGraph can consume MCP servers through the MCP adapters. They compose. Neither holds state; that is the checkpointer's job, and it is the talk's thesis.
