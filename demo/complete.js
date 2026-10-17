// Slide 14 — step 1: the job updates its own state. The database does the rest.
const d = db.getSiblingDB("agentdemo");
const r = d.runs.updateOne(
  { runId: "run-1842" },
  { $set: { status: "completed", "jobs.0.status": "completed", "jobs.0.endedAt": new Date(),
            results: { accuracy: 0.93, latencyMs: 13 }, updatedAt: new Date() } }
);
print(`run-1842 -> completed   (matched ${r.matchedCount}, modified ${r.modifiedCount})`);
