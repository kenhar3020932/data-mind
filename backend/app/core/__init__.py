"""Core security and configuration modules."""
from .settings import settings
from .sql_gate import SQLGateResult, validate_sql

# Alias for backward compatibility
SQLGate = validate_sql

__all__ = ["settings", "SQLGate", "SQLGateResult", "validate_sql"]
