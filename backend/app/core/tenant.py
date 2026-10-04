"""Tenant isolation middleware for DataMind-King.

Ensures all data access is scoped by org_id to prevent cross-tenant leaks.
"""

from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException, Request
from http import HTTPStatus


class TenantIsolation:
    """Enforces tenant isolation via org_id in all requests."""

    def __init__(self) -> None:
        self._org_id_header = "x-organization-id"
        self._user_id_header = "x-user-id"

    def get_org_id(self, request: Request) -> str:
        """Extract org_id from request headers or JWT."""
        org_id = request.headers.get(self._org_id_header)
        if not org_id:
            # In production: extract from JWT claim
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Missing organization context",
            )
        return org_id

    def get_user_id(self, request: Request) -> str:
        """Extract user_id from request headers or JWT."""
        user_id = request.headers.get(self._user_id_header)
        if not user_id:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Missing user context",
            )
        return user_id

    def enforce_tenant(self, request: Request) -> dict[str, str]:
        """Get both org_id and user_id from request."""
        return {
            "org_id": self.get_org_id(request),
            "user_id": self.get_user_id(request),
        }


# Module-level singleton
tenant_isolation = TenantIsolation()


def get_current_org_id(request: Request) -> str:
    """FastAPI dependency to get org_id from request."""
    return tenant_isolation.get_org_id(request)


def get_current_user_id(request: Request) -> str:
    """FastAPI dependency to get user_id from request."""
    return tenant_isolation.get_user_id(request)


def build_tenant_filter(org_id: str) -> str:
    """Build a WHERE clause for tenant isolation."""
    return f"org_id = '{org_id}'"