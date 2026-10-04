"""Planning Agent Schemas for DataMind-King - Ultra God Mode Edition.

Defines structured schemas for PlanDAG generation, validation,
and execution with comprehensive metadata and audit fields.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class StepAcceptanceCriteria(BaseModel):
    """Machine-checkable acceptance criteria for a step."""
    criterion_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str = Field(..., min_length=1, max_length=500)
    check_type: Literal["output_exists", "metric_threshold", "schema_valid", "row_count", "custom"]
    threshold_value: float | None = None
    comparison_operator: Literal["gt", "gte", "lt", "lte", "eq", "neq"] | None = None
    is_mandatory: bool = True


class Step(BaseModel):
    """A single step in an execution plan DAG with Ultra God Mode features."""
    step_id: str = Field(default_factory=lambda: f"step_{uuid.uuid4().hex[:8]}")
    description: str = Field(..., min_length=1, max_length=1000)
    agent: str = Field(..., min_length=1, max_length=100, description="Agent name to execute this step")
    
    # Dependencies & Execution
    depends_on: list[str] = Field(default_factory=list, description="List of step_ids this step depends on")
    parallelizable: bool = Field(default=True, description="Can run in parallel with other steps")
    priority: Literal["critical", "high", "medium", "low"] = Field(default="medium")
    
    # Estimates
    estimated_duration_seconds: float = Field(ge=0.0, default=0.0)
    estimated_cost_usd: float = Field(ge=0.0, default=0.0)
    estimated_tokens: int = Field(ge=0, default=0)
    
    # Resilience
    fallback_strategy: str | None = Field(None, max_length=500, description="What to do if this step fails")
    max_retries: int = Field(ge=0, le=5, default=1)
    timeout_seconds: float = Field(ge=0.0, default=300.0)
    
    # Quality
    acceptance_criteria: list[StepAcceptanceCriteria] = Field(default_factory=list)
    expected_outputs: dict[str, Any] = Field(default_factory=dict, description="Expected output schema")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("depends_on")
    @classmethod
    def validate_no_self_dependency(cls, v: list[str], info: Any) -> list[str]:
        """Prevent circular self-dependency."""
        step_id = info.data.get("step_id")
        if step_id and step_id in v:
            raise ValueError(f"Step '{step_id}' cannot depend on itself")
        return v


class PlanRiskAssessment(BaseModel):
    """Risk assessment for the entire plan."""
    overall_risk: Literal["low", "medium", "high", "critical"] = "medium"
    risk_factors: list[str] = Field(default_factory=list)
    mitigation_strategies: list[str] = Field(default_factory=list)
    confidence_in_success: float = Field(ge=0.0, le=1.0, default=0.8)


class PlanDAG(BaseModel):
    """Directed acyclic graph of task steps - Ultra God Mode Edition."""
    plan_id: str = Field(default_factory=lambda: f"plan-{uuid.uuid4()}")
    goal: str = Field(..., min_length=1, max_length=2000, description="High-level goal of this plan")
    description: str = Field(..., min_length=1, max_length=5000)
    
    # Core Structure
    steps: list[Step] = Field(..., min_length=1)
    parallel_groups: list[list[str]] = Field(
        default_factory=list, 
        description="Groups of step_ids that can execute in parallel"
    )
    
    # Estimates (auto-calculated)
    total_duration_seconds: float = Field(ge=0.0, default=0.0)
    adjusted_duration_seconds: float = Field(ge=0.0, default=0.0, description="Duration after parallelism")
    total_cost_usd: float = Field(ge=0.0, default=0.0)
    total_tokens: int = Field(ge=0, default=0)
    parallelism_factor: float = Field(ge=1.0, default=1.0)
    
    # Quality & Validation
    risk_assessment: PlanRiskAssessment | None = None
    assumptions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    
    # Critic Validation
    critic_score: float = Field(ge=0.0, le=1.0, default=0.0)
    critic_approved: bool = False
    critic_feedback: str | None = None
    
    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0")
    org_id: str = Field(..., min_length=1, max_length=36)
    task_id: str | None = None

    @model_validator(mode="after")
    def calculate_totals(self) -> "PlanDAG":
        """Auto-calculate totals from steps."""
        if not self.steps:
            return self
        
        # Calculate raw totals
        self.total_duration_seconds = sum(s.estimated_duration_seconds for s in self.steps)
        self.total_cost_usd = sum(s.estimated_cost_usd for s in self.steps)
        self.total_tokens = sum(s.estimated_tokens for s in self.steps)
        
        # Calculate parallelism factor from parallel_groups
        if self.parallel_groups:
            max_parallel = max(len(group) for group in self.parallel_groups)
            self.parallelism_factor = float(max_parallel)
            self.adjusted_duration_seconds = self.total_duration_seconds / self.parallelism_factor
        else:
            self.adjusted_duration_seconds = self.total_duration_seconds
        
        return self

    @field_validator("steps")
    @classmethod
    def validate_unique_step_ids(cls, v: list[Step]) -> list[Step]:
        """Ensure all step_ids are unique."""
        step_ids = [step.step_id for step in v]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("Duplicate step_ids found in plan")
        return v


class PlanningInput(BaseModel):
    """Input schema for Planning Agent - Ultra God Mode Edition."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    org_id: str = Field(..., min_length=1, max_length=36, description="Tenant ID")
    
    # Task Description
    task_description: str = Field(..., min_length=1, max_length=5000)
    goal: str | None = Field(None, max_length=1000, description="High-level goal")
    
    # Context for AI Decision Making
    data_size_mb: float = Field(default=0.0, ge=0.0, description="Estimated data size")
    complexity: Literal["low", "medium", "high", "very_high"] = Field(default="medium")
    user_role: Literal["analyst", "data_scientist", "business_user", "admin"] = Field(default="analyst")
    available_agents: list[str] = Field(
        default_factory=lambda: [
            "sql_agent", "profiling_agent", "dashboard_agent",
            "data_quality_agent", "planning_agent", "verification_agent"
        ]
    )
    
    # Constraints
    constraints: dict[str, Any] = Field(default_factory=dict)
    budget_limit_usd: float | None = Field(None, ge=0.0)
    time_limit_seconds: float | None = Field(None, ge=0.0)
    required_agents: list[str] | None = Field(None, description="Agents that must be used")
    
    # Preferences
    prefer_parallelism: bool = Field(default=True)
    require_fallbacks: bool = Field(default=True)
    max_steps: int = Field(default=50, ge=1, le=200)
    
    # Audit
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PlanningOutput(BaseModel):
    """Output schema for Planning Agent - Ultra God Mode Edition."""
    success: bool
    task_id: str
    
    # Plan Data
    plan: PlanDAG | None = None
    
    # Summary Statistics
    step_count: int = Field(ge=0, default=0)
    critical_steps: int = Field(ge=0, default=0)
    parallel_groups_count: int = Field(ge=0, default=0)
    
    # Estimates
    estimated_cost_usd: float = Field(ge=0.0, default=0.0)
    estimated_duration_seconds: float = Field(ge=0.0, default=0.0)
    estimated_tokens: int = Field(ge=0, default=0)
    
    # Quality Metrics
    confidence: float = Field(ge=0.0, le=1.0, description="Evidence-based confidence score")
    critic_score: float = Field(ge=0.0, le=1.0, default=0.0)
    risk_level: Literal["low", "medium", "high", "critical"] | None = None
    
    # Performance
    latency_ms: float = Field(ge=0.0, default=0.0)
    attempts_used: int = Field(ge=1, default=1)
    
    # Cost & Usage
    tokens_used: int = Field(ge=0, default=0)
    cost_usd: float = Field(ge=0.0, default=0.0)
    
    # Error Handling
    error: str | None = None
    degraded_mode: bool = False
    fallback_plan: PlanDAG | None = None
    
    # Audit
    completed_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("step_count", mode="before")
    @classmethod
    def sync_step_count(cls, v: int, info: Any) -> int:
        """Auto-sync step_count with plan.steps length."""
        plan = info.data.get("plan")
        if plan and plan.steps:
            return len(plan.steps)
        return v

    @field_validator("critical_steps", mode="before")
    @classmethod
    def sync_critical_steps(cls, v: int, info: Any) -> int:
        """Auto-count critical priority steps."""
        plan = info.data.get("plan")
        if plan and plan.steps:
            return sum(1 for s in plan.steps if s.priority == "critical")
        return v

    @field_validator("parallel_groups_count", mode="before")
    @classmethod
    def sync_parallel_groups(cls, v: int, info: Any) -> int:
        """Auto-sync parallel_groups_count."""
        plan = info.data.get("plan")
        if plan and plan.parallel_groups:
            return len(plan.parallel_groups)
        return v
