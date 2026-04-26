You are running **stage 4 of the spec-driven pipeline**: design.

You are working inside this repo: `{repo_path}`
Task ID: `{task_id}`

## Reads

- `{flow_dir}/EXPLORE.md` (skip if greenfield)
- `{flow_dir}/RESEARCH.md`
- `{flow_dir}/REQUIREMENTS.md`

## What this stage produces

A single artifact at: **`{artifact_path}`**

## What to put in the artifact

```
# Design — <one-line title>

> Reads: REQUIREMENTS.md (acceptance criteria are the contract)
> Generated: <date>

## Approach

<2–4 sentences: chosen direction; alternatives considered>

## Components touched

| File / module | Change |
|---|---|
| `path/x` | what & why |

## New files

- `path/new.ext` — purpose

## Data / state

<schemas, payload shapes, persisted state, env vars>

## Public API / surface

<functions, signals, CLI flags, hotkeys, etc.>

## Failure modes

| Failure | How we detect | What we do |
|---|---|---|

## Alternatives considered

<why we didn't pick the others>

## Risks / known unknowns

- <what could go wrong>
```

## The target / issue

```
{issue_text}
```

## Discipline

- Map every AC in REQUIREMENTS.md to a component or decision.
- Resolve all "Open questions" — pick a side, justify, or escalate (commit but flag for human review).
- Reuse existing patterns from EXPLORE.md → "Prior art" before inventing.
- Pseudocode in tables OK. **No code in this stage.**

## When you're done

Write the file at `{artifact_path}`. Do **not** commit it. Do **not** continue. Report the path and stop.
