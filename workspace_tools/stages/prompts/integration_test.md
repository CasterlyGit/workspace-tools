You are running **stage 7 of the spec-driven pipeline**: integration & verification.

You are working inside this repo: `{repo_path}`
Task ID: `{task_id}`

## Reads

- `{flow_dir}/REQUIREMENTS.md` (the ACs)
- `{flow_dir}/TEST_PLAN.md`
- `{flow_dir}/IMPLEMENTATION.log`

## What this stage produces

A single artifact at: **`{artifact_path}`** — `INTEGRATION.md`.

## What to put in the artifact

```
# Integration — <title>

## Test runs

- `<full test command>` — <result>

## AC verification

- [x] AC-1 — verified by `<test name or manual check>` (link/path)
- [x] AC-2 — ...
- [ ] AC-N — pending manual / deferred

## Outstanding issues

- <anything found that wasn't fixed; link to a follow-up issue if filed>

## Decision

- ✅ Ready to merge
- ⚠️ Ready with caveats — see Outstanding
- ❌ Not ready — return to design or implementation
```

## What to do

1. **Run the full test suite.** Confirm green.
2. **Walk every AC** in REQUIREMENTS.md:
   - Automated → cite the test name + path. Mark ✅.
   - Manual → mark ⏳ "pending human review" and list the steps.
   - Failed → list as Outstanding; pick the decision tier.
3. **Walk every failure mode** in DESIGN.md and confirm the handling exists.
4. **Decide** ✅ / ⚠️ / ❌.
5. **Do NOT open a PR yourself** — the orchestrator opens the PR after this stage commits. Just produce the report.

## The target / issue

```
{issue_text}
```

## When you're done

Write the file at `{artifact_path}`. Do **not** commit it. Do **not** open a PR. Report the decision and stop.
