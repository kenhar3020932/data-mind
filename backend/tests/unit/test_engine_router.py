"""Unit tests for engine router."""

from __future__ import annotations

import pytest

from app.services.engine_service import EngineRouter, EngineType


class TestEngineRouter:
    """Test suite for engine selection logic."""

    def setup_method(self) -> None:
        self.router = EngineRouter()

    def test_small_dataset_uses_duckdb(self) -> None:
        selection = self.router.select(100 * 1024 * 1024)  # 100MB
        assert selection.engine == EngineType.DUCKDB
        assert "DuckDB" in selection.reason

    def test_medium_dataset_uses_clickhouse(self) -> None:
        selection = self.router.select(50 * 1024 * 1024 * 1024)  # 50GB
        assert selection.engine == EngineType.CLICKHOUSE
        assert "ClickHouse" in selection.reason

    def test_large_dataset_uses_spark(self) -> None:
        selection = self.router.select(1500 * 1024 * 1024 * 1024)  # 1.5TB
        assert selection.engine == EngineType.SPARK
        assert "Spark" in selection.reason

    def test_boundary_10gb(self) -> None:
        selection = self.router.select(10 * 1024 * 1024 * 1024)  # Exactly 10GB
        assert selection.engine == EngineType.CLICKHOUSE

    def test_boundary_1tb(self) -> None:
        selection = self.router.select(1000 * 1024 * 1024 * 1024)  # Exactly 1TB
        assert selection.engine == EngineType.SPARK

    def test_zero_size_uses_duckdb(self) -> None:
        selection = self.router.select(0)
        assert selection.engine == EngineType.DUCKDB

    def test_memory_estimates_decrease_with_scale(self) -> None:
        small = self.router.select(100 * 1024 * 1024)
        large = self.router.select(100 * 1024 * 1024 * 1024)
        assert small.estimated_memory_mb < large.estimated_memory_mb
