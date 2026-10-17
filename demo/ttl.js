// Slide 15 — Memory has a half-life. The writer sets expiresAt per document.
const d = db.getSiblingDB("agentdemo");
const ttl = d.sessions.getIndexes().find(i => i.expireAfterSeconds !== undefined);
print("TTL index on sessions:", JSON.stringify({ key: ttl.key, expireAfterSeconds: ttl.expireAfterSeconds }));
d.sessions.deleteMany({});
d.sessions.insertMany([
  { sessionId: "sess-1842", runId: "run-1842", context: "scratch: last 3 tool outputs", expiresAt: new Date(Date.now() + 60 * 1000) },
  { sessionId: "sess-1841", runId: "run-1841", context: "scratch: tuning notes",        expiresAt: new Date(Date.now() + 24 * 3600 * 1000) }
]);
d.sessions.find({}, { _id: 0, sessionId: 1, expiresAt: 1 }).forEach(s => print("  ", JSON.stringify(s)));
print("sessions now:", d.sessions.countDocuments(), "— the TTL monitor runs about once a minute; run ttl-check.js in ~90 s");
print("audit is NOT in the expiry list:", d.audit.getIndexes().some(i => i.expireAfterSeconds !== undefined) ? "WRONG — audit has a TTL" : "no TTL index on audit");
