"""Script to generate agent registry documentation.

Scans all agent modules and produces a registry index with metadata
about each agent's capabilities, prompts, and dependencies.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path


def scan_agents(agents_dir: str) -> list[dict]:
    """Scan agent directory and collect metadata for each agent."""
    agents = []
    base = Path(agents_dir)

    for pkg in sorted(base.iterdir()):
        if not pkg.is_dir() or pkg.name.startswith("_"):
            continue
        try:
            mod = importlib.import_module(f"app.agents.{pkg.name}")
            for name in dir(mod):
                cls = getattr(mod, name)
                if (
                    isinstance(cls, type)
                    and hasattr(cls, "name")
                    and hasattr(cls, "execute")
                ):
                    agents.append({
                        "name": cls.name,
                        "class": f"{mod.__name__}.{name}",
                        "description": getattr(cls, "description", ""),
                        "prompt_version": getattr(cls, "prompt_version", "v1.0"),
                        "model_tier": getattr(cls, "model_tier", "sonnet"),
                    })
        except ImportError:
            continue

    return agents


def generate_registry(output_file: str) -> None:
    """Generate agent registry JSON file."""
    agents = scan_agents("app/agents")
    registry = {
        "version": "1.0.0",
        "generated_at": "2026-10-04",
        "agent_count": len(agents),
        "agents": agents,
    }

    out = Path(output_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(registry, indent=2))
    print(f"Generated registry with {len(agents)} agents: {output_file}")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "agent_registry.json"
    generate_registry(output)