"""OpenTelemetry configuration for DataMind-King."""

from __future__ import annotations

import os
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


class TracingConfig:
    """Configure OpenTelemetry tracing."""

    def __init__(self, service_name: str = "datamind-king") -> None:
        self.service_name = service_name
        self.provider: TracerProvider | None = None

    def setup(self) -> None:
        """Initialize tracing with in-memory exporter for dev."""
        from opentelemetry.sdk.resources import Resource
        resource = Resource.create({"service.name": self.service_name})
        self.provider = TracerProvider(resource=resource)

        # Add console exporter (in production, use OTLP exporter)
        console_exporter = ConsoleSpanExporter()
        span_processor = BatchSpanProcessor(console_exporter)
        self.provider.add_span_processor(span_processor)

        trace.set_tracer_provider(self.provider)

        # Set trace context propagator
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(console_exporter)
        )

    def get_tracer(self, name: str) -> Any:
        """Get a tracer instance."""
        if self.provider is None:
            self.setup()
        return trace.get_tracer(name)

    def inject_context(self, context: dict[str, str]) -> None:
        """Inject trace context into outgoing requests."""
        carrier: dict[str, str] = {}
        TraceContextTextMapPropagator().inject(carrier)
        context.update(carrier)


# Module-level singleton
tracing = TracingConfig()


def setup_tracing(service_name: str = "datamind-king") -> None:
    """Setup tracing for the application."""
    tracing.service_name = service_name
    tracing.setup()


def get_tracer(name: str) -> Any:
    """Get a tracer by name."""
    return tracing.get_tracer(name)