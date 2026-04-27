#!/usr/bin/env bash
BIN_DIR="${BIN_DIR:-$(cd "$(dirname "$0")" && pwd)}"
# Wrap an interactive `claude` skill run with .state.json updates so the
# Obsidian status page shows live state ("amending..." / "iterating...")
# before, during, and after the run.
#
# Usage:
#   run-skill-with-state.sh <state-file> <ticket-key> <flag> <repo-dir> <claude args...>
#
# <flag> is the field name we toggle in state.json: e.g. "amending", "iterating".
# While running:    state[ticket-key][flag] = true, [flag]_pid = <pid>, [flag]_started_at = <iso>
# After exit:       deletes those fields, writes [flag]_ended_at = <iso>
#
# Both before AND after, runs inbox-process.sh once to redraw the status page.
set -u
PATH=/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin

STATE=$1
KEY=$2
FLAG=$3
REPO_DIR=$4
shift 4

mark() {
  local field=$1 value=$2
  local TMP=$(mktemp)
  if [ "$value" = "true" ]; then
    local NOW=$(date '+%Y-%m-%dT%H:%M:%S')
    jq --arg k "$KEY" --arg f "$FLAG" --argjson p $$ --arg t "$NOW" \
       '.[$k][$f] = true | .[$k][$f + "_pid"] = $p | .[$k][$f + "_started_at"] = $t' \
       "$STATE" > "$TMP" && mv "$TMP" "$STATE"
  else
    local NOW=$(date '+%Y-%m-%dT%H:%M:%S')
    jq --arg k "$KEY" --arg f "$FLAG" --arg t "$NOW" \
       'del(.[$k][$f], .[$k][$f + "_pid"]) | .[$k][$f + "_ended_at"] = $t' \
       "$STATE" > "$TMP" && mv "$TMP" "$STATE"
  fi
}

# Best-effort redraw — non-blocking, ignore failures.
redraw() { ${BIN_DIR:-$HOME/bin}/inbox-process.sh >/dev/null 2>&1 || true; }

# Mark started, redraw, run claude.
mark "$FLAG" true
redraw

trap 'mark "$FLAG" false; redraw' EXIT INT TERM

cd "$REPO_DIR" || { echo "no such dir: $REPO_DIR"; exit 1; }

# Thread these to the agent's bash subprocesses so progress-tick.sh can
# write back to the right state entry.
export INBOX_STATE_FILE="$STATE"
export INBOX_TICKET_KEY="$KEY"

"$@"
