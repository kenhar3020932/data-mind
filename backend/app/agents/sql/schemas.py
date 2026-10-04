"""SQL Agent Schemas for DataMind-King - Ultra God Mode Edition.

Defines structured schemas for SQL query execution with comprehensive
validation, engine-specific options, and detailed result metadata.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class QueryAnalysis(BaseModel):
    """Pre-execution analysis of the SQL query."""
    query_hash: str = Field(default="", description="SHA256 hash of the query")
    complexity_score: float = Field(ge=0.0, le=10.0, default=0.0, description="Query complexity (0-10)")
    tables_accessed: list[str] = Field(default_factory=list)
    columns_accessed: list[str] = Field(default_factory=list)
    has_aggregations: bool = False
    has_joins: bool = False
    has_subqueries: bool = False
    has_ctes: bool = False
    estimated_cost_multiplier: float = Field(ge=1.0, default=1.0)
    
    # Security analysis
    is_read_only: bool = True
    tenant_isolation_verified: bool = False
    injection_risk_detected: bool = False

    @field_validator("query_hash", mode="before")
    @classmethod
    def compute_query_hash(cls, v: str, info: Any) -> str:
        """Auto-compute query hash if not provided."""
        if v:
            return v
        query = info.data.get("query", "")
        if query:
            return hashlib.sha256(query.encode()).hexdigest()[:16]
        return ""


class EngineOptions(BaseModel):
    """Engine-specific execution options."""
    # Common options
    timeout_seconds: float = Field(default=300.0, ge=1.0, le=3600.0)
    max_memory_mb: int = Field(default=1024, ge=64, le=32768)
    
    # DuckDB specific
    duckdb_threads: int = Field(default=4, ge=1, le=32)
    
    # ClickHouse specific
    clickhouse_max_execution_time: int = Field(default=300, ge=1, le=3600)
    clickhouse_max_memory_usage: int = Field(default=10 * 1024 * 1024 * 1024)  # 10GB
    
    # Trino/Spark specific
    distributed_execution: bool = False
    partition_count: int = Field(default=10, ge=1, le=1000)


class SQLQueryInput(BaseModel):
    """Input schema for SQL Query Execution - Ultra God Mode Edition."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    org_id: str = Field(..., min_length=1, max_length=36, description="Tenant ID")
    
    # Query
    query: str = Field(..., min_length=1, max_length=50000, description="SQL query to execute")
    dialect: Literal["duckdb", "postgres", "clickhouse", "trino", "mysql"] = Field(
        default="duckdb",
        description="SQL dialect for parsing"
    )
    
    # Engine Selection
    engine: Literal["duckdb", "clickhouse", "trino", "auto"] = Field(
        default="auto",
        description="Target engine. 'auto' selects based on data size."
    )
    
    # Execution Options
    limit: int = Field(default=1000, ge=1, le=100000, description="Max rows to return")
    offset: int = Field(default=0, ge=0)
    include_execution_plan: bool = Field(default=False, description="Include EXPLAIN output")
    
    # Engine-specific options
    engine_options: EngineOptions = Field(default_factory=EngineOptions)
    
    # Context for AI Decision Making
    data_size_bytes: int = Field(default=0, ge=0, description="Estimated dataset size")
    expected_row_count: int | None = Field(None, ge=0)
    query_purpose: Literal["exploration", "reporting", "dashboard", "export", "validation"] = Field(
        default="exploration"
    )
    
    # Audit
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("query")
    @classmethod
    def validate_query_safety(cls, v: str) -> str:
        """Basic query safety checks."""
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty")
        
        # Check for obvious injection patterns
        dangerous_patterns = ["; DROP", "; DELETE", "; UPDATE", "1=1", "' OR '1'='1"]
        query_upper = v.upper()
        for pattern in dangerous_patterns:
            if pattern in query_upper:
                raise ValueError(f"Potentially dangerous pattern detected: {pattern}")
        
        return v


class ColumnMetadata(BaseModel):
    """Metadata for a single result column."""
    name: str
    dtype: str
    nullable: bool = True
    sample_values: list[Any] = Field(default_factory=list)
    unique_count: int | None = None
    null_count: int | None = None


class ExecutionMetrics(BaseModel):
    """Detailed execution performance metrics."""
    execution_time_ms: float = Field(ge=0.0)
    planning_time_ms: float = Field(ge=0.0, default=0.0)
    data_transfer_time_ms: float = Field(ge=0.0, default=0.0)
    
    # Resource usage
    memory_used_mb: float = Field(ge=0.0, default=0.0)
    cpu_time_ms: float = Field(ge=0.0, default=0.0)
    rows_scanned: int = Field(ge=0, default=0)
    bytes_scanned: int = Field(ge=0, default=0)
    
    # Query plan (if requested)
    execution_plan: str | None = None
    
    # Engine-specific metrics
    engine_metrics: dict[str, Any] = Field(default_factory=dict)


