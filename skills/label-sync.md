---
description: "Apply the standard label kit (~/.claude/commands/_labels.json) to a GitHub repo. Idempotent."
---

You are running **`/label-sync`**.

**Args:** $ARGUMENTS  → `<owner>/<repo>` (e.g. `CasterlyGit/curby`). If empty, use the cwd's git remote.

## What to do

1. Load `~/.claude/commands/_labels.json` and parse the `labels` array.
2. List existing labels: `gh label list --repo <owner>/<repo> --json name,color,description --limit 200`
3. For each label in the kit:
   - If the name doesn't exist → `gh label create <name> --repo <owner>/<repo> --color <hex> --description "<desc>"`
   - If it exists with different color/description → `gh label edit <name> --repo <owner>/<repo> --color <hex> --description "<desc>"`
   - If identical → skip silently
4. Report a one-line per repo summary: `created N, updated M, kept K`.

Do **not** delete labels that exist on the repo but aren't in the kit — preserve any user-added labels.

If `gh` returns an auth error → tell the user `gh auth refresh -s repo` and stop.
