// Slide 14 — the other branch: a job fails. Same event path, different status.
const d = db.getSiblingDB("agentdemo");
const r = d.runs.updateOne(
  { runId: "run-1842" },
  { $set: { status: "failed", "jobs.0.status": "failed", "jobs.0.endedAt": new Date(),
            failureSummary: "out of memory at epoch 7 on the 2000 ms window", updatedAt: new Date() } }
);
print(`run-1842 -> failed   (matched ${r.matchedCount}, modified ${r.modifiedCount})`);
