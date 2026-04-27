---
description: "Greenfield orchestrator: turn an idea into a new repo + GitHub Project + initial commit via the SDD pipeline."
---

You are running **`/automate`** — the greenfield orchestrator.

**Input idea:** $ARGUMENTS

You will create a brand-new project from this idea: a local repo, a GitHub repo, a GitHub Project board, and an initial commit shaped by the spec-driven pipeline. The user has signed up for hands-off operation — don't ask permission at every stage; just do it and report.

---

## Hard preflight (fail fast if any of these are missing)

Run these checks before touching anything. If any fail, **stop and tell the user exactly what's missing and how to fix it.**

```bash
which gh                                  # must exist
gh auth status                            # must show authenticated with repo + project + workflow scopes
gh api user --jq .login                   # must return a username (we'll use this for the repo owner)
which claude                              # the agent runtime
ls ~/Documents/Dev                        # must exist; mkdir -p if missing
```

If `gh` is missing → "Run `brew install gh && gh auth login -s repo,project,workflow`, then re-invoke `/automate`."

If `gh auth status` is missing scopes → "Run `gh auth refresh -s repo,project,workflow`, then re-invoke."

---

## Pipeline

### Step 1 — Slugify and reserve a name

From the idea, derive a kebab-case slug ≤ 30 chars. Lowercase letters and digits only, no leading/trailing hyphens. Reject if a directory already exists at `~/Documents/Dev/<slug>/` or a repo `<owner>/<slug>` exists on GitHub — pick a numeric suffix (`<slug>-2`, etc.) if needed.

Print the chosen slug and pause for ~1 line of explanation, then continue.

### Step 2 — Local scaffold

```bash
mkdir -p ~/Documents/Dev/<slug>
cd ~/Documents/Dev/<slug>
git init -b main
```

Write a minimal `README.md` (just the project name + the original idea as the description) and a sensible `.gitignore` for the language you expect (if unsure, write a generic one covering `.DS_Store`, `.env`, `__pycache__/`, `node_modules/`, `dist/`, `build/`, `.venv/`).

Create the artifact dir: `mkdir -p .flow/init/`.

### Step 3 — GitHub repo + Project

```bash
gh repo create <owner>/<slug> --private --source . --remote origin
gh project create --owner @me --title "<slug>" --format json
# parse the project URL/number from the response
```

Then set up the standard columns. GitHub Projects v2 uses **status field options**, not classic columns. Use `gh project field-create` to add a single-select status field with options `Backlog`, `Up Next`, `In Progress`, `In Review`, `Done` (if a default Status field already exists, edit its options to match).

If `gh project` calls fail (older gh, missing scope, etc.), **continue without the project board** — log it as a "follow-up: re-run project setup" in `.flow/init/SETUP_NOTES.md`. The repo + pipeline still proceed.

### Step 4 — Run the pipeline

Run these stages in order, **invoking each via the Skill tool**. After each stage, `git add -A && git commit -m "<stage>: <one-line summary>"` so the artifact is persisted before the next stage starts. **Do not skip stages. Do not run stages out of order.**

Greenfield skips `explore` (nothing to map yet) but otherwise runs the full chain:

1. **`_pipeline:research`** — args: the idea. Investigate the problem space, libraries, prior art. Writes `.flow/init/RESEARCH.md`.
2. **`_pipeline:requirements`** — args: the idea. Translate idea into ACs. Writes `.flow/init/REQUIREMENTS.md`.
3. **`_pipeline:design`** — args: the idea. Implementation spec. Writes `.flow/init/DESIGN.md`.
4. **`_pipeline:test-plan`** — args: the idea. Coverage matrix. Writes `.flow/init/TEST_PLAN.md`.
5. **`_pipeline:implement`** — args: the idea. Writes the code per design + the tests per plan. Commits as it goes.
6. **`_pipeline:integration-test`** — args: the idea. **For greenfield only**, override the stage's PR-opening behavior: instead of opening a PR, just commit `INTEGRATION.md` to `main`. The initial green-field landing IS the first delivery. (Tell the integration-test stage explicitly: "this is greenfield-init mode — commit on main, do not open a PR.")

After each Skill call returns, verify the expected artifact exists; if not, stop and report which stage didn't produce its file.

### Step 5 — Push everything

```bash
git push -u origin main
```

Move the GitHub Project card (if created) to `Done` for the "init" item — or just leave it; greenfield init isn't a tracked issue.

### Step 6 — Report

Print, in this exact shape:

```
✅ <slug> shipped.
   Local:    ~/Documents/Dev/<slug>/
   Repo:     https://github.com/<owner>/<slug>
   Project:  <project URL or "(skipped — see SETUP_NOTES.md)">
   ACs:     <count> defined, <count> verified
   Next:    file issues against the repo and run /iterate <url> to extend.
```

Stop.

---

## Discipline

- **One commit per stage** — the PR-style readability matters even on `main`.
- **Don't invent scope.** If the idea says "a fibonacci script", you ship a fibonacci script — not a fibonacci framework with plugins. The user can `/iterate` to extend.
- **No PR for greenfield init.** Initial commits land on `main`. Brownfield `/iterate` is where PRs happen.
- **If a stage fails**, stop. Don't try to "fix forward" — leave the partial state, report the failure, let the user decide.
- **Bypass-mode is on**, so don't second-guess your own commands; just run them. But still print what you're about to do before destructive ops (rm, force push, etc. — none of which should be needed in greenfield).
