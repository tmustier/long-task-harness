# Long Task Harness

A Claude Code skill for maintaining continuity across long-running tasks that span multiple sessions.

## About

This skill codifies the patterns and practices from Anthropic's engineering article: **[Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)**.

The core problem: AI agents lose context across sessions. Each new context window starts fresh, creating a "shift change" problem where continuity is lost. This skill provides structured workflows to maintain progress documentation, feature tracking, and session handoff protocols.

## Key Features

- **Progress Documentation**: Maintain `claude-progress.md` files documenting work history
- **Feature List Strategy**: Track testable features in structured JSON format
- **Session Startup Protocol**: Consistent initialization steps for each new session
- **Incremental Work Pattern**: One feature per session with git-based checkpointing

## Installation

### Option 1: Clone to your skills directory

```bash
git clone https://github.com/tmustier/long-task-harness.git ~/.claude/skills/long-task-harness
```

### Option 2: Symlink from a local clone

```bash
git clone https://github.com/tmustier/long-task-harness.git ~/projects/long-task-harness
ln -s ~/projects/long-task-harness/long-task-harness ~/.claude/skills/long-task-harness
```

## Usage

Once installed, invoke the skill when starting a complex, multi-session project:

```
Use the long-task-harness skill to set up this project for multi-session work
```

The skill will guide you through:
1. Initializing progress tracking files
2. Creating a feature list for the project
3. Establishing session startup protocols

## Optional: CLAUDE.md Configuration

Add this to your `~/.claude/CLAUDE.md` to prompt Claude to consider the skill when planning:

```markdown
## Planning complex tasks
When a task warrants planning (or the user explicitly asks for a plan), consider whether the `long-task-harness` skill would help - especially for work that may span multiple sessions or has many discrete features to track.
```

## License

MIT
