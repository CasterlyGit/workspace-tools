---
description: "Implement an inbox ticket end-to-end: file as GitHub issue (if needed), branch, code, test, push, open PR. One agent loop, no Python orchestrator. Target 3-8 minutes wall clock."
---

You are running **`/iterate-fast`** — the inbox-ticket-to-PR skill.

**Args:** `$ARGUMENTS` — either a path to an inbox markdown file (e.g. `~/Documents/Dev/curby/inbox/fix-foo.md`), or a GitHub issue URL, or `owner/repo#N`.

This skill replaces the Python orchestrator. One agent, one loop, the actual code. No sub-stages, no `.flow/` artifacts, no spec ceremony unless the ticket explicitly asks for it.

---

## Hard constraints

1. **Time budget:** 8 minutes max for the code change. If it's bigger, halt and propose splitting.
2. **Token discipline:** read the ticket, read the source you'll edit, write code. Skip exploration unless the ticket is genuinely ambiguous about location.
3. **Code first, docs maybe.** Deliverable is committed code. Spec artifacts (`.flow/*.md`) only if the ticket has `pipeline: full` (rare).
4. **Verify before claiming done.** Run tests. Report what passed.
5. **Halt if blocked.** Ambiguous ticket → ask. Can't find the code → ask. Don't guess.

---

## Steps

### 1. Resolve the input

```bash
ARG="$ARGUMENTS"
```

- If `$ARG` matches `*/inbox/*.md` → it's an inbox file. Read it. Repo is the parent (`dirname dirname $ARG`).
- If `$ARG` is a GitHub URL → `gh issue view` it.
- If `$ARG` is `owner/repo#N` → split, `gh issue view N --repo owner/repo`.

Get: `repo_path`, `issue_number` (file as new issue if inbox-only), `title`, `body`.

### 2. File the ticket as a GitHub issue (if it's inbox-only)

Inbox-only means: a markdown file with no `gh_issue:` line in its frontmatter or body.

```bash
gh issue create --repo "$OWNER_REPO" --title "$TITLE" --body "$BODY" --label "inbox"
```

Capture the issue number. Update the inbox file: prepend a line `<!-- gh_issue: <num> -->` so we don't double-file.

### 3. Create / switch to the branch

```bash
cd "$REPO_PATH"
git fetch origin

# Reuse an existing auto/<N>-* branch if any (resume across slug changes)
EXISTING=$(git branch --list "auto/${ISSUE_NUM}-*" --format "%(refname:short)" | head -1)
if [ -n "$EXISTING" ]; then
  BRANCH="$EXISTING"
  git checkout "$BRANCH"
else
  SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9' '-' | sed 's/--*/-/g; s/^-//; s/-$//' | cut -c1-40)
  BRANCH="auto/${ISSUE_NUM}-${SLUG}"
  git checkout -b "$BRANCH" main
fi
```

### 4. Read the ticket carefully

What is the user actually asking for?

- **Acceptance criteria** (`AC-1`, `AC-2`, …) → each must be addressed.
- **Out-of-scope** → respect it.
- **Magic line `pipeline: full`** → user wants full SDD ceremony with `.flow/` artifacts. (Rare; if present, do REQUIREMENTS / DESIGN / IMPLEMENTATION as separate commits in `.flow/issue-<num>/`.)
- **Magic line `pipeline: bugfix`** → write a regression test alongside the fix.

Default: implement directly, write a regression test if the change is non-trivial, no spec docs.

### 5. Implement

- Read source files you'll edit. Use the existing code's patterns and style.
- One commit per coherent change. Subject: `<type>(<scope>): <what> — issue #<N>`.
- Don't add features beyond the ACs.
- Don't refactor surrounding code unless the ticket asks.

### 6. Test

Find the test runner (Makefile, pyproject.toml, package.json) and run:
- Targeted tests for what you changed (fast).
- Full suite if it's quick (<30s).

If tests fail because of your change → fix.
If they fail pre-existing → note and proceed.
If no relevant test coverage → say so in the final report.

### 7. Push and open PR

```bash
git push -u origin "$BRANCH"

gh pr create --repo "$OWNER_REPO" \
  --title "$TITLE" \
  --body "$(cat <<EOF
Closes #${ISSUE_NUM}.

## Changes
- <bullet per commit>

## Verification
- <test result>

🤖 Implemented via /iterate-fast
EOF
)" \
  --base main --head "$BRANCH"
```

If a PR is already open for this branch, skip — just push.

### 8. Final report

Print to stdout:
- Issue number + URL
- Branch name
- Commits (sha + subject)
- Test result
- PR URL
- "Done." — and stop.

---

## When to halt

| Situation | Action |
|---|---|
| Ticket is empty or one-line vague ("fix it", "make it work") | Reply asking for specifics on the issue. Exit. |
| Can't find the code area the ticket describes | Comment on the issue asking for a pointer. Exit. |
| Required dependency missing (`gh`, repo not cloned) | Tell the user how to fix it. Exit. |
| Change is >8 minutes of work | Propose splitting into smaller issues. Exit. |
| You'd need to break a public API | Halt; the ticket should explicitly authorize this. |

---

## After the PR is open

This skill is **done** when the PR is open. The user reviews. If they want changes, they post a PR comment and run `/pr-amend <pr-url>` — that's a different skill, with its own contract.

Do **not** chain into reviewing your own work, opening follow-ups, or starting a new task. Stop.
