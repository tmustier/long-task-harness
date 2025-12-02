#!/usr/bin/env python3
"""
Extract relevant feature information from features.json for session startup.

Default: shows incomplete features (full details) + completed features (names only)
Use --all for full features.json content.
"""

import argparse
import json
import sys
from pathlib import Path


def find_features_file() -> Path | None:
    """Find features.json in current directory or parents."""
    cwd = Path.cwd()
    for path in [cwd, *cwd.parents]:
        features_file = path / "features.json"
        if features_file.exists():
            return features_file
    return None


def format_feature_compact(feature: dict) -> str:
    """Format a feature as compact JSON (for incomplete features)."""
    # Include all fields for incomplete features
    return json.dumps(feature, indent=2)


def format_feature_oneline(feature: dict) -> str:
    """Format a feature as a single line (for completed features)."""
    status = "✓" if feature.get("passes") else "○"
    return f"  {feature['id']:20} {feature['name']:40} {status}"


def format_output(data: dict, show_all: bool) -> str:
    """Format the features output."""
    features = data.get("features", [])
    metadata = data.get("metadata", {})

    total = len(features)
    completed = [f for f in features if f.get("passes")]
    incomplete = [f for f in features if not f.get("passes")]

    output_parts = []

    # Summary line
    output_parts.append(f"[Features: {len(completed)}/{total} complete]\n")

    if show_all:
        # Show full JSON
        output_parts.append("\n" + json.dumps(data, indent=2))
        return ''.join(output_parts)

    # Priority order (if available)
    priority_order = metadata.get("priority_order", [])

    # Sort incomplete by priority order
    if priority_order:
        def priority_key(f):
            try:
                return priority_order.index(f["id"])
            except ValueError:
                return len(priority_order)
        incomplete = sorted(incomplete, key=priority_key)

    # Incomplete features (full details)
    if incomplete:
        output_parts.append("\nINCOMPLETE (full details):\n")
        for feature in incomplete:
            output_parts.append(f"\n{format_feature_compact(feature)}\n")
    else:
        output_parts.append("\nAll features complete! 🎉\n")

    # Completed features (names only)
    if completed:
        output_parts.append(f"\nCOMPLETED ({len(completed)}):\n")
        # Sort by id for consistent display
        for feature in sorted(completed, key=lambda f: f["id"]):
            output_parts.append(format_feature_oneline(feature) + "\n")

    # Hint
    output_parts.append(f"\n[Full details: --all]")

    return ''.join(output_parts)


def main():
    parser = argparse.ArgumentParser(
        description="Extract relevant feature information from features.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 read_features.py           # incomplete (full) + completed (names)
  python3 read_features.py --all     # full features.json
        """
    )
    parser.add_argument('--all', action='store_true',
                        help='Show full features.json content')
    parser.add_argument('--file', type=Path,
                        help='Path to features.json (default: auto-detect)')

    args = parser.parse_args()

    # Find features file
    if args.file:
        features_file = args.file
    else:
        features_file = find_features_file()

    if not features_file or not features_file.exists():
        print("Error: features.json not found", file=sys.stderr)
        print("Run from a project directory with features.json, or use --file", file=sys.stderr)
        sys.exit(1)

    # Read and parse
    try:
        data = json.loads(features_file.read_text())
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in features.json: {e}", file=sys.stderr)
        sys.exit(1)

    # Format output
    output = format_output(data, args.all)
    print(output)


if __name__ == "__main__":
    main()
