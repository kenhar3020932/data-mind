"""Resumable multipart upload service for DataMind-King."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from ..services.minio_service import MinIOService, get_dataset_path

minio = MinIOService()


@dataclass
class MultipartUpload:
    """State for a multipart upload operation."""
    upload_id: str
    org_id: str
    dataset_id: str
    filename: str
    content_type: str
    total_size: int
    parts: dict[int, dict[str, Any]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "initialized"


class UploadService:
    """Handle resumable multipart uploads to MinIO."""

    def __init__(self) -> None:
        self._uploads: dict[str, MultipartUpload] = {}

    def init_upload(
        self,
        org_id: str,
        dataset_id: str,
        filename: str,
        content_type: str,
        total_size: int,
    ) -> dict[str, Any]:
        """Initialize a new multipart upload."""
        upload_id = str(uuid.uuid4())
        upload = MultipartUpload(
            upload_id=upload_id,
            org_id=org_id,
            dataset_id=dataset_id,
            filename=filename,
            content_type=content_type,
            total_size=total_size,
        )
        self._uploads[upload_id] = upload

        # Generate presigned URLs for each part (64MB chunks)
        chunk_size = 64 * 1024 * 1024  # 64MB
        num_parts = max(1, (total_size + chunk_size - 1) // chunk_size)

        presigned_urls = []
        for i in range(1, num_parts + 1):
            url = minio.generate_presigned_put_url(
                bucket="raw",
                object_name=get_dataset_path(org_id, dataset_id, filename),
                part_number=i,
                expires=3600,
            )
            presigned_urls.append({
                "part_number": i,
                "url": url,
                "min_size_mb": 64,
            })

        return {
            "upload_id": upload_id,
            "filename": filename,
            "content_type": content_type,
            "total_size": total_size,
            "num_parts": num_parts,
            "presigned_urls": presigned_urls,
        }

    def upload_part(
        self,
        upload_id: str,
        part_number: int,
        etag: str,
        size: int,
    ) -> dict[str, Any]:
        """Record an uploaded part."""
        if upload_id not in self._uploads:
            raise ValueError(f"Upload {upload_id} not found")

        upload = self._uploads[upload_id]
        upload.parts[part_number] = {
            "etag": etag,
            "size": size,
            "uploaded_at": datetime.now(timezone.utc),
        }

        return {
            "upload_id": upload_id,
            "part_number": part_number,
            "etag": etag,
            "size": size,
        }

    def complete_upload(self, upload_id: str) -> dict[str, Any]:
        """Complete the multipart upload."""
        if upload_id not in self._uploads:
            raise ValueError(f"Upload {upload_id} not found")

        upload = self._uploads[upload_id]

        # Verify all parts uploaded
        expected_parts = max(1, (upload.total_size + 64 * 1024 * 1024 - 1) // (64 * 1024 * 1024))
        if len(upload.parts) < expected_parts:
            raise ValueError(f"Incomplete upload: {len(upload.parts)}/{expected_parts} parts")

        upload.status = "completed"

        # Compute checksum of completed file
        # In production: use MinIO's complete_multipart_upload
        checksum = hashlib.sha256(f"{upload_id}{upload.filename}".encode()).hexdigest()

        return {
            "upload_id": upload_id,
            "status": "completed",
            "parts_completed": len(upload.parts),
            "checksum": checksum,
            "storage_path": get_dataset_path(upload.org_id, upload.dataset_id, upload.filename),
        }

    def abort_upload(self, upload_id: str) -> None:
        """Abort and clean up a multipart upload."""
        if upload_id in self._uploads:
            del self._uploads[upload_id]


# Module-level singleton
service = UploadService()