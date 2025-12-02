#!/usr/bin/env python3
"""
Initialize the long-task-harness structure in the current project.

Creates:
- claude-progress.md: Work history and session notes
- features.json: Testable feature checklist
- init.sh: Environment setup script (optional)
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path


def get_script_dir():
    """Get the directory containing this script."""
    return Path(__file__).parent.resolve()


def get_skill_dir():
    """Get the skill root directory."""
    return get_script_dir().parent


def create_progress_file(project_dir: Path, project_name: str):
    """Create the claude-progress.md file from template."""
    template_path = get_skill_dir() / "assets" / "progress_template.md"
    output_path = project_dir / "claude-progress.md"

    if output_path.exists():
        print(f"  ⚠️  claude-progress.md already exists, skipping")
        return

    if template_path.exists():
        content = template_path.read_text()
        content = content.replace("{{PROJECT_NAME}}", project_name)
        content = content.replace("{{DATE}}", datetime.now().strftime("%Y-%m-%d"))
    else:
        content = f"""# {project_name} - Progress Log

## Project Overview

**Started**: {datetime.now().strftime("%Y-%m-%d")}
**Status**: In Progress

## Current State

[Describe the current state of the project]

## Session Log

### Session 1 - {datetime.now().strftime("%Y-%m-%d")}

**Goal**: [What you're working on]

**Accomplished**:
- [List accomplishments]

**Next Steps**:
- [List next steps]

**Blockers**:
- [List any blockers]
"""

    output_path.write_text(content)
    print(f"  ✅ Created claude-progress.md")


def create_features_file(project_dir: Path):
    """Create the features.json file from template."""
    template_path = get_skill_dir() / "assets" / "features_template.json"
    output_path = project_dir / "features.json"

    if output_path.exists():
        print(f"  ⚠️  features.json already exists, skipping")
        return

    if template_path.exists():
        shutil.copy(template_path, output_path)
    else:
        features = {
            "version": "1.0",
            "description": "Feature checklist for the project",
            "features": [
                {
                    "id": "feature-001",
                    "name": "Example Feature",
                    "description": "Description of the feature",
                    "steps": [
                        "Step 1: Do something",
                        "Step 2: Do something else"
                    ],
                    "passes": False,
                    "notes": ""
                }
            ]
        }
        output_path.write_text(json.dumps(features, indent=2))

    print(f"  ✅ Created features.json")


def create_init_script(project_dir: Path):
    """Create an optional init.sh script for environment setup."""
    output_path = project_dir / "init.sh"

    if output_path.exists():
        print(f"  ⚠️  init.sh already exists, skipping")
        return

    content = """#!/bin/bash
# Environment initialization script
# Customize this for your project's setup needs

echo "Initializing project environment..."

# Example: Install dependencies
# npm install
# pip install -r requirements.txt

# Example: Start services
# docker-compose up -d

# Example: Run migrations
# python manage.py migrate

echo "Environment ready!"
"""

    output_path.write_text(content)
    os.chmod(output_path, 0o755)
    print(f"  ✅ Created init.sh")


def check_claude_md(project_dir: Path) -> bool:
    """Check if CLAUDE.md exists and contains harness instructions."""
    claude_md = project_dir / "CLAUDE.md"
    if not claude_md.exists():
        return False
    content = claude_md.read_text()
    return "long-task-harness" in content.lower() or "claude-progress.md" in content


def get_claude_md_snippet() -> str:
    """Return the CLAUDE.md snippet to add."""
    return '''## Multi-Session Development

This project uses `long-task-harness`. After `/compact` or new sessions:

1. Read `claude-progress.md` for work history
2. Read `features.json` for feature tracking
3. Check `git log --oneline -10` for recent commits
4. Continue from "Next Steps" in the latest session
'''


def main():
    project_dir = Path.cwd()
    project_name = project_dir.name

    print(f"\n🚀 Initializing long-task-harness in: {project_dir}\n")

    create_progress_file(project_dir, project_name)
    create_features_file(project_dir)
    create_init_script(project_dir)

    # Check CLAUDE.md integration
    has_claude_md_integration = check_claude_md(project_dir)

    print(f"""
✅ Harness initialized!

Next steps:
1. Edit features.json to add your project's specific features
2. Update claude-progress.md with project overview
3. Customize init.sh for your environment setup
4. Create an initial git commit: git add . && git commit -m "Initialize long-task-harness"

At the start of each session, read:
- claude-progress.md for context
- features.json for next tasks
- git log for recent history
""")

    if not has_claude_md_integration:
        print("""⚠️  Add this to CLAUDE.md for context reload after /compact:
""")
        print(get_claude_md_snippet())


if __name__ == "__main__":
    main()
