# Long-Task-Harness Instructions for AGENTS.md

Add the following block to your project's AGENTS.md file to enable session continuity
with agents that use AGENTS.md (Codex, Droid, Pi-agent, etc.).

---

## Multi-Session Development Protocol

This project uses structured session continuity tracking. Follow this protocol at the start of each session and before commits.

### Session Startup

At the start of each session:

1. Read `claude-progress.md` for work history (focus on last 3 sessions)
2. Read `features.json` for incomplete features
3. Run `git log --oneline -10` to see recent commits
4. Continue from "Next Steps" in the latest session entry

### During Work

- Work on ONE feature at a time
- Commit frequently with descriptive messages
- Update `features.json` when features pass tests

### Before Commits

Before any git commit:

1. Ensure `claude-progress.md` is staged with session notes
2. Update `features.json` if features were completed
3. Never commit without documenting what was accomplished

### Session End

Before ending a session, update `claude-progress.md` with:

- What was accomplished this session
- Any key decisions made (and why)
- Next steps for the following session
- Current blockers or open questions

### File Locations

- `claude-progress.md` - Session history and notes
- `features.json` - Feature tracking with completion status
