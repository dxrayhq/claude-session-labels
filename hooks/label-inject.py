#!/usr/bin/env python3
"""UserPromptSubmit hook for Claude Code session labeling.

On first prompt: injects an instruction for Claude to generate a session label.
On every prompt: writes shell PID -> session_id mapping (for the VS Code extension).

Install: add to ~/.claude/settings.json under hooks.UserPromptSubmit
"""
import json, sys, os, subprocess

data = json.load(sys.stdin)
session_id = data.get('session_id', '')
if not session_id:
    sys.exit(0)

labels_file = os.path.expanduser('~/.claude/session-labels.json')
pid_map_file = os.path.expanduser('~/.claude/pid-to-session.json')
try:
    with open(labels_file) as f:
        labels = json.load(f)
except:
    labels = {}

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

label = labels.get(session_id)

if label:
    sys.exit(0)

# No label yet - inject instruction for Claude
print("""[Session label needed. Run this as the LAST action in your response (after all other tool calls):
~/.claude/hooks/save-label.sh "emoji description"

Emoji + short description (up to 30 chars) of the USER'S GOAL - what THEY want to achieve, NOT what you (Claude) are doing to help them.

User says "find my resume, I want to update LinkedIn" -> "update LinkedIn profile" (NOT "search for resume")
User says "where's the auth code? there's a bug" -> "fix auth bug" (NOT "search auth code")

Use the user's language. No comments about the label.]""")
