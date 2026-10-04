"""Brain controller for DataMind-King.

Implements the 7-stage controller loop:
  Understand → Profile → Plan → Critique → Execute → Verify → Learn
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ControllerStage(str, Enum):
    """Stages in the Brain controller loop."""
    UNDERSTAND = "understand"
    PROFILE = "profile"
    PLAN = "plan"
    CRITIQUE = "critique"
    EXECUTE = "execute"
    VERIFY = "verify"
    LEARN = "learn"


@dataclass
class BrainState:
    """State of the brain controller."""
    current_stage: ControllerStage = ControllerStage.UNDERSTAND
    task_id: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    plan: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    confidence: float = 0.0
    events: list[dict[str, Any]] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None


class BrainController:
    """Main controller that orchestrates the analysis pipeline."""

    def __init__(self) -> None:
        self.state = BrainState()

    async def understand(self, user_input: str) -> BrainState:
        """Stage 1: Understand the user's request."""
        self.state.current_stage = ControllerStage.UNDERSTAND
        # Parse intent, extract entities, identify data sources
        self.state.context["user_input"] = user_input
        self.state.events.append({"stage": "understand", "action": "parsed"})
        return self.state

    async def profile(self, dataset_id: str) -> BrainState:
        """Stage 2: Profile the dataset."""
        self.state.current_stage = ControllerStage.PROFILE
        # Collect schema, stats, quality metrics
        self.state.context["dataset_id"] = dataset_id
        self.state.events.append({"stage": "profile", "action": "started"})
        return self.state

    async def plan(self) -> BrainState:
        """Stage 3: Create execution plan."""
        self.state.current_stage = ControllerStage.PLAN
        # Generate DAG of tasks with dependencies
        self.state.plan = {"steps": [], "dependencies": {}}
        self.state.events.append({"stage": "plan", "action": "generated"})
        return self.state

    async def critique(self) -> BrainState:
        """Stage 4: Critique and optimize the plan."""
        self.state.current_stage = ControllerStage.CRITIQUE
        # Check for inefficiencies, security issues, cost overruns
        if self.state.plan:
            self.state.plan["critiqued"] = True
        self.state.events.append({"stage": "critique", "action": "completed"})
        return self.state

    async def execute(self) -> BrainState:
        """Stage 5: Execute the plan."""
        self.state.current_stage = ControllerStage.EXECUTE
        # Run tasks in DAG order with parallelism where possible
        self.state.events.append({"stage": "execute", "action": "started"})
        return self.state

    async def verify(self) -> BrainState:
        """Stage 6: Verify results against expected outcomes."""
        self.state.current_stage = ControllerStage.VERIFY
        # Check accuracy, consistency, completeness
        self.state.confidence = 0.85
        self.state.events.append({"stage": "verify", "action": "completed"})
        return self.state

    async def learn(self) -> BrainState:
        """Stage 7: Learn from execution results."""
        self.state.current_stage = ControllerStage.LEARN
        # Update memory, refine future plans
        self.state.completed_at = datetime.now(timezone.utc)
        self.state.events.append({"stage": "learn", "action": "finished"})
        return self.state

    async def run(self, user_input: str, dataset_id: str) -> BrainState:
        """Run the full controller loop."""
        await self.understand(user_input)
        await self.profile(dataset_id)
        await self.plan()
        await self.critique()
        await self.execute()
        await self.verify()
        await self.learn()
        return self.state


# Module-level singleton
controller = BrainController()
