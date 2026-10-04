"""Python Agent schemas for DataMind-King."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PythonCodeInput(BaseModel):
    """Input for Python code execution."""
    code: str = Field(..., min_length=1, max_length=5000)
    timeout_seconds: float = Field(default=5.0, gt=0.0)
    org_id: str = Field(..., min_length=1, max_length=36)
    variables: dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    """Result of Python code execution."""
    success: bool
    output: str = ""
    error: str | None = None
    execution_time_ms: float = 0.0
    variables_after: dict[str, Any] = Field(default_factory=dict)


class PythonOutput(BaseModel):
    """Output schema for Python agent."""
    success: bool
    result: ExecutionResult | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    error: str | None = None