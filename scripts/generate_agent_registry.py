#!/usr/bin/env python3
"""Generate agent registry documentation and initialization code.

Scans all agent modules and generates:
- Registry index with metadata
- __init__.py exports
- Documentation stubs
"""
from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path
from typing import Any


AGENT_DIRS = [
    Path("backend/app/agents/sql"),
    Path("backend/app/agents/dashboard"),
    Path("backend/app/agents/data_quality"),
    Path("backend/app/agents/planning"),
    Path("backend/app/agents/viz"),
    Path("backend/app/agents/python"),
    Path("backend/app/agents/security"),
]


def scan_agents() -> list[dict[str, Any]]:
    """Scan agent directories and collect metadata."""
    agents = []

    for agent_dir in AGENT_DIRS:
        agent_path = Path(__file__).parent.parent / agent_dir
        if not agent_path.exists():
            continue

        agent_name = agent_path.name
        agent_file = agent_path / "agent.py"

        if not agent_file.exists():
            continue

        # Import the agent module
        module_path = f"app.agents.{agent_name}.agent"
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
            module = importlib.import_module(module_path)

            # Find agent class
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name.endswith("Agent") and hasattr(obj, "name"):
                    agents.append({
                        "name": obj.name,
                        "class": name,
                        "module": module_path,
                        "description": obj.description,
                        "prompt_version": getattr(obj, "prompt_version", "v1.0"),
                        "model_tier": getattr(obj, "model_tier", "sonnet"),
                    })
        except ImportError as exc:
            print(f"Warning: Could not import {module_path}: {exc}")

    return agents


def generate_registry_init(agents: list[dict[str, Any]]) -> str:
    """Generate __init__.py content for agent registry."""
    lines = [
        '"""Agent Registry - Auto-generated. DO NOT EDIT MANUALLY."""',
        'from __future__ import annotations',
        "",
        "from .base import registry",
        "",
        "",
        "# Register all agents",
    ]

    for agent in agents:
        lines.append(f"from app.agents.{agent['name']}.agent import {agent['class']}")
        lines.append(f"registry.register({agent['class']})")

    lines.extend(["", "", "__all__ = ['registry']", ""])
    return "\n".join(lines)


def generate_documentation(agents: list[dict[str, Any]]) -> str:
    """Generate markdown documentation for all agents."""
    lines = [
        "# DataMind-King Agent Registry",
        "",
        f"**Generated:** {agents.__class__.__name__} agents registered",
        "",
        "| Agent | Description | Model Tier | Version |",
        "|-------|-------------|------------|---------|",
    ]

    for agent in sorted(agents, key=lambda a: a["name"]):
        lines.append(
            f"| {agent['name']} | {agent['description']} | {agent['model_tier']} | {agent['prompt_version']} |"
        )

    lines.extend([
        "",
        "## Usage",
        "",
        "```python",
        "from app.agents.base import registry",
        "",
        "# Get agent instance",
        "agent = registry.get_instance('sql_agent')",
        "",
        "# List all agents",
        "all_agents = registry.list_agents()",
        "```",
        "",
    ])

    return "\n".join(lines)


def main() -> None:
    """Generate registry files."""
    project_root = Path(__file__).parent.parent

    # Scan agents
    print("Scanning agents...")
    agents = scan_agents()

    if not agents:
        print("No agents found!")
        return

    print(f"Found {len(agents)} agents:")
    for agent in agents:
        print(f"  - {agent['name']}: {agent['description']}")

    # Generate __init__.py
    init_content = generate_registry_init(agents)
    registry_init = project_root / "backend" / "app" / "agents" / "__init__.py"
    registry_init.write_text(init_content)
    print(f"\n✓ Updated {registry_init}")

    # Generate documentation
    doc_content = generate_documentation(agents)
    docs_file = project_root / "docs" / "AGENT_REGISTRY.md"
    docs_file.parent.mkdir(parents=True, exist_ok=True)
    docs_file.write_text(doc_content)
    print(f"✓ Generated {docs_file}")

    print("\nRegistry generation complete!")


if __name__ == "__main__":
    main()
