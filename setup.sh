#!/usr/bin/env bash
set -euo pipefail

# hsops — contributor setup. Checks python3, runs the hook tests, and shows how to load
# the plugin from this clone. It installs nothing and needs no sudo.
# Usage: ./setup.sh

cd "$(dirname "$0")"

echo "=== hsops Setup ==="

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 (3.7 or newer) is required. Install it with your OS package manager, then rerun ./setup.sh." >&2; exit 1; }
echo "Found $(python3 --version)"

# Hook tests (stdlib only; they use a temporary data folder, not ~/.config/hsops)
echo "Running hook tests..."
python3 -B tests/run.py

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Load the plugin from this clone:"
echo "  Claude Code:  claude --plugin-dir \"$(pwd)\""
echo "  Codex:        codex plugin marketplace add \"$(pwd)\""
echo ""
echo "Next steps:"
echo "  1. Run the tests again after edits: python3 -B tests/run.py"
echo "  2. Read CLAUDE.md for the architecture and conventions"
echo "  3. Read CONTRIBUTING.md before opening a pull request"
