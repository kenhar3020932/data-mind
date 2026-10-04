"""Plan validator and critic for DataMind-King."""

from __future__ import annotations

from typing import Any


class PlanCritic:
    """Critique and optimize execution plans."""

    def __init__(self) -> None:
        self.findings: list[dict[str, Any]] = []

    def critique(self, plan: dict[str, Any]) -> dict[str, Any]:
        """Analyze a plan and return findings."""
        steps = plan.get("steps", [])
        self.findings = []

        # Check for circular dependencies
        dependencies = plan.get("dependencies", {})
        if self._has_cycle(dependencies):
            self.findings.append({
                "type": "error",
                "message": "Circular dependency detected in plan",
            })

        # Check for missing fallback steps
        for step in steps:
            if "fallback" not in step:
                self.findings.append({
                    "type": "warning",
                    "message": f"Step '{step.get('name', '')}' has no fallback",
                })

        return {
            "plan": plan,
            "findings": self.findings,
            "approved": len([f for f in self.findings if f["type"] == "error"]) == 0,
        }

    def _has_cycle(self, dependencies: dict[str, list[str]]) -> bool:
        """Detect cycles in dependency graph using DFS."""
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for dep in dependencies.get(node, []):
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in rec_stack:
                    return True
            rec_stack.discard(node)
            return False

        for node in dependencies:
            if node not in visited:
                if dfs(node):
                    return True
        return False


# Module-level singleton
critic = PlanCritic()
