"""Prometheus metrics for DataMind-King."""

from __future__ import annotations

from prometheus_client import Counter, Histogram, Gauge, start_http_server
from prometheus_client import CollectorRegistry


class MetricsCollector:
    """Prometheus metrics for DataMind-King."""

    def __init__(self) -> None:
        self.registry = CollectorRegistry()

        # Request metrics
        self.request_count = Counter(
            'request_count',
            'Total request count',
            ['method', 'endpoint', 'status'],
            registry=self.registry,
        )

        self.request_duration = Histogram(
            'request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry,
        )

        # Job metrics
        self.jobs_created = Counter(
            'jobs_created',
            'Total jobs created',
            ['agent_name', 'status'],
            registry=self.registry,
        )

        self.jobs_duration = Histogram(
            'jobs_duration_seconds',
            'Job duration in seconds',
            ['agent_name'],
            registry=self.registry,
        )

        # Dataset metrics
        self.datasets_uploaded = Counter(
            'datasets_uploaded',
            'Total datasets uploaded',
            ['org_id', 'format'],
            registry=self.registry,
        )

        self.dataset_size_bytes = Gauge(
            'dataset_size_bytes',
            'Dataset size in bytes',
            ['org_id', 'dataset_id'],
            registry=self.registry,
        )

        # LLM metrics
        self.llm_tokens = Counter(
            'llm_tokens_total',
            'Total LLM tokens used',
            ['model', 'type'],
            registry=self.registry,
        )

        self.llm_cost = Counter(
            'llm_cost_usd_total',
            'Total LLM cost in USD',
            ['model'],
            registry=self.registry,
        )

    def start_server(self, port: int = 9090) -> None:
        """Start Prometheus metrics server."""
        start_http_server(port, registry=self.registry)

    def record_request(self, method: str, endpoint: str, status: int, duration: float) -> None:
        """Record a request metric."""
        self.request_count.labels(method=method, endpoint=endpoint, status=str(status)).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_job(self, agent_name: str, status: str, duration: float) -> None:
        """Record a job metric."""
        self.jobs_created.labels(agent_name=agent_name, status=status).inc()
        self.jobs_duration.labels(agent_name=agent_name).observe(duration)


# Module-level singleton
metrics = MetricsCollector()