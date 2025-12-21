#!/usr/bin/env python3
"""
Install session continuity hooks for Cursor (1.7+).

Creates .cursor/hooks.json with afterFileEdit hook that reminds
the agent to update claude-progress.md when committing.
"""

import json
import os
from pathlib import Path


def get_hooks_config():
    """Return the hooks configuration for long-task-harness in Cursor."""
    return {
        "version": 1,
        "hooks": {
            "afterFileEdit": [
                {
                    "command": "python3 ~/.claude/skills/long-task-harness/scripts/cursor_after_edit.py"
                }
            ]
        }
    }


def install_hooks(project_dir: Path) -> bool:
    """Install hooks to project's .cursor/hooks.json."""
    cursor_dir = project_dir / ".cursor"
    hooks_path = cursor_dir / "hooks.json"

    cursor_dir.mkdir(exist_ok=True)

    if hooks_path.exists():
        with open(hooks_path, "r") as f:
            existing = json.load(f)
        
        # Check if already installed
        if "hooks" in existing and "afterFileEdit" in existing.get("hooks", {}):
            for hook in existing["hooks"]["afterFileEdit"]:
                if "long-task-harness" in hook.get("command", ""):
                    print("  ⚠️  Cursor hooks already installed, skipping")
                    return False

        # Merge hooks
        if "hooks" not in existing:
            existing["hooks"] = {}
        if "afterFileEdit" not in existing["hooks"]:
            existing["hooks"]["afterFileEdit"] = []
        
        new_hooks = get_hooks_config()
        existing["hooks"]["afterFileEdit"].extend(new_hooks["hooks"]["afterFileEdit"])
        existing["version"] = 1
    else:
        existing = get_hooks_config()

    with open(hooks_path, "w") as f:
        json.dump(existing, f, indent=2)

    print("  ✅ Installed Cursor hooks to .cursor/hooks.json")
    return True


def uninstall_hooks(project_dir: Path) -> bool:
    """Remove long-task-harness hooks from .cursor/hooks.json."""
    hooks_path = project_dir / ".cursor" / "hooks.json"

    if not hooks_path.exists():
        print("  ⚠️  No .cursor/hooks.json found")
        return False

    with open(hooks_path, "r") as f:
        config = json.load(f)

    if "hooks" not in config:
        print("  ⚠️  No hooks configured")
        return False

    modified = False
    for event_name in list(config["hooks"].keys()):
        filtered = []
        for hook in config["hooks"][event_name]:
            if "long-task-harness" not in hook.get("command", ""):
                filtered.append(hook)
            else:
                modified = True
        
        if filtered:
            config["hooks"][event_name] = filtered
        else:
            del config["hooks"][event_name]

    if modified:
        with open(hooks_path, "w") as f:
            json.dump(config, f, indent=2)
        print("  ✅ Removed long-task-harness hooks from Cursor")
        return True
    else:
        print("  ⚠️  No long-task-harness hooks found")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Install or uninstall long-task-harness hooks for Cursor"
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
