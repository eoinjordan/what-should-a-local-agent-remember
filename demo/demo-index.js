// Slide 12 — The question creates the index.
// Two questions the agent asked constantly, and proof that each one hits its index.
const d = db.getSiblingDB("agentdemo");

function indexOf(plan) {               // walk the winning plan down to the IXSCAN
  let s = plan;
  while (s) { if (s.indexName) return s.indexName; s = s.inputStage; }
  return "COLLSCAN";
}
function show(cursor) {
  const ex = cursor.explain("executionStats");
  const es = ex.executionStats;
  print(`    index used    : ${indexOf(ex.queryPlanner.winningPlan)}`);
  print(`    keys examined : ${es.totalKeysExamined}   docs examined: ${es.totalDocsExamined}   returned: ${es.nReturned}`);
}

print("Q1  Is anything still training for this project?");
print('    runs.find({ projectId: "project-512482", status: "training" })');
show(d.runs.find({ projectId: "project-512482", status: "training" }));
d.runs.find({ projectId: "project-512482", status: "training" }, { _id: 0, runId: 1, status: 1 })
 .forEach(r => print("    →", JSON.stringify(r)));

print("\nQ2  What happened most recently?");
print('    runs.find({ projectId: "project-512482" }).sort({ updatedAt: -1 }).limit(1)');
show(d.runs.find({ projectId: "project-512482" }).sort({ updatedAt: -1 }).limit(1));
d.runs.find({ projectId: "project-512482" }, { _id: 0, runId: 1, status: 1, updatedAt: 1 })
 .sort({ updatedAt: -1 }).limit(1).forEach(r => print("    →", JSON.stringify(r)));

print("\nThe trade: every insert and every status update now maintains both indexes.");
print("  indexes on runs:", d.runs.getIndexes().map(i => i.name).join(", "));
