"""Visualization Agent Schemas for DataMind-King - Ultra God Mode Edition.

Defines structured schemas for intelligent chart generation with
Vega-Lite compliance, accessibility standards, and design system integration.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class DesignSystemConfig(BaseModel):
    """Configuration for applying the Neural Data Glass design system."""
    apply_tokens: bool = Field(default=True, description="Apply standard colors and fonts")
    colorblind_safe: bool = Field(default=True, description="Use colorblind-friendly palette")
    responsive: bool = Field(default=True, description="Enable container-based sizing")
    theme: Literal["light", "dark", "auto"] = Field(default="auto")
    
    # Overrides
    primary_color: str | None = None
    font_family: str | None = None
    border_radius: int | None = None


class AccessibilityConfig(BaseModel):
    """Accessibility settings for the chart."""
    aria_label: str | None = Field(None, max_length=500)
    description: str | None = Field(None, max_length=1000)
    high_contrast: bool = Field(default=False)
    screen_reader_optimized: bool = Field(default=True)


class ChartEncoding(BaseModel):
    """Vega-Lite encoding configuration."""
    x_field: str | None = Field(None, description="Field for X axis")
    y_field: str | None = Field(None, description="Field for Y axis")
    color_field: str | None = Field(None, description="Field for color grouping")
    size_field: str | None = Field(None, description="Field for point size")
    tooltip_fields: list[str] = Field(default_factory=list, description="Fields to show in tooltip")
    
    # Aggregations
    x_aggregate: Literal["sum", "avg", "count", "min", "max", None] = None
    y_aggregate: Literal["sum", "avg", "count", "min", "max", None] = None


class ChartSpec(BaseModel):
    """Complete Vega-Lite specification wrapper."""
    vega_lite_schema: str = Field(
        default="https://vega.github.io/schema/vega-lite/v5.json",
        pattern=r"^https://vega\.github\.io/schema/vega-lite/v\d+\.json$"
    )
    
    # Core Config
    chart_type: Literal["line", "bar", "pie", "scatter", "area", "heatmap", "histogram", "table"]
    title: str = Field(default="", max_length=200)
    description: str = Field(default="", max_length=1000)
    
    # Dimensions
    width: Literal["container", "auto"] | int = Field(default="container")
    height: int = Field(default=400, ge=100, le=2000)
    
    # Data & Encoding
    data_values: list[dict[str, Any]] = Field(default_factory=list)
    encoding: ChartEncoding = Field(default_factory=ChartEncoding)
    
    # Styling
    design_config: DesignSystemConfig = Field(default_factory=DesignSystemConfig)
    accessibility: AccessibilityConfig = Field(default_factory=AccessibilityConfig)
    
    # Raw Spec (for direct rendering if needed)
    raw_spec: dict[str, Any] = Field(default_factory=dict)

    @field_validator("data_values")
    @classmethod
    def validate_data_not_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("Chart data cannot be empty")
        return v


class VisualizationInput(BaseModel):
    """Input schema for Visualization Agent - Ultra God Mode Edition."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    org_id: str = Field(..., min_length=1, max_length=36, description="Tenant ID")
    
    # Data
    data: list[dict[str, Any]] = Field(..., min_length=1, description="Dataset to visualize")
    
    # Intent
    goal: str | None = Field(None, max_length=1000, description="Natural language goal for the chart")
    chart_type_preference: Literal["auto", "line", "bar", "pie", "scatter", "area", "heatmap", "histogram"] = Field(
        default="auto",
        description="Preferred chart type. 'auto' lets the agent decide."
    )
    
    # Configuration
    title: str | None = Field(None, max_length=200)
    design_config: DesignSystemConfig = Field(default_factory=DesignSystemConfig)
    accessibility: AccessibilityConfig = Field(default_factory=AccessibilityConfig)
    
    # Constraints
    max_data_points: int = Field(default=10000, ge=1, le=100000, description="Limit for performance")
    
    # Audit
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("data")
    @classmethod
    def validate_data_structure(cls, v: list) -> list:
        if not v:
            raise ValueError("Data list cannot be empty")
        if not isinstance(v[0], dict):
            raise ValueError("Data must be a list of dictionaries")
        return v


class VisualizationOutput(BaseModel):
    """Output schema for Visualization Agent - Ultra God Mode Edition."""
    success: bool
    task_id: str
    
    # Result
    spec: ChartSpec | None = None
    
    # Metadata
    chart_type_selected: str = ""
    data_points_processed: int = Field(ge=0, default=0)
    columns_used: list[str] = Field(default_factory=list)
    
    # Quality & Performance
    confidence: float = Field(ge=0.0, le=1.0, description="Evidence-based confidence")
    generation_time_ms: float = Field(ge=0.0, default=0.0)
    
    # Accessibility & Compliance
    accessibility_compliant: bool = False
    design_system_applied: bool = False
    
    # Cost & Usage
    tokens_used: int = Field(ge=0, default=0)
    cost_usd: float = Field(ge=0.0, default=0.0)
    
    # Error Handling
    error: str | None = None
    error_details: dict[str, Any] | None = None
    
    # Audit
    completed_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("data_points_processed", mode="before")
    @classmethod
    def sync_data_points(cls, v: int, info: Any) -> int:
        spec = info.data.get("spec")
        if spec and spec.data_values:
            return len(spec.data_values)
        return v

    @field_validator("columns_used", mode="before")
    @classmethod
    def sync_columns_used(cls, v: list, info: Any) -> list:
        spec = info.data.get("spec")
        if spec and spec.data_values:
            return list(spec.data_values[0].keys())
        return v

    @model_validator(mode="after")
    def check_compliance(self) -> "VisualizationOutput":
        if self.spec:
            self.accessibility_compliant = self.spec.accessibility.screen_reader_optimized
            self.design_system_applied = self.spec.design_config.apply_tokens
        return self
