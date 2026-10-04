"""Unit tests for Ultra God Mode agents."""

from __future__ import annotations

import pytest

from app.agents.sql.agent import SQLAgent
from app.agents.dashboard.agent import DashboardAgent
from app.agents.data_quality.agent import DataQualityAgent
from app.agents.base import TaskBrief


class TestSQLAgent:
    """Test suite for SQLAgent with dynamic tool selection."""

    def setup_method(self) -> None:
        self.agent = SQLAgent()

    def test_select_engine_small_dataset(self) -> None:
        """Test engine selection for small dataset."""
        engine = self.agent._select_engine(100 * 1024 * 1024)  # 100MB
        assert engine == "duckdb"

    def test_select_engine_medium_dataset(self) -> None:
        """Test engine selection for medium dataset."""
        engine = self.agent._select_engine(50 * 1024 * 1024 * 1024)  # 50GB
        assert engine == "clickhouse"

    def test_select_engine_large_dataset(self) -> None:
        """Test engine selection for large dataset."""
        engine = self.agent._select_engine(1500 * 1024 * 1024 * 1024)  # 1.5TB
        assert engine == "trino"

    def test_calculate_confidence(self) -> None:
        """Test evidence-based confidence calculation."""
        result = {"validation_passed": True, "row_count": 100}
        confidence = self.agent._calculate_confidence(result, 50.0)
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.8  # Should be high for successful execution

    @pytest.mark.asyncio
    async def test_execute_valid_query(self) -> None:
        """Test executing a valid SQL query."""
        brief = TaskBrief(
            task_id="test-1",
            description="Test query",
            context={"query": "SELECT 1"},
            org_id="org-1",
        )
        ack = await self.agent.acknowledge(brief)
        assert ack.accepted is True

        result = await self.agent.execute(brief, ack)
        assert result.success is True
        assert result.confidence > 0
        assert result.output.get("engine") in ("duckdb", "clickhouse", "trino")

    @pytest.mark.asyncio
    async def test_execute_invalid_query(self) -> None:
        """Test executing invalid SQL query."""
        brief = TaskBrief(
            task_id="test-2",
            description="Invalid query",
            context={"query": "DROP TABLE users"},
            org_id="org-1",
        )
        ack = await self.agent.acknowledge(brief)
        result = await self.agent.execute(brief, ack)
        assert result.success is False
        assert "rejected" in result.error.lower() or "gate" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_no_query(self) -> None:
        """Test executing with no query."""
        brief = TaskBrief(
            task_id="test-3",
            description="No query",
            context={},
            org_id="org-1",
        )
        ack = await self.agent.acknowledge(brief)
        assert ack.accepted is False
        result = await self.agent.execute(brief, ack)
        assert result.success is False
        assert "sql query" in result.error.lower()


class TestDashboardAgent:
    """Test suite for DashboardAgent with dynamic tool selection."""

    def setup_method(self) -> None:
        self.agent = DashboardAgent()

    def test_select_tool_simple(self) -> None:
        """Test tool selection for simple dashboard."""
        tool = self.agent._select_tool(3, "simple", {})
        assert tool == "vega_lite"

    def test_select_tool_medium(self) -> None:
        """Test tool selection for medium dashboard."""
        tool = self.agent._select_tool(10, "medium", {})
        assert tool in ("superset", "metabase")

    def test_select_tool_complex(self) -> None:
        """Test tool selection for complex dashboard."""
        tool = self.agent._select_tool(25, "complex", {})
        assert tool == "metabase"

    def test_calculate_confidence(self) -> None:
        """Test evidence-based confidence calculation."""
        confidence = self.agent._calculate_confidence(5, "vega_lite", True)
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.7

    @pytest.mark.asyncio
    async def test_execute_valid_dashboard(self) -> None:
        """Test creating a valid dashboard."""
        brief = TaskBrief(
            task_id="dash-1",
            description="Create dashboard",
            context={"layout": [{"x": 0, "y": 0, "w": 6, "h": 4}]},
            org_id="org-1",
        )
        ack = await self.agent.acknowledge(brief)
        assert ack.accepted is True

        result = await self.agent.execute(brief, ack)
        assert result.success is True
        assert result.confidence > 0
        assert result.output.get("widgets") > 0


class TestDataQualityAgent:
    """Test suite for DataQualityAgent with dynamic tool selection."""

    def setup_method(self) -> None:
        self.agent = DataQualityAgent()

    def test_select_tool_quick(self) -> None:
        """Test tool selection for quick profile."""
        tool = self.agent._select_tool("quick", False, {})
        assert tool == "pandas_profiling"

    def test_select_tool_full(self) -> None:
        """Test tool selection for full profile."""
        tool = self.agent._select_tool("full", True, {})
        assert tool == "great_expectations"

    def test_select_tool_standard(self) -> None:
        """Test tool selection for standard profile."""
        tool = self.agent._select_tool("standard", False, {})
        assert tool == "polars"

    def test_calculate_confidence(self) -> None:
        """Test evidence-based confidence calculation."""
        metrics = {"completeness": 0.95, "uniqueness": 0.98}
        confidence = self.agent._calculate_confidence(metrics, "polars", 5000)
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.8

    @pytest.mark.asyncio
    async def test_execute_valid_profile(self) -> None:
        """Test profiling a valid dataset."""
        brief = TaskBrief(
            task_id="dq-1",
            description="Profile dataset",
            context={"dataset_id": "ds-123", "row_count": 1000},
            org_id="org-1",
        )
        ack = await self.agent.acknowledge(brief)
        assert ack.accepted is True

        result = await self.agent.execute(brief, ack)
        assert result.success is True
        assert result.confidence > 0
        assert result.output.get("dataset_id") == "ds-123"
        assert "metrics" in result.output

    @pytest.mark.asyncio
    async def test_execute_no_dataset(self) -> None:
        """Test profiling with no dataset."""
        brief = TaskBrief(
            task_id="dq-2",
            description="No dataset",
            context={},
            org_id="org-1",
        )
        ack = await self.agent.acknowledge(brief)
        assert ack.accepted is False
        result = await self.agent.execute(brief, ack)
        assert result.success is False
        assert "dataset" in result.error.lower()