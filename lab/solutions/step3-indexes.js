// Step 3 solution — one index per question, equality first, then sort. Run as:  mongosh solutions/step3-indexes.js
const d = db.getSiblingDB("agentdemo");
d.runs.dropIndexes();
d.runs.createIndex({ projectId: 1, status: 1 });        // Q1: equality on projectId, equality on status
d.runs.createIndex({ projectId: 1, updatedAt: -1 });    // Q2: equality on projectId, then the sort

function report(label, cursor) {
  const ex = cursor.explain("executionStats");
  let s = ex.queryPlanner.winningPlan, idx = "COLLSCAN";
  while (s) { if (s.indexName) { idx = s.indexName; break; } s = s.inputStage; }
  print(`${label}\n  index: ${idx}   keys examined: ${ex.executionStats.totalKeysExamined}   docs examined: ${ex.executionStats.totalDocsExamined}   returned: ${ex.executionStats.nReturned}`);
}
report("Q1  anything still training for this project?", d.runs.find({ projectId: "project-512482", status: "training" }));
report("Q2  what happened most recently for this project?", d.runs.find({ projectId: "project-512482" }).sort({ updatedAt: -1 }).limit(1));

// The write cost: every insert and every status change (every few seconds for a training run) now maintains two index
// entries as well as the document. status has tiny cardinality, which is why it is second, not first; a partial index
// { projectId: 1 } with partialFilterExpression { status: "training" } is cheaper if "training" is the only status you ask about.
//
// One index for both? { projectId: 1, status: 1, updatedAt: -1 } serves Q1 and a status-filtered version of Q2
// ("latest training run"). Plain Q2 (latest run regardless of status) still wants { projectId: 1, updatedAt: -1 },
// because the sort key must follow the equality keys directly. Let explain() settle it: keys examined should equal returned.
