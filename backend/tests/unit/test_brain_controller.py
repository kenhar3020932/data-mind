"""Unit tests for Brain controller."""

from __future__ import annotations

import pytest

from app.brain.langgraph_controller import BrainController


class TestBrainController:
    """Test suite for Brain controller."""

    def test_controller_initialization(self) -> None:
        """Test controller can be instantiated."""
        controller = BrainController()
        assert controller is not None

    @pytest.mark.asyncio
    async def test_run_controller(self) -> None:
        """Test running the controller loop."""
        controller = BrainController()
        result = await controller.run(
            user_input="Analyze sales data",
            dataset_id="ds-123",
        )
        # Result is now a dict (TypedDict)
        assert result["current_stage"] == "learn"
        assert len(result["events"]) == 7
        assert result["confidence"] > 0

    def test_state_schema(self) -> None:
        """Test BrainState schema structure."""
        from app.brain.langgraph_controller import BrainState
        initial_state: BrainState = {
            "current_stage": "understand",
            "task_id": "task-123",
            "context": {},
            "plan": None,
            "result": None,
            "confidence": 0.0,
            "events": [],
        }
        assert initial_state["current_stage"] == "understand"