"""Agent service for DataMind-King."""

from __future__ import annotations

from typing import Any

from app.agents.base import AgentRegistry, BaseAgent, TaskBrief

registry = AgentRegistry()


class AgentService:
    """Service for running agents."""

    async def run_agent(
        self,
        agent_name: str,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run a named agent with the given task."""
        agent_cls = registry.get(agent_name)
        if agent_cls is None:
            return {"error": f"Agent '{agent_name}' not found"}

        agent = agent_cls()
        brief = TaskBrief(
            task_id="",
            description=task,
            context=context or {},
        )
        result = await agent.run(brief)
        return {
            "task_id": result.task_id,
            "success": result.success,
            "output": result.output,
            "confidence": result.confidence,
            "error": result.error,
        }


# Module-level singleton
service = AgentService()
