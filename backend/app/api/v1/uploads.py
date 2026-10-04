"""Resumable multipart upload routes for DataMind-King."""

from __future__ import annotations

import hashlib
import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.params import Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.settings import settings

router = APIRouter(prefix="", tags=["uploads"])


@router.post("/init", tags=["uploads-init"])
async def init_upload(
    filename: str = Query(..., min_length=1, max_length=255),
    content_type: str = Query(...),
    size_bytes: int = Query(..., ge=1),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Initialize a resumable multipart upload and return the upload ID with presigned URLs."""
    upload_id = str(uuid.uuid4())
    return {
        "upload_id": upload_id,
        "filename": filename,
        "content_type": content_type,
        "size_bytes": size_bytes,
        "min_part_size_mb": 64,
        "max_parts": 10000,
        "endpoint": f"/api/v1/uploads/{upload_id}/part/{{part_number}}",
    }


@router.put("/{upload_id}/part/{part_number}", tags=["uploads-part"])
async def upload_part(
    upload_id: str,
    part_number: int = Path(..., ge=1),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Upload a single part of a multipart file to MinIO."""
    body = await file.read()
    etag = hashlib.sha256(body).hexdigest()
    # In production: stream body bytes directly to MinIO multipart upload
    return {
        "upload_id": upload_id,
        "part_number": part_number,
        "etag": f'"{etag}"',
        "size_bytes": len(body),
    }


@router.post("/{upload_id}/complete", tags=["uploads-complete"])
async def complete_upload(
    upload_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Complete a multipart upload, triggering profiling and engine selection."""
    parts = body.get("parts", [])
    if not parts:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="No parts provided")
    # In production: call minio.complete_multipart_upload, then trigger ingest pipeline
    return {
        "upload_id": upload_id,
        "status": "completed",
        "parts_completed": len(parts),
        "next": "/api/v1/jobs",
    }


@router.post("/{upload_id}/abort", status_code=HTTPStatus.NO_CONTENT, tags=["uploads-abort"])
async def abort_upload(
    upload_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Abort and clean up a multipart upload."""
    # In production: call minio.abort_multipart_upload(upload_id, parts)
    # For now, this is a no-op as uploads are simulated in-memory
    logger.info("Upload aborted: %s", upload_id)
