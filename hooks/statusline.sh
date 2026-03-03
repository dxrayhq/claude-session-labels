#!/bin/bash
# Claude Code status line: shows session label + project name + context usage.
# Reads label from ~/.claude/session-labels.json (written by save-label.sh).
# Each session gets a stable color based on its ID hash.
#
# Install: add to ~/.claude/settings.json under statusLine
INPUT=$(cat)

# Parse JSON fields
eval "$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
sid = d.get('session_id', d.get('sessionId', ''))
cwd = d.get('cwd', '')
cw = d.get('context_window', {})
used = cw.get('used_percentage') or cw.get('used') or 0
used = int(round(float(used))) if used else 0
print(f'SID=\"{sid}\"')
print(f'CWD=\"{cwd}\"')
print(f'USED=\"{used}\"')
" 2>/dev/null)"

# Read session label from JSON store
LABEL=""
LABELS_FILE="$HOME/.claude/session-labels.json"
if [ -f "$LABELS_FILE" ] && [ -n "$SID" ]; then
  LABEL=$(python3 -c "
import json, sys
try:
  with open('$LABELS_FILE') as f:
    d = json.load(f)
  print(d.get('$SID', ''))
except: pass
" 2>/dev/null)
fi

# Project name from cwd
PROJECT=$(basename "$CWD")

# Color from session_id hash (stable per session, different between sessions)
COLORS=(31 32 33 34 35 36 91 92 93 94 95 96)
if [ -n "$SID" ]; then
  HASH=$(echo -n "$SID" | cksum | cut -d' ' -f1)
  COLOR=${COLORS[$((HASH % ${#COLORS[@]}))]}
else
  COLOR=37
fi

# Output
if [ -n "$LABEL" ]; then
  printf "\033[${COLOR}m%s: %s\033[0m  \033[90mctx %s%%\033[0m" "$PROJECT" "$LABEL" "$USED"
else
  printf "\033[${COLOR}m%s\033[0m  \033[90mctx %s%%\033[0m" "$PROJECT" "$USED"
fi
