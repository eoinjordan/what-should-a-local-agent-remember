// Step 2 — a first document. One run = one document. Fill the blanks from your step-1 list, then run:
//   mongosh step2-run-document.js
const d = db.getSiblingDB("agentdemo");
d.lab_runs.drop();

const run = {
  runId: "run-1842",
  projectId: "project-512482",
  orgId: "org-71",
  objective: { metric: "accuracy", target: 0.92 },
  status: "training",                              // the field the agent lost on restart
  configuration: { /* TODO: the settings the job ran with, snapshotted */ },
  jobs: [ /* TODO: the job the platform returned, with its id and status */ ],
  results: null,                                   // TODO: latest result, or null until there is one
  approvals: [ /* TODO: who allowed the train action, and when */ ],
  createdAt: new Date(), updatedAt: new Date()
};

d.lab_runs.insertOne(run);
printjson(d.lab_runs.findOne({ runId: "run-1842" }, { _id: 0 }));

// Now argue, in one line each (write them as comments here, then compare with solutions/step2-run-document.js):
// What grows without bound?            ->
// What changes every few seconds?      ->
// What needs a history, not a field?   ->
// Which query must be fast?            ->
