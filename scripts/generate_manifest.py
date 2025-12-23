#!/usr/bin/env python3
"""
Generate a .manifest.yaml for progressive disclosure of codebase structure.

Extracts metadata from code files (docstrings, exports, dependencies) into
a single manifest that agents can read cheaply before diving into full files.

Usage:
    python3 generate_manifest.py [directory] [--output manifest.yaml]
    
The manifest enables agents to understand codebase structure without reading
every file, paying the token cost only when they need specific details.
"""

import argparse
import ast
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Any


def extract_python_metadata(file_path: Path) -> dict[str, Any] | None:
    """Extract metadata from a Python file using AST parsing."""
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError):
        return None
    
    metadata = {}
    
    # Module docstring
    docstring = ast.get_docstring(tree)
    if docstring:
        # Take first paragraph only for brevity
        first_para = docstring.split('\n\n')[0].strip()
        # Truncate if too long
        if len(first_para) > 200:
            first_para = first_para[:197] + '...'
        metadata['purpose'] = first_para
    
    # Find __all__ if defined
    exports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == '__all__':
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant):
                                exports.append(elt.value)
    
    # If no __all__, extract top-level public classes and functions
    if not exports:
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef) and not node.name.startswith('_'):
                exports.append(node.name)
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                exports.append(node.name)
    
    if exports:
        metadata['exports'] = exports[:10]  # Limit to avoid bloat
        if len(exports) > 10:
            metadata['exports_truncated'] = True
    
    # Extract imports to infer dependencies
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    
    # Filter to likely local imports (not stdlib/third-party)
    # This is heuristic - could be improved
    local_imports = [i for i in imports if not i.startswith('_') and i.islower()]
    if local_imports:
        metadata['imports'] = sorted(local_imports)[:10]
    
    # Line count as complexity hint
    line_count = len(content.splitlines())
    if line_count > 500:
        metadata['size'] = 'large'
    elif line_count > 100:
        metadata['size'] = 'medium'
    else:
        metadata['size'] = 'small'
    
    return metadata if metadata else None


def extract_js_ts_metadata(file_path: Path) -> dict[str, Any] | None:
    """Extract basic metadata from JS/TS files (simplified, no full parsing)."""
    try:
        content = file_path.read_text()
    except UnicodeDecodeError:
        return None
    
    metadata = {}
    lines = content.splitlines()
    
    # Look for JSDoc at top of file
    if lines and lines[0].strip().startswith('/**'):
        doc_lines = []
        for line in lines:
            doc_lines.append(line)
            if '*/' in line:
                break
        if doc_lines:
            # Extract description from JSDoc
            doc_text = ' '.join(doc_lines)
            # Simple extraction - get text between /** and */
            import re
            match = re.search(r'/\*\*\s*\n?\s*\*?\s*(.+?)(?:\n|\*)', doc_text)
            if match:
                metadata['purpose'] = match.group(1).strip()[:200]
    
    # Count exports
    export_count = content.count('export ')
    if export_count > 0:
        metadata['export_count'] = export_count
    
    # Line count
    line_count = len(lines)
    if line_count > 500:
        metadata['size'] = 'large'
    elif line_count > 100:
        metadata['size'] = 'medium'
    else:
        metadata['size'] = 'small'
    
    return metadata if metadata else None


def should_include_file(file_path: Path, root: Path) -> bool:
    """Determine if a file should be included in the manifest."""
    # Skip hidden files/directories
    for part in file_path.relative_to(root).parts:
        if part.startswith('.'):
            return False
    
    # Skip common non-code directories
    skip_dirs = {'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build', 
                 'egg-info', '.git', '.pytest_cache', '.mypy_cache'}
    for part in file_path.relative_to(root).parts:
        if part in skip_dirs or part.endswith('.egg-info'):
            return False
    
    # Skip test files (could be configurable)
    name = file_path.name
    if name.startswith('test_') or name.endswith('_test.py'):
        return False
    
    return True


