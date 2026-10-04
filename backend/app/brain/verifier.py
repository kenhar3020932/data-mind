"""Verifier agent for DataMind-King.

Validates execution results against expected outcomes.
"""

from __future__ import annotations

from typing import Any


class VerificationAgent:
    """Verify results and detect hallucinations."""

    def __init__(self) -> None:
        self.checks: list[str] = []

    def verify_result(self, result: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
        """Verify a result against expected values."""
        checks = []
        passed = True

        # Check required fields
        for field in expected.get("fields", []):
            if field not in result:
                checks.append({"field": field, "passed": False, "reason": "Missing field"})
                passed = False
            else:
                checks.append({"field": field, "passed": True})

        # Check value ranges
        for field, bounds in expected.get("ranges", {}).items():
            value = result.get(field)
            if value is not None:
                min_val = bounds.get("min")
                max_val = bounds.get("max")
                if min_val is not None and value < min_val:
                    checks.append({"field": field, "passed": False, "reason": f"Below minimum {min_val}"})
                    passed = False
                elif max_val is not None and value > max_val:
                    checks.append({"field": field, "passed": False, "reason": f"Above maximum {max_val}"})
                    passed = False
                else:
                    checks.append({"field": field, "passed": True})

        return {
            "passed": passed,
            "checks": checks,
            "confidence": sum(1 for c in checks if c["passed"]) / max(len(checks), 1),
        }


# Module-level singleton
verifier = VerificationAgent()
