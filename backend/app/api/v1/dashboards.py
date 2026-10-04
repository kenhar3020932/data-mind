"""Dashboard management routes for DataMind-King."""

from __future__ import annotations

import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.user import User
from app.models.dashboard import Dashboard

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["dashboards"])


async def require_user(db: AsyncSession = Depends(get_db), user=None) -> User:
    """Placeholder dependency for user auth."""
    return user  # type: ignore[return-value]


@router.get("", tags=["dashboards-list"])
async def list_dashboards(
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(require_user),
) -> dict:
    """List dashboards for the current organization."""
    stmt = select(Dashboard).where(Dashboard.org_id == user.org_id).order_by(Dashboard.created_at.desc())
    result = await db.execute(stmt)
    dashboards = result.scalars().all()
    return {
        "items": [
            {
                "id": d.id,
                "name": d.name,
                "org_id": d.org_id,
                "widget_count": len(d.widgets) if d.widgets else 0,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in dashboards
        ],
        "total": len(dashboards),
    }


@router.post("", status_code=HTTPStatus.CREATED, tags=["dashboards-create"])
async def create_dashboard(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(require_user),
) -> dict:
    """Create a new dashboard."""
    from app.models.dashboard import Dashboard as DashboardModel
    import uuid
    dashboard = DashboardModel(
        id=str(uuid.uuid4()),
        org_id=user.org_id,
        name=body.get("name", "Untitled"),
        widgets=body.get("widgets", []),
        layout=body.get("layout", {"columns": 12, "rowHeight": 4}),
        created_by=user.id,
    )
    db.add(dashboard)
    await db.commit()
    await db.refresh(dashboard)
    return {
        "id": dashboard.id,
        "name": dashboard.name,
        "org_id": dashboard.org_id,
        "status": "created",
        "widgets": len(dashboard.widgets) if dashboard.widgets else 0,
    }


@router.get("/{dashboard_id}", tags=["dashboards-get"])
async def get_dashboard(
    dashboard_id: str,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(require_user),
) -> dict:
    """Get a single dashboard, enforcing tenant isolation."""
    stmt = select(Dashboard).where(
        (Dashboard.id == dashboard_id) & (Dashboard.org_id == user.org_id)
    )
    result = await db.execute(stmt)
    dashboard = result.scalar_one_or_none()
    if dashboard is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Dashboard not found")
    return {
        "id": dashboard.id,
        "name": dashboard.name,
        "org_id": dashboard.org_id,
        "widgets": dashboard.widgets or [],
        "layout": dashboard.layout or {},
        "created_at": dashboard.created_at.isoformat() if dashboard.created_at else None,
    }


@router.delete("/{dashboard_id}", status_code=HTTPStatus.NO_CONTENT, tags=["dashboards-delete"])
async def delete_dashboard(
    dashboard_id: str,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(require_user),
) -> None:
    """Delete a dashboard, enforcing tenant isolation."""
    stmt = delete(Dashboard).where(
        (Dashboard.id == dashboard_id) & (Dashboard.org_id == user.org_id)
    )
    result = await db.execute(stmt)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Dashboard not found")
    logger.info("Dashboard %s deleted by user %s", dashboard_id, user.id)
