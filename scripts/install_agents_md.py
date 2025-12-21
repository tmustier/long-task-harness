#!/usr/bin/env python3
"""
Add long-task-harness instructions to AGENTS.md.

For use with agents that read AGENTS.md for persistent instructions
(Codex, Droid, Pi-agent, etc.).
"""

import os
from pathlib import Path

HARNESS_MARKER = "## Multi-Session Development Protocol"

INSTRUCTIONS = """
## Multi-Session Development Protocol

This project uses structured session continuity tracking. Follow this protocol at the start of each session and before commits.

### Session Startup

At the start of each session:

1. Read `claude-progress.md` for work history (focus on last 3 sessions)
2. Read `features.json` for incomplete features
3. Run `git log --oneline -10` to see recent commits
4. Continue from "Next Steps" in the latest session entry

### During Work

- Work on ONE feature at a time
- Commit frequently with descriptive messages
- Update `features.json` when features pass tests

### Before Commits

Before any git commit:

1. Ensure `claude-progress.md` is staged with session notes
2. Update `features.json` if features were completed
3. Never commit without documenting what was accomplished

### Session End

Before ending a session, update `claude-progress.md` with:

- What was accomplished this session
- Any key decisions made (and why)
- Next steps for the following session
- Current blockers or open questions
"""


def check_agents_md(project_dir: Path) -> dict:
    """Check AGENTS.md status and return info."""
    agents_md = project_dir / "AGENTS.md"
    
    result = {
        "exists": agents_md.exists(),
        "has_harness": False,
        "path": agents_md
    }
    
    if agents_md.exists():
        content = agents_md.read_text()
        result["has_harness"] = HARNESS_MARKER in content
    
    return result


def install_instructions(project_dir: Path) -> bool:
    """Add harness instructions to AGENTS.md."""
    agents_md = project_dir / "AGENTS.md"
    
    if agents_md.exists():
        content = agents_md.read_text()
        if HARNESS_MARKER in content:
            print("  ⚠️  AGENTS.md already contains harness instructions")
            return False
        
        # Append to existing file
        with open(agents_md, "a") as f:
            f.write("\n" + INSTRUCTIONS)
        print("  ✅ Added harness instructions to existing AGENTS.md")
    else:
        # Create new file
        with open(agents_md, "w") as f:
            f.write("# Agent Instructions\n")
            f.write(INSTRUCTIONS)
        print("  ✅ Created AGENTS.md with harness instructions")
    
    return True


def uninstall_instructions(project_dir: Path) -> bool:
    """Remove harness instructions from AGENTS.md."""
    agents_md = project_dir / "AGENTS.md"
    
    if not agents_md.exists():
        print("  ⚠️  No AGENTS.md found")
        return False
    
    content = agents_md.read_text()
    
    if HARNESS_MARKER not in content:
        print("  ⚠️  No harness instructions found in AGENTS.md")
        return False
    
    # Find and remove the harness section
    lines = content.split("\n")
    new_lines = []
    skip = False
    
    for line in lines:
        if line.strip() == HARNESS_MARKER.strip():
            skip = True
            continue
        
        # Stop skipping at next major section
        if skip and line.startswith("## ") and HARNESS_MARKER not in line:
            skip = False
        
        if not skip:
            new_lines.append(line)
    
    # Write back
    new_content = "\n".join(new_lines).strip()
    if new_content:
        with open(agents_md, "w") as f:
            f.write(new_content + "\n")
        print("  ✅ Removed harness instructions from AGENTS.md")
    else:
        # File would be empty, delete it
        agents_md.unlink()
        print("  ✅ Removed AGENTS.md (was only harness instructions)")
    
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Add or remove long-task-harness instructions in AGENTS.md"
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove instructions instead of adding"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check status, don't modify"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Project directory (default: current directory)"
    )

    args = parser.parse_args()

    if args.check:
        status = check_agents_md(args.path)
        if status["exists"]:
            if status["has_harness"]:
                print("✅ AGENTS.md exists with harness instructions")
            else:
                print("⚠️  AGENTS.md exists but missing harness instructions")
        else:
            print("⚠️  No AGENTS.md found")
        return

    if args.uninstall:
        uninstall_instructions(args.path)
    else:
        install_instructions(args.path)


if __name__ == "__main__":
    main()
