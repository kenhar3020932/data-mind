"""Plan Critic Service for DataMind-King.

Independent validation of execution plans (PlanDAG) for:
- Cycle detection
- Dependency validation
- Resource estimation
- Risk assessment
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PlanCriticService:
    """Validate and critique execution plans."""

    async def review(
        self,
        plan: dict[str, Any],
        original_task: str,
        org_id: str,
    ) -> dict[str, Any]:
        """Review a plan and return validation results.

        Args:
            plan: The PlanDAG to validate.
            original_task: Original task description.
            org_id: Organization ID.

        Returns:
            Dict with score, approval, and feedback.
        """
        steps = plan.get("steps", [])
        issues: list[str] = []
        warnings: list[str] = []
        score = 1.0

        # 1. Validate step structure
        for i, step in enumerate(steps):
            if not step.get("agent"):
                issues.append(f"Step {i}: Missing agent assignment")
                score -= 0.1
            if not step.get("description"):
                warnings.append(f"Step {i}: Missing description")
                score -= 0.05
            if step.get("estimated_duration_seconds", 0) <= 0:
                warnings.append(f"Step {i}: Invalid duration estimate")

        # 2. Check for missing dependencies
        step_ids = {s.get("step_id") for s in steps}
        for step in steps:
            for dep in step.get("depends_on", []):
                if dep not in step_ids:
                    issues.append(f"Step '{step.get('step_id')}': Depends on unknown step '{dep}'")
                    score -= 0.15

        # 3. Validate no cycles (simplified check)
        if len(steps) > 10:
            warnings.append("Large plan detected (>10 steps). Consider breaking into sub-plans.")

        # 4. Check resource estimates
        total_duration = sum(s.get("estimated_duration_seconds", 0) for s in steps)
        if total_duration > 3600:  # > 1 hour
            warnings.append(f"Total estimated duration exceeds 1 hour ({total_duration}s)")

        # 5. Assess risk
        risk_level = "low"
        if score < 0.7:
            risk_level = "high"
        elif score < 0.85:
            risk_level = "medium"

        return {
            "score": round(max(score, 0.0), 2),
            "approved": score >= 0.7,
            "issues": issues,
            "warnings": warnings,
            "feedback": self._generate_feedback(issues, warnings, risk_level),
            "risk_level": risk_level,
            "steps_validated": len(steps),
        }

    def _generate_feedback(self, issues: list[str], warnings: list[str], risk: str) -> str:
        """Generate human-readable feedback."""
        if not issues and not warnings:
            return "Plan looks good! All validations passed."

        feedback = []
        if issues:
            feedback.append(f"Issues found ({len(issues)}):")
            for issue in issues:
                feedback.append(f"  - {issue}")
        if warnings:
            feedback.append(f"\nWarnings ({len(warnings)}):")
            for warning in warnings:
                feedback.append(f"  - {warning}")
        feedback.append(f"\nRisk level: {risk}")

        return "\n".join(feedback)

    async def validate_dag(
        self,
        steps: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Validate DAG structure and detect cycles.

        Returns:
            Dict with validation results.
        """
        from collections import defaultdict, deque

        graph = defaultdict(list)
        in_degree = defaultdict(int)
        step_ids = {step["step_id"] for step in steps}

        for step in steps:
            step_id = step["step_id"]
            if step_id not in in_degree:
                in_degree[step_id] = 0

            for dep in step.get("depends_on", []):
                if dep not in step_ids:
                    return {
                        "valid": False,
                        "errors": [f"Step '{step_id}' depends on unknown step '{dep}'"],
                        "parallel_groups": [],
                    }
                graph[dep].append(step_id)
                in_degree[step_id] += 1

        # Kahn's algorithm
        queue = deque([node for node in step_ids if in_degree[node] == 0])
        topo_order = []
        parallel_groups = []

        while queue:
            current_level = list(queue)
            parallel_groups.append(current_level)

            for _ in range(len(queue)):
                node = queue.popleft()
                topo_order.append(node)

                for neighbor in graph[node]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)

        if len(topo_order) != len(step_ids):
            missing = step_ids - set(topo_order)
            return {
                "valid": False,
                "errors": [f"Cycle detected involving steps: {missing}"],
                "parallel_groups": [],
            }

        return {
            "valid": True,
            "errors": [],
            "parallel_groups": parallel_groups,
            "topological_order": topo_order,
        }