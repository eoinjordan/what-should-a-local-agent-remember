"""Lesson 6, last step: look at what the checkpointer stored.

The course points at the `checkpointing_db` database with `checkpoints` and
`checkpoint_writes` collections, one set of documents per thread_id.
Run:  .venv/bin/python check_memory.py [thread_id]
"""
import sys
from pymongo import MongoClient
import key_param

db = MongoClient(key_param.mongodb_uri)["checkpointing_db"]
print("collections:", db.list_collection_names())
for name in ("checkpoints", "checkpoint_writes"):
    print(f"{name}: {db[name].count_documents({})} documents")

threads = db.checkpoints.distinct("thread_id")
print("threads:", threads)
tid = sys.argv[1] if len(sys.argv) > 1 else (threads[-1] if threads else None)
if tid and db.checkpoints.count_documents({"thread_id": tid}):
    n = db.checkpoints.count_documents({"thread_id": tid})
    latest = db.checkpoints.find({"thread_id": tid}).sort("checkpoint_id", -1).limit(1)[0]
    print(f"\nthread {tid}: {n} checkpoints; latest keys: {sorted(latest.keys())}")
    print("  the state itself is stored serialised in 'checkpoint' - that is the conversation the agent resumes from")