def generate_manifest(root_dir: Path) -> dict[str, Any]:
    """Generate a manifest for all code files in a directory."""
    manifest = {
        'generated': datetime.now().isoformat(),
        'root': str(root_dir.resolve()),
        'files': {}
    }
    
    # Supported extensions and their extractors
    extractors = {
        '.py': extract_python_metadata,
        '.js': extract_js_ts_metadata,
        '.ts': extract_js_ts_metadata,
        '.tsx': extract_js_ts_metadata,
        '.jsx': extract_js_ts_metadata,
    }
    
    for ext, extractor in extractors.items():
        for file_path in root_dir.rglob(f'*{ext}'):
            if not should_include_file(file_path, root_dir):
                continue
            
            rel_path = str(file_path.relative_to(root_dir))
            metadata = extractor(file_path)
            
            if metadata:
                manifest['files'][rel_path] = metadata
    
    # Sort files by path for consistent output
    manifest['files'] = dict(sorted(manifest['files'].items()))
    
    # Add summary stats
    manifest['summary'] = {
        'total_files': len(manifest['files']),
        'by_size': {
            'small': sum(1 for f in manifest['files'].values() if f.get('size') == 'small'),
            'medium': sum(1 for f in manifest['files'].values() if f.get('size') == 'medium'),
            'large': sum(1 for f in manifest['files'].values() if f.get('size') == 'large'),
        }
    }
    
    return manifest


def format_yaml(manifest: dict) -> str:
    """Format manifest as YAML (simple implementation, no external deps)."""
    lines = ['# Auto-generated manifest for progressive disclosure',
             '# Agents: read this first to understand codebase structure',
             '# Regenerate with: python3 scripts/generate_manifest.py',
             '']
    
    def format_value(val, indent=0):
        prefix = '  ' * indent
        if isinstance(val, dict):
            result = []
            for k, v in val.items():
                if isinstance(v, (dict, list)):
                    result.append(f'{prefix}{k}:')
                    result.append(format_value(v, indent + 1))
                else:
                    result.append(f'{prefix}{k}: {format_scalar(v)}')
            return '\n'.join(result)
        elif isinstance(val, list):
            if not val:
                return f'{prefix}[]'
            result = []
            for item in val:
                if isinstance(item, dict):
                    result.append(f'{prefix}-')
                    result.append(format_value(item, indent + 1))
                else:
                    result.append(f'{prefix}- {format_scalar(item)}')
            return '\n'.join(result)
        else:
            return f'{prefix}{format_scalar(val)}'
    
    def format_scalar(val):
        if isinstance(val, bool):
            return 'true' if val else 'false'
        elif isinstance(val, str):
            if '\n' in val or ':' in val or '#' in val or val.startswith('"'):
                return f'"{val}"'
            return val
        else:
            return str(val)
    
    lines.append(format_value(manifest))
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Generate a manifest for progressive codebase disclosure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 generate_manifest.py                    # Current directory
    python3 generate_manifest.py ./src              # Specific directory
    python3 generate_manifest.py -o .manifest.yaml  # Custom output file
        """
    )
    parser.add_argument('directory', nargs='?', default='.',
                        help='Root directory to scan (default: current)')
    parser.add_argument('-o', '--output', default='.manifest.yaml',
                        help='Output file path (default: .manifest.yaml)')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON instead of YAML')
    parser.add_argument('--stdout', action='store_true',
                        help='Print to stdout instead of file')
    
    args = parser.parse_args()
    
    root_dir = Path(args.directory).resolve()
    if not root_dir.is_dir():
        print(f"Error: {root_dir} is not a directory", file=sys.stderr)
        sys.exit(1)
    
    print(f"Scanning {root_dir}...", file=sys.stderr)
    manifest = generate_manifest(root_dir)
    
    if args.json:
        import json
        output = json.dumps(manifest, indent=2)
    else:
        output = format_yaml(manifest)
    
    if args.stdout:
        print(output)
    else:
        output_path = Path(args.output)
        output_path.write_text(output)
        print(f"  ✅ Generated {output_path} ({manifest['summary']['total_files']} files)", 
              file=sys.stderr)


if __name__ == '__main__':
    main()
