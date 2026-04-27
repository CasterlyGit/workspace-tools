You are running **stage 2 of the spec-driven pipeline**: focused research.

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
- **Be concise.** Output only what's NEW vs. the artifacts you read. If
  this stage adds nothing beyond what's already documented, say that and
  stop.

## Reads

- `{flow_dir}/EXPLORE.md` — read the "Open questions for the next stage" list

## What this stage produces

A single artifact at: **`{artifact_path}`**

## What to put in the artifact

```
# Research — <issue/target one-liner>

> Reads: EXPLORE.md
> Generated: <date>

## Resolved

- **Q: <question>**
  A: <answer>. Evidence: `path/file.py:42`, or doc link.

## Constraints to honor

- <existing API / shape / behavior the change must not break>

## Prior art in this repo

- `path/similar.py` — does X. We can mirror its pattern for ...

## External references (if any)

- <library or API name> — <what we learned, link>

## Remaining unknowns (for design to handle)

- <unknown>: <option A | option B | gut call>
```

## The target / issue

```
{issue_text}
```

## Discipline

- Resolve every "open question" from EXPLORE.md, OR move it to "Remaining unknowns" with a note.
- One question → one short answer. No essays.
- Read code deeply; trace call paths; check tests that pin behavior.
- Use WebFetch sparingly and only if local sources don't answer.

## When you're done

Write the file at `{artifact_path}`. Do **not** commit it. Do **not** continue. Report the path and stop.
