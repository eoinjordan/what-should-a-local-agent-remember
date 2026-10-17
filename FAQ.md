# Questions this talk gets

Each answer follows the same shape the talk uses: say the question back, name the mechanism, walk it on the running example (a run, a job, a status change), say what you would measure.

## Schema

**What if `jobs` grows without bound? When would you split runs, jobs and events?**
The symptom is the 16 MB document limit; the disease is the hot cache page. A run document with every job event embedded is rewritten on every status change, so every write touches a large page. Split by read pattern: keep the current job and the latest result embedded, because the agent reads them with the run; move job events and training logs to their own collections keyed by `runId`, because they grow, are queried on their own, and are shared with dashboards that never read the run. Measure the document size distribution and the write rate on the status field before deciding.

**One document per project with every run embedded. When does it stop working?**
When the read pattern changes from "this project" to "this run". A project document bounds nothing: runs are unbounded, each run's jobs are unbounded, and the hot query in the talk is "what is still training for this project", which only needs the run header. Split runs out and keep a summary (counts, latest run id) in the project.

## Indexing

**Why `{ projectId: 1, status: 1 }` in that order? Could one index serve both queries?**
Equality first, then sort, then range. Both hot queries start with an equality on `projectId`. `{ projectId: 1, status: 1, updatedAt: -1 }` serves "anything still training" and a filtered version of "most recent"; the plain "most recent for a project" sort still prefers `{ projectId: 1, updatedAt: -1 }`. Check with `explain("executionStats")`: keys examined should equal documents returned.

**What is wrong with your index?**
Write amplification on a churning field. `status` changes every few seconds for a training run, so every change maintains two index entries. `status` has tiny cardinality, which is why it sits second. A partial index on `status: "training"` is cheaper if that is the only status you query. Measure the index write cost against the read frequency before adding a third index.

## Change streams

**What happens when the consumer is down for an hour?**
The resume token. The consumer stores the token of the last event it handled; on restart it opens the stream with `resume_after`. The oplog is a ring, so if the outage outlasts the oplog window the token is gone and the consumer falls back to a scan by `updatedAt` since the last processed time. Either way the handler is idempotent: resuming a run that is already resumed is a no-op. The demo kit's `watch.py` does both.

**What about an event delivered twice?**
At-least-once delivery is the contract. Record each event's `_id` (the token) in a `processed` collection with a unique key; a duplicate insert fails and the event is skipped.

## Lifecycle

**TTL runs about once a minute. What does that mean for correctness?**
A document can outlive `expiresAt` by up to a minute. That is fine for scratch data, which is the point of TTL. Nothing with a correctness requirement should rely on it; approvals and audit never get a TTL.

**What never gets a TTL?**
Anything you would reach for when someone asks why: audit history, approvals, experiment summaries, baseline results.

## Vectors

**What do you embed, what do you filter on, and how do you evaluate retrieval?**
Embed the messy text (the failure summary); filter on the structured fields beside it (`projectId`, status, date). Evaluate with a held-out set of "failures like this one" judged by a human, and measure recall at five, because that is the `limit` the agent uses.

**Why not a separate vector store?**
You can, but then the embedding and the record it describes are governed by two sets of rules, two lifetimes and two access-control lists. Keeping the embedding beside the document means one query mode added to data you already govern. Self-managed Vector Search exists for Community and Enterprise from MongoDB 8.2; the Pi in the talk runs plain `mongod`, so the demo does an exact cosine scan over its 107 chunks, which gives the same top five.

## Safety

**Two agents pick up the same approved action. Who wins?**
The approval record is the lock. A conditional update from `approved` to `executing` that also stamps the agent id matches exactly one document; the other agent matches zero and stops. No transaction needed for a single-document state transition.

**How do you represent approvals, scopes and destructive actions?**
As documents, with a JSON schema that refuses actions outside the vocabulary before any decision is made, and a policy collection the governor reads before it approves. The demo kit's `propose.js` shows all three outcomes: approved by policy, rejected for lack of policy, refused by schema.

## Architecture

**Why not Postgres with JSONB?**
It works. The difference is whether the hot queries are over the document's shape or across it, and what you lose: change streams with resume tokens, per-document TTL, and a vector index beside the document. Name those three and let the audience decide.

**Why MongoDB Community on a single-board computer rather than Atlas?**
Because "local agent" means the state has to live where the agent runs. The Pi has no cloud behind it, and everything in the talk, including the change stream and the checkpointer, works on Community Edition. Atlas adds hosted Vector Search and operations; the data model is the same.

**How is an MCP tool different from a LangChain tool?**
Identical to the model: a name, a description, a JSON schema in, text out. A LangChain `@tool` is a function inside the agent's process, usable only by that framework in that language. An MCP tool is served by a separate process over a standard protocol, so any client can discover and call it, and LangGraph can consume MCP servers through the adapters. They compose. Neither holds state; that is the checkpointer's job.

**If runs outgrow one node, what is the shard key?**
Shard by what you query by. `runId` is unique and spreads evenly but turns every project query into scatter-gather. `projectId` targets both hot queries but a busy project is a hot shard. `{ projectId, createdAt }` or a hashed `projectId` are the usual compromises, depending on whether range-by-time or spread matters more. Change streams still work across shards; event order is per shard, which the consumer design has to allow for.
