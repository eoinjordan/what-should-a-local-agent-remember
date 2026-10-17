// Step 5 — memory has a half-life. Run as:  mongosh step5-ttl.js   then, ~90 s later:  mongosh step5-ttl.js check
const d = db.getSiblingDB("agentdemo");
const mode = (typeof process !== "undefined" && process.argv.slice(-1)[0] === "check") ? "check" : "write";

if (mode === "write") {
  d.lab_sessions.drop(); d.lab_audit.drop();
  // TODO: a TTL index on lab_sessions where the WRITER decides each document's lifetime.
  // d.lab_sessions.createIndex({ ... }, { ... });
  d.lab_sessions.insertMany([
    { sessionId: "sess-1842", context: "scratch: last 3 tool outputs", expiresAt: new Date(Date.now() + 60 * 1000) },
    { sessionId: "sess-1841", context: "scratch: tuning notes",        expiresAt: new Date(Date.now() + 24 * 3600 * 1000) }
  ]);
  d.lab_audit.insertOne({ at: new Date(), actor: "human", event: "approved train", runId: "run-1842" });
  print("sessions:", d.lab_sessions.countDocuments(), " audit:", d.lab_audit.countDocuments(), "- run again with 'check' in about 90 seconds");
} else {
  print("sessions now:", d.lab_sessions.countDocuments(), "(expect 1: sess-1842 is gone)");
  print("audit now:   ", d.lab_audit.countDocuments(), "(expect 1, and no TTL index on it)");
  print("TTL on audit?", d.lab_audit.getIndexes().some(i => i.expireAfterSeconds !== undefined) ? "YES - wrong" : "no");
}
// What goes in the "review" column for your own system? Raw logs? Failed attempts? Large prompts? Decide, then say why.
