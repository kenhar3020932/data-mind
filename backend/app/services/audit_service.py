"""Audit log service for DataMind-King."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.audit import AuditLog


async def create_audit_entry(
    db: AsyncSession,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    user_id: str | None = None,
    org_id: str | None = None,
    request_id: str | None = None,
    metadata_: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> AuditLog:
    """Create an audit log entry. Returns the persisted AuditLog."""
    entry = AuditLog(
        org_id=org_id or "",
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        request_id=request_id or "",
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def get_audit_logs(
    db: AsyncSession,
    org_id: str,
    user_id: str | None = None,
    action: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[AuditLog], int]:
    """Retrieve audit logs with filtering and pagination."""
    base = select(AuditLog).where(AuditLog.org_id == org_id)
    if user_id:
        base = base.where(AuditLog.user_id == user_id)
    if action:
        base = base.where(AuditLog.action == action)

    total_result = await db.execute(
        select(func.count()).select_from(base.subquery())
    )
    total: int = total_result.scalar_one()

    query = base.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    logs = list(result.scalars().all())

    return logs, total
