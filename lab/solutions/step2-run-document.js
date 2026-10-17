// Step 2 solution — the talk's run document, with the reasoning beside each field.
const d = db.getSiblingDB("agentdemo");
d.lab_runs.drop();
d.lab_runs.insertOne({
  runId: "run-1842",                                   // the thread id: what a restarted agent asks for first
  projectId: "project-512482", orgId: "org-71",        // discovered once, then read, never re-discovered
  objective: { metric: "accuracy", target: 0.92 },     // embedded: small, bounded, read with the run
  status: "training",                                  // embedded: read before every action; changes often (see below)
  configuration: { windowMs: 2000, learningRate: 0.001 }, // embedded snapshot: what THIS job ran with, even if the project changes later
  jobs: [ { jobId: "job-203", type: "training", status: "running", startedAt: new Date() } ], // current job only; events go elsewhere
  results: { accuracy: 0.89, latencyMs: 14, fromJobId: "job-199" }, // latest result, tied to the job it came from
  approvals: [ { action: "train", by: "human", at: new Date() } ],   // the last approval; the full history is a log
  createdAt: new Date(), updatedAt: new Date()
});
printjson(d.lab_runs.findOne({ runId: "run-1842" }, { _id: 0 }));

// What grows without bound?          jobs[] if every job and every event is embedded. Keep the current job; reference job events and logs.
// What changes every few seconds?    status (and jobs.0.status). Fine to embed, but it is why the index on status costs writes.
// What needs a history, not a field? approvals, status transitions, actions. "Why did it do that?" is a history question: append-only log.
// Which query must be fast?          "what is still training for this project" -> { projectId, status }, and "latest for this project".
