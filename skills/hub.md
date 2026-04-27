---
description: "Bootstrap or refresh the master Workspace project — your Jira-like all-up view of issues across every repo."
---

You are running **`/hub`**.

**Args:** $ARGUMENTS — optional. If `refresh`, just re-pull issues from all linked repos. Otherwise: full bootstrap (idempotent).

## What this does

GitHub Projects v2 supports multi-repo. We create one master Project ("Workspace") that aggregates issues from every repo you `/onboard`. This is your daily dashboard — Backlog / Up Next / In Progress / In Review / Done across everything.

## Steps

### 1. Create or find the Workspace project

```bash
HUB_NUM=$(gh project list --owner @me --format json --jq '.projects[] | select(.title=="Workspace") | .number')
if [ -z "$HUB_NUM" ]; then
  HUB_NUM=$(gh project create --owner @me --title "Workspace" --format json --jq .number)
fi
echo "Hub project #$HUB_NUM"
```

### 2. Apply the board kit

Invoke `/board-setup` with `$HUB_NUM`. Same Status options (Backlog → Done), same Priority + Target fields.

### 3. Discover repos to link

```bash
# All repos owned by the user. Filter to ones that have at least one open issue or PR.
gh repo list <owner> --json nameWithOwner,isArchived --jq '.[] | select(.isArchived==false) | .nameWithOwner'
```

For each, link to the hub:

```bash
gh project link $HUB_NUM --owner @me --repo <owner>/<repo>
```

### 4. Backfill open issues

```bash
for REPO in <linked repos>; do
  gh issue list --repo "$REPO" --state open --json url --jq '.[].url' | while read URL; do
    gh project item-add $HUB_NUM --owner @me --url "$URL" 2>/dev/null || true
  done
done
```

### 5. Add convenient views (best-effort — graphql)

The hub becomes much more useful with extra views:

- **Up Next** — filter `Status = "Up Next"`, sort by Priority ascending
- **By Repo** — group by Repository
- **Roadmap** — timeline view, group by Target

Try via GraphQL `createProjectV2View`. If unsupported by your gh version, leave the user a one-line note pointing them to the project URL to set up views by hand. Don't fail the whole bootstrap on this.

### 6. Print summary

```
Hub: https://github.com/users/<owner>/projects/<num>
  Repos linked: <count>
  Open issues: <count>
  Views: <created list, or "set up manually">
```
