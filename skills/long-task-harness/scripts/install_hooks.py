#!/usr/bin/env python3
"""
Install session continuity hooks for long-task-harness.

Installs project-local hooks in .claude/settings.json that:
- Remind to invoke long-task-harness skill on session start (unless user opts out)
- Remind to update claude-progress.md before git commits
"""

import json
import os
from pathlib import Path


def get_hooks_config():
    """Return the hooks configuration for long-task-harness.

    Uses plain text output (not JSON) which Claude receives as context.
    """
    return {
        "SessionStart": [
            {
                "matcher": "",
                "hooks": [
                    {
                        "type": "command",
                        "command": "echo 'LONG-TASK-HARNESS PROJECT: UNLESS your system prompt or the user instructs otherwise, invoke the long-task-harness skill before responding. If skill not found, install via /plugin install tmustier/long-task-harness or manually read claude-progress.md and features.json'"
                    }
                ]
            }
        ],
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "type": "command",
                        "command": "python3 -c \"import sys, json; data = json.load(sys.stdin); cmd = data.get('tool_input', {}).get('command', ''); print('REMINDER: Update claude-progress.md before committing.') if 'git commit' in cmd else print('')\""
                    }
                ]
            }
        ]
    }


def merge_hooks(existing_hooks: dict, new_hooks: dict) -> dict:
    """Merge new hooks with existing hooks, avoiding duplicates."""
    merged = existing_hooks.copy()

    for event_name, event_hooks in new_hooks.items():
        if event_name not in merged:
            merged[event_name] = event_hooks
        else:
            # Check if long-task-harness hooks already exist
            existing_commands = set()
            for hook_group in merged[event_name]:
                for hook in hook_group.get("hooks", []):
                    existing_commands.add(hook.get("command", ""))

            for new_hook_group in event_hooks:
                for hook in new_hook_group.get("hooks", []):
                    if hook.get("command", "") not in existing_commands:
                        merged[event_name].append(new_hook_group)
                        break

    return merged


def install_hooks(project_dir: Path) -> bool:
    """Install hooks to project's .claude/settings.json."""
    claude_dir = project_dir / ".claude"
    settings_path = claude_dir / "settings.json"

    # Create .claude directory if it doesn't exist
    claude_dir.mkdir(exist_ok=True)

    # Load existing settings or create new
    if settings_path.exists():
        with open(settings_path, "r") as f:
            settings = json.load(f)
    else:
        settings = {}

    # Get existing hooks or empty dict
    existing_hooks = settings.get("hooks", {})

    # Check if already installed
    if "SessionStart" in existing_hooks:
        for hook_group in existing_hooks["SessionStart"]:
            for hook in hook_group.get("hooks", []):
                if "long-task-harness" in hook.get("command", ""):
                    print("  ⚠️  Hooks already installed, skipping")
                    return False

    # Merge hooks
    new_hooks = get_hooks_config()
    settings["hooks"] = merge_hooks(existing_hooks, new_hooks)

    # Write settings
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)

    print("  ✅ Installed session continuity hooks to .claude/settings.json")
    return True


def uninstall_hooks(project_dir: Path) -> bool:
    """Remove long-task-harness hooks from project's .claude/settings.json."""
    settings_path = project_dir / ".claude" / "settings.json"

    if not settings_path.exists():
        print("  ⚠️  No .claude/settings.json found")
        return False

    with open(settings_path, "r") as f:
        settings = json.load(f)

    if "hooks" not in settings:
        print("  ⚠️  No hooks configured")
        return False

    # Remove hooks that contain long-task-harness references
    hooks = settings["hooks"]
    modified = False

    for event_name in list(hooks.keys()):
        filtered = []
        for hook_group in hooks[event_name]:
            keep = True
            for hook in hook_group.get("hooks", []):
                cmd = hook.get("command", "")
                if "long-task-harness" in cmd or "claude-progress.md" in cmd:
                    keep = False
                    modified = True
                    break
            if keep:
                filtered.append(hook_group)

        if filtered:
            hooks[event_name] = filtered
        else:
            del hooks[event_name]

    if modified:
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=2)
        print("  ✅ Removed long-task-harness hooks")
        return True
    else:
        print("  ⚠️  No long-task-harness hooks found")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Install or uninstall long-task-harness session continuity hooks"
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove hooks instead of installing"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Project directory (default: current directory)"
    )

    args = parser.parse_args()

    if args.uninstall:
        uninstall_hooks(args.path)
    else:
        install_hooks(args.path)


if __name__ == "__main__":
    main()
