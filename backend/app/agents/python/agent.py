"""Python execution agent for DataMind-King.

Runs Python code in a sandboxed environment.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.core.sandbox import sandbox
from app.agents.base import Acknowledgement, AgentResult, BaseAgent, TaskBrief

_prompt = """\
You are a Python Code Agent for DataMind-King. Your task is to execute
Python code snippets safely in a sandboxed environment.

RULES:
1. All code runs in a sandbox with no network access.
2. Blocked modules: os, sys, subprocess, socket, etc.
3. Timeout: 5 seconds per execution.
4. Log all executions with request_id.
"""


class PythonAgent(BaseAgent):
    """Python code execution agent with sandbox."""

    name = "python_agent"
    description = "Executes Python code in a sandboxed environment"
    prompt_version = "v1.0"
    model_tier = "haiku"

    async def acknowledge(self, brief: TaskBrief) -> Acknowledgement:
        has_code = "code" in brief.context or "script" in brief.context
        return Acknowledgement(
            task_id=brief.task_id,
            agent_name=self.name,
            accepted=has_code,
            estimated_duration_seconds=10.0 if has_code else 0.0,
            reason="Python code found in context" if has_code else "No Python code in task brief",
        )

    async def execute(self, brief: TaskBrief, ack: Acknowledgement) -> AgentResult:
        code = brief.context.get("code", "") or brief.context.get("script", "")
        if not code:
            return AgentResult(
                task_id=brief.task_id,
                success=False,
                error="No Python code provided",
            )
        result = sandbox.execute(code, timeout_seconds=5.0)
        return AgentResult(
            task_id=brief.task_id,
            success=result.success,
            output={"stdout": result.output, "stderr": result.error},
            confidence=0.9 if result.success else 0.0,
            error=result.error,
            tokens_used=0,
            cost_usd=0.0,
            completed_at=datetime.now(timezone.utc),
        )


from app.agents.base import registry
registry.register(PythonAgent)
