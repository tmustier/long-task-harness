#!/usr/bin/env python3
"""
Extract relevant sections from claude-progress.md for session startup.

Default: header sections (Overview, Key Decisions, Current State) + last 3 sessions
Use -n N for more sessions, --all for everything.
"""

import argparse
import re
import sys
from pathlib import Path


def find_progress_file() -> Path | None:
    """Find claude-progress.md in current directory or parents."""
    cwd = Path.cwd()
    for path in [cwd, *cwd.parents]:
        progress_file = path / "claude-progress.md"
        if progress_file.exists():
            return progress_file
    return None


def parse_progress_file(content: str) -> tuple[str, list[tuple[str, str]]]:
    """
    Parse claude-progress.md into header and sessions.

    Returns:
        (header_content, [(session_title, session_content), ...])
    """
    # Remove HTML comments (including template blocks)
    content_no_comments = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    # Split at "## Session Log" or first "### Session"
    session_log_match = re.search(r'^## Session Log\s*$', content_no_comments, re.MULTILINE)

    if session_log_match:
        header = content_no_comments[:session_log_match.start()].rstrip()
        sessions_content = content_no_comments[session_log_match.end():]
    else:
        # No "## Session Log" header, look for first session directly
        first_session = re.search(r'^### Session \d+', content_no_comments, re.MULTILINE)
        if first_session:
            header = content_no_comments[:first_session.start()].rstrip()
            sessions_content = content_no_comments[first_session.start():]
        else:
            # No sessions found
            return content_no_comments, []

    # Parse individual sessions
    session_pattern = re.compile(r'^### Session (\d+.*?)(?=^### Session |\Z)', re.MULTILINE | re.DOTALL)
    sessions = []

    for match in session_pattern.finditer(sessions_content):
        session_text = match.group(0).strip()
        # Skip empty or template sessions
        if not session_text or 'YYYY-MM-DD' in session_text:
            continue
        # Extract title from first line
        first_line = session_text.split('\n')[0]
        title = first_line.replace('### ', '').strip()
        sessions.append((title, session_text))

    return header, sessions


def format_output(header: str, sessions: list[tuple[str, str]],
                  num_sessions: int | None, show_all: bool) -> str:
    """Format the output with header and selected sessions."""
    total_sessions = len(sessions)

    if show_all or num_sessions is None or num_sessions >= total_sessions:
        selected_sessions = sessions
        omitted = 0
    else:
        selected_sessions = sessions[-num_sessions:]
        omitted = total_sessions - num_sessions

    output_parts = []

    # Status line
    if total_sessions > 0:
        if omitted > 0:
            first_shown = total_sessions - len(selected_sessions) + 1
            output_parts.append(f"[Showing: header + sessions {first_shown}-{total_sessions} of {total_sessions}]\n")
        else:
            output_parts.append(f"[Showing: header + all {total_sessions} sessions]\n")
    else:
        output_parts.append("[Showing: header only (no sessions found)]\n")

    # Header
    output_parts.append(header)

    # Sessions
    if selected_sessions:
        output_parts.append("\n\n---\n\n## Session Log\n")
        for _, session_content in selected_sessions:
            output_parts.append(f"\n{session_content}\n")

    # Hint about more content
    if omitted > 0:
        output_parts.append(f"\n---\n[{omitted} earlier session(s) available: -n N or --all]")

    return ''.join(output_parts)


def main():
    parser = argparse.ArgumentParser(
        description="Extract relevant sections from claude-progress.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 read_progress.py           # header + last 3 sessions
  python3 read_progress.py -n 5      # header + last 5 sessions
  python3 read_progress.py --all     # everything
        """
    )
    parser.add_argument('-n', '--sessions', type=int, default=3,
                        help='Number of recent sessions to show (default: 3)')
    parser.add_argument('--all', action='store_true',
                        help='Show all sessions')
    parser.add_argument('--file', type=Path,
                        help='Path to claude-progress.md (default: auto-detect)')

    args = parser.parse_args()

    # Find progress file
    if args.file:
        progress_file = args.file
    else:
        progress_file = find_progress_file()

    if not progress_file or not progress_file.exists():
        print("Error: claude-progress.md not found", file=sys.stderr)
        print("Run from a project directory with claude-progress.md, or use --file", file=sys.stderr)
        sys.exit(1)

    # Read and parse
    content = progress_file.read_text()
    header, sessions = parse_progress_file(content)

    # Format output
    output = format_output(header, sessions, args.sessions, args.all)
    print(output)


if __name__ == "__main__":
    main()
