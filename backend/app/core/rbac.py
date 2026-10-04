"""Casbin RBAC policy engine for DataMind-King.

Implements role-based access control with domain-based tenant isolation.
Uses Casbin's built-in domain support for multi-tenancy.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from casbin import Enforcer


class RBACManager:
    """Role-Based Access Control manager using Casbin with domain support."""

    def __init__(self, model_path: str | None = None, policy_path: str | None = None) -> None:
        """Initialize Casbin enforcer with domain support."""
        self.model_path = model_path or str(Path(__file__).parent.parent.parent / "rbac_model.conf")
        self.policy_path = policy_path or str(Path(__file__).parent.parent.parent / "rbac_policy.csv")
        self._enforcer: Enforcer | None = None

    def _get_enforcer(self) -> Enforcer:
        """Lazy-load the Casbin enforcer."""
        if self._enforcer is None:
            self._enforcer = Enforcer(self.model_path, self.policy_path)
        return self._enforcer

    def is_allowed(
        self,
        user_id: str,
        org_id: str,
        resource: str,
        action: str,
    ) -> bool:
        """Check if a user has permission to perform an action on a resource.

        Uses domain-based tenant isolation via Casbin's domain support.
        """
        enforcer = self._get_enforcer()
        # Casbin enforce signature: (sub, dom, obj, act)
        return enforcer.enforce(user_id, org_id, resource, action)

    def add_role(self, user_id: str, role: str, org_id: str) -> bool:
        """Add a role to a user within an organization (domain)."""
        enforcer = self._get_enforcer()
        return enforcer.add_role_for_user(user_id, role, org_id)

    def delete_role(self, user_id: str, role: str, org_id: str) -> bool:
        """Remove a role from a user."""
        enforcer = self._get_enforcer()
        return enforcer.delete_role_for_user(user_id, role, org_id)

    def get_roles(self, user_id: str, org_id: str | None = None) -> list[str]:
        """Get all roles for a user (optionally filtered by org/domain)."""
        enforcer = self._get_enforcer()
        # Try with domain first, fall back to basic query
        try:
            return enforcer.get_roles_for_user(user_id, org_id)
        except TypeError:
            # Some versions don't support domain parameter
            return enforcer.get_roles_for_user(user_id)

    def get_permissions(self, user_id: str, org_id: str) -> list[tuple[str, str, str]]:
        """Get all permissions for a user in an organization."""
        enforcer = self._get_enforcer()
        return enforcer.get_permissions_for_user(user_id, org_id)


# Module-level singleton
rbac = RBACManager()


def check_permission(
    user_id: str,
    org_id: str,
    resource: str,
    action: str,
) -> bool:
    """Convenience function to check permissions."""
    return rbac.is_allowed(user_id, org_id, resource, action)