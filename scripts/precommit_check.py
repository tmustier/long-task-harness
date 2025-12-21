#!/usr/bin/env python3
"""
Pre-commit hook for long-task-harness.

Checks if claude-progress.md is staged and outputs session metadata.
Called by Claude Code's PreToolUse hook on git commit commands.

Input: JSON on stdin with tool_input.command
Output: Metadata on stderr, exit code 0 (allow) or 2 (block)
"""

import json
import subprocess
import sys


def get_git_metadata():
    """Gather git metadata for the current staged changes."""
    # Get staged files
    staged = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True, text=True
    )
    staged_files = staged.stdout.strip().split('\n') if staged.stdout.strip() else []

    # Get diff stats
    diffstat = subprocess.run(
        ['git', 'diff', '--cached', '--stat'],
        capture_output=True, text=True
    )

    # Get last commit hash
    last_commit = subprocess.run(
        ['git', 'rev-parse', '--short', 'HEAD'],
        capture_output=True, text=True
    )
    last_hash = last_commit.stdout.strip() if last_commit.returncode == 0 else 'unknown'

    # Get current branch
    branch = subprocess.run(
        ['git', 'branch', '--show-current'],
        capture_output=True, text=True
    )
    branch_name = branch.stdout.strip() if branch.returncode == 0 else 'unknown'

    # Format file changes
    file_changes = []
    for line in diffstat.stdout.strip().split('\n')[:-1]:  # Skip summary line
        if line.strip():
            file_changes.append(line.strip())

    return {
        'staged_files': staged_files,
        'last_hash': last_hash,
        'branch': branch_name,
        'file_changes': file_changes
    }


def format_metadata(meta: dict) -> str:
    """Format metadata for display."""
    lines = [
        "",
        "Session Metadata (for claude-progress.md):",
        f"  Commits: {meta['last_hash']}..HEAD",
        f"  Branch: {meta['branch']}",
        "  Files Changed:"
    ]
    for change in meta['file_changes']:
        lines.append(f"    {change}")
    return '\n'.join(lines)


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

    # Get metadata
    meta = get_git_metadata()
    metadata_str = format_metadata(meta)

    # Check if progress.md is staged
    progress_staged = 'claude-progress.md' in meta['staged_files']

    if progress_staged:
        print(f"[OK] claude-progress.md is staged.{metadata_str}", file=sys.stderr)
        sys.exit(0)
    else:
        print(f"""BLOCKED: claude-progress.md not staged.
{metadata_str}

Steps:
1. Update claude-progress.md with session notes (include metadata above)
2. git add claude-progress.md
3. git commit""", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
