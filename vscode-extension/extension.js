const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

const home = process.env.HOME || '';
const pidMapPath = path.join(home, '.claude', 'pid-to-session.json');
const labelsPath = path.join(home, '.claude', 'session-labels.json');

// Track which terminals have been renamed (pid -> label)
const renamed = new Map();

function readJSON(filePath) {
    try { return JSON.parse(fs.readFileSync(filePath, 'utf-8')); }
    catch { return {}; }
}

async function sendRename(terminal, label) {
    const shellPid = await terminal.processId;
    if (!shellPid) return;

    if (renamed.get(shellPid) === label) return;

    // Write /rename command, then dismiss autocomplete with Escape, then submit with Enter.
    // Delays are needed because Claude Code's Ink TUI processes input asynchronously.
    terminal.sendText(`/rename ${label}`, false);
    await new Promise(r => setTimeout(r, 300));
    terminal.sendText('\x1b', false); // Escape - dismiss autocomplete
    await new Promise(r => setTimeout(r, 100));
    terminal.sendText('\r', false);   // Enter - submit

    renamed.set(shellPid, label);
}

async function renameAll() {
    const pidMap = readJSON(pidMapPath);
    const labels = readJSON(labelsPath);

    for (const terminal of vscode.window.terminals) {
        const shellPid = await terminal.processId;
        if (!shellPid) continue;

        const sessionId = pidMap[String(shellPid)];
        if (!sessionId) continue;

        const label = labels[sessionId];
        if (!label) continue;

        if (renamed.get(shellPid) === label) continue;

        await sendRename(terminal, label);
        await new Promise(r => setTimeout(r, 600));
    }
}

function activate(context) {
    const watch = (filePath) => {
        try {
            const watcher = fs.watch(filePath, () => renameAll());
            context.subscriptions.push({ dispose: () => watcher.close() });
        } catch {}
    };

    watch(labelsPath);
    watch(pidMapPath);

    // Terminal focus change - catches resumed sessions
    context.subscriptions.push(
        vscode.window.onDidChangeActiveTerminal(async (terminal) => {
            if (!terminal) return;
            await renameAll();
        })
    );
}

function deactivate() {}

module.exports = { activate, deactivate };
