You are running **stage 3 of the spec-driven pipeline**: requirements.

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
- **Be concise.** Output only what's NEW vs. the artifacts you read.

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

## The target / issue (body + every comment)

The block below is the full issue text — original body plus every comment, in order. Treat **comments as first-class content**: they may add new acceptance criteria, refine existing ones, or change priority. If a comment contradicts the original body, the most recent wins. If a comment adds a feature, derive an AC for it. Do not silently drop any user-stated ask as "out of scope" unless the user explicitly wrote that — if you're unsure, include it in `## Open questions` rather than dropping it.

```
{issue_text}
```

## Discipline

- 3–8 ACs. More than 8 = mixing concerns. If the user has piled on more, fold related asks into one AC or list them in Open questions.
- Behavior-level, not implementation-level (no "use a hashmap").
- Every AC must reference a real UI element, file, signal, exit code, etc. by name.

## When you're done

Write the file at `{artifact_path}`. Do **not** commit it. Do **not** continue. Report the path and stop.
