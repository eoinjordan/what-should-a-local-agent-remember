// Slide 10 — Our first document. One run = one document.
const d = db.getSiblingDB("agentdemo");
printjson(d.runs.findOne({ runId: "run-1842" }, { _id: 0 }));
