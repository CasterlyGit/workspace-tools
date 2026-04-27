#!/bin/bash
BIN_DIR="${BIN_DIR:-$(cd "$(dirname "$0")" && pwd)}"
# inbox-watcher.sh — fswatch loop that fires inbox-process.sh on new/deleted
# .md files inside any repo's inbox/ directory.

PATH=/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin
DEV=${DEV:-$HOME/Documents/Dev}

# Refresh vault symlinks first so newly onboarded repos get watched too
${BIN_DIR:-$HOME/bin}/sync-vault.sh 2>&1 || true

# Build the list of paths to watch
PATHS=()
for project in "$DEV"/*/; do
  [ -d "$project/.git" ] || continue
  mkdir -p "$project/inbox"
  PATHS+=("$project/inbox")
done

if [ ${#PATHS[@]} -eq 0 ]; then
  echo "[inbox-watcher] no repos to watch — sleeping until restart"
  exec tail -f /dev/null
fi

echo "[inbox-watcher] watching ${#PATHS[@]} path(s):"
for p in "${PATHS[@]}"; do echo "  - $p"; done

# Bootstrap scan: process every existing top-level .md in each inbox at
# startup so files created while the watcher was off get picked up.
echo "[inbox-watcher] bootstrap scan…"
for p in "${PATHS[@]}"; do
  for f in "$p"/*.md; do
    [ -f "$f" ] || continue
    ${BIN_DIR:-$HOME/bin}/inbox-process.sh "$f" || true
  done
done
# Also regenerate the status file once after the scan
${BIN_DIR:-$HOME/bin}/inbox-process.sh
echo "[inbox-watcher] bootstrap done; entering live watch"

VAULT=${VAULT:-$HOME/Documents/ObsidianVault/Specs}

ITER_LOG=/tmp/inbox-iterate.log
[ -f "$ITER_LOG" ] || touch "$ITER_LOG"

fswatch -0 \
  --event Created --event Removed --event Renamed \
  --event MovedTo --event MovedFrom --event Updated \
  --exclude "\.state\.json$" \
  --exclude "\.gitkeep$" \
  --exclude "\.gitignore$" \
  "${PATHS[@]}" \
  "$ITER_LOG" \
| while IFS= read -r -d "" CHANGED; do
    case "$CHANGED" in
      */inbox/*.md)
        REL=${CHANGED#*/inbox/}
        case "$REL" in */*) continue ;; esac
        ${BIN_DIR:-$HOME/bin}/inbox-process.sh "$CHANGED" || true
        ;;
      "$ITER_LOG")
        # Agent printed something — refresh the status table to show new
        # stage count + breadcrumb. Throttled by the script's own debounce.
        ${BIN_DIR:-$HOME/bin}/inbox-process.sh || true
        ;;
    esac
  done
