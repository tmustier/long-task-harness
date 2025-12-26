# long-task-harness - Progress Log

## Project Overview

**Started**: 2024-11-15
**Status**: Active Development
**Repository**: https://github.com/tmustier/long-task-harness

### Project Goals

A skill for filesystem-based agents to maintain continuity across long-running tasks that span multiple sessions. Codifies patterns from Anthropic's "Effective Harnesses for Long-Running Agents" and HumanLayer's "Advanced Context Engineering for Coding Agents".

### Key Decisions

- **[D1]** Use `.long-task-harness/` directory for all files (v0.3.0) - keeps project root clean
- **[D2]** Pre-commit warns instead of blocking (v0.3.0) - less disruptive workflow
- **[D3]** Prefix Claude Code-specific scripts with `claude_code_` - clarifies scope

---

## Current State

**Last Updated**: 2024-12-27

### What's Working
- Session progress tracking with context-efficient reading
- Feature tracking with bidirectional history
- Claude Code hooks (optional)
- Multi-agent support via AGENTS.md/CLAUDE.md

### What's Not Working
- N/A

### Blocked On
- N/A

---

## Session Log

### Session 1 | 2024-12-27 | Commits: 10f22fc..5317e46

#### Metadata
- **Features**: v030-release (completed)
- **Files Changed**: 
  - `.long-task-harness/` (+new) - harness initialization for self-tracking

#### Goal
Release v0.3.0 - initialize harness for dogfooding, tag release

#### Accomplished
- [x] Initialized long-task-harness for itself (dogfooding)
- [x] Created features.json with v0.3.0 features
- [x] Commit harness files
- [x] Tag v0.3.0
- [x] Push to origin

#### Decisions
- **[D4]** Use long-task-harness itself to track its own development - dogfooding demonstrates the skill

#### Next Steps
- v0.3.0 released! No immediate next steps.

---

<!--
SESSION TEMPLATE - Copy for new sessions

### Session N | YYYY-MM-DD | Commits: abc123..def456

#### Metadata
- **Features**: feature-id (started|progressed|completed|blocked)
- **Files Changed**: 
  - `path/to/file` (+lines/-lines) - brief description

#### Goal
[One-liner]

#### Accomplished
- [x] Completed task
- [ ] Incomplete task

#### Decisions
- **[DN]** Decision and rationale

#### Next Steps
1. Priority task
-->
