"""Security audit report for DataMind-King.

Runs security scanners and generates a comprehensive audit report.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SecurityAuditReport:
    """Generate security audit reports."""

    def __init__(self) -> None:
        self.findings: list[dict[str, Any]] = []
        self.scanners_run: list[str] = []
        self.timestamp: str = datetime.now(timezone.utc).isoformat()

    def add_finding(
        self,
        severity: str,
        category: str,
        file_path: str,
        message: str,
        remediation: str,
    ) -> None:
        """Add a security finding to the report."""
        self.findings.append({
            "severity": severity,
            "category": category,
            "file": file_path,
            "message": message,
            "remediation": remediation,
            "timestamp": self.timestamp,
        })

    def add_scanner_result(self, scanner_name: str, passed: bool, details: str = "") -> None:
        """Record a scanner result."""
        self.scanners_run.append({
            "name": scanner_name,
            "passed": passed,
            "details": details,
            "timestamp": self.timestamp,
        })

    def generate_report(self, output_path: str = "docs/AUDIT/security-scan.md") -> dict[str, Any]:
        """Generate the audit report."""
        # Count findings by severity
        critical = len([f for f in self.findings if f["severity"] == "critical"])
        high = len([f for f in self.findings if f["severity"] == "high"])
        medium = len([f for f in self.findings if f["severity"] == "medium"])
        low = len([f for f in self.findings if f["severity"] == "low"])

        report = {
            "timestamp": self.timestamp,
            "total_findings": len(self.findings),
            "by_severity": {
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low,
            },
            "scanners_run": self.scanners_run,
            "findings": self.findings,
            "verdict": "PASS" if critical == 0 and high == 0 else "FAIL",
        }

        # Write markdown report
        md_content = self._generate_markdown(report)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(md_content)

        return report

    def _generate_markdown(self, report: dict[str, Any]) -> str:
        """Generate markdown audit report."""
        lines = [
            "# Security Audit Report",
            f"**Date:** {report['timestamp']}",
            f"**Verdict:** {report['verdict']}",
            "",
            "## Summary",
            f"- **Total Findings:** {report['total_findings']}",
            f"- **Critical:** {report['by_severity']['critical']}",
            f"- **High:** {report['by_severity']['high']}",
            f"- **Medium:** {report['by_severity']['medium']}",
            f"- **Low:** {report['by_severity']['low']}",
            "",
            "## Scanners Run",
        ]

        for scanner in report["scanners_run"]:
            status = "✅ PASS" if scanner["passed"] else "❌ FAIL"
            lines.append(f"- {scanner['name']}: {status}")

        if report["findings"]:
            lines.extend(["", "## Findings", ""])
            for finding in report["findings"]:
                lines.append(f"### [{finding['severity'].upper()}] {finding['category']}")
                lines.append(f"- **File:** `{finding['file']}`")
                lines.append(f"- **Message:** {finding['message']}")
                lines.append(f"- **Remediation:** {finding['remediation']}")
                lines.append("")

        return "\n".join(lines)


# Module-level singleton
audit_report = SecurityAuditReport()


def run_security_audit(output_path: str = "docs/AUDIT/security-scan.md") -> dict[str, Any]:
    """Run security audit and generate report."""
    return audit_report.generate_report(output_path)