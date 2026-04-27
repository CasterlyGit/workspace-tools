You are running **stage 6 of the spec-driven pipeline**: implementation.

You are working inside this repo: `{repo_path}`
Task ID: `{task_id}`

## Token discipline (read this first)

Earlier stages already mapped the repo and produced the artifacts listed
in **Reads** below. Treat those artifacts as the source of truth:

- **Read the listed artifacts** + the source files you actually edit.
  Do NOT re-list directories. Do NOT re-grep for things the design
  already located.
- **Be concise** in IMPLEMENTATION.log — one line per commit, plus
  short NOTE lines for any deviations. No retrospectives.

## ⚠ Hard guardrail: AC-DESIGN consistency

Before writing any code: scan REQUIREMENTS.md for ACs (lines starting
with `AC-` or `**AC-`). If any AC is **not addressed** in DESIGN.md,
**halt immediately** — write a single line to `{artifact_path}`:

```
NEEDS_DESIGN: AC-N (and AC-M, …) present in REQUIREMENTS.md but absent from DESIGN.md
```

…and exit without committing code. The orchestrator will surface this
and re-run the design stage. Do NOT silently flag the AC as
"out of scope for this stage" or "follow-up issue" — that's how amends
end up as artifact-only commits with no code.

## Reads

- `{flow_dir}/DESIGN.md` — **may be absent** in lighter pipeline shapes. If missing, design from the issue body below; the design is whatever needs to change to satisfy it.
- `{flow_dir}/TEST_PLAN.md` — **may be absent** in lighter pipeline shapes. If missing, write a regression test alongside the fix.

## What this stage produces

A single artifact at: **`{artifact_path}`** — `IMPLEMENTATION.log`, listing the commits you made (one per line).

PLUS: actual source code changes. Commit them on the current git branch as you go. Match the project's existing conventions.

## Amend detection: respond to PR feedback

**User feedback check**: Below is the last comment posted to this GitHub issue/PR.

```
{user_feedback}
```

**If there is feedback** (i.e. the user posted a comment with requested changes):

1. Read the PRIOR `IMPLEMENTATION.log` to see what was already done.
2. Parse the feedback: what's wrong? what should change?
3. **Implement ONLY the feedback.** Do NOT re-implement working code.
4. **Run only targeted tests** for the changed parts. Skip full regression
   unless it's quick.
5. Target: finish in 2-5 min, not 10-15. Be surgical.
6. Log each commit clearly: e.g. `fix(dock): address feedback — AC-5 now
   works cross-app (cursor polling)`.

**If this is a fresh implementation:**

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
