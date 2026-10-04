"""BI provisioning service for DataMind-King."""

from __future__ import annotations

from typing import Any


class BIProvisioner:
    """Provision and manage BI tools per organization."""

    def __init__(self) -> None:
        self._instances: dict[str, dict[str, str]] = {}

    def provision(
        self,
        engine: str,
        org_id: str,
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Provision a BI tool for an organization."""
        if engine not in ('superset', 'metabase', 'grafana'):
            raise ValueError(f"Invalid BI engine: {engine}")

        url_map = {
            'superset': f'https://superset-{org_id}.datamind.local',
            'metabase': f'https://metabase-{org_id}.datamind.local',
            'grafana': f'https://grafana-{org_id}.datamind.local',
        }

        instance = {
            'engine': engine,
            'org_id': org_id,
            'url': url_map[engine],
            'status': 'provisioned',
            'config': config or {},
        }

        key = f"{engine}:{org_id}"
        self._instances[key] = instance

        return instance

    def get_status(self, engine: str, org_id: str) -> dict[str, Any] | None:
        """Get provisioning status for a BI instance."""
        key = f"{engine}:{org_id}"
        return self._instances.get(key)

    def deprovision(self, engine: str, org_id: str) -> bool:
        """Deprovision a BI instance."""
        key = f"{engine}:{org_id}"
        if key in self._instances:
            del self._instances[key]
            return True
        return False

    def list_instances(self) -> list[dict[str, Any]]:
        """List all provisioned BI instances."""
        return list(self._instances.values())


# Module-level singleton
provisioner = BIProvisioner()