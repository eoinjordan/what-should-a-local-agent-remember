"""Slide 14 - From polling to events.

The change-stream consumer from the slide, plus the failure path the talk says aloud:
  * resume token   - persisted in agentdemo.checkpoints after every event, so a
                     restarted consumer picks up where it left off (kill it, update a
                     run while it is down, start it again: the event still arrives).
  * idempotency    - each event's _id is recorded in agentdemo.processed; a redelivered
                     event is skipped instead of resuming the agent twice.
Run:  python3 watch.py        (Ctrl-C to stop)
"""
import os, sys, time, datetime as dt
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

URI = os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017/?replicaSet=rs0")
db = MongoClient(URI, serverSelectionTimeoutMS=5000)["agentdemo"]
runs, checkpoints, processed = db.runs, db.checkpoints, db.processed

B, G, Y, R, C, X = "\033[1m", "\033[32m", "\033[33m", "\033[31m", "\033[36m", "\033[0m"
def log(msg): print(f"{C}{dt.datetime.now():%H:%M:%S}{X} {msg}", flush=True)
utcnow = lambda: dt.datetime.now(dt.timezone.utc)

pipeline = [{"$match": {
    "operationType": "update",
    "updateDescription.updatedFields.status": {"$in": ["completed", "failed"]}
}}]

class Agent:                      # stand-in for the real agent runtime
    def resume(self, thread_id, run):
        status = run["status"]
        colour = G if status == "completed" else R
        extra = f"  failure={run.get('failureSummary')!r}" if status == "failed" else f"  results={run.get('results')}"
        log(f"{B}agent.resume(thread_id={thread_id!r}){X}  status={colour}{status}{X}{extra}")
        log(f"   next tool -> {'summarise what changed' if status == 'completed' else 'ask a human before retrying'}")
agent = Agent()

ckpt = checkpoints.find_one({"_id": "watch.py"})
token = ckpt["token"] if ckpt else None
log(f"watching agentdemo.runs for status in {{completed, failed}}  "
    f"({'resuming after saved token' if token else 'no checkpoint - starting from now'})")

while True:
    try:
        with runs.watch(pipeline, full_document="updateLookup", resume_after=token) as cs:
            for change in cs:
                token = change["_id"]
                run = change["fullDocument"]
                try:
                    processed.insert_one({"_id": token, "runId": run["runId"], "at": utcnow()})
                except DuplicateKeyError:
                    log(f"{Y}duplicate delivery for {run['runId']} - already handled, skipping{X}")
                    continue
                log(f"{Y}change event{X}  runId={run['runId']}  updatedFields={list(change['updateDescription']['updatedFields'])}")
                agent.resume(thread_id=run["runId"], run=run)
                checkpoints.replace_one({"_id": "watch.py"}, {"_id": "watch.py", "token": token, "at": utcnow()}, upsert=True)
                log("   checkpoint saved (resume token)")
    except KeyboardInterrupt:
        log("stopped - resume token kept in agentdemo.checkpoints"); sys.exit(0)
    except PyMongoError as e:
        log(f"{R}stream error: {e} - reconnecting in 2 s{X}"); time.sleep(2)
