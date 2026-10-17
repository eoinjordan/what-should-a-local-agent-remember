// Step 5 — run about 90 s after step5-ttl.js (or its solution). The TTL monitor sweeps roughly once a minute.
const d = db.getSiblingDB("agentdemo");
if (!d.getCollectionNames().includes("lab_sessions")) {
  print("nothing to check yet - run  mongosh step5-ttl.js  first, wait about 90 s, then run this again");
} else {
  print("sessions now:", d.lab_sessions.countDocuments(), "(expect 1: sess-1842 is gone)");
  print("audit now:   ", d.lab_audit.countDocuments(), "(expect 1)");
  print("TTL on audit?", d.lab_audit.getIndexes().some(i => i.expireAfterSeconds !== undefined) ? "YES - wrong" : "no, as it should be");
}
