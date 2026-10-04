"""Unit tests for upload service with mocked MinIO."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.services.upload_service import MultipartUpload, UploadService


class TestUploadService:
    """Test suite for upload service."""

    def setup_method(self) -> None:
        self.service = UploadService()

    @patch('app.services.upload_service.minio')
    def test_init_upload(self, mock_minio) -> None:
        """Test upload initialization."""
        mock_minio.generate_presigned_put_url.return_value = "http://example.com/presigned-url"

        result = self.service.init_upload(
            org_id="org-123",
            dataset_id="ds-456",
            filename="data.csv",
            content_type="text/csv",
            total_size=1024 * 1024,  # 1MB
        )
        assert "upload_id" in result
        assert result["filename"] == "data.csv"
        assert result["total_size"] == 1024 * 1024
        assert "presigned_urls" in result
        assert len(result["presigned_urls"]) > 0

    def test_upload_part(self) -> None:
        """Test recording an uploaded part."""
        # Manually add upload to service state
        upload = MultipartUpload(
            upload_id="test-upload-id",
            org_id="org-123",
            dataset_id="ds-456",
            filename="data.csv",
            content_type="text/csv",
            total_size=1024 * 1024,
        )
        self.service._uploads["test-upload-id"] = upload

        part_result = self.service.upload_part(
            upload_id="test-upload-id",
            part_number=1,
            etag='"abc123"',
            size=512 * 1024,
        )
        assert part_result["part_number"] == 1
        assert part_result["etag"] == '"abc123"'

    @patch('app.services.upload_service.minio')
    def test_complete_upload_success(self, mock_minio) -> None:
        """Test completing a multipart upload."""
        # Create upload
        self.service.init_upload(
            org_id="org-123",
            dataset_id="ds-456",
            filename="data.csv",
            content_type="text/csv",
            total_size=1024 * 1024,
        )

        # Upload all parts (for 1MB with 64MB chunks, only 1 part needed)
        upload_id = list(self.service._uploads.keys())[0]
        self.service.upload_part(
            upload_id=upload_id,
            part_number=1,
            etag='"part1"',
            size=1024 * 1024,
        )

        # Complete upload
        complete_result = self.service.complete_upload(upload_id)
        assert complete_result["status"] == "completed"
        assert "checksum" in complete_result

    @patch('app.services.upload_service.minio')
    def test_complete_upload_incomplete_fails(self, mock_minio) -> None:
        """Test that incomplete upload fails."""
        # Create upload with larger size requiring multiple parts
        self.service.init_upload(
            org_id="org-123",
            dataset_id="ds-456",
            filename="data.csv",
            content_type="text/csv",
            total_size=1024 * 1024 * 1024,  # 1GB
        )

        # Only upload one part when multiple are expected
        upload_id = list(self.service._uploads.keys())[0]
        self.service.upload_part(
            upload_id=upload_id,
            part_number=1,
            etag='"part1"',
            size=64 * 1024 * 1024,
        )

        # Should fail because not all parts uploaded
        with pytest.raises(ValueError, match="Incomplete upload"):
            self.service.complete_upload(upload_id)

    @patch('app.services.upload_service.minio')
    def test_abort_upload(self, mock_minio) -> None:
        """Test aborting an upload."""
        # Create upload
        self.service.init_upload(
            org_id="org-123",
            dataset_id="ds-456",
            filename="data.csv",
            content_type="text/csv",
            total_size=1024 * 1024,
        )
        upload_id = list(self.service._uploads.keys())[0]

        # Abort
        self.service.abort_upload(upload_id)

        # Should fail after abort
        with pytest.raises(ValueError, match="not found"):
            self.service.upload_part(upload_id, 1, '"etag"', 1024)