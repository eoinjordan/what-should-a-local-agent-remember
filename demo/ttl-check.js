// Slide 15 — run this a minute or two after ttl.js: sess-1842 is gone, sess-1841 is kept.
const d = db.getSiblingDB("agentdemo");
print("sessions now:", d.sessions.countDocuments());
d.sessions.find({}, { _id: 0, sessionId: 1, expiresAt: 1 }).forEach(s => print("  ", JSON.stringify(s)));
