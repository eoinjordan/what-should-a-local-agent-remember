// reset.js — put the demo database back to its starting state.
// Run:  mongosh reset.js        (any db; the script selects agentdemo itself)
// Seeds the run document from slide 10 (run-1842, status "training"), a few sibling
// runs so the slide-12 queries have something to find, the two indexes from slide 12,
// the TTL index from slide 15, and the policy + approvals collections from slide 18.
const d = db.getSiblingDB("agentdemo");
d.dropDatabase();

const T = (minsAgo) => new Date(Date.now() - minsAgo * 60000);

// ---- slide 10: one run = one document --------------------------------------
d.runs.insertMany([
  {
    runId: "run-1842", projectId: "project-512482", orgId: "org-71",
    objective: { metric: "accuracy", target: 0.92 },
    status: "training",
    configuration: { windowMs: 2000, learningRate: 0.001 },
    jobs: [ { jobId: "job-203", type: "training", status: "running", startedAt: T(4) } ],
    results: { accuracy: 0.89, latencyMs: 14 },
    approvals: [ { action: "train", by: "human", at: T(5) } ],
    createdAt: T(5), updatedAt: T(1)
  },
  {
    runId: "run-1841", projectId: "project-512482", orgId: "org-71",
    objective: { metric: "accuracy", target: 0.92 }, status: "completed",
    configuration: { windowMs: 1000, learningRate: 0.001 },
    jobs: [ { jobId: "job-199", type: "training", status: "completed", startedAt: T(70), endedAt: T(62) } ],
    results: { accuracy: 0.91, latencyMs: 11 },
    approvals: [ { action: "train", by: "human", at: T(71) } ],
    createdAt: T(71), updatedAt: T(62)
  },
  {
    runId: "run-1840", projectId: "project-512482", orgId: "org-71",
    objective: { metric: "accuracy", target: 0.92 }, status: "failed",
    configuration: { windowMs: 500, learningRate: 0.01 },
    jobs: [ { jobId: "job-195", type: "training", status: "failed", startedAt: T(130), endedAt: T(127) } ],
    results: null,
    failureSummary: "loss diverged after 3 epochs; learning rate too high for 500 ms windows",
    failureEmbedding: [0.12, -0.44, 0.31, 0.08, -0.27, 0.55, -0.10, 0.19],   // stand-in: a real one is 1536 floats
    approvals: [ { action: "train", by: "human", at: T(131) } ],
    createdAt: T(131), updatedAt: T(127)
  },
  {
    runId: "run-1839", projectId: "project-512482", orgId: "org-71",
    objective: { metric: "accuracy", target: 0.92 }, status: "completed",
    configuration: { windowMs: 2000, learningRate: 0.0005 },
    jobs: [ { jobId: "job-190", type: "training", status: "completed", startedAt: T(300), endedAt: T(290) } ],
    results: { accuracy: 0.87, latencyMs: 15 },
    approvals: [ { action: "train", by: "human", at: T(301) } ],
    createdAt: T(301), updatedAt: T(290)
  },
  {
    runId: "run-77", projectId: "project-9", orgId: "org-71",
    objective: { metric: "f1", target: 0.80 }, status: "training",
    configuration: { windowMs: 1000, learningRate: 0.001 },
    jobs: [ { jobId: "job-12", type: "training", status: "running", startedAt: T(2) } ],
    results: null, approvals: [ { action: "train", by: "human", at: T(3) } ],
    createdAt: T(3), updatedAt: T(2)
  }
]);
d.runs.createIndex({ runId: 1 }, { unique: true });

// ---- slide 12: the question creates the index ------------------------------
d.runs.createIndex({ projectId: 1, status: 1 });
d.runs.createIndex({ projectId: 1, updatedAt: -1 });

// ---- slide 15: memory has a half-life --------------------------------------
d.sessions.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });

// ---- slide 18: guardrails are data too -------------------------------------
d.createCollection("approvals", {
  validator: { $jsonSchema: {
    bsonType: "object",
    required: ["action", "requestedBy", "scope", "decision", "at"],
    additionalProperties: false,
    properties: {
      _id: {},
      action:      { enum: ["start_training", "tune_hyperparameters", "deploy_model"] },
      requestedBy: { bsonType: "string" },
      approvedBy:  { bsonType: "string" },
      scope:       { bsonType: "object", required: ["orgId", "projectId"],
                     properties: { orgId: { bsonType: "string" }, projectId: { bsonType: "string" } } },
      decision:    { enum: ["proposed", "approved", "rejected", "executed"] },
      reason:      { bsonType: "string", maxLength: 300 },
      policyId:    { bsonType: ["string", "null"] },
      at:          { bsonType: "date" },
      decidedAt:   { bsonType: "date" }
    }
  } },
  validationLevel: "strict", validationAction: "error"
});
d.approvals.createIndex({ "scope.projectId": 1, decision: 1, at: -1 });

d.policies.insertMany([
  { _id: "train-non-destructive", active: true, action: "start_training",
    scope: { orgId: "org-71" }, approver: "eoin", maxConcurrentRuns: 1,
    description: "Training is non-destructive; allowed while no other run in the project is training." },
  { _id: "tune-within-bounds", active: true, action: "tune_hyperparameters",
    scope: { orgId: "org-71" }, approver: "eoin",
    description: "Hyperparameter edits are allowed; the change is recorded against the run." }
  // Note what is missing: there is no policy for deploy_model. The database refuses it.
]);

d.audit.createIndex({ at: -1 });
d.checkpoints.drop();   // the change-stream consumer's resume token
d.processed.drop();     // idempotency keys for delivered events
d.threads.drop();       // resume.py's thread state (Demo 3)

print("agentdemo reset:");
print("  runs       ", d.runs.countDocuments(), " (run-1842 is", d.runs.findOne({ runId: "run-1842" }).status + ")");
print("  policies   ", d.policies.countDocuments());
print("  indexes on runs:", d.runs.getIndexes().map(i => i.name).join(", "));