class SQLQueryOutput(BaseModel):
    """Output schema for SQL Query Execution - Ultra God Mode Edition."""
    success: bool
    task_id: str
    
    # Query Info
    query: str
    query_hash: str = ""
    sanitized_query: str | None = None
    
    # Results
    rows: list[dict[str, Any]] = Field(default_factory=list)
    columns: list[ColumnMetadata] = Field(default_factory=list)
    row_count: int = Field(ge=0, default=0)
    total_row_count: int | None = Field(None, ge=0, description="Total rows before LIMIT")
    
    # Execution Details
    engine_used: str
    dialect: str
    execution_metrics: ExecutionMetrics = Field(default_factory=ExecutionMetrics)
    
    # Quality & Validation
    confidence: float = Field(ge=0.0, le=1.0, description="Evidence-based confidence")
    validation_passed: bool = True
    tenant_isolation_verified: bool = False
    
    # Cost & Usage
    estimated_cost_usd: float = Field(ge=0.0, default=0.0)
    tokens_used: int = Field(ge=0, default=0)
    
    # Error Handling
    error: str | None = None
    error_details: dict[str, Any] | None = None
    degraded_mode: bool = False
    retry_count: int = Field(ge=0, default=0)
    
    # Audit
    completed_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("row_count", mode="before")
    @classmethod
    def sync_row_count(cls, v: int, info: Any) -> int:
        """Auto-sync row_count with actual rows length."""
        rows = info.data.get("rows", [])
        return len(rows) if rows else v

    @field_validator("query_hash", mode="before")
    @classmethod
    def compute_hash_if_missing(cls, v: str, info: Any) -> str:
        """Auto-compute query hash if not provided."""
        if v:
            return v
        query = info.data.get("query", "")
        if query:
            return hashlib.sha256(query.encode()).hexdigest()[:16]
        return ""

    @model_validator(mode="after")
    def calculate_confidence_if_missing(self) -> "SQLQueryOutput":
        """Auto-calculate confidence based on execution metrics."""
        if self.confidence == 0.0 and self.success:
            # Simple confidence calculation
            validation_score = 1.0 if self.validation_passed else 0.0
            speed_score = min(1.0, 1000.0 / max(self.execution_metrics.execution_time_ms, 1))
            retry_penalty = max(0.5, 1.0 - (self.retry_count * 0.2))
            
            self.confidence = round(
                (validation_score * 0.5 + speed_score * 0.3 + 0.2) * retry_penalty,
                2
            )
        return self


class BatchQueryInput(BaseModel):
    """Input for executing multiple queries in batch."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    org_id: str = Field(..., min_length=1, max_length=36)
    
    queries: list[SQLQueryInput] = Field(..., min_length=1, max_length=100)
    
    # Batch options
    execute_in_parallel: bool = Field(default=False)
    stop_on_first_error: bool = Field(default=True)
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BatchQueryOutput(BaseModel):
    """Output for batch query execution."""
    success: bool
    task_id: str
    
    results: list[SQLQueryOutput] = Field(default_factory=list)
    
    # Summary
    total_queries: int = Field(ge=0, default=0)
    successful_queries: int = Field(ge=0, default=0)
    failed_queries: int = Field(ge=0, default=0)
    
    # Performance
    total_execution_time_ms: float = Field(ge=0.0, default=0.0)
    total_cost_usd: float = Field(ge=0.0, default=0.0)
    
    # Quality
    overall_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    
    error: str | None = None
    completed_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("total_queries", mode="before")
    @classmethod
    def sync_total_queries(cls, v: int, info: Any) -> int:
        results = info.data.get("results", [])
        return len(results) if results else v

    @field_validator("successful_queries", mode="before")
    @classmethod
    def sync_successful_queries(cls, v: int, info: Any) -> int:
        results = info.data.get("results", [])
        return sum(1 for r in results if r.success) if results else v

    @field_validator("failed_queries", mode="before")
    @classmethod
    def sync_failed_queries(cls, v: int, info: Any) -> int:
        results = info.data.get("results", [])
        return sum(1 for r in results if not r.success) if results else v

    @model_validator(mode="after")
    def calculate_summary_metrics(self) -> "BatchQueryOutput":
        """Auto-calculate summary metrics."""
        if self.results:
            self.total_execution_time_ms = sum(
                r.execution_metrics.execution_time_ms for r in self.results
            )
            self.total_cost_usd = sum(r.estimated_cost_usd for r in self.results)
            
            successful = [r for r in self.results if r.success]
            if successful:
                self.overall_confidence = round(
                    sum(r.confidence for r in successful) / len(successful),
                    2
                )
        return self
