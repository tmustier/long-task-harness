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

Clone and copy to your skills directory:

```bash
gh repo clone tmustier/long-task-harness /tmp/lth && \
  cp -r /tmp/lth/skills/long-task-harness ~/.claude/skills/ && \
  rm -rf /tmp/lth
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
- **SessionStart**: Requires Claude to invoke the skill (only skips if explicitly told to)
- **PreToolUse**: Blocks git commits unless `claude-progress.md` is staged

## Files Created

| File | Purpose |
|------|---------|
| `claude-progress.md` | Session-by-session work log |
| `features.json` | Feature checklist with pass/fail status |

## License

MIT
