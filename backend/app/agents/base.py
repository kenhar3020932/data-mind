"""Base Agent Class - Ultra God Mode.

Defines the abstract interface for all DataMind-King agents with
proper ABC enforcement, type-safe interfaces, and registry management.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TaskBrief(BaseModel):
    """Task brief passed to agents for execution."""

    task_id: str
    org_id: str = "test-org"  # Default for tests
    context: dict[str, Any] = Field(default_factory=dict)
    description: str | None = None  # Alias for context['task'] for backward compatibility

    def get(self, key: str, default: Any = None) -> Any:
        """Get context value with default."""
        return self.context.get(key, default)

    @classmethod
    def create(cls, task_id: str, description: str | None = None, **kwargs: Any) -> "TaskBrief":
        """Create a TaskBrief from description.

        Args:
            task_id: Unique task identifier.
            description: Task description.
            **kwargs: Additional fields (org_id, context, etc.).

        Returns:
            TaskBrief instance.
        """
        context = kwargs.pop("context", {})
        if description:
            context["task"] = description
        return cls(task_id=task_id, context=context, **kwargs)


class Acknowledgement(BaseModel):
    """Agent acknowledgement of a task."""

    task_id: str
    agent_name: str
    accepted: bool
    estimated_duration_seconds: float = 0.0
    reason: str = ""


class AgentResult(BaseModel):
    """Result from agent execution."""

    task_id: str
    success: bool
    output: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    tokens_used: int = 0
    cost_usd: float = 0.0
    error: str | None = None
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def duration_ms(self) -> float:
        """Calculate execution duration in milliseconds if timestamp available."""
        return 0.0  # Computed by caller

    def __eq__(self, other: object) -> bool:
        """Compare results for equality."""
        if not isinstance(other, AgentResult):
            return NotImplemented
        return (
            self.task_id == other.task_id
            and self.success == other.success
            and self.output == other.output
            and abs(self.confidence - other.confidence) < 0.001
        )


class BaseAgent(ABC):
    """Abstract base class for all DataMind-King agents.

    All agents must implement acknowledge() and execute() methods.
    Subclasses should set class-level metadata (name, description, etc.).
    """

    name: str = "base_agent"
    description: str = ""
    prompt_version: str = "v1.0"
    model_tier: str = "sonnet"

    async def run(self, brief: TaskBrief) -> AgentResult:
        """Run the agent with automatic acknowledge + execute flow.

        Args:
            brief: Task brief with all context.

        Returns:
            AgentResult with output and metrics.
        """
        ack = await self.acknowledge(brief)
        if not ack.accepted:
            return AgentResult(
                task_id=brief.task_id,
                success=False,
                error=f"Agent {self.name} rejected task: {ack.reason}",
                confidence=0.0,
            )
        return await self.execute(brief, ack)

    async def self_check(self, result: AgentResult) -> AgentResult:
        """Validate agent result for correctness and completeness.

        Args:
            result: Agent execution result.

        Returns:
            Validated result (no-op by default).
        """
        return result

    @abstractmethod
    async def acknowledge(self, brief: TaskBrief) -> Acknowledgement:
        """Acknowledge a task and provide execution estimate.

        Args:
            brief: Task brief containing task_id, org_id, and context.

        Returns:
            Acknowledgement with acceptance status and timing estimate.
        """

    @abstractmethod
    async def execute(self, brief: TaskBrief, ack: Acknowledgement) -> AgentResult:
        """Execute the agent's core functionality.

        Args:
            brief: Task brief with all context.
            ack: Prior acknowledgement.

        Returns:
            AgentResult with output, confidence, and metrics.
        """


class AgentRegistry:
    """Registry for agent discovery and lifecycle management.

    Maintains singleton instance for global access.
    """

    def __init__(self) -> None:
        self._agents: dict[str, type[BaseAgent]] = {}
        self._instances: dict[str, BaseAgent] = {}

    def register(self, agent_class: type[BaseAgent]) -> None:
        """Register an agent class.

        Args:
            agent_class: Agent class to register.
        """
        if not issubclass(agent_class, BaseAgent):
            raise TypeError(f"{agent_class.__name__} must subclass BaseAgent")
        self._agents[agent_class.name] = agent_class
        logger.info(f"Registered agent: {agent_class.name}")

    def get(self, name: str) -> type[BaseAgent] | None:
        """Get registered agent class by name.

        Args:
            name: Agent name.

        Returns:
            Agent class or None if not found.
        """
        return self._agents.get(name)

    def get_instance(self, name: str) -> BaseAgent | None:
        """Get or create agent instance.

        Args:
            name: Agent name.

        Returns:
            Agent instance or None.
        """
        if name not in self._instances:
            agent_class = self._agents.get(name)
            if agent_class:
                self._instances[name] = agent_class()
        return self._instances.get(name)

    def list_agents(self) -> list[dict[str, Any]]:
        """List all registered agents as dicts.

        Returns:
            List of agent metadata dicts.
        """
        return [
            {
                "name": info["name"],
                "description": info["description"],
                "prompt_version": info["prompt_version"],
                "model_tier": info["model_tier"],
            }
            for info in self.list_agent_info().values()
        ]

    def list_agent_info(self) -> dict[str, dict[str, Any]]:
        """Get metadata for all registered agents.

        Returns:
            Dict mapping agent name to metadata.
        """
        return {
            name: {
                "name": cls.name,
                "description": cls.description,
                "prompt_version": cls.prompt_version,
                "model_tier": cls.model_tier,
            }
            for name, cls in self._agents.items()
        }

    def get_agent_info(self, name: str) -> dict[str, Any] | None:
        """Get metadata about a registered agent.

        Args:
            name: Agent name.

        Returns:
            Agent metadata dict or None.
        """
        agent_class = self._agents.get(name)
        if agent_class:
            return {
                "name": agent_class.name,
                "description": agent_class.description,
                "prompt_version": agent_class.prompt_version,
                "model_tier": agent_class.model_tier,
            }
        return None


# Module-level singleton
registry = AgentRegistry()
