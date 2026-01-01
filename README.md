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
- **Git Pre-Commit Hook**: Optional repo-local warning for agents without native hooks

### New in v0.4.3

- **Fix: SessionStart hook visibility**: Claude Code SessionStart hooks now use `systemMessage` JSON output format, making the reminder actually visible to agents (requires Claude Code v1.0.64+)

### New in v0.4.2

- **Fix: Agent-visible warnings**: Hooks now inject warnings that agents actually see
  - Pi: Uses `tool_result` modification (warning appended to git add output)
  - Claude Code: Uses `PreToolUse` prompt-based hook (agent evaluates and includes warning)
  - Codex/Cursor: Uses git pre-commit hook
- **Consistent messaging**: All agents show the same warning format with `features.json` reminder

### New in v0.4.1

- **Optional Git Pre-Commit Hook**: Repo-local warning for agents without native hooks

### New in v0.4.0

- **Multi-Agent Hooks**: Native support for Claude Code, Factory Droid, and Pi agent
- **Status Line**: Quick session overview (`status_line.py --full`)
- **Declarative Rules**: Define rules in markdown to catch issues before commit
- **Git Add Wrapper**: `git_add.py` checks rules at staging time

### From v0.3.0

- **Cleaner File Layout**: All harness files in `.long-task-harness/` directory
- **Improved Commit Flow**: Pre-commit warns instead of blocking

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
3. Installing agent hooks (optional, depending on your agent)

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

- **Claude Code / Factory Droid / Pi**: Optionally install native hooks for reminders
- **Codex / Cursor / Other**: Add harness instructions to AGENTS.md and optionally install a git pre-commit hook

On first invocation, the skill will prompt you to configure persistent invocation for your agent.

### Claude Code Hooks

For Claude Code users who want automatic reminders:

```bash
python3 <SKILL_PATH>/scripts/claude_code_install_hooks.py
```

This adds to `.claude/settings.json`:
- **SessionStart**: Reminds to invoke the skill on new sessions
- **PreToolUse**: Warns if `.long-task-harness/long-task-progress.md` not staged

### Git Pre-Commit Hook (Optional)

For agents without native hooks (Codex, Cursor, etc.), you can install a repo-local pre-commit hook.
This affects all commits in the current repository clone.

```bash
python3 <SKILL_PATH>/scripts/precommit_install_hook.py
```

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
| `status_line.py` | Quick status overview (`--full`, `--json`) |
| `check_rules.py` | Check operations against declarative rules |
| `git_add.py` | Git add wrapper with rule checking |
| `claude_code_install_hooks.py` | Install Claude Code hooks |
| `claude_code_precommit_check.py` | Claude Code pre-commit check |
| `droid_install_hooks.py` | Install Factory Droid hooks |
| `droid_precommit_check.py` | Factory Droid pre-commit check |
| `precommit_check.py` | Shared pre-commit check logic |
| `precommit_install_hook.py` | Install repo-local git pre-commit hook |
| `pi_install_hooks.py` | Install Pi agent hooks |

### Status Line

Get a quick overview of your session:

```bash
python3 ~/.claude/skills/long-task-harness/scripts/status_line.py
# Output: S2 | F:4/8 [v040-pi-hooks] | main (U:2)

python3 ~/.claude/skills/long-task-harness/scripts/status_line.py --full
# Multi-line detailed status
```

### Declarative Rules

Define rules in `.long-task-harness/rules/*.md` to catch issues:

```markdown
---
name: warn-console-log
enabled: true
event: file
file_pattern: \\.tsx?$
pattern: console\\.log\\(
action: warn
---

🐛 **Debug code detected** - Remove console.log before committing.
```

Check rules manually or use `git_add.py` for automatic checking:

```bash
# Check a bash command against rules
python3 ~/.claude/skills/long-task-harness/scripts/check_rules.py bash "rm -rf /"

# Stage files with rule checking
python3 ~/.claude/skills/long-task-harness/scripts/git_add.py .
```

### Agent-Specific Hooks

| Agent | Install Command |
|-------|-----------------|
| Claude Code | `python3 <SKILL_PATH>/scripts/claude_code_install_hooks.py` |
| Factory Droid | `python3 <SKILL_PATH>/scripts/droid_install_hooks.py` |
| Pi Agent | `python3 <SKILL_PATH>/scripts/pi_install_hooks.py` |
| Codex / Cursor / Other | `python3 <SKILL_PATH>/scripts/precommit_install_hook.py` |

All installers support `--uninstall` to remove hooks.

## License

MIT
