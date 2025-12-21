# Long Task Harness

A skill for filesystem-based agents to maintain continuity across long-running tasks that span multiple sessions.

## About

This skill codifies patterns from Anthropic's **[Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)** and HumanLayer's **[Advanced Context Engineering for Coding Agents](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents)**.

The core problem: AI agents lose context across sessions. Each new context window starts fresh, creating a "shift change" problem where continuity is lost. This skill provides structured workflows for progress documentation, feature tracking, and session handoff.

## Key Features

- **Progress Documentation**: Maintain `claude-progress.md` with structured session logs
- **Feature Tracking**: Track features in `features.json` with pass/fail status
- **Context-Efficient Scripts**: Load only recent sessions (~78% context reduction)
- **Session Hooks**: Auto-remind Claude to invoke the skill; block commits without progress updates

### New in v0.2.0-beta

- **Bidirectional Linking**: Sessions reference features; features track their session history
- **History Research Protocol**: Guidance for using subagents to find relevant history without context bloat
- **Targeted Reading**: `--session N` and `--list` flags for precise history lookup
- **Git Metadata**: Pre-commit hook outputs commit range and file changes for session entries

## Installation

Clone directly to your skills directory:

```bash
gh repo clone tmustier/long-task-harness ~/.claude/skills/long-task-harness
```

## Usage

Once installed, invoke the skill when starting a complex, multi-session project:

```
invoke the long-task-harness skill
```

The skill will guide you through:
1. Initializing progress tracking files (`claude-progress.md`, `features.json`)
2. Creating a feature list for the project
3. Installing session hooks (optional)

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

### Session Hooks

Install hooks to auto-remind Claude at session start:

```bash
python3 ~/.claude/skills/long-task-harness/scripts/install_hooks.py
```

This adds to `.claude/settings.json`:
- **SessionStart**: Requires Claude to invoke the skill (only skips if explicitly told to)
- **PreToolUse**: Blocks git commits unless `claude-progress.md` is staged; outputs session metadata

## Files Created

| File | Purpose |
|------|---------|
| `claude-progress.md` | Session-by-session work log with structured metadata |
| `features.json` | Feature checklist with history tracking (v2 format) |

## Scripts

| Script | Purpose |
|--------|---------|
| `init_harness.py` | Initialize harness in a project |
| `read_progress.py` | Read sessions (`--list`, `--session N`, `-n 5`) |
| `read_features.py` | Read features (`--feature ID`, `--json`) |
| `session_metadata.py` | Generate git metadata for session entries |
| `install_hooks.py` | Install/uninstall session hooks |

## License

MIT
