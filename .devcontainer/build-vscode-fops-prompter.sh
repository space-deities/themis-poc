#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../vscode-fops-prompter"

# Install deps, compile TS, then package a VSIX into this folder
npm ci
npm run compile
npx --yes @vscode/vsce package
