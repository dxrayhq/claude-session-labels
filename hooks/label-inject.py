#!/usr/bin/env python3
"""UserPromptSubmit hook for Claude Code session labeling.

On first prompt: generates a label from the user's message and saves it.
On every prompt: writes shell PID -> session_id mapping and "working" status.

Install: add to ~/.claude/settings.json under hooks.UserPromptSubmit
"""
import json, sys, os, subprocess

data = json.load(sys.stdin)
session_id = data.get('session_id', '')
if not session_id:
    sys.exit(0)

labels_file = os.path.expanduser('~/.claude/session-labels.json')
pid_map_file = os.path.expanduser('~/.claude/pid-to-session.json')
status_file = os.path.expanduser('~/.claude/session-status.json')
try:
    with open(labels_file) as f:
        labels = json.load(f)
except:
    labels = {}

# Write "working" status for VS Code extension tab indicator
try:
    with open(status_file) as f:
        statuses = json.load(f)
except:
    statuses = {}
statuses[session_id] = 'working'
with open(status_file, 'w') as f:
    json.dump(statuses, f, ensure_ascii=False, indent=2)

# Find the OUTERMOST shell PID (terminal shell, not Claude's subprocess).
# Walks the process tree upward and picks the last shell encountered.
def find_shell_pid():
    pid = os.getpid()
    last_shell = None
    while pid > 1:
        try:
            r = subprocess.run(['ps', '-o', 'ppid=,comm=', '-p', str(pid)],
                               capture_output=True, text=True)
            parts = r.stdout.strip().split(None, 1)
            if len(parts) < 2:
                break
            ppid = int(parts[0])
            comm = os.path.basename(parts[1].strip()).lstrip('-')
            if comm in ('zsh', 'bash', 'fish', 'sh'):
                last_shell = pid
            pid = ppid
        except:
            break
    return last_shell

shell_pid = find_shell_pid()
if shell_pid:
    try:
        with open(pid_map_file) as f:
            pid_map = json.load(f)
    except:
        pid_map = {}
    pid_map[str(shell_pid)] = session_id
    with open(pid_map_file, 'w') as f:
        json.dump(pid_map, f, ensure_ascii=False, indent=2)

# If label already exists, nothing more to do
label = labels.get(session_id)
if label:
    sys.exit(0)

# No label yet - inject instruction for Claude to generate one
print("""[Session label needed. Run this as the LAST action in your response (after all other tool calls):
~/.claude/hooks/save-label.sh "emoji описание"

Emoji + short description (up to 30 chars) of the USER'S GOAL - what THEY want to achieve, NOT what you (Claude) are doing to help them.

User says "найди моё резюме, хочу линкедин обновить" -> "обновить LinkedIn" (NOT "поиск резюме")
User says "где код авторизации? там баг" -> "фикс бага авторизации" (NOT "поиск кода авторизации")

Use the user's language. No comments about the label.]""")
