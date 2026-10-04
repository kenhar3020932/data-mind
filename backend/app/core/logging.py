"""Structured logging with structlog for DataMind-King."""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

LOGGING_FORMATTERS = {
    "json": structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer()
    ),
    "pretty": structlog.dev.ConsoleRenderer(),
}


def setup_logging(level: int = logging.INFO) -> None:
    """Configure structlog for structured JSON logging."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.set_exc_info,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            LOGGING_FORMATTERS["json"],
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger bound to the given name."""
    return structlog.get_logger(name)


def log_request(request_id: str, method: str, path: str, status: int, duration_ms: float) -> None:
    """Log an HTTP request/response cycle with request_id and trace info."""
    get_logger("http.access").info(
        "request",
        request_id=request_id,
        method=method,
        path=path,
        status=status,
        duration_ms=duration_ms,
    )


def log_error(request_id: str, error: Exception, context: dict[str, Any] | None = None) -> None:
    """Log an error with request_id and optional context."""
    ctx = context or {}
    get_logger("error").error(
        "error",
        request_id=request_id,
        error_type=type(error).__name__,
        error_message=str(error),
        **ctx,
    )
