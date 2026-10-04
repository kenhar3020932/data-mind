#!/usr/bin/env python3
"""Check for stubs, TODOs, and incomplete implementations in codebase."""

import os
import re
import sys
from pathlib import Path


STUB_PATTERNS = [
    r'^\s*pass\s*$',
    r'^\s*#\s*TODO',
    r'^\s*#\s*FIXME',
    r'NotImplementedError',
    r'^\s*\.\.\.\s*$',
]

SKIP_DIRS = {'__pycache__', '.venv', 'node_modules', '.git', 'test'}


def check_file(filepath: Path) -> list[str]:
    """Check a single file for stubs."""
    issues = []
    try:
        content = filepath.read_text(encoding='utf-8')
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            for pattern in STUB_PATTERNS:
                if re.search(pattern, line):
                    issues.append(f"{filepath}:{i}: {line.strip()}")
                    break
    except (UnicodeDecodeError, PermissionError):
        pass
    return issues


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / 'backend' / 'app'
    frontend_dir = project_root / 'frontend' / 'src'

    all_issues = []

    # Check backend Python files
    if backend_dir.exists():
        for filepath in backend_dir.rglob('*.py'):
            if any(skip in filepath.parts for skip in SKIP_DIRS):
                continue
            if 'test_' in filepath.name or filepath.name.endswith('_test.py'):
                continue
            issues = check_file(filepath)
            all_issues.extend(issues)

    # Check frontend TypeScript files
    if frontend_dir.exists():
        for ext in ['*.ts', '*.tsx']:
            for filepath in frontend_dir.rglob(ext):
                if any(skip in filepath.parts for skip in SKIP_DIRS):
                    continue
                issues = check_file(filepath)
                all_issues.extend(issues)

    if all_issues:
        print("❌ STUBS/TODOs FOUND:")
        for issue in all_issues[:20]:  # Show first 20
            print(f"  {issue}")
        if len(all_issues) > 20:
            print(f"  ... and {len(all_issues) - 20} more")
        sys.exit(1)
    else:
        print("✅ No stubs or TODOs found")
        sys.exit(0)


if __name__ == '__main__':
    main()
