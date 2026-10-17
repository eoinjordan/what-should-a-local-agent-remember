// Slide 17 — Not every question is semantic. The structured half, live.
// The semantic half ($vectorSearch) needs Atlas Vector Search or a self-managed mongot;
// this Pi runs plain mongod, so the embedding is stored beside the record but not searched here.
const d = db.getSiblingDB("agentdemo");
const startOfToday = new Date(); startOfToday.setUTCHours(0, 0, 0, 0);
print('runs.find({ projectId: "project-512482", "jobs.status": "failed", updatedAt: { $gte: startOfToday } })');
d.runs.find({ projectId: "project-512482", "jobs.status": "failed", updatedAt: { $gte: startOfToday } },
            { _id: 0, runId: 1, status: 1, failureSummary: 1, failureEmbedding: 1 })
 .forEach(r => printjson(r));
print("\nSame collection. Same document. The embedding sits beside the structured fields and is filtered by them.");
