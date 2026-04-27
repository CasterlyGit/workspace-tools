#!/bin/bash
# sync-vault.sh — keep ~/Documents/ObsidianVault/Specs in sync with active repos.
#
# For every git repo at ~/Documents/Dev/<name>/, ensure:
#   1. ~/Documents/Dev/<name>/inbox/ exists with a .gitignore + .gitkeep
#   2. ~/Documents/ObsidianVault/Specs/<name> is a symlink → that repo's inbox/
#
# `inbox/` is the user's local "Jira tickets" folder — only ticket .md files
# show up there. SDD pipeline artifacts (REQUIREMENTS, DESIGN, etc.) stay in
# the repo's `.flow/` directory, NOT in the vault.

set -u
VAULT=${VAULT:-$HOME/Documents/ObsidianVault/Specs}
DEV=${DEV:-$HOME/Documents/Dev}
mkdir -p "$VAULT"

cat > "$VAULT/README.md" <<'EOF'
# Workspace

Each subfolder is a project (a GitHub repo cloned to `~/Documents/Dev/<repo>/`).

## How to "raise a ticket"

1. Open a project folder (e.g. `curby/`).
2. Create a new note. Filename → issue title; body → issue body.
3. Save. The watcher files the issue on GitHub, adds it to the project + the
   Workspace hub, and (default) kicks off `/iterate` so an agent starts
   working on it immediately.
4. **Delete the file when done** — the corresponding GitHub issue auto-closes.

## Magic lines (optional, anywhere in the first 10 lines)

```
type: bug          # default: feature. valid: bug | feature | polish | chore | docs | security
priority: p1       # valid: p0 | p1 | p2 | p3
auto-iterate: no   # default: yes. set "no" to file the issue but skip running /iterate
```

A first-line `# Heading` overrides the filename as the title.

## What's NOT here

SDD pipeline artifacts (REQUIREMENTS, DESIGN, TEST_PLAN, etc.) live in each
repo's `.flow/` directory — committed alongside the code. Open them directly
from `~/Documents/Dev/<repo>/.flow/` if you want to read or edit them.
EOF

for project in "$DEV"/*/; do
  [ -d "$project/.git" ] || continue
  name=$(basename "$project")
  mkdir -p "$project/inbox"
  # gitignore for the inbox/ — keep the dir, ignore the contents
  if [ ! -f "$project/inbox/.gitignore" ]; then
    cat > "$project/inbox/.gitignore" <<'EOF'
*
!.gitignore
!.gitkeep
EOF
    touch "$project/inbox/.gitkeep"
  fi
  ln -snf "$project/inbox" "$VAULT/$name"
done

echo "[sync-vault] vault refreshed — $(ls -1 "$VAULT" | grep -v '^README' | wc -l | tr -d ' ') projects symlinked"
