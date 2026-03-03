#!/bin/bash
# Saves a session label to the JSON store.
# Called by Claude via the Bash tool as the last action in a response.
# Usage: save-label.sh "emoji description"
LABEL="$1"
SID="$CLAUDE_SESSION_ID"
LABELS_FILE="$HOME/.claude/session-labels.json"

if [ -z "$LABEL" ] || [ -z "$SID" ]; then
  exit 0
fi

python3 -c "
import json, os
path = os.path.expanduser('$LABELS_FILE')
try:
    with open(path) as f: data = json.load(f)
except: data = {}
data['$SID'] = '''$LABEL'''
with open(path, 'w') as f: json.dump(data, f, ensure_ascii=False, indent=2)
"
