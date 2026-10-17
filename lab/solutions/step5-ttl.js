// Step 5 solution — the writer decides each document's lifetime; the TTL monitor enforces it; audit never gets one.
// Run:  mongosh solutions/step5-ttl.js    then ~90 s later:  mongosh step5-ttl.js check
const d = db.getSiblingDB("agentdemo");
d.lab_sessions.drop(); d.lab_audit.drop();
d.lab_sessions.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });   // 0 = expire at the time stored in expiresAt
d.lab_sessions.insertMany([
  { sessionId: "sess-1842", context: "scratch: last 3 tool outputs", expiresAt: new Date(Date.now() + 60 * 1000) },
  { sessionId: "sess-1841", context: "scratch: tuning notes",        expiresAt: new Date(Date.now() + 24 * 3600 * 1000) }
]);
d.lab_audit.createIndex({ at: -1 });                                       // an index, yes; a TTL, never
d.lab_audit.insertOne({ at: new Date(), actor: "human", event: "approved train", runId: "run-1842" });
print("sessions:", d.lab_sessions.countDocuments(), " audit:", d.lab_audit.countDocuments());
// Review column, for most teams: raw logs and failed attempts. They are where the next debugging session lives, and
// "review" is the honest word for "nobody has decided yet". The database should make changing your mind cheap: a
// TTL index can be added or dropped later without touching the documents.
