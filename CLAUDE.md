# Claude Session Labels - Installation Guide

This file tells Claude Code how to install claude-session-labels.
When a user says "install this", follow these steps.

## Installation Steps

### 1. Copy hook scripts

Copy these files from the repo to `~/.claude/hooks/`:
- `hooks/label-inject.py` -> `~/.claude/hooks/label-inject.py`
- `hooks/save-label.sh` -> `~/.claude/hooks/save-label.sh`
- `hooks/statusline.sh` -> `~/.claude/hooks/statusline.sh`
- `hooks/session-status.py` -> `~/.claude/hooks/session-status.py`

Make `save-label.sh` and `statusline.sh` executable (`chmod +x`).

### 2. Merge settings into ~/.claude/settings.json

Read the user's existing `~/.claude/settings.json` first. Merge (do NOT overwrite) the entries below.

CRITICAL: The hooks format requires a NESTED structure. Each event contains an array of rule groups, and each rule group has a `hooks` array inside it. Do NOT flatten this structure.

After merging, the hooks section should look like this (the user may have other entries too):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'INPUT=$(cat); SID=$(echo \"$INPUT\" | python3 -c \"import sys,json; print(json.load(sys.stdin).get(\\\"session_id\\\",\\\"\\\"))\" 2>/dev/null); if [ -n \"$SID\" ] && [ -n \"$CLAUDE_ENV_FILE\" ]; then echo \"export CLAUDE_SESSION_ID=\\\"$SID\\\"\" >> \"$CLAUDE_ENV_FILE\"; fi'"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/label-inject.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/session-status.py"
          }
        ]
      }
    ]
  },
  "permissions": {
    "allow": [
      "Bash(~/.claude/hooks/save-label.sh:*)"
    ]
  },
  "statusLine": {
    "type": "command",
    "command": "~/.claude/hooks/statusline.sh"
  }
}
```

WRONG (will cause "Expected array" error):
```json
"SessionStart": [{ "type": "command", "command": "..." }]
```

CORRECT (note the nested `hooks` array):
```json
"SessionStart": [{ "hooks": [{ "type": "command", "command": "..." }] }]
```

### 3. VS Code extension (optional)

Ask the user if they want the VS Code terminal tab renaming extension.
If yes, copy `vscode-extension/` to `~/.vscode/extensions/claude-session-labels/` and tell them to reload VS Code.

Note: this extension sends `/rename` to terminals via `sendText()` only when Claude is idle (triggered by the Stop hook). It uses persistent state (VS Code globalState, keyed by session_id) to avoid re-renaming sessions that already have the correct label. Not everyone wants it.

### 4. Verify

Tell the user to restart Claude Code and send any prompt. The label should appear in the status line after 1-2 messages.
