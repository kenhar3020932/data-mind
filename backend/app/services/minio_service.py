"""MinIO client service for DataMind-King.

Handles S3-compatible object storage operations for data ingestion
and retrieval with per-tenant prefix isolation.
"""

from __future__ import annotations

import io
from typing import BinaryIO

from minio import Minio
from minio.commonconfig import CopySource
from minio.deleteobjects import DeleteObject
try:
    from minio.error import S3Error as MinioException
except ImportError:
    MinioException = Exception  # type: ignore[misc,assignment]

from ..core.settings import settings


class MinIOService:
    """MinIO service for object storage operations."""

    def __init__(self) -> None:
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

    def bucket_exists(self, bucket: str) -> bool:
        """Check if a bucket exists."""
        try:
            return self.client.bucket_exists(bucket)
        except MinioException:
            return False

    def create_bucket(self, bucket: str, region: str = "us-east-1") -> None:
        """Create a bucket if it doesn't exist."""
        if not self.bucket_exists(bucket):
            self.client.make_bucket(bucket, region=region)

    def upload_file(
        self,
        bucket: str,
        object_name: str,
        file_path: str,
        mime_type: str = "application/octet-stream",
    ) -> dict:
        """Upload a file to MinIO."""
        self.create_bucket(bucket)
        self.client.fput_object(bucket, object_name, file_path, content_type=mime_type)
        return {"bucket": bucket, "object_name": object_name}

    def upload_stream(
        self,
        bucket: str,
        object_name: str,
        data: bytes,
        mime_type: str = "application/octet-stream",
    ) -> dict:
        """Upload bytes to MinIO."""
        self.create_bucket(bucket)
        self.client.put_object(
            bucket,
            object_name,
            io.BytesIO(data),
            length=len(data),
            content_type=mime_type,
        )
        return {"bucket": bucket, "object_name": object_name}

    def upload_multipart(
        self,
        bucket: str,
        object_name: str,
        parts_data: list[tuple[int, bytes]],
        mime_type: str = "application/octet-stream",
    ) -> dict:
        """Upload multipart data to MinIO."""
        self.create_bucket(bucket)
        # In production: use minio's native multipart upload
        # This is a simplified implementation
        total_size = sum(len(data) for _, data in parts_data)
        self.client.put_object(
            bucket,
            object_name,
            io.BytesIO(b"".join(data for _, data in parts_data)),
            length=total_size,
            content_type=mime_type,
        )
        return {"bucket": bucket, "object_name": object_name, "parts": len(parts_data)}

    def get_object(self, bucket: str, object_name: str) -> bytes:
        """Download an object from MinIO."""
        response = self.client.get_object(bucket, object_name)
        return response.read()

    def list_objects(self, bucket: str, prefix: str = "") -> list[str]:
        """List objects in a bucket with optional prefix."""
        objects = []
        for obj in self.client.list_objects(bucket, prefix=prefix, recursive=True):
            objects.append(obj.object_name)
        return objects

    def delete_object(self, bucket: str, object_name: str) -> None:
        """Delete an object from MinIO."""
        self.client.remove_object(bucket, object_name)

    def delete_objects(self, bucket: str, object_names: list[str]) -> None:
        """Delete multiple objects from MinIO."""
        delete_keys = [DeleteObject(name) for name in object_names]
        self.client.remove_objects(bucket, delete_keys)

    def get_presigned_url(
        self,
        bucket: str,
        object_name: str,
        expires: int = 3600,
    ) -> str:
        """Get a presigned URL for an object."""
        return self.client.presigned_get_object(bucket, object_name, expires=expires)

    def generate_presigned_put_url(
        self,
        bucket: str,
        object_name: str,
        part_number: int = 1,
        expires: int = 3600,
    ) -> str:
        """Generate presigned PUT URL for multipart upload part."""
        from datetime import timedelta
        # Note: MinIO presigned_put_object doesn't support part_number directly
        # In production, use S3 SDK's initiate_multipart_upload + presigned_part_upload
        return self.client.presigned_put_object(
            bucket, object_name, expires=timedelta(seconds=expires)
        )


# Module-level singleton
minio_service = MinIOService()


def get_tenant_prefix(org_id: str) -> str:
    """Generate tenant-scoped storage prefix."""
    return f"{org_id}/"


def get_dataset_path(org_id: str, dataset_id: str, filename: str) -> str:
    """Generate full path for dataset storage."""
    return f"{get_tenant_prefix(org_id)}datasets/{dataset_id}/{filename}"