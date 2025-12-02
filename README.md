# Long Task Harness

A Claude Code plugin for maintaining continuity across long-running tasks that span multiple sessions.

## About

This plugin codifies the patterns and practices from Anthropic's engineering article: **[Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)**.

The core problem: AI agents lose context across sessions. Each new context window starts fresh, creating a "shift change" problem where continuity is lost. This plugin provides structured workflows to maintain progress documentation, feature tracking, and session handoff protocols.

## Key Features

- **Progress Documentation**: Maintain `claude-progress.md` files documenting work history
- **Feature List Strategy**: Track testable features in structured JSON format
- **Session Startup Protocol**: Consistent initialization steps for each new session
- **Context-Efficient Scripts**: Load only recent sessions (~78% context reduction)
- **Session Hooks**: Auto-remind Claude to invoke the skill on startup

## Installation

### Option 1: Plugin Install (Recommended)

```
/plugin install tmustier/long-task-harness
```

Works on both Claude Code CLI and Claude Code web.

### Option 2: Clone to skills directory (CLI only)

```bash
git clone https://github.com/tmustier/long-task-harness.git ~/long-task-harness
ln -s ~/long-task-harness/skills/long-task-harness ~/.claude/skills/long-task-harness
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
python3 ~/.claude/skills/long-task-harness/scripts/read_progress.py    # header + last 3 sessions
python3 ~/.claude/skills/long-task-harness/scripts/read_features.py    # incomplete + completed summary
```

### Session Hooks

Install hooks to auto-remind Claude at session start:

```bash
python3 ~/.claude/skills/long-task-harness/scripts/install_hooks.py
```

This adds to `.claude/settings.json`:
- **SessionStart**: Reminds to invoke skill (unless user opts out)
- **PreToolUse**: Reminds to update progress before git commit

## Files Created

| File | Purpose |
|------|---------|
| `claude-progress.md` | Session-by-session work log |
| `features.json` | Feature checklist with pass/fail status |

## License

MIT
