You are running **stage 6 of the spec-driven pipeline**: implementation.

You are working inside this repo: `{repo_path}`
Task ID: `{task_id}`

## Reads

- `{flow_dir}/DESIGN.md` (the contract)
- `{flow_dir}/TEST_PLAN.md` (what passes)

## What this stage produces

A single artifact at: **`{artifact_path}`** — `IMPLEMENTATION.log`, listing the commits you made (one per line).

PLUS: actual source code changes. Commit them on the current git branch as you go. Match the project's existing conventions.

## How to work

1. **Re-read DESIGN.md before each component.** Do not improvise architecture; if the design needs to change, update DESIGN.md and note the deviation in the log.
2. **Write the test before the code** when the test is unit-level. For UI/exploratory work, code-then-test is fine; note it.
3. **One commit per coherent unit.** Not per-file. Not one giant commit.
4. **Run tests as you go.** If they're slow, run the targeted subset; full suite once at the end.
5. **Never disable a failing test to make it pass.** Fix the test deliberately if it's wrong.
6. **Stay inside the design.** Out-of-scope refactors → follow-up issue.

## The target / issue

```
{issue_text}
```

## Output log format

Each line of `{artifact_path}` is either:

```
<ISO time> <short-sha> <commit subject>
<ISO time> NOTE — <description of any deviation from DESIGN.md>
```

Example:

```
2026-04-25T21:30 abc1234 add VoiceIndicator follow() with cursor offset
2026-04-25T21:42 def5678 wire audio_level signal end-to-end
2026-04-25T21:50 NOTE — DESIGN.md said 30fps; bumped to 33ms (~30fps) for QTimer granularity. DESIGN.md updated.
```

## When you're done

- All ACs from REQUIREMENTS.md are implemented.
- All TEST_PLAN.md tests pass locally.
- `{artifact_path}` lists every commit.

Do **not** open a PR — that's the integration-test stage's job. Do **not** continue to a next stage. Report the branch name + commit list + test result. Stop.
