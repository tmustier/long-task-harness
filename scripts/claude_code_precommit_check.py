#!/usr/bin/env python3
"""
Pre-commit hook for long-task-harness.

Checks if long-task-progress.md is staged and outputs session metadata.
Called by Claude Code's PreToolUse hook on git commit commands.

Input: JSON on stdin with tool_input.command
Output: Metadata on stderr, exit code 0 (allow with warning or success)
"""

import json
import sys

from precommit_check import run_check


def main():
    # Parse input from Claude Code hook
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # Not valid JSON, allow command
        sys.exit(0)

    command = data.get('tool_input', {}).get('command', '')

    # Only check git commit commands
    if 'git commit' not in command:
        sys.exit(0)

    sys.exit(run_check())


if __name__ == "__main__":
    main()
