// Slide 18 — the agent proposes; the database decides. Three proposals:
//   1. start_training   → a policy exists and nothing else is training → approved
//   2. deploy_model     → no policy for it → rejected by the governor, with a reason
//   3. delete_project   → not even in the schema → refused at insert, never reaches a decision
const d = db.getSiblingDB("agentdemo");
const scope = { orgId: "org-71", projectId: "project-512482" };
function propose(doc) {
  try {
    const r = d.approvals.insertOne({ requestedBy: "agent", scope, decision: "proposed", at: new Date(), ...doc });
    print(`proposed  ${doc.action.padEnd(16)} id=${r.insertedId}`);
    return r.insertedId;
  } catch (e) {
    print(`REFUSED   ${doc.action.padEnd(16)} ${e.codeName || "DocumentValidationFailure"}: "${doc.action}" is not an action the schema allows`);
  }
}
const ids = [ propose({ action: "start_training", reason: "non-destructive training run" }),
              propose({ action: "deploy_model",   reason: "accuracy 0.93 beats target 0.92" }),
              propose({ action: "delete_project", reason: "clean up" }) ].filter(Boolean);
sleep(1500);
print("\nThe approval records, as the governor left them:");
d.approvals.find({ _id: { $in: ids } }, { _id: 0, action: 1, requestedBy: 1, approvedBy: 1, decision: 1, policyId: 1, reason: 1 })
 .forEach(a => printjson(a));
print("\nAudit trail — who asked, who decided, under which policy, why:");
d.audit.find({}, { _id: 0, actor: 1, event: 1, action: 1, policyId: 1, reason: 1 }).sort({ at: -1 }).limit(2).forEach(a => printjson(a));
