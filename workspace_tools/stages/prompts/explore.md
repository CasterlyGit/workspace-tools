You are running **stage 1 of the spec-driven pipeline**: codebase exploration.

You are working inside this repo: `{repo_path}`
Task ID: `{task_id}`

## Token discipline (read this first)

You are the FIRST stage — no prior artifact to lean on. But later stages
will lean on YOUR artifact, so make it dense and small:

- **Be brief.** One screen of high-signal facts beats five screens.
  Later stages should rarely need to re-grep what you found.
- **No directory dumps.** A `find` / `tree` listing belongs in your
  scratch space, not the artifact. Convert it into "the relevant
  modules are X, Y, Z and they relate as …".
- **Cap at ~100 lines.** If you need more, you're including too much.

## What this stage produces

A single artifact at: **`{artifact_path}`**

(That path must exist when you stop. The orchestrator verifies it. Do not write anywhere else.)

## What to put in the artifact

A short, scannable Markdown file under these headings:

```
# Explore — <repo name>

## Stack
- language, framework, package manager, test runner

## Layout
- `src/` — ...
- `tests/` — ...

## Entry points
- run: `<command>`
- test: `<command>`
- build: `<command>`

## Conventions
- naming, formatting, lint, type hints — quote 1-2 concrete file paths

## Recent activity
- branch: `<name>`
- last commits:
  - `<sha>` <subject>
- uncommitted: <yes/no, brief>

## Files relevant to this target
- `path/x.py` — <one-line reason>
- `path/y.py` — ...

## Open questions for the next stage
- ...
```

## The target / issue

```
{issue_text}
```

## Discipline

- Use Glob + Grep + a small number of Reads. **Don't read everything.**
- Skip vendored dirs (`node_modules`, `.venv`, `dist`, `build`).
- 5-minute time budget for exploration; if you've burned that, write what you have.
- The "Files relevant to this target" list is the most important section — it must be non-empty (or explicitly explain why nothing existing is relevant — e.g. greenfield).

## When you're done

Write the file at `{artifact_path}`. Do **not** commit it — the orchestrator commits per stage. Do **not** continue to a next stage. Just report the path.
