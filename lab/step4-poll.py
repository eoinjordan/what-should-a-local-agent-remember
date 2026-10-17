"""Step 4, starter - the polling loop the talk calls "the agent doing the database's job".

It reads run-1842 every two seconds until the status is completed or failed. Every check is a read;
every wait is latency; and if this process dies between polls, nothing remembers that it was waiting.

Replace this with a change-stream consumer (see the hints at the bottom), then test the failure path:
start it, Ctrl-C it, run  mongosh ../demo/fail.js  while it is down, start it again.
"""
import os, time, datetime as dt
from pymongo import MongoClient

db = MongoClient(os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017/?replicaSet=rs0"))["agentdemo"]
runs = db.runs

def resume_agent(run):
    print(f"{dt.datetime.now():%H:%M:%S} agent.resume(thread_id={run['runId']!r}) status={run['status']}")

print("polling run-1842 every 2 s ... (Ctrl-C to stop)")
while True:
    run = runs.find_one({"runId": "run-1842"})
    print(f"{dt.datetime.now():%H:%M:%S} read: status={run['status']}")
    if run["status"] in ("completed", "failed"):
        resume_agent(run)
        break
    time.sleep(2)

# Hints for the rewrite:
#   pipeline = [{"$match": {"operationType": "update",
#                "updateDescription.updatedFields.status": {"$in": ["completed", "failed"]}}}]
#   with runs.watch(pipeline, full_document="updateLookup", resume_after=token) as stream: ...
#   store change["_id"] (the resume token) in db.checkpoints after each event, load it at start,
#   and record each token in db.processed with a unique _id so a redelivered event is skipped.
