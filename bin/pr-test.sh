#!/bin/bash
# pr-test.sh — checkout a PR's branch and LAUNCH the app on it, so you can
# see the agent's changes running. That's all this does. Tests already ran
# during the orchestrator's integration-test stage; this script is purely
# "let me try the change."
#
# Usage: pr-test.sh <repo-name> <pr-number>
#   e.g. pr-test.sh curby 14
#        pr-test.sh neon-stereo 10

set -u
REPO="${1:-}"
PR="${2:-}"
if [ -z "$REPO" ] || [ -z "$PR" ]; then
  echo "usage: pr-test.sh <repo-name> <pr-number>"
  exit 1
fi

DIR=~/Documents/Dev/$REPO
[ -d "$DIR/.git" ] || { echo "✗ no repo at $DIR"; exit 1; }
cd "$DIR"

echo "── checking out PR #$PR ──"
gh pr checkout "$PR" || { echo "✗ checkout failed"; exit 1; }
BRANCH=$(git branch --show-current)
echo "── on branch: $BRANCH ──"
echo ""

# ── Launch the app on the PR branch ─────────────────────────────────────────
echo "════════════════════════════════════════════"
echo "▶ launching $REPO on $BRANCH"
echo "  (this is the agent's code — verify the change here)"
echo "════════════════════════════════════════════"
echo ""

if [ -f main.py ]; then
  if [ ! -d .venv ]; then
    echo "── creating .venv ──"
    python3 -m venv .venv
  fi
  source .venv/bin/activate
  if [ -f requirements.txt ]; then
    pip install -q -r requirements.txt 2>&1 | tail -3
  fi
  echo "── python main.py (quit the app to come back here) ──"
  echo ""
  python -u main.py
  echo ""
  echo "── app exited ──"
elif [ -f package.json ]; then
  if [ ! -d node_modules ]; then
    echo "── npm install ──"
    npm install
  fi
  echo "── npm run dev (quit the app — Cmd-Q or Ctrl-C — to come back here) ──"
  echo ""
  npm run dev
  echo ""
  echo "── app exited ──"
else
  echo "✗ don't know how to launch $REPO — no main.py or package.json"
fi

# ── After the user quits, show next-step commands ───────────────────────────
echo ""
echo "════════════════════════════════════════════"
echo "  PR #$PR — what's next?"
echo "════════════════════════════════════════════"
echo "still on branch: $(git branch --show-current)"
echo ""
echo "  ✅ merge if it works:    gh pr merge $PR --squash --delete-branch"
echo "  ↩️  go back to main:     git switch main"
echo "  🔄 relaunch this PR app: $0 $REPO $PR"
echo ""
