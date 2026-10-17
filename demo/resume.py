"""Demo 3 (Q&A) - "the state was never in the process".

A tiny multi-step agent whose only memory is a document in agentdemo.threads.
Each step takes a couple of seconds and writes its progress before moving on.

  python3 resume.py            start (or continue) the run for run-1842
  Ctrl-C mid-step, then run it again: it picks up at the step it was on, because the
  checkpoint document - not the Python process - knows where it got to.
  python3 resume.py --reset    forget the thread and start from step 1
"""
import os, sys, time, datetime as dt
from pymongo import MongoClient

URI = os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017/?replicaSet=rs0")
db = MongoClient(URI, serverSelectionTimeoutMS=5000)["agentdemo"]
threads = db.threads
B, G, Y, C, X = "\033[1m", "\033[32m", "\033[33m", "\033[36m", "\033[0m"
def log(m): print(f"{C}{dt.datetime.now():%H:%M:%S}{X} {m}", flush=True)

THREAD_ID = "run-1842"
STEPS = [
    ("discover ids",       "look up project-512482 and its DSP block ids"),
    ("snapshot config",    "record windowMs=2000, learningRate=0.001 against the run"),
    ("start training job", "POST the job, store jobId job-203 on the run document"),
    ("wait for the event", "no polling - the change stream will wake us (slide 14)"),
    ("summarise",          "compare results with run-1841 and write the summary"),
]

if "--reset" in sys.argv:
    threads.delete_one({"_id": THREAD_ID}); log(f"thread {THREAD_ID} forgotten"); sys.exit(0)

state = threads.find_one({"_id": THREAD_ID}) or {"_id": THREAD_ID, "step": 0, "log": []}
if state["step"] >= len(STEPS):
    log(f"{G}thread {THREAD_ID} already finished all {len(STEPS)} steps - run with --reset to start over{X}"); sys.exit(0)
if state["step"]:
    log(f"{Y}resuming thread {THREAD_ID} at step {state['step'] + 1} of {len(STEPS)} - the process restarted, the thread did not{X}")
else:
    log(f"starting thread {THREAD_ID}")

try:
    for n in range(state["step"], len(STEPS)):
        name, what = STEPS[n]
        log(f"{B}step {n + 1}/{len(STEPS)}  {name}{X}  - {what}")
        time.sleep(2.5)                                   # the slow part: an API call, a training job...
        threads.update_one({"_id": THREAD_ID},
                           {"$set": {"step": n + 1, "updatedAt": dt.datetime.now(dt.timezone.utc)},
                            "$push": {"log": {"step": n + 1, "name": name, "at": dt.datetime.now(dt.timezone.utc)}}},
                           upsert=True)
        log(f"   checkpoint written: step={n + 1}")
    log(f"{G}done - {len(STEPS)} steps, state in agentdemo.threads{X}")
except KeyboardInterrupt:
    saved = (threads.find_one({"_id": THREAD_ID}) or {}).get("step", 0)
    print(); log(f"{Y}killed mid-step. Checkpoint says step={saved}. Run me again.{X}")
