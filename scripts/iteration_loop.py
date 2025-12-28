#!/usr/bin/env python3
"""
Iteration loop manager for long-task-harness.

Implements Ralph-style iteration loops where the same prompt is repeated
until a completion condition is met.

Usage:
  # Start a loop
  python3 iteration_loop.py start "Build feature X" --promise "COMPLETE" --max 50
  
  # Check loop status (called by agent at end of each iteration)
  python3 iteration_loop.py check
  
  # Cancel active loop
  python3 iteration_loop.py cancel
  
  # Show loop status
  python3 iteration_loop.py status
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def get_harness_dir() -> Path:
    """Find .long-task-harness directory."""
    cwd = Path.cwd()
    for path in [cwd, *cwd.parents]:
        harness_dir = path / ".long-task-harness"
        if harness_dir.exists():
            return harness_dir
    # Create in cwd if not found
    harness_dir = cwd / ".long-task-harness"
    harness_dir.mkdir(exist_ok=True)
    return harness_dir


def get_loop_file() -> Path:
    """Get path to iteration loop state file."""
    return get_harness_dir() / "iteration-loop.json"


def load_loop_state() -> dict | None:
    """Load current loop state if exists."""
    loop_file = get_loop_file()
    if loop_file.exists():
        return json.loads(loop_file.read_text())
    return None


def save_loop_state(state: dict):
    """Save loop state."""
    get_loop_file().write_text(json.dumps(state, indent=2))


def delete_loop_state():
    """Remove loop state file."""
    loop_file = get_loop_file()
    if loop_file.exists():
        loop_file.unlink()


def start_loop(prompt: str, promise: str | None, max_iterations: int):
    """Start a new iteration loop."""
    if load_loop_state():
        print("Error: Loop already active. Use 'cancel' first or 'check' to continue.", file=sys.stderr)
        sys.exit(1)
    
    state = {
        "prompt": prompt,
        "completion_promise": promise,
        "max_iterations": max_iterations,
        "iteration": 1,
        "started": datetime.now().isoformat(),
        "history": []
    }
    save_loop_state(state)
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                    ITERATION LOOP STARTED                        ║
╠══════════════════════════════════════════════════════════════════╣
║ Iteration: 1 of {max_iterations if max_iterations > 0 else '∞':<47} ║
║ Promise: {(promise or 'None'):<54} ║
╚══════════════════════════════════════════════════════════════════╝

PROMPT:
{prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INSTRUCTIONS FOR COMPLETION:
""")
    
    if promise:
        print(f"""To complete this loop, output this EXACT text when the statement is TRUE:
  <promise>{promise}</promise>

RULES:
  - Use <promise> XML tags exactly as shown
  - The statement MUST be completely true
  - Do NOT output the promise to escape - only when genuinely complete
  - After each work session, run: python3 scripts/iteration_loop.py check

If stuck after many iterations, document blockers and suggest alternatives.
""")
    else:
        print("""No completion promise set. Loop runs until max iterations or manual cancel.
After each work session, run: python3 scripts/iteration_loop.py check
""")


def check_loop(last_output: str | None = None):
    """
    Check if loop should continue.
    
    Called by agent at end of each iteration. Reads last output from stdin if not provided.
    Returns exit code:
      0 = continue (prompt printed to stdout)
      1 = complete (loop ended)
      2 = error
    """
    state = load_loop_state()
    if not state:
        print("No active loop.", file=sys.stderr)
        sys.exit(2)
    
    iteration = state["iteration"]
    max_iter = state["max_iterations"]
    promise = state.get("completion_promise")
    prompt = state["prompt"]
    
    # Read last output from stdin if not provided
    if last_output is None and not sys.stdin.isatty():
        last_output = sys.stdin.read()
    
    # Check for completion promise in output
    if promise and last_output:
        # Look for <promise>TEXT</promise> pattern
        match = re.search(r'<promise>(.*?)</promise>', last_output, re.DOTALL)
        if match:
            promise_text = match.group(1).strip()
            # Normalize whitespace for comparison
            promise_normalized = ' '.join(promise.split())
            text_normalized = ' '.join(promise_text.split())
            
            if promise_normalized == text_normalized:
                print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                    ✅ LOOP COMPLETE                              ║
