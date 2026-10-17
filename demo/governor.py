"""Slide 18 - An agent that can act must be explainable.

A change stream on agentdemo.approvals sees every proposal the agent inserts and
decides it from the policies collection - before any actuator or API call fires.
Every decision is appended to agentdemo.audit. Run:  python3 governor.py
"""
import os, datetime as dt
from pymongo import MongoClient

URI = os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017/?replicaSet=rs0")
db = MongoClient(URI, serverSelectionTimeoutMS=5000)["agentdemo"]
B, G, R, C, X = "\033[1m", "\033[32m", "\033[31m", "\033[36m", "\033[0m"
def log(m): print(f"{C}{dt.datetime.now():%H:%M:%S}{X} {m}", flush=True)
now = lambda: dt.datetime.now(dt.timezone.utc)

def decide(p):
    pol = db.policies.find_one({"active": True, "action": p["action"], "scope.orgId": p["scope"]["orgId"]})
    if not pol:
        return None, "rejected", f"no active policy permits {p['action']} in {p['scope']['orgId']}"
    if pol.get("maxConcurrentRuns"):
        busy = db.runs.count_documents({"projectId": p["scope"]["projectId"], "status": "training"})
        if busy >= pol["maxConcurrentRuns"]:
            return pol["_id"], "rejected", f"{busy} run(s) already training in {p['scope']['projectId']}; policy allows {pol['maxConcurrentRuns']}"
    return pol["_id"], "approved", f"policy {pol['_id']} satisfied - {pol['description'].split(';')[0].lower()}"

log("governor watching agentdemo.approvals for decision = proposed")
with db.approvals.watch([{"$match": {"operationType": "insert", "fullDocument.decision": "proposed"}}]) as cs:
    for ch in cs:
        p = ch["fullDocument"]
        policy_id, decision, why = decide(p)
        upd = {"decision": decision, "decidedAt": now(), "policyId": policy_id, "reason": why}
        if decision == "approved":
            upd["approvedBy"] = db.policies.find_one({"_id": policy_id})["approver"]
        db.approvals.update_one({"_id": p["_id"], "decision": "proposed"}, {"$set": upd})
        db.audit.insert_one({"at": now(), "actor": "governor", "event": f"proposal_{decision}",
                             "approvalId": p["_id"], "action": p["action"], "scope": p["scope"],
                             "policyId": policy_id, "reason": why})
        colour = G if decision == "approved" else R
        log(f"{colour}{B}{decision.upper()}{X}  {p['action']}  for {p['scope']['projectId']}  - {why}")
