# What Should a Local Agent Remember?

Saving state for agents running at the edge. Materials from a talk by Eoin Jordan, shared so you can re-run every demo on your own machine, do the lab, and take the design habits back to your own agent.

In one sentence: learning how to use MongoDB to hold short-term and long-term memory state for local and remote agentic AI projects, with practical notes from factory automation: lessons learned, and how to bring the pattern into the systems you already run.

The talk's argument in three lines: **model for the workload** (start with the questions the agent will ask when things go wrong), **index for the questions** (every index is a trade), and **treat AI memory as data** (persist what matters, expire what doesn't, make every action explainable). Everything was shown live on a RUBIK Pi 3 single-board computer running Ubuntu 24.04 and MongoDB 9.0 Community Edition, with no cloud behind it.

## Start here

| If you want to | Open |
|---|---|
| Watch the talk (25 min, narrated) | [video/what-should-a-local-agent-remember.mp4](video/what-should-a-local-agent-remember.mp4), chapters in [video/chapters.md](video/chapters.md) |
| Read the slides | [slides/what-should-a-local-agent-remember.pdf](slides/what-should-a-local-agent-remember.pdf), or the [web viewer](https://eoinjordan.github.io/what-should-a-local-agent-remember/) (served from `docs/` by GitHub Pages) |
| Keep one page | [handout/handout.pdf](handout/handout.pdf): the three takeaways, the run document, the two indexes, the consumer, the TTL and the approval record |
| Run the demos | [demo/](demo/README.md): one `docker compose up` for the database, then one script per slide |
| Do the 10-minute lab | [lab/](lab/README.md): five steps, each one a design habit, starter and solution for each |
| Ask the questions the talk gets | [FAQ.md](FAQ.md) |
| Go further | [RESOURCES.md](RESOURCES.md), and the [study sheet](study/ai-agents-skill-badge-study-sheet.md) for the MongoDB University skill badge |
| Follow the MongoDB University course on your own hardware | [course-on-pi/](course-on-pi/README.md) |

## Quick start

You need Docker (or a MongoDB replica set you already have), `mongosh`, and Python 3 with `pymongo`.

```bash
cd demo
docker compose up -d          # a single-node replica set on localhost:27017
mongosh reset.js              # seed the agentdemo database
./run-demo.sh                 # every demo step, with 13 checks; ends "13 passed, 0 failed"
```

Then follow [demo/README.md](demo/README.md) slide by slide, or start the lab.

## What is in this repo

| Folder | Contents |
|---|---|
| `slides/` | The deck as PDF and as the original .pptx (40 slides: 23 main, 17 backup, presenter notes embedded). |
| `docs/` | The deck as a self-contained web page with keyboard navigation. Publish it with GitHub Pages from `docs/`. |
| `handout/` | One printable page. |
| `demo/` | The demo kit: reset, the first document, the two indexes with `explain()`, the change-stream consumer with a resume token, TTL, the structured query, the policy governor, and the resumable five-step agent. |
| `lab/` | The five-step lab from the talk, with a sanitised agent workflow log to start from. |
| `captures/` | Screenshots and GIFs of every demo step as it ran on the Pi. |
| `course-on-pi/` | The MongoDB University "AI Agents with MongoDB" code arranged to run on self-managed MongoDB without paid APIs. |
| `animations/` | The thirteen diagram animations from the slides as HTML and GIF. |
| `video/` | The chapter list of the narrated run-through; the recording itself is shared on request (it was recorded before the final edits to the deck). |

## Verify

```bash
cd demo && ./run-demo.sh
```

Runs every demo step non-interactively, including the resume-token path and the TTL wait, and checks 13 expected lines. It should end with `13 passed, 0 failed`.

## Licence

Code (`demo/`, `lab/`, `course-on-pi/`, `animations/`) is under the Apache License 2.0, see [LICENSE](LICENSE). Slides, handout, video, captures and text are under Creative Commons Attribution 4.0, see [LICENSE-CONTENT](LICENSE-CONTENT). The MongoDB University course code in `course-on-pi/` derives from [mongodb-university/curriculum](https://github.com/mongodb-university/curriculum) and the two datasets it loads are MongoDB's, CC BY 3.0.
