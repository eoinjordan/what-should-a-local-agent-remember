# Step 1 solution: what must persist

Read against `data/workflow-log.jsonl`.

**1. Identifiers the agent had to be told or discover.** Project id 512482, org id 71, DSP block id 3, learn block id 4, and every job id the platform returned (203, then 204). The agent discovered the first four with two tool calls at 19:02 and then lost all of them at the restart at 19:03:04. They belong on the run document (`projectId`, `orgId`, the configuration snapshot) the moment they are known, keyed by a `runId` the agent is given back, so a restarted process can read one document instead of re-discovering.

**2. Where it lost the job.** At 19:03:12 the restarted agent says "I don't have a record of an active job" and starts job 204 while job 203 is still running. One field, `status: "training"` on the run document, read before acting, would have prevented the duplicate. The platform then queues 204 behind 203, and at 19:06:05 the agent reads a result that belongs to job 199 from an earlier run and treats it as the outcome: the stale-result mistake. The run document's `jobs[]` entry with the current `jobId` and `results` tied to that job would have stopped it.

**3. Evidence versus scratch.** Keep: every `start_training`, `update_learn_block` and `delete_dataset_version` call with its arguments (actions and their arguments are the audit trail), each job's final status and reason ("loss diverged after 3 epochs"), and the configuration the job ran with. Expire: the thirteen `get_job_status` polls with their progress values, and the conversational text. Review: the failed job's full output, if the platform exposes it.

**4. The action that needed an approval.** `delete_dataset_version` at 19:09:35. It is destructive, it was not requested by the user, and the agent cannot explain it afterwards. An approval collection with a schema that only admits a known vocabulary of actions would have refused it at insert, and a policy would have required a human decision before anything ran. Retrying a failed job with the same configuration (19:09:34) is the other one: the retry should have read the failure reason from the run's history first.

The state that must persist, as a list: run id, project and org ids, configuration snapshot, current status, current job id and its status, the latest result with the job it came from, the history of status transitions and actions, and approvals. That list is the run document on slide 10.
