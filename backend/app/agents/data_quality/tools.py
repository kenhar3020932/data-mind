"""SQL Agent Tools for DataMind-King - Ultra God Mode Edition."""

from __future__ import annotations

import logging
from typing import Any

import sqlglot
from sqlglot import exp

from app.core.sql_gate import validate_sql as gate_validate

logger = logging.getLogger(__name__)


def validate_and_sanitize_sql(query: str, dialect: str = "duckdb", org_id: str | None = None) -> dict[str, Any]:
    """
    Validate SQL query using sqlglot and enforce security policies.
    
    Args:
        query: The SQL query to validate.
        dialect: The SQL dialect (e.g., duckdb, postgres, clickhouse).
        org_id: Optional tenant ID for isolation checks.
        
    Returns:
        Dict with validation result, sanitized query, and any errors.
    """
    try:
        # 1. Parse the query to check syntax
        parsed = sqlglot.parse_one(query, read=dialect)
        
        # 2. Enforce Security Gate (Injection prevention, destructive ops)
        gate_result = gate_validate(query, dialect=dialect, org_id=org_id)
        
        if not gate_result.is_allowed:
            return {
                "valid": False,
                "sanitized_query": None,
                "error": f"Security Gate Blocked: {gate_result.reason}",
                "suggestion": "Remove destructive operations or ensure proper tenant scoping."
            }
            
        # 3. Return success with sanitized query and metadata
        return {
            "valid": True,
            "sanitized_query": gate_result.sanitized_query or query,
            "tables_accessed": [table.name for table in parsed.find_all(exp.Table)],
            "columns_accessed": [col.name for col in parsed.find_all(exp.Column)],
            "query_type": parsed.__class__.__name__,
        }
        
    except Exception as e:
        logger.warning(f"SQL Validation failed: {e}")
        return {
            "valid": False,
            "sanitized_query": None,
            "error": f"Syntax Error: {str(e)}",
            "suggestion": "Check your SQL syntax and try again."
        }


def estimate_query_complexity_and_cost(query: str, size_bytes: int = 0) -> dict[str, Any]:
    """
    Estimate query complexity and resource usage using AST analysis.
    
    Args:
        query: The SQL query to analyze.
        size_bytes: Estimated size of the data being queried.
        
    Returns:
        Dict with complexity score, estimated memory, duration, and cost multiplier.
    """
    try:
        parsed = sqlglot.parse_one(query)
        
        # 1. Analyze AST for complexity markers
        joins = list(parsed.find_all(exp.Join))
        aggregations = list(parsed.find_all(exp.Group)) + list(parsed.find_all(exp.Func))
        subqueries = list(parsed.find_all(exp.Subquery))
        ctes = list(parsed.find_all(exp.CTE))
        
        # 2. Calculate Complexity Score (0-10)
        complexity_score = 1.0  # Base
        complexity_score += len(joins) * 1.5
        complexity_score += len(subqueries) * 2.0
        complexity_score += len(ctes) * 1.2
        complexity_score += min(len(aggregations) * 0.5, 3.0)
        
        # 3. Estimate Resources
        size_mb = size_bytes / (1024 * 1024) if size_bytes > 0 else 10  # Default 10MB if unknown
        
        # Memory: Joins and Aggregations require more memory
        est_memory_mb = size_mb * (1 + (len(joins) * 0.5) + (len(aggregations) * 0.2))
        
        # Duration: Rough estimate based on complexity and size
        base_duration_ms = (size_mb * 10) if size_mb < 100 else (size_mb * 2)
        est_duration_ms = base_duration_ms * (complexity_score / 2.0)
        
        # Cost Multiplier: For billing/resource tracking
        cost_multiplier = round(complexity_score / 2.0, 2)
        
        return {
            "valid": True,
            "complexity_score": round(min(complexity_score, 10.0), 2),
            "estimated_memory_mb": round(est_memory_mb, 2),
            "estimated_duration_ms": round(est_duration_ms, 2),
            "cost_multiplier": cost_multiplier,
            "optimization_tips": _get_optimization_tips(parsed, joins, subqueries)
        }
        
    except Exception as e:
        logger.warning(f"Cost Estimation failed: {e}")
        return {
            "valid": False,
            "error": f"Could not estimate cost: {str(e)}",
            "complexity_score": 0.0,
            "estimated_memory_mb": 0.0,
            "estimated_duration_ms": 0.0,
            "cost_multiplier": 1.0,
            "optimization_tips": []
        }


def _get_optimization_tips(parsed: exp.Expression, joins: list, subqueries: list) -> list[str]:
    """Generate simple optimization tips based on AST."""
    tips = []
    if len(joins) > 3:
        tips.append("Consider breaking down complex joins into CTEs for better readability and performance.")
    if len(subqueries) > 2:
        tips.append("Multiple subqueries detected. Try using JOINs or CTEs instead.")
    if not parsed.find(exp.Limit):
        tips.append("No LIMIT clause found. Consider adding one to prevent large data transfers.")
    return tips
