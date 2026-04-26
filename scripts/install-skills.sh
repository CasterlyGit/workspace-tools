#!/bin/bash
# install-skills.sh — make the ~/.claude/commands/iterate.md skill delegate to
# the Python orchestrator. Idempotent.

set -e

SKILL=~/.claude/commands/iterate.md
TS=$(date +%s)
[ -f "$SKILL" ] && cp "$SKILL" "$SKILL.bak.$TS"

cat > "$SKILL" <<'EOF'
---
description: "Brownfield orchestrator: take a GitHub issue, run the SDD pipeline on the existing repo, open a PR. Delegates to the workspace-tools Python orchestrator (deterministic stage progression, resumable, future-proof for more stages / providers / hooks)."
---

You are running **`/iterate`**.

**Args:** $ARGUMENTS — full issue URL, owner/repo#N, or `next`.

## What to do

Run the orchestrator. It does everything (resolve issue, branch, run all 7 SDD stages, commit per stage, open PR), and stage progression is in Python so individual stage prompts saying "Stop." won't end the run early.

```bash
cd /Users/casterly/Documents/Dev/workspace-tools
python -m workspace_tools.cli iterate "$ARGUMENTS"
```

Stream the orchestrator's output to the user as it runs. Each line is prefixed with the stage name (e.g. `[explore] ...`, `[design] ...`).

If the run halts partway, leave the branch in place so the next invocation can resume — the pipeline auto-skips stages whose artifact is already on disk.

## When done

Print the PR URL (or the halt reason). Stop.
EOF

echo "✓ wrote $SKILL"
[ -f "$SKILL.bak.$TS" ] && echo "  (previous version backed up to $SKILL.bak.$TS)"
