"""Unit tests for tracing and metrics."""

from __future__ import annotations

import pytest

from app.core.tracing import TracingConfig, setup_tracing, get_tracer
from app.core.metrics import MetricsCollector


class TestTracing:
    """Test suite for tracing."""

    def test_tracing_initialization(self) -> None:
        """Test tracing can be initialized."""
        config = TracingConfig()
        assert config.service_name == "datamind-king"

    def test_setup_tracing(self) -> None:
        """Test tracing setup."""
        setup_tracing("test-service")
        tracer = get_tracer("test-tracer")
        assert tracer is not None

    def test_get_tracer(self) -> None:
        """Test getting tracer instance."""
        tracer = get_tracer("my-tracer")
        assert tracer is not None


class TestMetrics:
    """Test suite for metrics."""

    def setup_method(self) -> None:
        self.metrics = MetricsCollector()

    def test_record_request(self) -> None:
        """Test recording request metrics."""
        self.metrics.record_request("GET", "/api/test", 200, 0.1)
        # No exception means success

    def test_record_job(self) -> None:
        """Test recording job metrics."""
        self.metrics.record_job("sql_agent", "success", 1.5)
        # No exception means success

    def test_metric_counters_exist(self) -> None:
        """Test that metrics are properly configured."""
        assert self.metrics.request_count is not None
        assert self.metrics.jobs_created is not None
        assert self.metrics.dataset_size_bytes is not None