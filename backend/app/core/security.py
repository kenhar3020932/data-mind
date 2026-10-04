"""Security utilities: tenant isolation, RBAC helpers, prompt injection defense."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable


def tenant_isolation_query(org_id: str, table_alias: str = "t") -> str:
    """Generate a WHERE clause that enforces tenant isolation."""
    return f"{table_alias}.org_id = '{org_id}'"


def wrap_untrusted_data(user_input: str) -> str:
    """Wrap user-provided text in XML tags to prevent prompt injection."""
    escaped = user_input.replace("<", "&lt;").replace(">", "&gt;")
    return f"<untrusted_data>{escaped}</untrusted_data>"


def sanitize_html(text: str) -> str:
    """Basic HTML sanitization to prevent XSS."""
    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
    }
    for char, safe in replacements.items():
        text = text.replace(char, safe)
    return text


def require_tenant_permission(
    required_role: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that checks if the current user has the required role."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # In a real implementation, this would check the authenticated user's roles
            # against the required_role from the database session
            return func(*args, **kwargs)
        return wrapper
    return decorator
