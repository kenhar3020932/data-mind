"""Gitleaks configuration for DataMind-King.

Scan for hardcoded secrets in code, config files, and commits.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


class GitleaksScanner:
    """Run gitleaks to detect secrets in the codebase."""

    def __init__(self, repo_path: str = ".") -> None:
        self.repo_path = repo_path

    def scan(self, verbose: bool = False) -> dict[str, Any]:
        """Run gitleaks scan and return results."""
        cmd = ["gitleaks", "detect", "--source", self.repo_path, "--report-format", "json"]
        if verbose:
            cmd.append("--verbose")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            findings = []
            if result.stdout:
                import json
                findings = json.loads(result.stdout)

            return {
                "found_secrets": len(findings),
                "findings": findings,
                "exit_code": result.returncode,
            }
        except FileNotFoundError:
            return {
                "found_secrets": -1,
                "findings": [],
                "error": "gitleaks not installed",
            }
        except subprocess.TimeoutExpired:
            return {
                "found_secrets": -1,
                "findings": [],
                "error": "Scan timed out",
            }

    def check_no_secrets(self) -> bool:
        """Check that no secrets are found in the codebase."""
        result = self.scan()
        return result["found_secrets"] == 0


# Module-level singleton
scanner = GitleaksScanner()


def scan_for_secrets(verbose: bool = False) -> dict[str, Any]:
    """Convenience function to scan for secrets."""
    return scanner.scan(verbose)


def check_clean() -> bool:
    """Check that repository is clean of secrets."""
    return scanner.check_no_secrets()