# Claude Session Labels - Installation Guide

This file tells Claude Code how to install claude-session-labels.
When a user says "install this", follow these steps.

## Installation Steps

### 1. Copy hook scripts

Copy these files from the repo to `~/.claude/hooks/`:
- `hooks/label-inject.py` -> `~/.claude/hooks/label-inject.py`
- `hooks/save-label.sh` -> `~/.claude/hooks/save-label.sh`
- `hooks/statusline.sh` -> `~/.claude/hooks/statusline.sh`

Make `save-label.sh` and `statusline.sh` executable (`chmod +x`).

### 2. Merge settings into ~/.claude/settings.json

Read the user's existing `~/.claude/settings.json` first. Merge (do NOT overwrite) the following:

**hooks.SessionStart** - add this hook (append to existing array if any):
```json
{
  "hooks": [
    {
      "type": "command",
      "command": "bash -c 'INPUT=$(cat); SID=$(echo \"$INPUT\" | python3 -c \"import sys,json; print(json.load(sys.stdin).get(\\\"session_id\\\",\\\"\\\"))\" 2>/dev/null); if [ -n \"$SID\" ] && [ -n \"$CLAUDE_ENV_FILE\" ]; then echo \"export CLAUDE_SESSION_ID=\\\"$SID\\\"\" >> \"$CLAUDE_ENV_FILE\"; fi'"
    }
  ]
}
```

**hooks.UserPromptSubmit** - add this hook (append to existing array if any):
```json
{
  "hooks": [
    {
      "type": "command",
      "command": "python3 ~/.claude/hooks/label-inject.py"
    }
  ]
}
```

**permissions.allow** - add this entry (append to existing array if any):
```
"Bash(~/.claude/hooks/save-label.sh:*)"
```

**statusLine** - set this (warn user if they already have a statusLine configured):
```json
{
  "type": "command",
  "command": "~/.claude/hooks/statusline.sh"
}
```

### 3. VS Code extension (optional)

Ask the user if they want the VS Code terminal tab renaming extension.
If yes, copy `vscode-extension/` to `~/.vscode/extensions/claude-session-labels/` and tell them to reload VS Code.

Note: this extension is a workaround that steals focus briefly. Not everyone wants it.

### 4. Verify

Tell the user to restart Claude Code and send any prompt. The label should appear in the status line after 1-2 messages.
