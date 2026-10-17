"""Step 4 solution - a change-stream consumer that survives a restart.

Run it, Ctrl-C it, run  mongosh ../demo/fail.js  while it is down, run it again: the missed event arrives,
because the resume token in agentdemo.lab_checkpoints marks where this consumer got to.
"""
import os, sys, time, datetime as dt
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

db = MongoClient(os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017/?replicaSet=rs0"))["agentdemo"]
runs, checkpoints, processed = db.runs, db.lab_checkpoints, db.lab_processed

def resume_agent(run):
    print(f"{dt.datetime.now():%H:%M:%S} agent.resume(thread_id={run['runId']!r}) status={run['status']}", flush=True)

pipeline = [{"$match": {"operationType": "update",
                        "updateDescription.updatedFields.status": {"$in": ["completed", "failed"]}}}]
ckpt = checkpoints.find_one({"_id": "step4"})
token = ckpt["token"] if ckpt else None
print(f"{dt.datetime.now():%H:%M:%S} watching ({'resuming after saved token' if token else 'from now'})", flush=True)

while True:
    try:
        with runs.watch(pipeline, full_document="updateLookup", resume_after=token) as stream:
            for change in stream:
                token = change["_id"]                                   # the resume token
                run = change["fullDocument"]
                try:
                    processed.insert_one({"_id": token, "runId": run["runId"]})   # idempotency: a redelivery fails here
                except DuplicateKeyError:
                    print("duplicate delivery skipped", flush=True); continue
                resume_agent(run)
                checkpoints.replace_one({"_id": "step4"}, {"_id": "step4", "token": token}, upsert=True)
    except KeyboardInterrupt:
        print("stopped - token kept in agentdemo.lab_checkpoints"); sys.exit(0)
    except PyMongoError as e:
        print(f"stream error: {e} - reconnecting", flush=True); time.sleep(2)
