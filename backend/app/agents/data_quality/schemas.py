"""Data Quality Agent Schemas for DataMind-King - Ultra God Mode Edition."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class ColumnProfile(BaseModel):
    """Profile statistics for a single column."""
    column_name: str
    dtype: str
    null_count: int = Field(ge=0)
    null_percentage: float = Field(ge=0.0, le=100.0)
    unique_count: int = Field(ge=0)
    unique_percentage: float = Field(ge=0.0, le=100.0)
    
    # Numeric stats (optional)
    min_value: float | None = None
    max_value: float | None = None
    mean_value: float | None = None
    median_value: float | None = None
    std_dev: float | None = None
    
    # Categorical stats (optional)
    top_values: list[dict[str, Any]] = Field(default_factory=list)
    
    # Quality flags
    is_potential_pii: bool = False
    is_potential_key: bool = False
    outlier_count: int = Field(ge=0, default=0)
    
    # Detected issues
    issues: list[str] = Field(default_factory=list)


class QualityMetrics(BaseModel):
    """Comprehensive data quality metrics."""
    completeness: float = Field(ge=0.0, le=1.0, description="Ratio of non-null values")
    uniqueness: float = Field(ge=0.0, le=1.0, description="Ratio of unique rows")
    consistency: float = Field(ge=0.0, le=1.0, description="Schema and format consistency")
    validity: float = Field(ge=0.0, le=1.0, description="Values within expected ranges")
    
    # Advanced metrics
    accuracy: float = Field(ge=0.0, le=1.0, default=0.0, description="Match against known truths")
    timeliness: float = Field(ge=0.0, le=1.0, default=0.0, description="Data freshness score")
    integrity: float = Field(ge=0.0, le=1.0, default=0.0, description="Referential integrity score")
    
    # Composite score
    overall_quality: float = Field(ge=0.0, le=1.0, default=0.0)

    @model_validator(mode="after")
    def calculate_overall_quality(self) -> "QualityMetrics":
        """Auto-calculate overall quality as weighted average."""
        if self.overall_quality == 0.0:
            self.overall_quality = round(
                (self.completeness * 0.25) +
                (self.uniqueness * 0.15) +
                (self.consistency * 0.20) +
                (self.validity * 0.20) +
                (self.accuracy * 0.10) +
                (self.timeliness * 0.05) +
                (self.integrity * 0.05),
                4
            )
        return self


class DataIssue(BaseModel):
    """Represents a single data quality issue found during profiling."""
    issue_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    severity: Literal["critical", "high", "medium", "low", "info"]
    category: Literal[
        "missing_values", "duplicates", "outliers", "type_mismatch",
        "format_inconsistency", "range_violation", "referential_integrity",
        "pii_detected", "encoding_issue", "unit_inconsistency"
    ]
    column_name: str | None = None
    description: str
    affected_rows: int = Field(ge=0)
    affected_percentage: float = Field(ge=0.0, le=100.0)
    suggested_fix: str | None = None
    auto_fixable: bool = False


class ProfilingInput(BaseModel):
    """Input schema for Data Profiling Task."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dataset_id: str = Field(..., min_length=1, description="Dataset identifier or path")
    org_id: str = Field(..., min_length=1, max_length=36, description="Tenant ID")
    
    # Profiling Configuration
    profile_level: Literal["quick", "standard", "full"] = Field(
        default="standard",
        description="Depth of profiling"
    )
    tool_preference: Literal["great_expectations", "pandas_profiling", "polars", "auto"] = Field(
        default="auto",
        description="Preferred profiling tool"
    )
    
    # Context for AI Decision Making
    row_count: int = Field(default=0, ge=0, description="Estimated row count")
    column_count: int = Field(default=0, ge=0, description="Estimated column count")
    has_complex_patterns: bool = Field(default=False)
    target_columns: list[str] | None = Field(
        default=None, 
        description="Specific columns to profile (None = all)"
    )
    
    # Audit
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("dataset_id")
    @classmethod
    def validate_dataset_id(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("dataset_id cannot be empty or whitespace")
        return v


class ProfilingOutput(BaseModel):
    """Output schema for Data Profiling Result."""
    success: bool
    task_id: str
    
    # Result Data
    dataset_id: str
    tool_used: str | None = None
    profile_level: str | None = None
    
    # Quality Metrics
    metrics: QualityMetrics | None = None
    
    # Detailed Results
    column_profiles: list[ColumnProfile] = Field(default_factory=list)
    issues_found: list[DataIssue] = Field(default_factory=list)
    
    # Summary Stats
    rows_processed: int = Field(ge=0, default=0)
    columns_profiled: int = Field(ge=0, default=0)
    total_issues: int = Field(ge=0, default=0)
    critical_issues: int = Field(ge=0, default=0)
    
    # Performance & Quality
    confidence: float = Field(ge=0.0, le=1.0, description="Evidence-based confidence")
    latency_ms: float = Field(ge=0.0, default=0.0)
    
    # Cost & Usage
    tokens_used: int = 0
    cost_usd: float = 0.0
    
    # Error Handling
    error: str | None = None
    degraded_mode: bool = False
    
    # Audit
    completed_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("total_issues", mode="before")
    @classmethod
    def sync_total_issues(cls, v: int, info: Any) -> int:
        """Auto-sync total_issues with issues_found length."""
        issues = info.data.get("issues_found", [])
        return len(issues) if issues else v

    @field_validator("critical_issues", mode="before")
    @classmethod
    def sync_critical_issues(cls, v: int, info: Any) -> int:
        """Auto-count critical issues."""
        issues = info.data.get("issues_found", [])
        if issues:
            return sum(1 for i in issues if i.severity == "critical")
        return v
