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

**Last Updated**: 2025-12-31

### What's Working
- Session progress tracking with context-efficient reading
- Feature tracking with bidirectional history
- Claude Code hooks (optional)
- Multi-agent support via AGENTS.md/CLAUDE.md
- Status line for quick session overview
- Declarative rules for catching issues before commit
- Factory Droid hooks support
- Pi agent hooks for session title tracking
- git_add.py wrapper with rule checking
- Repo-local git pre-commit hook installer for unsupported agents

### What's Not Working
- N/A

### Blocked On
- N/A

---

## Session Log

### Session 3 | 2025-12-31 | Commits: 8dc36b7..HEAD

#### Metadata
- **Features**: v041-precommit-hook (completed)
- **Files Changed**: 
  - `scripts/precommit_check.py` (+new) - shared pre-commit check logic
  - `scripts/precommit_install_hook.py` (+new) - repo-local hook installer
  - `scripts/claude_code_precommit_check.py` (+/-) - reuse shared check
  - `scripts/droid_precommit_check.py` (+/-) - reuse shared check
  - `README.md` (+/-) - document v0.4.1 optional pre-commit hook
  - `SKILL.md` (+/-) - add unsupported-agent hook guidance
  - `.long-task-harness/init.sh` (+new) - environment setup template
  - `.gitignore` (+/-) - ignore runtime artifacts
  - `.long-task-harness/features.json` (+/-) - add v041-precommit-hook
  - `.long-task-harness/long-task-progress.md` (+/-) - session update

#### Goal
Add a repo-local pre-commit hook installer for unsupported agents.

#### Accomplished
- [x] Added shared precommit_check.py used by Claude/Droid and git hook
- [x] Implemented precommit_install_hook.py with install/uninstall/force
- [x] Documented optional git pre-commit hook for unsupported agents
- [x] Bumped docs to v0.4.1
- [x] Updated harness metadata
- [x] Added init.sh template and ignored runtime artifacts

#### Decisions
- **[D7]** Offer the git pre-commit hook only for agents without native hooks; warn that it is repo-local

#### Next Steps
1. Consider adding a Codex notify hook helper in a future release.

### Session 2 | 2024-12-31 | Commits: 207a6db..de3d4e7

#### Metadata
- **Features**: v040-status-rules, v040-git-add, v040-droid-hooks, v040-pi-hooks (all completed)
- **Files Changed**: 
  - `scripts/status_line.py` (+297) - quick session overview (compact/full/json)
  - `scripts/check_rules.py` (+396) - declarative rule checking
  - `scripts/git_add.py` (+292) - git add wrapper with rule checking
  - `scripts/droid_install_hooks.py` (+191) - Factory Droid hooks installer
  - `scripts/droid_precommit_check.py` (+121) - Factory Droid pre-commit
  - `hooks/pi/resume-sessions.ts` (+133) - Pi agent session title tracking
  - `.long-task-harness/rules/` (+new) - default rule templates

#### Goal
Add status/rules features, multi-agent hooks support, release v0.4.0

#### Accomplished
- [x] Status line for quick session overview (compact, full, json output)
- [x] Declarative rules system - define rules in markdown, catch issues before commit
- [x] git_add.py wrapper - checks rules at staging time
- [x] Factory Droid hooks - session start reminder + pre-commit checks
- [x] Pi agent hooks - session title tracking from commit messages
- [x] Update progress files and features.json
- [x] Tag and push v0.4.0

#### Decisions
- **[D5]** Support multiple agent platforms - Claude Code, Factory Droid, Pi agent each get native hooks
- **[D6]** Rules are opt-in - create `.long-task-harness/rules/*.md` to enable

#### Next Steps
- v0.4.0 released!

---

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
