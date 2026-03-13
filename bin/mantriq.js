#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

/**
 * MANTRIQ Node.js Wrapper
 * Executes the Python MANTRIQ CLI
 */

function findPython() {
    const pythonPaths = ['python', 'python3', 'py'];
    for (const p of pythonPaths) {
        try {
            // Simple check to see if command exists
            const { execSync } = require('child_process');
            execSync(`${p} --version`, { stdio: 'ignore' });
            return p;
        } catch (e) {
            continue;
        }
    }
    return null;
}

const pythonCmd = findPython();

if (!pythonCmd) {
    console.error('\x1b[31mError: Python not found!\x1b[0m');
    console.log('Please install Python and make sure it is in your PATH.');
    process.exit(1);
}

// Get project root (parent of bin/)
const projectRoot = path.resolve(__dirname, '..');

// Command to execute: python -m mantriq.cli
const args = ['-m', 'mantriq.cli', ...process.argv.slice(2)];

const child = spawn(pythonCmd, args, {
    cwd: projectRoot,
    stdio: 'inherit',
    env: { ...process.env, PYTHONPATH: projectRoot }
});

child.on('exit', (code) => {
    process.exit(code);
});

child.on('error', (err) => {
    console.error('\x1b[31mError launching MANTRIQ:\x1b[0m', err.message);
    process.exit(1);
});
