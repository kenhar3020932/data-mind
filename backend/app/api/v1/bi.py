"""BI (Business Intelligence) provisioning routes for DataMind-King."""

from __future__ import annotations

from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.user import User

router = APIRouter(prefix="", tags=["bi"])


async def require_user(db: AsyncSession = Depends(get_db), user=None) -> User:
    """Placeholder dependency for user auth."""
    return user  # type: ignore[return-value]


@router.post("/provision/{engine}", tags=["bi-provision"])
async def provision_bi(
    engine: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_user),
) -> dict:
    """Provision a BI tool (Superset/Metabase/Grafana) for the current org."""
    if engine not in ("superset", "metabase", "grafana"):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Engine must be one of: superset, metabase, grafana",
        )
    # In production: provision BI tool via InfrastructureAgent
    return {
        "engine": engine,
        "org_id": user.org_id,
        "status": "provisioned",
        "url": f"https://{engine}-{user.org_id}.datamind.local",
    }


@router.get("/status/{engine}", tags=["bi-status"])
async def bi_status(
    engine: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_user),
) -> dict:
    """Check the status of a provisioned BI tool."""
    if engine not in ("superset", "metabase", "grafana"):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Engine must be one of: superset, metabase, grafana",
        )
    # In production: query BI tool health endpoint
    return {
        "engine": engine,
        "org_id": user.org_id,
        "status": "running",
        "health": "ok",
    }


@router.post("/dashboard", tags=["bi-dashboard"])
async def create_bi_dashboard(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_user),
) -> dict:
    """Create a dashboard in the BI tool."""
    # In production: call DashboardBuilderAgent to create BI dashboard
    return {
        "org_id": user.org_id,
        "status": "created",
        "dashboard_id": "",
    }
