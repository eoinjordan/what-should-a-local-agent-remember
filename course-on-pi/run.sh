#!/usr/bin/env bash
# One-shot setup and run on the RUBIK Pi (or any box with a MongoDB replica set on localhost).
#   ./run.sh            install deps, load data, run the agent, show the memory collections
#   ./run.sh agent      just run the agent again (new thread_id)
#   ./run.sh agent t1   run on thread "t1" - run it twice to see memory survive a restart
set -euo pipefail
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
PY=.venv/bin/python
case "${1:-all}" in
  all)
    .venv/bin/pip install -q "langchain==0.3.24" "langchain-openai==0.3.14" "langgraph==0.3.31" \
        "langgraph-checkpoint-mongodb==0.1.3" "pymongo==4.11.3" fastembed requests
    $PY data.py
    $PY main.py "${2:-}"
    $PY check_memory.py ;;
  data)   $PY data.py ;;
  agent)  $PY main.py "${2:-}" ;;
  memory) $PY check_memory.py "${2:-}" ;;
esac
