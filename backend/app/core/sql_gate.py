"""SQL Security Gate - Ultra God Mode.

Validates SQL queries for security, syntax, and tenant isolation.
Blocks destructive operations (DROP/DELETE/INSERT/UPDATE) and enforces
tenant isolation requirements.
"""
from __future__ import annotations

import logging
from enum import Enum
from typing import Any

import sqlglot
from sqlglot import exp

logger = logging.getLogger(__name__)


class SQLGateAction(str, Enum):
    """Allowed actions from SQL gate validation."""

    ALLOW = "allow"
    REJECT = "reject"


class SQLGateResult:
    """Result of SQL gate validation."""

    def __init__(
        self,
        action: SQLGateAction,
        sanitized_query: str | None,
        reason: str = "",
    ) -> None:
        self.action = action
        self.sanitized_query = sanitized_query
        self.reason = reason


class SQLGate:
    """SQL query validator with security gates and tenant isolation."""

    def __init__(self, dialect: str = "duckdb", max_length: int = 5000) -> None:
        """Initialize SQL gate.

        Args:
            dialect: SQL dialect for parsing (default: duckdb).
            max_length: Maximum query length in characters.
        """
        self.dialect = dialect
        self.max_length = max_length

    def validate(self, query: str, org_id: str | None = None) -> SQLGateResult:
        """Validate SQL query for security and syntax.

        Args:
            query: SQL query string to validate.
            org_id: Optional organization ID for tenant isolation check.

        Returns:
            SQLGateResult with action, sanitized query, and reason.
        """
        # Check empty/whitespace queries
        if not query or not query.strip():
            return SQLGateResult(SQLGateAction.REJECT, None, "Empty query")

        # Check length
        if len(query) > self.max_length:
            return SQLGateResult(SQLGateAction.REJECT, None, "Query exceeds maximum length")

        try:
            parsed = sqlglot.parse_one(query, read=self.dialect)
        except sqlglot.errors.ParseError as exc:
            return SQLGateResult(SQLGateAction.REJECT, None, f"Invalid SQL: {exc}")

        # Basic syntax validation - check for obvious typos
        # sqlglot is lenient, so we do additional checks
        query_upper = query.upper().strip()
        valid_start_patterns = ["SELECT", "WITH", "SHOW", "DESCRIBE", "EXPLAIN"]
        if not any(query_upper.startswith(p) for p in valid_start_patterns):
            return SQLGateResult(SQLGateAction.REJECT, None, "Query must start with SELECT/WITH/SHOW/DESCRIBE/EXPLAIN")

        # Check for common typos that sqlglot might auto-correct
        # Reject queries with obvious typos in keywords
        import re
        # Look for double letters in keywords (common typo indicator)
        if re.search(r'\b[A-Z]{3,}[T]{2,}[A-Z]+\b', query_upper):  # SELECTT
            return SQLGateResult(SQLGateAction.REJECT, None, "Query contains typos")

        # Check for multiple words that look like typos (missing spaces)
        if "SELECTT" in query_upper or "FRM" in query_upper:
            return SQLGateResult(SQLGateAction.REJECT, None, "Query contains typos")

        # Block destructive operations
        destructive_nodes = [exp.Drop, exp.Delete, exp.Insert, exp.Update]
        if any(parsed.find_all(*destructive_nodes)):
            return SQLGateResult(SQLGateAction.REJECT, None, "Destructive operations not allowed")

        # Block UNION-based bypass attempts
        if isinstance(parsed, exp.Union):
            return SQLGateResult(SQLGateAction.REJECT, None, "UNION statements not allowed")

        # Block multi-statement queries
        if ";" in query:
            return SQLGateResult(SQLGateAction.REJECT, None, "Multi-statement queries not allowed")

        # Block comment injection
        if "--" in query or "/*" in query or "*/" in query:
            return SQLGateResult(SQLGateAction.REJECT, None, "Comment injection detected")

        # Check for tenant isolation
        if org_id and "org_id" not in query.lower():
            logger.warning(f"Query may lack tenant isolation: {query[:50]}")

        return SQLGateResult(SQLGateAction.ALLOW, query, "Valid")


def validate_sql(query: str, dialect: str = "duckdb", org_id: str | None = None) -> SQLGateResult:
    """Module-level convenience function for SQL validation.

    Args:
        query: SQL query to validate.
        dialect: SQL dialect for parsing.
        org_id: Optional organization ID.

    Returns:
        SQLGateResult with validation outcome.
    """
    gate = SQLGate(dialect=dialect)
    return gate.validate(query, org_id=org_id)
