---
description: "Brownfield orchestrator: take a GitHub issue, run the SDD pipeline on the existing repo, open a PR. Defaults to `instant` (one fast call) — heavier shapes only when the ticket asks for it."
---

You are running **`/iterate`**.

**Args:** $ARGUMENTS — full issue URL, owner/repo#N, or `next`.

## What to do

Run the orchestrator. It does everything (resolve issue, branch, run the chosen pipeline shape, commit per stage, open PR). Stage progression is in Python — stage prompts saying "Stop." can't end the run early.

```bash
cd ${DEV:-$HOME/Documents/Dev}/workspace-tools
python -m workspace_tools.cli iterate "$ARGUMENTS"
```

## Default-to-fast principle

Default shape is `instant` — one Haiku call, no `.flow/*.md` artifact ceremony, target wall clock 60-180s. Heavier shapes (`quickfix`, `bugfix`, `full`) run only when:

- the ticket body has a `pipeline: <shape>` magic line, or
- labels (`feature`, `bug`, `polish`) map to a heavier shape, or
- the agent escalates with `ESCALATE: <reason>` in its log.

Exit code 3 = escalation. Surface the reason; tell the user to add `pipeline: bugfix` (or `full`) and re-run.

## Streaming

Stream stdout. Lines are stage-prefixed (`[instant] ...`, `[design] ...`).

If the run halts mid-pipeline, leave the branch alone — re-running auto-resumes.

## When done

Print the PR URL (or halt / escalation reason). Stop.
