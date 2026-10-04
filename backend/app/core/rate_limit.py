"""Rate limiting for DataMind-King using slowapi + Redis."""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

limiter = Limiter(key_func=get_remote_address)


def get_rate_limit_key(request: Request) -> str:
    """Generate a rate limit key based on user ID or IP."""
    user_id = getattr(getattr(request, "state", None), "user_id", None)
    if user_id:
        return f"user:{user_id}"
    return f"ip:{request.client.host}"
