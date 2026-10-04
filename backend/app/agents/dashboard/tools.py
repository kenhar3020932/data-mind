"""SQL Agent tools for DataMind-King."""
from __future__ import annotations
from typing import Any

def validate_sql(query: str, dialect: str = "duckdb") -> dict[str, Any]:
    """Validate SQL query using sqlglot."""
    from app.core.sql_gate import validate_sql as gate_validate
    result = gate_validate(query, dialect=dialect)
    return {
        "valid": result.action == "allow",
        "sanitized_query": result.sanitized_query,
        "reason": result.reason,
    }

def estimate_query_cost(query: str, size_bytes: int) -> dict[str, Any]:
    """Estimate execution cost based on query and data size."""
    import re
    has_join = bool(re.search(r"JOIN", query.upper()))
    has_aggregation = bool(re.search(r"(GROUP BY|COUNT|SUM|AVG)", query.upper()))
    
    base_cost = size_bytes / (1024 * 1024) * 0.0001
    join_penalty = 1.5 if has_join else 1.0
    aggregation_penalty = 1.3 if has_aggregation else 1.0
    
    return {
        "estimated_memory_mb": int(size_bytes / (1024 * 1024) * 0.5),
        "estimated_duration_ms": int(size_bytes / (1024 * 1024) * 10),
        "cost_multiplier": round(join_penalty * aggregation_penalty, 2),
    }
