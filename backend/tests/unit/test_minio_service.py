"""Unit tests for MinIO service."""

from __future__ import annotations

import pytest

from app.services.minio_service import MinIOService, get_tenant_prefix, get_dataset_path


class TestMinIOService:
    """Test suite for MinIO service utilities."""

    def test_get_tenant_prefix(self) -> None:
        """Test tenant prefix generation."""
        assert get_tenant_prefix("org-123") == "org-123/"

    def test_get_dataset_path(self) -> None:
        """Test dataset path generation."""
        path = get_dataset_path("org-123", "ds-456", "data.parquet")
        assert path == "org-123/datasets/ds-456/data.parquet"

    def test_minio_service_initialization(self) -> None:
        """Test MinIO service can be instantiated."""
        service = MinIOService()
        assert service.client is not None