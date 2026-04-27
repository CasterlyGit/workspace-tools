#!/usr/bin/env bash
BIN_DIR="${BIN_DIR:-$(cd "$(dirname "$0")" && pwd)}"
# Emit a progress checkpoint from inside a running skill.
# Updates inbox/.state.json and triggers a non-blocking status redraw.
#
# Usage:  progress-tick.sh <step> <total> "<short-label>"
#
# Env (set by run-skill-with-state.sh launcher):
#   INBOX_STATE_FILE  — path to inbox/.state.json
#   INBOX_TICKET_KEY  — the ticket filename (key in state.json)
#
# Silent failure if env not set — calling progress-tick from a non-launcher
# session is a no-op, not an error.
set -u
PATH=/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin

STATE=${INBOX_STATE_FILE:-}
KEY=${INBOX_TICKET_KEY:-}
if [ -z "$STATE" ] || [ -z "$KEY" ] || [ ! -f "$STATE" ]; then
  exit 0
fi

STEP=${1:?step required}
TOTAL=${2:?total required}
LABEL=${3:-}
NOW=$(date '+%Y-%m-%dT%H:%M:%S')

TMP=$(mktemp)
jq --arg k "$KEY" --argjson s "$STEP" --argjson t "$TOTAL" --arg l "$LABEL" --arg ts "$NOW" \
   '.[$k].progress = {step: $s, total: $t, label: $l, updated_at: $ts}' \
   "$STATE" > "$TMP" && mv "$TMP" "$STATE"

# Non-blocking redraw — don't slow the agent down.
${BIN_DIR:-$HOME/bin}/inbox-process.sh >/dev/null 2>&1 &
disown 2>/dev/null || true
exit 0
