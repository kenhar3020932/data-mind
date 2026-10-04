"""Report generation routes for DataMind-King."""

from __future__ import annotations

from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.job import Job
from app.models.user import User

router = APIRouter(prefix="", tags=["reports"])


async def require_user(db: AsyncSession = Depends(get_db), user=None) -> User:
    """Placeholder dependency for user auth."""
    return user  # type: ignore[return-value]


@router.post("/generate", tags=["reports-generate"])
async def generate_report(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_user),
) -> dict:
    """Generate a report from a job result."""
    job_id = body.get("job_id", "")
    fmt = body.get("format", "pdf")  # pdf, xlsx, zip
    job = (await db.execute(
        select(Job).where((Job.id == job_id) & (Job.org_id == user.org_id))
    )).scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Job not found")
    # In production: generate PDF/XLSX/ZIP via ReportEngineAgent
    return {
        "job_id": job_id,
        "format": fmt,
        "status": "queued",
        "download_url": f"/api/v1/reports/{job_id}/{fmt}",
    }


@router.get("/{job_id}/{format}", tags=["reports-download"])
async def download_report(
    job_id: str,
    format: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_user),
) -> dict:
    """Download a generated report file."""
    job = (await db.execute(
        select(Job).where((Job.id == job_id) & (Job.org_id == user.org_id))
    )).scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Job not found")
    if format not in ("pdf", "xlsx", "zip"):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid format")
    # In production: return FileResponse with generated report
    return {"job_id": job_id, "format": format, "status": "generated"}
