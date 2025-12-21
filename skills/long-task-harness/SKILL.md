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
> Hooks are small scripts that run automatically at key moments. They solve the problem of me forgetting to follow the harness workflow. Specifically, these hooks will:
>
> - **On session start**: Require me to invoke this skill (only skips if you explicitly tell me not to)
> - **Before git commits**: Block the commit unless `claude-progress.md` is staged
>
> The hooks are stored in this project's `.claude/settings.json` — they won't affect other projects."

If yes, run:
```bash
python3 scripts/install_hooks.py
```

This installs project-local hooks to `.claude/settings.json` that:

| Hook | When | Action |
|------|------|--------|
| SessionStart | New session or post-compact | Requires invoking this skill before responding |
| PreToolUse | Before `git commit` | Blocks unless `claude-progress.md` is staged |

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

### Maintaining Bidirectional Links (v2 Format)

The v2 format introduces **bidirectional linking** between sessions and features. This enables efficient history lookup for long-running projects.

#### Session Entry Structure (claude-progress.md)

Each session should include structured metadata:

```markdown
### Session 5 | 2024-12-18 | Commits: a1b2c3d..e4f5g6h

#### Metadata
- **Features**: auth-001 (progressed), api-003 (completed)
- **Files Changed**: 
  - `src/auth/login.ts` (+45/-12) - added refresh token logic
  - `tests/auth.test.ts` (+30/-0) - new test cases
- **Commit Summary**: `feat(auth): add refresh tokens`, `test: auth flow coverage`

#### Goal
[One-liner describing session objective]

#### Accomplished
- [x] Task completed
- [ ] Task incomplete (carried forward)

#### Decisions
- **[D1]** Chose JWT refresh over sliding sessions - better for mobile clients

#### Context & Learnings
[What future sessions need to know - focus on WHY, not the struggle]

#### Next Steps
1. [Priority] → affects: feature-id
```

#### Feature History Structure (features.json)

When updating a feature, also update its `history` block:

```json
{
  "id": "auth-001",
  "name": "User authentication",
  "passes": false,
  "history": {
    "sessions": [
      {"session": 3, "date": "2024-12-15", "action": "started", "summary": "Initial login flow"},
      {"session": 5, "date": "2024-12-18", "action": "progressed", "summary": "Added refresh tokens"}
    ],
    "files": ["src/auth/login.ts", "src/auth/tokens.ts", "tests/auth.test.ts"],
    "decisions": [
      {"session": 3, "decision": "Use JWT for stateless auth"},
      {"session": 5, "decision": "Refresh tokens over sliding sessions"}
    ]
  }
}
```

#### When to Update Links

| Event | Update claude-progress.md | Update features.json |
|-------|---------------------------|---------------------|
| Start working on feature | Add to Metadata: `feature-id (started)` | Add session entry with `action: started` |
| Make progress | Add to Metadata: `feature-id (progressed)` | Add session entry with `action: progressed` |
| Complete feature | Add to Metadata: `feature-id (completed)` | Set `passes: true`, add final session entry |
| Make key decision | Add to Decisions: `[DN] decision text` | Add to `history.decisions` array |
| Touch new file | Add to Files Changed | Add to `history.files` array if new |

#### Why This Matters

Bidirectional links enable **efficient history retrieval** for long projects:
- Need context on a feature? → Check `history.sessions` for relevant session numbers
- Resuming after weeks? → Subagent can find all sessions touching that feature
- Debugging a file? → Find which features/sessions modified it

This avoids the "read all history or read nothing" problem.

### History Research Protocol (For Long Projects)

When a project has 10+ sessions, avoid trawling through all history in the main context. Instead, use a **research-first** approach that keeps the main agent focused.

#### When to Use This Protocol

- Resuming work on a feature not touched in several sessions
- Debugging an issue in unfamiliar code
- Before starting work that might duplicate past decisions

#### The Pattern: Find, Then Read

The goal is NOT to summarize history for the main agent. The goal is to **point the main agent to exactly what it needs to read**.

**Step 1: Research (isolated context)**

Spawn a subagent to explore history and return POINTERS:

```
Research the history of [feature-id / file / topic] in this project.

Search:
- features.json for the feature's history.sessions, history.files, history.decisions
- claude-progress.md for sessions that mention this feature/file

Return (be specific, not summarizing):
- Which session numbers are relevant (e.g., "Sessions 5, 12, 23")
- Which files were involved (exact paths)
- Key decision references (e.g., "Decision [D3] in Session 5")
- Recommendation: "Read Session 12 for most recent context on this feature"

Do NOT summarize the content. Just tell me WHERE to look.
```

**Step 2: Targeted Read (main context)**

Main agent then reads ONLY the specific sessions/sections identified:

```bash
# List all sessions to scan titles quickly
python3 ~/.claude/skills/long-task-harness/scripts/read_progress.py --list

# Read a specific session by number
python3 ~/.claude/skills/long-task-harness/scripts/read_progress.py --session 12

# Read the feature's full history
python3 ~/.claude/skills/long-task-harness/scripts/read_features.py --feature auth-001

# Then read the actual code files identified
```

#### Why Pointers, Not Summaries

| Approach | Problem |
|----------|---------|
| Subagent summarizes everything | Main agent misses nuance; can't verify; "shielded" from relevant context |
| Main agent reads everything | Context bloat; "dumb zone"; wastes tokens on irrelevant history |
| **Subagent finds, main agent reads** | Main agent has full context of what matters; exploration waste isolated |

The subagent's job is to be a **scout**, not a **translator**. It maps the terrain so the main agent can navigate directly to what matters.

#### Anti-Patterns

- **Over-using subagents**: For short histories (<10 sessions), just read directly
- **Trusting summaries blindly**: Always verify critical context by reading source
- **Anthropomorphizing**: Don't create "history agent" or "decision agent" - it's just context isolation
- **Skipping human review**: Research can be wrong; review the pointers before acting on them

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

- `features_template_v2.json` - Template for feature tracking with history (recommended)
- `progress_template_v2.md` - Template for progress docs with structured metadata (recommended)
- `features_template.json` - Legacy template (v1, no history tracking)
- `progress_template.md` - Legacy template (v1, unstructured sessions)

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
