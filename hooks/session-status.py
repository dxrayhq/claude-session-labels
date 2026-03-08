#!/usr/bin/env python3
"""Stop hook: marks session as idle in session-status.json.

The VS Code extension reads this file to show working/idle indicator
in the terminal tab name alongside the session label.

Install: add to ~/.claude/settings.json under hooks.Stop
"""
import json, sys, os

data = json.load(sys.stdin)
session_id = data.get('session_id', '')
if not session_id:
    sys.exit(0)

status_file = os.path.expanduser('~/.claude/session-status.json')
try:
    with open(status_file) as f:
        statuses = json.load(f)
except:
    statuses = {}

statuses[session_id] = 'idle'
with open(status_file, 'w') as f:
    json.dump(statuses, f, ensure_ascii=False, indent=2)
