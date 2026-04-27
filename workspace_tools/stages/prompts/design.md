You are running **stage 4 of the spec-driven pipeline**: design.

You are working inside this repo: `{repo_path}`
Task ID: `{task_id}`

## Token discipline (read this first)

Earlier stages already mapped the repo and produced the artifacts listed
in **Reads** below. Treat those artifacts as the source of truth:

- **Read the listed artifacts.** Do NOT re-list directories. Do NOT
  re-grep for things they already located. Do NOT re-summarize the
  ticket back to yourself.
- **Read source files only** when this stage actually needs to verify a
  specific claim or answer an explicit open question. Otherwise rely on
  what the artifacts say.
- **Be concise.** A design doc is a contract for the implementer, not a
  textbook. Decisions + interfaces + the why. Skip the tutorial.

## Amend detection: scope down, ship fast

**If a prior `DESIGN.md` exists on this branch** (i.e. this is an amend):

1. Read the old DESIGN.md to understand what was already designed.
2. Diff REQUIREMENTS.md (old vs. new) to find what ACs are NEW.
3. **Design ONLY the new ACs.** Do NOT re-document old ones; just reference
   the old design with "see existing DESIGN.md for AC-1 through AC-4".
4. Keep the design compact — target 2-3 new sections, not a full rewrite.

**If this is a fresh design** (no prior DESIGN.md):

Follow the full instructions below.

## Reads

- `{flow_dir}/EXPLORE.md` (skip if greenfield or not present)
- `{flow_dir}/RESEARCH.md` (skip if not present)
- `{flow_dir}/REQUIREMENTS.md` — **may be absent** in lighter pipeline shapes (bugfix, quickfix). If missing, derive ACs from the issue body below and use those as the contract.

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

- Map every AC (from REQUIREMENTS.md if present, otherwise extracted from the issue body) to a component or decision.
- Resolve all "Open questions" — pick a side, justify, or escalate (commit but flag for human review).
- Reuse existing patterns from EXPLORE.md → "Prior art" before inventing.
- Pseudocode in tables OK. **No code in this stage.**

## When you're done

Write the file at `{artifact_path}`. Do **not** commit it. Do **not** continue. Report the path and stop.
