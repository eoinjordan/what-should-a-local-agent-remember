# The 10-minute lab

Five steps, each one a design habit, all on the same running example: a training run driven by an agent. Not "watch me explain" but the habit built on a problem you have already felt. Starters are in this folder, solutions in `solutions/`. Every step runs against the `agentdemo` database from the demo kit, so start there:

```bash
cd ../demo && docker compose up -d && mongosh reset.js && cd ../lab
```

| Step | Habit | Starter | Check |
|---|---|---|---|
| 1 | Identify the state that must persist | `data/workflow-log.jsonl` + the questions below | your list against `solutions/step1-state.md` |
| 2 | Shape a first document and argue what to embed, reference or log | `step2-run-document.js` | `mongosh step2-run-document.js` inserts and prints it |
| 3 | Two query patterns, one compound index, and its write cost | `step3-indexes.js` | `explain()` shows `IXSCAN` and keys examined = returned |
| 4 | Replace a polling loop with a consumer that survives a restart | `step4-poll.py` | kill it, update a run, restart it, the event still arrives |
| 5 | TTL for session data, never for audit | `step5-ttl.js` | one session gone a minute later, audit untouched |

## Step 1 · What must persist? (2 min)

`data/workflow-log.jsonl` is a sanitised, shortened log of one agent session against an ML platform: tool calls, their arguments, the polling loop, a process restart, and the mistakes the talk opens with. Read it once and answer:

1. Which identifiers did the agent have to be told, or go and discover, before it could act? Where should they live after the first discovery?
2. Where did the agent lose track of a job? What single field would have prevented the duplicate job?
3. Which lines are evidence a human would want later, and which are scratch that can expire?
4. Which action should have required an approval record before it ran?

Write your list, then compare with `solutions/step1-state.md`.

## Step 2 · A first document (2 min)

Open `step2-run-document.js`. It inserts a run document with blanks. Fill it from your step-1 list, run it, then answer the four prompts at the bottom of the file: what grows without bound, what changes every few seconds, what needs a history rather than a field, and which query must be fast. The solution is the talk's run document with the reasoning beside each field.

## Step 3 · The question creates the index (2 min)

`step3-indexes.js` runs the two questions the agent asks most often, without indexes, and prints `explain()`. Add one compound index for each, re-run, and read `totalKeysExamined` against `nReturned`. Then write one sentence naming the write cost you just took on, and one naming whether a single index could serve both.

## Step 4 · Polling to events (3 min)

`step4-poll.py` is the loop the talk calls "the agent doing the database's job": it reads the run every two seconds until the status changes. Replace it with a change stream that matches status updates to `completed` or `failed`, stores the resume token after each event, and opens with `resume_after` on restart. Test the failure path: start it, Ctrl-C it, run `mongosh ../demo/fail.js`, start it again. The missed event should arrive.

## Step 5 · Half-life (1 min)

`step5-ttl.js` writes two session documents and one audit entry. Add the TTL index so the writer decides the lifetime per document, then run `mongosh step5-check.js` after about ninety seconds to confirm that only the short-lived session is gone and the audit collection still has no TTL index. Say out loud what you would put in the "review" column for your own system.
