You are running **stage 5 of the spec-driven pipeline**: test plan.

You are working inside this repo: `{repo_path}`
Task ID: `{task_id}`

## Reads

- `{flow_dir}/REQUIREMENTS.md` (every AC must be covered)
- `{flow_dir}/DESIGN.md` (failure modes table)

## What this stage produces

A single artifact at: **`{artifact_path}`**

## What to put in the artifact

```
# Test plan — <title>

## Coverage matrix

| AC | Test type | Test |
|---|---|---|
| AC-1 | unit / integration / manual | <name> |

## Unit tests

- `<test name>` — <what it asserts>

## Integration tests

- `<test name>` — <scenario>

## Manual checks

- [ ] <thing to eyeball during PR review>

## What we are NOT testing (and why)

- <items not worth covering in this iteration>
```

## Discipline

- One test per AC is usually enough.
- Match the test framework already in use (read EXPLORE.md > Conventions).
- For UI / visual changes, manual checks are fine — say so explicitly.

## When you're done

Write the file at `{artifact_path}`. Do **not** commit it. Do **not** continue. Report the path and stop.
