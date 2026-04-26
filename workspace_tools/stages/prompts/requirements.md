You are running **stage 3 of the spec-driven pipeline**: requirements.

You are working inside this repo: `{repo_path}`
Task ID: `{task_id}`

## Reads

- `{flow_dir}/RESEARCH.md`

## What this stage produces

A single artifact at: **`{artifact_path}`**

## What to put in the artifact

```
# Requirements — <one-line title>

> Source: <issue url / idea>
> Generated: <date>

## Problem

<one paragraph: what isn't possible / what's broken / what's being asked for>

## Users & contexts

- **Primary user**: <who triggers this and when>
- **Other affected**: <who else feels the change>

## Acceptance criteria

Testable, behavior-level statements. Each yes/no by inspection or test.

- [ ] AC-1: <observable behavior>
- [ ] AC-2: …

## Out of scope

- <explicit non-goals>

## Open questions

- <unknowns the next stage (design) needs to resolve>
```

## The target / issue

```
{issue_text}
```

## Discipline

- 3–8 ACs. More than 8 = mixing concerns.
- Behavior-level, not implementation-level (no "use a hashmap").
- Every AC must reference a real UI element, file, signal, exit code, etc. by name.

## When you're done

Write the file at `{artifact_path}`. Do **not** commit it. Do **not** continue. Report the path and stop.
