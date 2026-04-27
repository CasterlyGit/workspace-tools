---
description: "Amend an open PR based on the latest comment. Reads the comment, implements the delta, runs tests, pushes, and posts a confirmation reply. Surgical and verified — target 2-5 minutes wall clock."
---

You are running **`/pr-amend`** — the PR-comment-driven amend skill.

**Args:** `$ARGUMENTS` — a GitHub PR URL like `https://github.com/owner/repo/pull/N`.

This skill is for one job: a PR is open, the user posted a comment with feedback, you implement the delta and push. Nothing else. Be surgical.

---

## Hard constraints (read every time)

1. **Time budget:** 5 minutes of agent work, max. If the change needs more, halt and ask before continuing.
2. **Token discipline:** do NOT re-explore the repo. The branch already contains the prior implementation; the comment describes a delta. Read only what you'll edit.
3. **No artifact-only commits.** Every commit must change real source code (not just `.flow/*.md`, not just docs). If your only output is a markdown file, you misunderstood — re-read the comment.
4. **Verify before claiming done.** "Tests pass" means you ran them and saw green output. "Looks right" is not verification.
5. **Stop if blocked.** If the comment is ambiguous, the relevant code is unclear, or you can't reproduce the bug — halt, post a clarification comment, exit. Do not guess.

## Progress reporting (REQUIRED)

This skill is wired into an Obsidian status dashboard that shows live ETA/progress to the user. **You MUST call `progress-tick` at the start of each step below.** This is non-negotiable — without it the user sees a frozen "amending..." row and assumes you're hung.

Use the Bash tool:

```bash
~/bin/progress-tick.sh <step> 9 "<short-label>"
```

Step numbers correspond to the **Steps** section below (1 through 9). Label is one short phrase (≤ 30 chars), e.g. `"reading PR comments"`, `"running tests"`, `"pushing commits"`.

`progress-tick.sh` is a no-op if the env vars aren't set (e.g. you're testing the skill manually) — never causes a failure. Always call it; never skip it.

---

## Steps

### 1. Parse the PR URL and locate the repo

**First:** `~/bin/progress-tick.sh 1 9 "parsing PR URL"`

```bash
URL="$ARGUMENTS"
# Extract owner/repo and PR number from the URL.
OWNER_REPO=$(echo "$URL" | sed -E 's|https?://github\.com/([^/]+/[^/]+)/pull/[0-9]+.*|\1|')
PR_NUM=$(echo "$URL" | sed -E 's|.*/pull/([0-9]+).*|\1|')
REPO_NAME=$(echo "$OWNER_REPO" | cut -d/ -f2)
REPO_PATH="$HOME/Documents/Dev/$REPO_NAME"
```

If `$REPO_PATH` doesn't exist, halt: tell the user to clone it first.

### 2. Fetch PR state

**First:** `~/bin/progress-tick.sh 2 9 "fetching PR state"`

```bash
gh pr view "$PR_NUM" --repo "$OWNER_REPO" --json state,headRefName,title,comments,url
```

- If `state` ≠ `OPEN`, halt with: "PR is `$state`, nothing to amend."
- Capture `headRefName` — that's the branch we'll work on.

### 3. Identify the user's feedback comment

**First:** `~/bin/progress-tick.sh 3 9 "identifying feedback"`

The amend is the **last human comment** on the PR. Skip:
- Comments authored by `claude[bot]`, `github-actions[bot]`, anything with `[bot]` in the login.
- Comments that look like agent confirmation replies (start with `Addressed:` or `✓` or contain `Co-Authored-By: Claude`).

If there are no human comments, halt: "no feedback comment found."

Read the comment body. **Understand it before you act.** What's broken? What should change? Is it one issue or multiple?

### 4. Switch to the PR branch

**First:** `~/bin/progress-tick.sh 4 9 "switching to PR branch"`

```bash
cd "$REPO_PATH"
git fetch origin
git checkout "$headRefName"
git pull --ff-only origin "$headRefName"
```

