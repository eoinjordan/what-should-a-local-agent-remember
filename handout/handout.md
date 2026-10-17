# What Should a Local Agent Remember? One page

Saving state for agents running at the edge. The PDF version is `handout.pdf`.

**Model for the workload.** Start with the questions the agent asks when things go wrong. The document's shape follows the questions, not the data.
**Index for the questions.** Equality, then sort, then range. Every index is a bet on how the system is used, and every write pays for it.
**Treat AI memory as data.** Persist what matters, expire what doesn't, and make every action explainable from a record.

## 1 · The questions, before the schema

What runs are active for this project? What changed since the last good run? Which jobs are still pending? Which actions were approved by a human? What previous failure looks like this one?

## 2 · One run = one document

```js
{ runId: "run-1842", projectId: "project-512482", orgId: "org-71",
  objective: { metric: "accuracy", target: 0.92 },
  status: "training",
  configuration: { windowMs: 2000, learningRate: 0.001 },
  jobs: [ { jobId: "job-203", type: "training", status: "running" } ],
  results: { accuracy: 0.89, latencyMs: 14 },
  approvals: [ { action: "train", by: "human", at: ... } ],
  createdAt: ..., updatedAt: ... }
```

Embed what is small, bounded and read with the parent (config snapshot, latest result, current status). Reference what is large, unbounded or shared (job events, training logs, artifacts). Append-only log for the explanation trail (actions, status transitions, approvals).

## 3 · The question creates the index

```js
runs.find({ projectId: "project-512482", status: "training" })            // { projectId: 1, status: 1 }
runs.find({ projectId: "project-512482" }).sort({ updatedAt: -1 }).limit(1) // { projectId: 1, updatedAt: -1 }
```

Check with `explain("executionStats")`: keys examined should equal documents returned. Every status update now maintains both indexes.

## 4 · From polling to events

```python
pipeline = [{"$match": {"operationType": "update",
            "updateDescription.updatedFields.status": {"$in": ["completed", "failed"]}}}]
with runs.watch(pipeline, full_document="updateLookup", resume_after=saved_token) as cs:
    for change in cs:
        agent.resume(thread_id=change["fullDocument"]["runId"])
        save(change["_id"])   # the resume token
```

Resume token for downtime, idempotent handler for duplicates, a scan by `updatedAt` past the oplog window.

## 5 · Memory has a half-life

```js
db.sessions.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 })  // the writer stamps expiresAt per document
```

Short-term (temp job state, session context, cache, tool outputs): expire. Long-term (audit history, summaries, approvals, baselines): keep, index, audit. TTL sweeps about once a minute and never applies to audit.

## 6 · An agent that can act must be explainable

```js
{ action: "start_training", requestedBy: "agent", approvedBy: "eoin",
  scope: { orgId: "org-71", projectId: "project-512482" },
  decision: "approved", policyId: "train-non-destructive", reason: "non-destructive training run", at: ISODate(...) }
```

A schema refuses actions outside the vocabulary. A governor reads the policy collection before approving. Every decision lands in audit. The approval record is also the lock.

## Monday

- Developer: give every workflow a document and a thread id; replace one polling loop with a change stream.
- Architect: put a state layer between tools and the world; decide embed vs reference by read pattern.
- Platform lead: index from the query log; make lifetimes a schema decision; keep audit and approvals out of the expiry list.
- Manager: ask one question of any agent project: can it explain what it did? If the answer is not a collection, it is not ready.
