# The demo kit

One script per slide, all against one database, `agentdemo`. Shown in the talk on a RUBIK Pi 3 running MongoDB 9.0 Community; runs anywhere you have a replica set.

## Quick start

```bash
docker compose up -d        # single-node replica set rs0 on localhost:27017 (or point MONGO_URI at your own)
mongosh reset.js            # five runs, both indexes, the TTL index, policies, the approvals schema
./run-demo.sh               # every step below, non-interactively, with 13 checks
```

You need `mongosh` and Python 3 with `pymongo` on the host (`pip install pymongo`). The Python scripts read `MONGO_URI` if set; the default is `mongodb://127.0.0.1:27017/?replicaSet=rs0`.

## Step by step

| Slide | Command | What you see |
|---|---|---|
| reset | `mongosh reset.js` | run-1842 back on `training`; indexes and policies rebuilt. Run it between rehearsals. |
| 10 | `mongosh demo1-findone.js` | The run document. Ask yourself what is wrong with it. |
| 12 | `mongosh demo-index.js` | Both agent questions with `explain()`: the index each hits, one key examined. |
| 14 | terminal B `python3 watch.py`, then `mongosh complete.js` | The job updates its status; the change stream fires; the consumer resumes the agent by thread id and saves its resume token. |
| 14, 25 | Ctrl-C the watcher, `mongosh fail.js`, start `watch.py` again | The event that happened while the consumer was down arrives on restart. A redelivered event is skipped. |
| 15 | `mongosh ttl.js`, wait ~90 s, `mongosh ttl-check.js` | Two sessions with per-document `expiresAt`; the one-minute one is gone; audit has no TTL. |
| 17 | `mongosh queries.js` | Failed runs for the project today, with the embedding stored beside the fields. |
| 18 | terminal B `python3 governor.py`, then `mongosh propose.js` | `start_training` approved by policy, `deploy_model` rejected for lack of one, `delete_project` refused by the schema. Every decision in `audit`. |
| 25 | `python3 resume.py`, Ctrl-C mid-step, run again | A five-step agent whose only memory is one document in `threads`; it restarts at the step it was on. `--reset` starts over. |

`tmux-demo.sh` opens the three-terminal layout used in the talk. `serve-terminal.sh` is not included here; the talk served the Pi's terminal to a browser with ttyd to record the captures in `../captures/`.

## Verify

```bash
./run-demo.sh
```

Ends with `13 passed, 0 failed` and a non-zero exit code otherwise. It takes about two minutes because it waits for the TTL monitor.

## The semantic half of slide 17

`$vectorSearch` needs Atlas Vector Search or self-managed Search attached to your deployment. This kit runs on plain `mongod`, so the embedding is stored beside the record and the structured query is what runs; `../course-on-pi/` shows an exact cosine scan standing in for the index on a small collection.
