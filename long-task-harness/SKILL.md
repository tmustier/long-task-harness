---
name: long-task-harness
description: Maintains continuity across long-running tasks that span multiple Claude Code sessions. This skill should be used when starting a complex project that will require multiple sessions to complete, or when resuming work on an existing multi-session project. Provides structured workflows for progress documentation, feature tracking, and session handoff protocols.
---

# Long Task Harness

## Overview

This skill provides structured workflows for maintaining continuity across long-running tasks that span multiple Claude Code sessions. It addresses the "shift change" problem where context is lost between sessions by establishing progress documentation, feature tracking, and session startup protocols.

## When to Use This Skill

Invoke this skill when:
- Starting a complex project expected to span multiple sessions
- Resuming work on an existing multi-session project
- Working on tasks with 10+ discrete features or components
- Building something that requires iterative development with testing

## First-Time Setup

**On first invocation**, if `claude-progress.md` doesn't exist, offer two optional configurations:

### Option 1: CLAUDE.md Integration

Prompt:
> "Would you like me to add harness instructions to CLAUDE.md? This ensures context reloads after `/compact`."

If yes, add the snippet from "CLAUDE.md Integration" below.

### Option 2: Session Continuity Hooks (Recommended)

Prompt:
> "Would you like me to install session continuity hooks?
>
> Hooks are small scripts that run automatically at key moments and inject reminders into my context. They solve the problem of me forgetting to follow the harness workflow. Specifically, these hooks will:
>
> - **On session start**: Remind me to read CLAUDE.md and invoke this skill
> - **Before compaction**: Remind me to include harness instructions in the summary so my 'future self' knows to resume properly
> - **Before git commits**: Remind me to update claude-progress.md first
>
> The hooks are stored in this project's `.claude/settings.json` — they won't affect other projects."

If yes, run:
```bash
python3 scripts/install_hooks.py
```

This installs project-local hooks to `.claude/settings.json` that:

| Hook | When | Reminder |
|------|------|----------|
| SessionStart | New session or post-compact | Read CLAUDE.md, invoke skill, read progress files |
| PreCompact | Before context compaction | Include harness instructions in summary |
| PreToolUse | Before `git commit` | Update claude-progress.md first |

To remove hooks later: `python3 scripts/install_hooks.py --uninstall`

## Workflow

### Phase 1: Project Initialization

When starting a new multi-session project, initialize the harness structure:

1. **Run the initialization script** to create progress tracking files:
   ```bash
   python3 scripts/init_harness.py
   ```

2. **Review generated files**:
   - `claude-progress.md` - Work history and session notes
   - `features.json` - Testable feature checklist
   - `init.sh` - Environment setup script (if applicable)

3. **Populate the feature list** by editing `features.json` with specific, testable features. Each feature should have:
   - A clear description
   - Concrete steps to implement
   - A `passes` field (boolean) for tracking completion

4. **Create an initial git commit** marking the project setup.

### Phase 2: Session Startup Protocol

At the start of each new session, follow this protocol:

1. **Check current directory** and verify in the correct project
2. **Get project context** using the helper scripts (note: use the skill's base directory path shown above):
   ```bash
   python3 ~/.claude/skills/long-task-harness/scripts/read_progress.py    # header + last 3 sessions
   python3 ~/.claude/skills/long-task-harness/scripts/read_features.py    # incomplete (full) + completed (names)
   git log --oneline -10
   ```

   For more context if needed:
   - More sessions: `python3 ~/.claude/skills/long-task-harness/scripts/read_progress.py -n 5`
   - Full history: `python3 ~/.claude/skills/long-task-harness/scripts/read_progress.py --all`
   - Full features: `python3 ~/.claude/skills/long-task-harness/scripts/read_features.py --all`

3. **Run basic functionality tests** to verify current state
4. **Select next incomplete feature** to work on

### Phase 3: Incremental Work Pattern

During each session:

1. **Work on ONE feature** at a time
2. **Commit progress** with descriptive messages after each meaningful change
3. **Update `features.json`** when a feature passes all tests
4. **Update `claude-progress.md`** with session notes before ending
5. **Use git to revert** if changes break functionality

### Phase 4: Session Handoff

Before ending a session:

1. **Update `claude-progress.md`** with:
   - What was accomplished
   - Current state of the project
   - Next steps for the following session
   - Any blockers or open questions

2. **Commit all changes** including progress documentation

3. **Verify tests pass** before ending

## Critical Rules

- **Never remove or edit tests** to make them pass - fix the implementation instead
- **Never mark a feature as passing** without actually testing it
- **Always update progress documentation** before ending a session
- **Use browser automation** (Puppeteer MCP) when available for end-to-end testing
- **Commit frequently** with descriptive messages

## Resources

### scripts/

- `init_harness.py` - Initializes the harness structure in the current project
- `install_hooks.py` - Installs/uninstalls session continuity hooks to `.claude/settings.json`
- `read_progress.py` - Extracts header + recent sessions from claude-progress.md (use at session start)
- `read_features.py` - Shows incomplete features (full) + completed (names) from features.json

### references/

- `feature_list_guide.md` - Guide for writing effective feature specifications

### assets/

- `features_template.json` - Template for the feature tracking file
- `progress_template.md` - Template for the progress documentation file

---

## CLAUDE.md Integration

Add this to the project's `CLAUDE.md` to ensure continuity after `/compact`:

```markdown
## Multi-Session Development

This project uses `long-task-harness`. After `/compact` or new sessions:

1. Read `claude-progress.md` for work history
2. Read `features.json` for feature tracking
3. Check `git log --oneline -10` for recent commits
4. Continue from "Next Steps" in the latest session
```
