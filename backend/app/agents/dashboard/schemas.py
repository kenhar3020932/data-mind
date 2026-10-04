"""Dashboard Agent Schemas for DataMind-King - Ultra God Mode Edition."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class WidgetDataMapping(BaseModel):
    """Maps dataset columns to chart axes/fields."""
    x_axis: str | None = None
    y_axis: str | None = None
    group_by: str | None = None
    filter_column: str | None = None
    filter_value: Any | None = None


class WidgetConfig(BaseModel):
    """Configuration for a single dashboard widget."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal["chart", "table", "kpi", "text"] = Field(..., description="Widget type")
    title: str = Field(..., min_length=1, max_length=100, description="Widget title")
    
    # Visualization Specifics
    chart_type: Literal["bar", "line", "pie", "scatter", "area", "heatmap"] | None = None
    data_mapping: WidgetDataMapping | None = None
    
    # Layout & Styling
    position: dict[str, int] = Field(
        default_factory=dict, 
        description="Grid position {x, y, w, h}"
    )
    style: dict[str, Any] = Field(default_factory=dict, description="Custom CSS/Theme overrides")

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: dict) -> dict:
        if not v:
            return {"x": 0, "y": 0, "w": 1, "h": 1}
        required_keys = {"x", "y", "w", "h"}
        if not required_keys.issubset(v.keys()):
            raise ValueError(f"Position must contain keys: {required_keys}")
        return v


class DashboardInput(BaseModel):
    """Input schema for Dashboard Creation Task."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    org_id: str = Field(..., min_length=1, max_length=36, description="Tenant ID")
    
    # Content
    name: str = Field(..., min_length=1, max_length=200, description="Dashboard name")
    description: str | None = Field(None, max_length=500)
    widgets: list[WidgetConfig] = Field(default_factory=list, min_items=1)
    
    # Context for AI Decision Making
    goal: str | None = Field(None, description="Natural language goal for the dashboard")
    data_schema: dict[str, Any] | None = Field(None, description="Dataset schema for context")
    tool_preference: Literal["vega_lite", "superset", "metabase", "auto"] = Field(
        "auto", 
        description="Preferred BI tool. 'auto' lets the agent decide."
    )
    
    # Audit
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DashboardOutput(BaseModel):
    """Output schema for Dashboard Creation Result."""
    success: bool
    task_id: str
    
    # Result Data
    dashboard_id: str | None = None
    url: str | None = None
    tool_used: str | None = None
    widget_count: int = 0
    
    # Performance & Quality Metrics
    confidence: float = Field(ge=0.0, le=1.0, description="Evidence-based confidence score")
    latency_ms: float = Field(ge=0.0, description="Time taken to create dashboard")
    
    # Cost & Usage
    tokens_used: int = 0
    cost_usd: float = 0.0
    
    # Error Handling
    error: str | None = None
    degraded_mode: bool = False
    
    # Audit
    completed_at: datetime = Field(default_factory=datetime.utcnow)
