"""Unit tests for BIProvisioner."""

from __future__ import annotations

import pytest

from app.services.bi_provisioner import BIProvisioner


class TestBIProvisioner:
    """Test suite for BIProvisioner."""

    def setup_method(self) -> None:
        self.provisioner = BIProvisioner()

    def test_provision_superset(self) -> None:
        """Test Superset provisioning."""
        instance = self.provisioner.provision('superset', 'org-123')
        assert instance['engine'] == 'superset'
        assert instance['org_id'] == 'org-123'
        assert 'superset' in instance['url']
        assert instance['status'] == 'provisioned'

    def test_provision_metabase(self) -> None:
        """Test Metabase provisioning."""
        instance = self.provisioner.provision('metabase', 'org-456')
        assert instance['engine'] == 'metabase'
        assert 'metabase' in instance['url']

    def test_provision_grafana(self) -> None:
        """Test Grafana provisioning."""
        instance = self.provisioner.provision('grafana', 'org-789')
        assert instance['engine'] == 'grafana'
        assert 'grafana' in instance['url']

    def test_invalid_engine(self) -> None:
        """Test invalid engine raises error."""
        with pytest.raises(ValueError, match="Invalid BI engine"):
            self.provisioner.provision('invalid', 'org-123')

    def test_get_status(self) -> None:
        """Test getting instance status."""
        self.provisioner.provision('superset', 'org-123')
        status = self.provisioner.get_status('superset', 'org-123')
        assert status is not None
        assert status['status'] == 'provisioned'

    def test_get_status_not_found(self) -> None:
        """Test getting status for non-existent instance."""
        status = self.provisioner.get_status('superset', 'org-nonexistent')
        assert status is None

    def test_deprovision(self) -> None:
        """Test deprovisioning an instance."""
        self.provisioner.provision('superset', 'org-123')
        result = self.provisioner.deprovision('superset', 'org-123')
        assert result is True
        assert self.provisioner.get_status('superset', 'org-123') is None

    def test_deprovision_not_found(self) -> None:
        """Test deprovisioning non-existent instance."""
        result = self.provisioner.deprovision('superset', 'org-nonexistent')
        assert result is False

    def test_list_instances(self) -> None:
        """Test listing all instances."""
        self.provisioner.provision('superset', 'org-1')
        self.provisioner.provision('metabase', 'org-2')

        instances = self.provisioner.list_instances()
        assert len(instances) == 2