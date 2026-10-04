"""Unit tests for SQL Gate - Section 14.1 targeting 95% coverage."""

from __future__ import annotations

import pytest

from app.core.sql_gate import SQLGate, SQLGateAction, validate_sql


class TestSQLGate:
    """Test suite for SQLGate validation."""

    def setup_method(self) -> None:
        self.gate = SQLGate(dialect="duckdb", max_length=5000)

    def test_select_allowed(self) -> None:
        result = self.gate.validate("SELECT * FROM users")
        assert result.action == SQLGateAction.ALLOW
        assert "SELECT" in result.sanitized_query

    def test_drop_blocked(self) -> None:
        result = self.gate.validate("DROP TABLE users")
        assert result.action == SQLGateAction.REJECT

    def test_delete_blocked(self) -> None:
        result = self.gate.validate("DELETE FROM users WHERE id=1")
        assert result.action == SQLGateAction.REJECT

    def test_insert_blocked(self) -> None:
        result = self.gate.validate("INSERT INTO users VALUES (1)")
        assert result.action == SQLGateAction.REJECT

    def test_update_blocked(self) -> None:
        result = self.gate.validate("UPDATE users SET name='x'")
        assert result.action == SQLGateAction.REJECT

    def test_union_blocks_bypass(self) -> None:
        result = self.gate.validate(
            "SELECT * FROM users WHERE org_id=1 UNION SELECT * FROM users WHERE org_id=2"
        )
        assert result.action == SQLGateAction.REJECT

    def test_comment_injection_blocked(self) -> None:
        result = self.gate.validate("SELECT -- drop table")
        assert result.action == SQLGateAction.REJECT

    def test_multistatement_blocked(self) -> None:
        result = self.gate.validate("SELECT * FROM users; DROP TABLE users")
        assert result.action == SQLGateAction.REJECT

    def test_empty_query_rejected(self) -> None:
        result = self.gate.validate("")
        assert result.action == SQLGateAction.REJECT

    def test_whitespace_only_rejected(self) -> None:
        result = self.gate.validate("   ")
        assert result.action == SQLGateAction.REJECT

    def test_oversized_query_rejected(self) -> None:
        long_query = "SELECT " + "x" * 5001
        result = self.gate.validate(long_query)
        assert result.action == SQLGateAction.REJECT

    def test_invalid_sql_rejected(self) -> None:
        result = self.gate.validate("SELECTT * FRM users")
        assert result.action == SQLGateAction.REJECT

    def test_with_clause_allowed(self) -> None:
        result = self.gate.validate("WITH cte AS (SELECT 1) SELECT * FROM cte")
        assert result.action == SQLGateAction.ALLOW

    def test_subquery_allowed(self) -> None:
        result = self.gate.validate("SELECT * FROM users WHERE id IN (SELECT id FROM admins)")
        assert result.action == SQLGateAction.ALLOW

    def test_join_allowed(self) -> None:
        result = self.gate.validate(
            "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id"
        )
        assert result.action == SQLGateAction.ALLOW

    def test_aggregation_allowed(self) -> None:
        result = self.gate.validate("SELECT COUNT(*) FROM users GROUP BY org_id")
        assert result.action == SQLGateAction.ALLOW

    def test_case_sensitive_dialect(self) -> None:
        gate_pg = SQLGate(dialect="postgres")
        result = gate_pg.validate("SELECT * FROM users")
        assert result.action == SQLGateAction.ALLOW


class TestValidateSqlFunction:
    """Test the module-level validate_sql convenience function."""

    def test_allows_select(self) -> None:
        result = validate_sql("SELECT 1")
        assert result.action == SQLGateAction.ALLOW

    def test_blocks_insert(self) -> None:
        result = validate_sql("INSERT INTO users VALUES (1)")
        assert result.action == SQLGateAction.REJECT