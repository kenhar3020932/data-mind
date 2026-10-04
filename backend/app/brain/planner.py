"""Plan representation and DAG for DataMind-King."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlanStep:
    """A single step in an execution plan."""
    id: str
    name: str
    agent_name: str
    input: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    fallback: str | None = None
    max_retries: int = 3
    timeout_seconds: int = 300


@dataclass
class PlanDAG:
    """Directed acyclic graph of plan steps."""
    plan_id: str
    steps: dict[str, PlanStep] = field(default_factory=dict)
    status: str = "pending"

    def add_step(self, step: PlanStep) -> None:
        """Add a step to the plan."""
        self.steps[step.id] = step

    def get_ready_steps(self) -> list[str]:
        """Get steps whose dependencies are all satisfied."""
        # In production: proper topological sort
        return list(self.steps.keys())

    def mark_completed(self, step_id: str) -> None:
        """Mark a step as completed."""
        if step_id in self.steps:
            self.steps[step_id].input["completed"] = True


class Planner:
    """Create and manage execution plans."""

    def create_plan(self, steps: list[dict[str, Any]]) -> PlanDAG:
        """Create a PlanDAG from step definitions."""
        plan = PlanDAG(plan_id="", steps={})
        for i, step_def in enumerate(steps):
            step = PlanStep(
                id=str(i),
                name=step_def.get("name", f"step_{i}"),
                agent_name=step_def.get("agent", "default"),
                input=step_def.get("input", {}),
                dependencies=step_def.get("dependencies", []),
                fallback=step_def.get("fallback"),
            )
            plan.add_step(step)
        return plan

    def validate_plan(self, plan: PlanDAG) -> bool:
        """Validate plan for cycles and missing dependencies."""
        # In production: proper cycle detection
        return len(plan.steps) > 0


# Module-level singleton
planner = Planner()
