"""Middleware for DataMind-King: Request-ID, CORS, Timing."""

from __future__ import annotations

import uuid
import time
from typing import Any, Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .logging import log_request


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Add a unique request_id to every request and propagate it via headers."""

    async def dispatch(self, request: Request, call_next: Callable[..., Awaitable[Message]]) -> Message:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """Track request duration and log structured access logs."""

    async def dispatch(self, request: Request, call_next: Callable[..., Awaitable[Message]]) -> Message:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        request_id = getattr(request.state, "request_id", "unknown")
        log_request(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(duration_ms, 2),
        )
        return response


def create_cors_middleware(app: ASGIApp, allowed_origins: list[str]) -> ASGIApp:
    """Create a CORS middleware wrapper around the given app."""
    from starlette.middleware.cors import CORSMiddleware
    cors = CORSMiddleware(
        app=app,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        max_age=600,
    )
    return cors
