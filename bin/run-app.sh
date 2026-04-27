#!/bin/bash
# run-app.sh — switch to the latest main of a project and launch its app.

REPO="${1:-}"
[ -z "$REPO" ] && { echo "usage: run-app.sh <repo-name>"; exit 1; }

DIR=~/Documents/Dev/$REPO
[ -d "$DIR/.git" ] || { echo "✗ no repo at $DIR"; exit 1; }
cd "$DIR" || { echo "✗ couldn't cd into $DIR"; exit 1; }

echo ""
echo "════════════════════════════════════════════"
echo "▶ $REPO — pulling latest main and launching"
echo "════════════════════════════════════════════"
echo ""

echo "── $REPO: syncing main ──"
if ! git switch main 2>&1; then
  echo "✗ couldn't switch to main — there may be uncommitted changes."
  echo "  current branch: $(git branch --show-current)"
  echo "  status:"
  git status --short
  exit 1
fi

git pull --ff-only 2>&1 | tail -3
echo ""

if [ -f main.py ]; then
  if [ ! -d .venv ]; then
    echo "── creating .venv ──"
    python3 -m venv .venv
  fi
  source .venv/bin/activate
  if [ -f requirements.txt ]; then
    echo "── checking deps ──"
    pip install -q -r requirements.txt 2>&1 | tail -3
  fi
  echo ""
  echo "── launching: python main.py ──"
  echo "(curby's voice indicator will appear at your cursor)"
  echo "(press Esc inside curby to quit, or Ctrl+C here)"
  echo ""
  python -u main.py
  EXIT=$?
  echo ""
  echo "── curby exited (code $EXIT) ──"
elif [ -f package.json ]; then
  if [ ! -d node_modules ]; then
    echo "── npm install ──"
    npm install
  fi
  echo ""
  echo "── launching: npm run dev ──"
  npm run dev
  echo ""
  echo "── exited ──"
else
  echo "✗ don't know how to run $REPO — no main.py or package.json"
  exit 1
fi
