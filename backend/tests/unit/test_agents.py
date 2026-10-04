"""Unit tests for agent base class and contract."""

from __future__ import annotations

import pytest

from app.agents.base import (
    Acknowledgement,
    AgentResult,
    BaseAgent,
    TaskBrief,
    AgentRegistry,
)


class DummyAgent(BaseAgent):
    """Test agent that always accepts and succeeds."""

    name = "dummy_agent"
    description = "A dummy agent for testing"
    prompt_version = "v1.0"
    model_tier = "haiku"

    async def acknowledge(self, brief: TaskBrief) -> Acknowledgement:
        return Acknowledgement(
            task_id=brief.task_id,
            agent_name=self.name,
            accepted=True,
            estimated_duration_seconds=1.0,
            reason="Accepted",
        )

    async def execute(self, brief: TaskBrief, ack: Acknowledgement) -> AgentResult:
        return AgentResult(
            task_id=brief.task_id,
            success=True,
            output={"result": "done"},
            confidence=0.95,
        )


class TestBaseAgent:
    """Test suite for BaseAgent contract."""

    @pytest.mark.asyncio
    async def test_agent_run_success(self) -> None:
        agent = DummyAgent()
        brief = TaskBrief(task_id="t1", description="Test task")
        result = await agent.run(brief)
        assert result.success is True
        assert result.output == {"result": "done"}
        assert result.confidence == 0.95

    @pytest.mark.asyncio
    async def test_agent_self_check(self) -> None:
        agent = DummyAgent()
        result = AgentResult(task_id="t1", success=True, output={}, confidence=0.9)
        checked = await agent.self_check(result)
        assert checked == result  # No-op by default


class TestAgentRegistry:
    """Test suite for AgentRegistry."""

    def test_register_and_get(self) -> None:
        registry = AgentRegistry()
        registry.register(DummyAgent)
        cls = registry.get("dummy_agent")
        assert cls is not None
        assert cls.name == "dummy_agent"

    def test_get_nonexistent(self) -> None:
        registry = AgentRegistry()
        assert registry.get("nonexistent") is None

    def test_list_agents(self) -> None:
        registry = AgentRegistry()
        registry.register(DummyAgent)
        agents = registry.list_agents()
        assert len(agents) >= 1
        names = [a["name"] for a in agents]
        assert "dummy_agent" in names