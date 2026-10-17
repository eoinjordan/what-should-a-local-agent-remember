// Step 3 — the question creates the index. Run as:  mongosh step3-indexes.js
// The two questions the agent asks most often, with no index yet. Add the indexes where marked, re-run,
// and read totalKeysExamined against nReturned.
const d = db.getSiblingDB("agentdemo");
d.runs.dropIndexes();                      // start from only _id (reset.js created the talk's indexes)

// TODO: create one compound index for each question
// d.runs.createIndex({ ... });
// d.runs.createIndex({ ... });

function report(label, cursor) {
  const ex = cursor.explain("executionStats");
  let s = ex.queryPlanner.winningPlan, idx = "COLLSCAN";
  while (s) { if (s.indexName) { idx = s.indexName; break; } s = s.inputStage; }
  print(`${label}\n  index: ${idx}   keys examined: ${ex.executionStats.totalKeysExamined}   docs examined: ${ex.executionStats.totalDocsExamined}   returned: ${ex.executionStats.nReturned}`);
}
report("Q1  anything still training for this project?",
       d.runs.find({ projectId: "project-512482", status: "training" }));
report("Q2  what happened most recently for this project?",
       d.runs.find({ projectId: "project-512482" }).sort({ updatedAt: -1 }).limit(1));

// Write two sentences as comments before you look at the solution:
// The write cost I just took on is ...
// One index could / could not serve both because ...
