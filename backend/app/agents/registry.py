"""Agent registry module for DataMind-King.

Provides centralized agent discovery, registration, and lifecycle management.
"""
from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Central registry for all DataMind-King agents.

    Manages agent discovery, registration, and retrieval with support for
    hot-reloading and version tracking.
    """

    _agents: dict[str, dict[str, Any]] = {}
    _initialized: bool = False

    @classmethod
    def register(cls, agent: type) -> None:
        """Register an agent class in the registry."""
        if not hasattr(agent, "name"):
            raise ValueError(f"Agent class {agent.__name__} must have a 'name' attribute")
        cls._agents[agent.name] = {
            "class": agent,
            "module": agent.__module__,
            "description": getattr(agent, "description", ""),
            "prompt_version": getattr(agent, "prompt_version", "v1.0"),
            "model_tier": getattr(agent, "model_tier", "sonnet"),
        }
        logger.debug("Registered agent: %s", agent.name)

    @classmethod
    def get(cls, name: str) -> type | None:
        """Get an agent class by name."""
        entry = cls._agents.get(name)
        return entry["class"] if entry else None

    @classmethod
    def list_agents(cls) -> list[dict[str, Any]]:
        """List all registered agents with metadata."""
        return [
            {
                "name": name,
                "description": info["description"],
                "prompt_version": info["prompt_version"],
                "model_tier": info["model_tier"],
                "module": info["module"],
            }
            for name, info in cls._agents.items()
        ]

    @classmethod
    def initialize(cls, agents_dir: str | None = None) -> None:
        """Auto-discover and register all agents from the agents package.

        Scans the agents directory for packages containing agent classes
        and registers them automatically.
        """
        if cls._initialized:
            return

        base_dir = Path(__file__).parent.parent.parent
        scan_dirs = [
            base_dir / "app" / "agents",
            Path(agents_dir) if agents_dir else None,
        ]

        for scan_dir in scan_dirs:
            if not scan_dir or not scan_dir.is_dir():
                continue

            for agent_pkg in sorted(scan_dir.iterdir()):
                if not agent_pkg.is_dir() or agent_pkg.name.startswith("_"):
                    continue
                try:
                    agent_mod = importlib.import_module(f"app.agents.{agent_pkg.name}")
                    for attr_name in dir(agent_mod):
                        attr = getattr(agent_mod, attr_name)
                        if (
                            isinstance(attr, type)
                            and hasattr(attr, "name")
                            and hasattr(attr, "execute")
                        ):
                            cls.register(attr)
                except ImportError as exc:
                    logger.warning("Failed to import agent package %s: %s", agent_pkg.name, exc)

        cls._initialized = True
        logger.info("Initialized registry with %d agents", len(cls._agents))

    @classmethod
    def clear(cls) -> None:
        """Clear all registered agents (for testing)."""
        cls._agents.clear()
        cls._initialized = False

    @classmethod
    def get_agent_count(cls) -> int:
        """Get the number of registered agents."""
        return len(cls._agents)

    @classmethod
    def has_agent(cls, name: str) -> bool:
        """Check if an agent is registered."""
        return name in cls._agents
