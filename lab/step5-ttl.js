// Step 5 — memory has a half-life. Run:  mongosh step5-ttl.js   then, about 90 s later:  mongosh step5-check.js
const d = db.getSiblingDB("agentdemo");
d.lab_sessions.drop(); d.lab_audit.drop();

// TODO: a TTL index on lab_sessions where the WRITER decides each document's lifetime.
// d.lab_sessions.createIndex({ ... }, { ... });

d.lab_sessions.insertMany([
  { sessionId: "sess-1842", context: "scratch: last 3 tool outputs", expiresAt: new Date(Date.now() + 60 * 1000) },
  { sessionId: "sess-1841", context: "scratch: tuning notes",        expiresAt: new Date(Date.now() + 24 * 3600 * 1000) }
]);
d.lab_audit.insertOne({ at: new Date(), actor: "human", event: "approved train", runId: "run-1842" });
print("sessions:", d.lab_sessions.countDocuments(), " audit:", d.lab_audit.countDocuments(), "- run step5-check.js in about 90 seconds");

// What goes in the "review" column for your own system? Raw logs? Failed attempts? Large prompts? Decide, then say why.
