# Long Task Harness

A skill for filesystem-based agents to maintain continuity across long-running tasks that span multiple sessions.

## About

This skill codifies patterns from Anthropic's **[Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)** and HumanLayer's **[Advanced Context Engineering for Coding Agents](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents)**.

The core problem: AI agents lose context across sessions. Each new context window starts fresh, creating a "shift change" problem where continuity is lost. This skill provides structured workflows for progress documentation, feature tracking, and session handoff.

## Key Features

- **Progress Documentation**: Maintain `.long-task-harness/long-task-progress.md` with structured session logs
- **Feature Tracking**: Track features in `.long-task-harness/features.json` with pass/fail status
- **Context-Efficient Scripts**: Load only recent sessions (~78% context reduction)
- **Session Hooks**: Auto-remind to invoke the skill; warn on commits without progress updates

### New in v0.3.0

- **Cleaner File Layout**: All harness files in `.long-task-harness/` directory
- **Improved Commit Flow**: Pre-commit warns + suggests `--amend` instead of blocking
- **Renamed Hooks Script**: `claude_code_install_hooks.py` (clarifies Claude Code-only)

### From v0.2.0

- **Bidirectional Linking**: Sessions reference features; features track their session history
- **History Research Protocol**: Guidance for using subagents to find relevant history without context bloat
- **Targeted Reading**: `--session N` and `--list` flags for precise history lookup
- **Git Metadata**: Pre-commit hook outputs commit range and file changes for session entries

## Installation

Clone the repository:

```bash
gh repo clone tmustier/long-task-harness ~/.claude/skills/long-task-harness
```

Or clone anywhere and reference the path in your AGENTS.md/CLAUDE.md.

## Usage

Once installed, invoke the skill when starting a complex, multi-session project:

```
invoke the long-task-harness skill
```

The skill will guide you through:
1. Initializing progress tracking files in `.long-task-harness/`
2. Creating a feature list for the project
3. Installing Claude Code hooks (optional, for non-plugin installs)

### Session Startup (after initialization)

On subsequent sessions, the skill uses context-efficient scripts:

```bash
# Default: header + last 3 sessions
python3 ~/.claude/skills/long-task-harness/scripts/read_progress.py

# List all sessions (compact view)
python3 ~/.claude/skills/long-task-harness/scripts/read_progress.py --list

# Read specific session by number
python3 ~/.claude/skills/long-task-harness/scripts/read_progress.py --session 12

# Show incomplete features with history
python3 ~/.claude/skills/long-task-harness/scripts/read_features.py

# Show specific feature details
python3 ~/.claude/skills/long-task-harness/scripts/read_features.py --feature auth-001
```

### Session Metadata

Get git metadata for your session entry:

```bash
python3 ~/.claude/skills/long-task-harness/scripts/session_metadata.py --since
```

### Multi-Agent Support

The skill works with any agent that can read markdown files:

- **Claude Code**: Optionally install hooks for automatic reminders
- **Cursor/Codex/Droid/Pi**: Add harness instructions to AGENTS.md

On first invocation, the skill will prompt you to configure persistent invocation for your agent.

### Claude Code Hooks

For Claude Code users who want automatic reminders:

```bash
python3 <SKILL_PATH>/scripts/claude_code_install_hooks.py
```

This adds to `.claude/settings.json`:
- **SessionStart**: Reminds to invoke the skill on new sessions
- **PreToolUse**: Warns if `.long-task-harness/long-task-progress.md` not staged, suggests amending

## Files Created

All files are created in `.long-task-harness/` directory:

| File | Purpose |
|------|---------|
| `long-task-progress.md` | Session-by-session work log with structured metadata |
| `features.json` | Feature checklist with history tracking (v2 format) |
| `init.sh` | Environment setup script (optional) |

## Scripts

| Script | Purpose |
|--------|---------|
| `init_harness.py` | Initialize harness in a project (creates `.long-task-harness/`) |
| `read_progress.py` | Read sessions (`--list`, `--session N`, `-n 5`) |
| `read_features.py` | Read features (`--feature ID`, `--json`) |
| `session_metadata.py` | Generate git metadata for session entries |
| `claude_code_install_hooks.py` | Install/uninstall Claude Code hooks |
| `claude_code_precommit_check.py` | Pre-commit hook (warns + suggests amend) |

## License

MIT
