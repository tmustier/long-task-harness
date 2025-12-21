#!/usr/bin/env python3
"""
Cursor afterFileEdit hook for long-task-harness.

Called by Cursor after file edits. Checks if progress tracking
files need updating and outputs reminders.

Input: JSON payload on stdin with edited file info
Output: Reminder message on stdout (shown to agent)
"""

import json
import sys
import os
from pathlib import Path


def main():
    try:
        payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    except (json.JSONDecodeError, Exception):
        payload = {}

    edited_file = payload.get("filePath", "")
    cwd = Path.cwd()
    progress_file = cwd / "claude-progress.md"
    features_file = cwd / "features.json"

    # Skip if editing the progress files themselves
    if "claude-progress.md" in edited_file or "features.json" in edited_file:
        sys.exit(0)

    # Check if this is a harness project
    if not progress_file.exists():
        sys.exit(0)

    # Output reminder (this goes to agent context)
    print("📋 LONG-TASK-HARNESS REMINDER: This project uses session continuity tracking.")
    print("   Before ending this session or committing, update:")
    print("   - claude-progress.md with session notes")
    print("   - features.json if any features were completed")


if __name__ == "__main__":
    main()
