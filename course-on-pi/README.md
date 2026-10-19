# AI Agents with MongoDB, followed on a RUBIK Pi 3

The MongoDB University skill badge [AI Agents with MongoDB](https://learn.mongodb.com/courses/ai-agents-with-mongodb) builds a two-tool LangGraph agent over the MongoDB docs, with MongoDB as its memory. The course assumes an Atlas cluster, OpenAI and VoyageAI. This folder is the same code, lesson for lesson, arranged to run on the Pi's own MongoDB 9.0 replica set with no paid API. The course's original code is at [mongodb-university/curriculum](https://github.com/mongodb-university/curriculum/tree/main/AI-Agents-with-MongoDB/01-Building-AI-Agents-with-MongoDB).

## Quick start

On the Pi (MongoDB running as replica set `rs0` on `127.0.0.1:27017`, Python 3.12):

```bash
cd ~/course-on-pi && ./run.sh
```

That installs the course's pinned packages into `.venv`, loads the two datasets (20 full pages, 107 chunks), runs the agent through the course's test queries, and prints what the checkpointer wrote.

| Lesson | Course step | File here | What changed for the Pi |
|---|---|---|---|
| 2 | `init_mongodb()`, `main()` | `main.py`, `key_param.py` | URI is the local replica set. Keys come from environment variables and are optional. |
| 2 | `data.py` | `data.py` | Reads the Hugging Face datasets over their JSON API, so no `datasets`/pyarrow. Embeds with the model in `embeddings.py`. Creates the vector index only if search is attached. |
| 3 | two `@tool` functions | `main.py` | Same signatures and docstrings. The vector tool uses `$vectorSearch` when an index exists, else an exact cosine scan over the 107 chunks. |
| 4 | prompt + `bind_tools` | `main.py` | Identical prompt text. |
| 5 | `GraphState`, `agent`, `tool_node`, `route_tools`, `init_graph`, `execute_graph` | `main.py` | Identical graph. |
| 6 | `MongoDBSaver`, `thread_id` | `main.py`, `check_memory.py` | Identical. `check_memory.py` is the "look at checkpointing_db" step from the video. |

## Verify

```bash
cd ~/course-on-pi && ./run.sh agent t1 && ./run.sh agent t1 && ./run.sh memory t1
```

Expected: the first run calls `get_information_for_question_answering` for the backup question, then answers "What did I just ask?" from the thread's history, then calls `get_page_content_for_summarization` with the title `View Database Access History`. The second run on the same thread shows the history is read back from MongoDB, not from the process. `check_memory.py` lists `checkpoints` and `checkpoint_writes` in `checkpointing_db` with that thread_id.

## The three swaps, and how to undo them

**LLM.** The course uses `ChatOpenAI(model="gpt-4o")`. Set `OPENAI_API_KEY` and the code does exactly that. Set `LLM_BASE_URL` instead to point at any OpenAI-compatible server; `llama-server` needs `--jinja` for tool calls, and a 3B model on the Pi is slow and unreliable at choosing tools. With neither set, `main.py` uses a scripted stand-in that issues the tool calls the course's test queries produce and reads "What did I just ask?" from the checkpointed history. It is there so the graph, tools and checkpointer can be exercised and inspected without a key. It is not a model, and the printed answers say so.

**Embeddings.** The course uses `voyage-3-lite` (512 dims). Set `VOYAGE_API_KEY` to use it. Otherwise `embeddings.py` uses `BAAI/bge-small-en-v1.5` (384 dims) through fastembed and onnxruntime, which fits in the Pi's spare RAM. `data.py` re-embeds the 107 chunks with whichever model is active, so query and document vectors always match.

**Vector search.** Plain `mongod` has no `$vectorSearch`. Two honest options:

1. Attach search to the Pi. Self-managed Search and Vector Search are supported on arm64 Ubuntu 24.04 from MongoDB 8.2 (see the [compatibility page](https://mongodb.com/docs/vector-search/deployment/compatibility-limitations/)). `mongot` wants several GB of RAM, which this Pi does not have spare while its VLM server is running. `data.py` will create the index automatically if search is present.
2. Keep plain `mongod` and let the tool do an exact cosine scan. For 107 vectors that is instant and returns the same top five an index would. It is the right teaching comparison too: the index is an approximation of this scan that stays fast at millions of vectors.

## How this connects to the talk

The course's memory lesson is slide 30 of the deck: `MongoDBSaver`, `thread_id` as the session key, state checkpointed per node transition. The "What did I just ask?" test is the thirty-second version of the Pi demo where the watcher is killed and resumes from its token. The course's two tools are the slide-21 distinction made concrete: a `find` by exact title on one side, a semantic search over the same documents on the other.