If the pull fails (diverged, conflicts), halt — do not try to merge. Tell the user the local branch needs attention.

### 5. Understand what's already done

**First:** `~/bin/progress-tick.sh 5 9 "reviewing prior commits"`

```bash
git log main..HEAD --oneline
```

This is the prior implementation on this branch. Read the messages. **Do not re-implement these.** The amend is a delta on top.

If a recent commit subject looks like the user's complaint is already addressed (e.g. user says "loading circle isn't showing done" and there's a commit "fix(dock): show done indicator on completion"), open that commit and check. If it really is fixed:
- Comment on the PR explaining where it was fixed (commit sha + file:line).
- Exit. Do not make a redundant commit.

### 6. Implement the delta

**First:** `~/bin/progress-tick.sh 6 9 "implementing delta"`

- Read only the source files you'll edit. No directory listings, no tree-wide greps.
- Make the smallest change that addresses the comment.
- One commit per logical change. Subject line: `fix(<scope>): <what> — addresses PR feedback`.
- If the comment has multiple distinct asks, one commit each.

### 7. Verify

**First:** `~/bin/progress-tick.sh 7 9 "running tests"`

Find and run the project's tests:

```bash
# Try, in this order:
[ -f Makefile ] && grep -q "^test:" Makefile && make test
[ -f pyproject.toml ] && (uv run pytest -x 2>/dev/null || pytest -x 2>/dev/null)
[ -f package.json ] && (npm test 2>/dev/null || yarn test 2>/dev/null)
```

- Run only tests for the changed module if the full suite is slow (>30s). Use `pytest path/to/test_module.py` or equivalent.
- If tests fail because of YOUR change → fix it.
- If tests fail for unrelated reasons → note in the commit message, but proceed.
- If there are no tests for what you changed (often true for UI runtime behavior) → say so explicitly in your final report. Do not claim it works.

### 8. Push

**First:** `~/bin/progress-tick.sh 8 9 "pushing & confirming"`

```bash
git push origin "$headRefName"
```

### 9. Confirm on the PR

**First:** `~/bin/progress-tick.sh 9 9 "final report"`

```bash
gh pr comment "$PR_NUM" --repo "$OWNER_REPO" --body "$(cat <<EOF
✓ Amend pushed.

**Addressed:**
- <bullet for each ask in the comment, with the commit sha that fixed it>

**Verification:**
- <test result: "all 47 tests pass" or "ran tests/test_dock.py — 12 pass" or "no automated test for hover behavior; manual verify recommended">

**Commits:** \`<sha1>\` … \`<shaN>\`
EOF
)"
```

### 10. Final report to the user

Print to stdout (the user is watching):
- Branch name
- Commit shas + subjects
- Test result (pass / fail / skipped, with counts)
- PR URL
- "Done." — and stop.

---

## When you should NOT proceed

| Situation | What to do |
|---|---|
| Comment is ambiguous ("make it better", "this is buggy") | Reply asking for specifics. Exit. |
| Can't find the code that the comment describes | Reply asking for a pointer. Exit. |
| Tests already fail on `main` (pre-existing) | Note it; proceed if your change passes its own tests. |
| Your change makes existing tests fail | Fix it before pushing. |
| The change is bigger than 5 minutes of work | Halt; post a comment proposing to split into a follow-up issue. |
| The branch already addresses this feedback | Comment with the commit sha; exit. Don't double-commit. |

---

## Anti-patterns (we got burned by these — don't repeat)

- ❌ Running an "explore" or "research" pass first. The branch IS the research. Read commits, edit code.
- ❌ Writing `.flow/issue-N/IMPLEMENTATION.md` and committing only that. The deliverable is **code**, the log is optional and goes in the commit message.
- ❌ Spawning a long subprocess and waiting silently. You're the agent; you have the tools; do the work directly.
- ❌ Marking work done because the prompt instructed you to, when tests didn't actually pass. Verify or say you didn't.
- ❌ Re-implementing what's already on the branch. Diff before you edit.

Done.
