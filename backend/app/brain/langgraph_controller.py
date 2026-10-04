"""LangGraph controller for DataMind-King.

Implements the 7-stage Brain controller loop using LangGraph:
  Understand → Profile → Plan → Critique → Execute → Verify → Learn
"""

from __future__ import annotations

from typing import Any

from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict


# Define state schema as TypedDict for LangGraph
class BrainState(TypedDict):
    """State for the Brain controller loop."""
    current_stage: str
    task_id: str
    context: dict[str, Any]
    plan: dict[str, Any] | None
    result: dict[str, Any] | None
    confidence: float
    events: list[dict[str, Any]]


class BrainController:
    """7-stage controller loop using LangGraph."""

    def __init__(self) -> None:
        self.graph = StateGraph(BrainState)
        self._build_graph()

    def _build_graph(self) -> None:
        """Build the LangGraph workflow."""
        # Define nodes for each stage
        self.graph.add_node("understand", self._stage_understand)
        self.graph.add_node("profile", self._stage_profile)
        self.graph.add_node("plan", self._stage_plan)
        self.graph.add_node("critique", self._stage_critique)
        self.graph.add_node("execute", self._stage_execute)
        self.graph.add_node("verify", self._stage_verify)
        self.graph.add_node("learn", self._stage_learn)

        # Define edges
        self.graph.set_entry_point("understand")
        self.graph.add_edge("understand", "profile")
        self.graph.add_edge("profile", "plan")
        self.graph.add_edge("plan", "critique")
        self.graph.add_edge("critique", "execute")
        self.graph.add_edge("execute", "verify")
        self.graph.add_edge("verify", "learn")
        self.graph.add_edge("learn", END)

    async def _stage_understand(self, state: BrainState) -> dict[str, Any]:
        """Stage 1: Understand the user's request."""
        state["current_stage"] = "understand"
        state["events"] = state.get("events", []) + [{"stage": "understand", "action": "parsed"}]
        return state

    async def _stage_profile(self, state: BrainState) -> dict[str, Any]:
        """Stage 2: Profile the dataset."""
        state["current_stage"] = "profile"
        state["events"] = state.get("events", []) + [{"stage": "profile", "action": "started"}]
        return state

    async def _stage_plan(self, state: BrainState) -> dict[str, Any]:
        """Stage 3: Create execution plan."""
        state["current_stage"] = "plan"
        state["plan"] = {"steps": [], "dependencies": {}}
        state["events"] = state.get("events", []) + [{"stage": "plan", "action": "generated"}]
        return state

    async def _stage_critique(self, state: BrainState) -> dict[str, Any]:
        """Stage 4: Critique and optimize the plan."""
        state["current_stage"] = "critique"
        if state.get("plan"):
            state["plan"]["critiqued"] = True
        state["events"] = state.get("events", []) + [{"stage": "critique", "action": "completed"}]
        return state

    async def _stage_execute(self, state: BrainState) -> dict[str, Any]:
        """Stage 5: Execute the plan."""
        state["current_stage"] = "execute"
        state["events"] = state.get("events", []) + [{"stage": "execute", "action": "started"}]
        return state

    async def _stage_verify(self, state: BrainState) -> dict[str, Any]:
        """Stage 6: Verify results."""
        state["current_stage"] = "verify"
        state["confidence"] = 0.85
        state["events"] = state.get("events", []) + [{"stage": "verify", "action": "completed"}]
        return state

    async def _stage_learn(self, state: BrainState) -> dict[str, Any]:
        """Stage 7: Learn from results."""
        state["current_stage"] = "learn"
        state["events"] = state.get("events", []) + [{"stage": "learn", "action": "finished"}]
        return state

    def compile(self) -> Any:
        """Compile the graph."""
        return self.graph.compile()

    async def run(self, user_input: str, dataset_id: str) -> dict[str, Any]:
        """Run the full controller loop."""
        initial_state: BrainState = {
            "current_stage": "understand",
            "task_id": f"task-{dataset_id}",
            "context": {"user_input": user_input, "dataset_id": dataset_id},
            "plan": None,
            "result": None,
            "confidence": 0.0,
            "events": [],
        }

        compiled = self.compile()
        result = await compiled.ainvoke(initial_state)
        return result


# Module-level singleton
controller = BrainController()