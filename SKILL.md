---
name: long-task-harness
description: Maintains continuity across long-running tasks that span multiple agent sessions. Use when starting or resuming a complex project that spans multiple sessions, or for tasks with many discrete features requiring iterative development.
---

# Long Task Harness

Structured workflows for maintaining continuity across agent sessions. Addresses the "shift change" problem where context is lost between sessions.

## First-Time Setup

**On first invocation**, check if `.long-task-harness/long-task-progress.md` exists in the project.

### If it doesn't exist: Initialize

```bash
python3 <SKILL_PATH>/scripts/init_harness.py
```

This creates a `.long-task-harness/` directory containing:
- `long-task-progress.md` - Session history and notes
- `features.json` - Feature tracking with pass/fail status
- `init.sh` - Environment setup script (optional)

### Then: Ensure persistent invocation

Check if AGENTS.md (for Codex/Droid/Cursor/Pi) or CLAUDE.md (for Claude Code) contains the harness snippet.

If not, prompt the user:

> "I notice this project doesn't have long-task-harness configured for automatic invocation. Would you like me to add the following to [AGENTS.md / CLAUDE.md]?
>
> ```markdown
> ## Multi-Session Development
> 
> This project uses long-task-harness for session continuity.
> At session start or after context reset, invoke the skill at:
> <SKILL_PATH>
> ```
>
> Where would you like me to add this?"

Use the actual path where you loaded this skill from for `<SKILL_PATH>`.

### Optional: Claude Code Hooks

For Claude Code users who want automatic enforcement:

> "Would you like to install Claude Code hooks? These will:
> - Remind to invoke this skill on session start
> - Warn before git commits if `.long-task-harness/long-task-progress.md` not staged"

If yes: `python3 <SKILL_PATH>/scripts/claude_code_install_hooks.py`

Note: These hooks are for Claude Code only. Other agents should use AGENTS.md instructions.

## Session Startup Protocol

At the start of each session:

```bash
python3 <SKILL_PATH>/scripts/read_progress.py    # Last 3 sessions
python3 <SKILL_PATH>/scripts/read_features.py    # Incomplete features
git log --oneline -10
```

Then continue from "Next Steps" in the latest session entry.

## During Work

1. Work on **one feature** at a time
2. Commit frequently with descriptive messages
3. Update `.long-task-harness/features.json` when features pass tests
4. Update `.long-task-harness/long-task-progress.md` before ending session

## Session Entry Format

```markdown
### Session N | YYYY-MM-DD | Commits: abc123..def456

#### Goal
[One-liner]

#### Accomplished
- [x] Task done
- [ ] Task carried forward

#### Decisions
- **[D1]** Decision made - reasoning

#### Next Steps
1. Priority task
```

## Before Ending Session

1. Update `.long-task-harness/long-task-progress.md` with session notes
2. Commit all changes including progress docs
3. Verify tests pass

## Critical Rules

- Never edit tests to make them pass - fix implementation
- Never mark features passing without testing
- Always update progress docs before ending
- Commit frequently

## Scripts

| Script | Purpose |
|--------|---------|
| `init_harness.py` | Initialize project with tracking files in `.long-task-harness/` |
| `claude_code_install_hooks.py` | Install/uninstall Claude Code hooks |
| `read_progress.py` | Read sessions (`--list`, `--session N`, `-n 5`) |
| `read_features.py` | Read features (`--feature ID`, `--json`) |
| `session_metadata.py` | Generate git metadata for session entries |
| `claude_code_precommit_check.py` | Pre-commit hook (warns if progress not staged) |
| `generate_manifest.py` | Generate `.manifest.yaml` for progressive codebase disclosure |

## History Research (10+ Sessions)

For long projects, use subagents as **scouts** to find relevant history:

```
Research the history of [feature/file] in this project.
Return POINTERS (session numbers, file paths, decision refs) - not summaries.
```

Then read only the specific sessions identified.

## Progressive Codebase Disclosure

For unfamiliar codebases, generate a manifest before diving in:

```bash
python3 <SKILL_PATH>/scripts/generate_manifest.py [directory]
```

This creates `.manifest.yaml` with:
- File purposes (from docstrings)
- Exports (classes, functions)
- Dependencies (imports)
- Size hints (small/medium/large)

**Read the manifest first**, then dive into specific files. This avoids wasting tokens on files you don't need.
