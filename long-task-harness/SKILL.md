---
name: long-task-harness
description: Maintains continuity across long-running tasks that span multiple Claude Code sessions. Use this skill when starting a complex project that will require multiple sessions to complete, or when resuming work on an existing multi-session project. Provides structured workflows for progress documentation, feature tracking, and session handoff protocols.
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

**On first invocation**, if `claude-progress.md` doesn't exist, prompt:

> "Would you like me to add harness instructions to CLAUDE.md? This ensures context reloads after `/compact`."

If yes, add the snippet from "CLAUDE.md Integration" below.

## Workflow

### Phase 1: Project Initialization

When starting a new multi-session project, initialize the harness structure:

1. **Run the initialization script** to create progress tracking files:
   ```bash
   python3 ~/.claude/skills/long-task-harness/scripts/init_harness.py
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
2. **Read progress files**:
   - `claude-progress.md` for work history
   - `git log --oneline -20` for recent commits
3. **Review feature list** in `features.json`
4. **Run basic functionality tests** to verify current state
5. **Select next incomplete feature** to work on

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