╠══════════════════════════════════════════════════════════════════╣
║ Completed in {iteration} iteration(s)                            
║ Promise detected: <promise>{promise}</promise>
╚══════════════════════════════════════════════════════════════════╝
""")
                # Record completion
                state["history"].append({
                    "iteration": iteration,
                    "completed": True,
                    "timestamp": datetime.now().isoformat()
                })
                # Archive the loop state before deleting
                archive_path = get_harness_dir() / f"iteration-loop-completed-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
                state["completed"] = datetime.now().isoformat()
                archive_path.write_text(json.dumps(state, indent=2))
                delete_loop_state()
                sys.exit(1)  # Complete
    
    # Check max iterations
    if max_iter > 0 and iteration >= max_iter:
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                    🛑 MAX ITERATIONS REACHED                     ║
╠══════════════════════════════════════════════════════════════════╣
║ Stopped at iteration {iteration} (max: {max_iter})
║ Loop ended without completion promise
╚══════════════════════════════════════════════════════════════════╝
""")
        state["history"].append({
            "iteration": iteration,
            "completed": False,
            "reason": "max_iterations",
            "timestamp": datetime.now().isoformat()
        })
        archive_path = get_harness_dir() / f"iteration-loop-maxed-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        state["stopped"] = datetime.now().isoformat()
        archive_path.write_text(json.dumps(state, indent=2))
        delete_loop_state()
        sys.exit(1)  # End (but not complete)
    
    # Continue loop - increment iteration
    state["iteration"] = iteration + 1
    state["history"].append({
        "iteration": iteration,
        "completed": False,
        "timestamp": datetime.now().isoformat()
    })
    save_loop_state(state)
    
    # Output prompt for next iteration
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                    🔄 CONTINUING LOOP                            ║
╠══════════════════════════════════════════════════════════════════╣
║ Iteration: {iteration + 1} of {max_iter if max_iter > 0 else '∞':<47} ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    if promise:
        print(f"To complete: output <promise>{promise}</promise> when TRUE\n")
    
    print("PROMPT:")
    print(prompt)
    print("\n" + "━" * 68)
    
    sys.exit(0)  # Continue


def cancel_loop():
    """Cancel active loop."""
    state = load_loop_state()
    if not state:
        print("No active loop to cancel.")
        return
    
    iteration = state["iteration"]
    print(f"Cancelled loop at iteration {iteration}")
    
    # Archive before deleting
    archive_path = get_harness_dir() / f"iteration-loop-cancelled-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    state["cancelled"] = datetime.now().isoformat()
    archive_path.write_text(json.dumps(state, indent=2))
    delete_loop_state()


def show_status():
    """Show current loop status."""
    state = load_loop_state()
    if not state:
        print("No active loop.")
        
        # Show recent archived loops
        harness_dir = get_harness_dir()
        archives = sorted(harness_dir.glob("iteration-loop-*.json"), reverse=True)[:3]
        if archives:
            print("\nRecent loops:")
            for arch in archives:
                data = json.loads(arch.read_text())
                status = "✅" if data.get("completed") else "🛑" if data.get("stopped") else "❌"
                iters = len(data.get("history", []))
                print(f"  {status} {arch.name}: {iters} iterations")
        return
    
    iteration = state["iteration"]
    max_iter = state["max_iterations"]
    promise = state.get("completion_promise", "None")
    started = state["started"]
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                    ITERATION LOOP STATUS                         ║
╠══════════════════════════════════════════════════════════════════╣
║ Iteration: {iteration} of {max_iter if max_iter > 0 else '∞':<47} ║
║ Promise: {promise:<54} ║
║ Started: {started:<54} ║
╚══════════════════════════════════════════════════════════════════╝

PROMPT:
{state['prompt'][:200]}{'...' if len(state['prompt']) > 200 else ''}
""")


def main():
    parser = argparse.ArgumentParser(
        description="Iteration loop manager for long-task-harness",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # start command
    start_parser = subparsers.add_parser("start", help="Start a new iteration loop")
    start_parser.add_argument("prompt", help="The prompt to repeat each iteration")
    start_parser.add_argument("--promise", "-p", help="Completion promise text (exact match required)")
    start_parser.add_argument("--max", "-m", type=int, default=0, help="Max iterations (0=unlimited)")
    
    # check command
    check_parser = subparsers.add_parser("check", help="Check if loop should continue")
    check_parser.add_argument("--output", "-o", help="Last output to check for promise (or pipe via stdin)")
    
    # cancel command
    subparsers.add_parser("cancel", help="Cancel active loop")
    
    # status command
    subparsers.add_parser("status", help="Show loop status")
    
    args = parser.parse_args()
    
    if args.command == "start":
        start_loop(args.prompt, args.promise, args.max)
    elif args.command == "check":
        check_loop(args.output)
    elif args.command == "cancel":
        cancel_loop()
    elif args.command == "status":
        show_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
