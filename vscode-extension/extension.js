const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

const home = process.env.HOME || '';
const pidMapPath = path.join(home, '.claude', 'pid-to-session.json');
const labelsPath = path.join(home, '.claude', 'session-labels.json');
const statusPath = path.join(home, '.claude', 'session-status.json');

const DEBOUNCE_MS = 1000;
const STATE_KEY = 'claude-rename.done';

let renameTimer = null;
let globalState = null;

function readJSON(filePath) {
    try { return JSON.parse(fs.readFileSync(filePath, 'utf-8')); }
    catch { return {}; }
}

function getRenamed() {
    return globalState ? globalState.get(STATE_KEY, {}) : {};
}

function setRenamed(sessionId, label) {
    if (!globalState) return;
    const map = getRenamed();
    map[sessionId] = label;
    globalState.update(STATE_KEY, map);
}

async function sendRename(terminal, label, sessionId) {
    if (getRenamed()[sessionId] === label) return;

    // /rename via sendText - writes to PTY, no focus switch
    terminal.sendText(`/rename ${label}`, false);
    await new Promise(r => setTimeout(r, 300));
    terminal.sendText('\x1b', false);
    await new Promise(r => setTimeout(r, 100));
    terminal.sendText('\r', false);

    setRenamed(sessionId, label);
}

async function renameIdleSessions() {
    const pidMap = readJSON(pidMapPath);
    const labels = readJSON(labelsPath);
    const statuses = readJSON(statusPath);
    const renamed = getRenamed();

    for (const terminal of vscode.window.terminals) {
        const shellPid = await terminal.processId;
        if (!shellPid) continue;

        const sessionId = pidMap[String(shellPid)];
        if (!sessionId) continue;

        const label = labels[sessionId];
        if (!label) continue;

        // Only rename when Claude is idle - no interruption
        const status = statuses[sessionId];
        if (status !== 'idle') continue;

        if (renamed[sessionId] === label) continue;

        await sendRename(terminal, label, sessionId);
        await new Promise(r => setTimeout(r, 600));
    }
}

function scheduleRename() {
    if (renameTimer) clearTimeout(renameTimer);
    renameTimer = setTimeout(() => {
        renameTimer = null;
        renameIdleSessions();
    }, DEBOUNCE_MS);
}

function watchFile(filePath, context) {
    try {
        let last = '';
        try { last = fs.readFileSync(filePath, 'utf-8'); } catch {}
        const watcher = fs.watch(filePath, () => {
            try {
                const current = fs.readFileSync(filePath, 'utf-8');
                if (current === last) return;
                last = current;
                scheduleRename();
            } catch {}
        });
        context.subscriptions.push({ dispose: () => watcher.close() });
    } catch {}
}

function activate(context) {
    globalState = context.globalState;

    watchFile(statusPath, context);
    watchFile(labelsPath, context);

    context.subscriptions.push(
        vscode.window.onDidChangeActiveTerminal(() => scheduleRename())
    );
}

function deactivate() {
    if (renameTimer) clearTimeout(renameTimer);
}

module.exports = { activate, deactivate };
