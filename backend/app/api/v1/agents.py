"""Agent management routes for DataMind-King."""

from __future__ import annotations

from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.agent import Agent
from app.models.user import User

router = APIRouter(prefix="", tags=["agents"])


async def require_user(db: AsyncSession = Depends(get_db), user=None) -> User:
    """Placeholder dependency for user auth."""
    return user  # type: ignore[return-value]


@router.get("", tags=["agents-list"])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_user),
    active_only: bool = True,
) -> dict:
    """List available agents, filtered by active status."""
    stmt = select(Agent).where(Agent.is_active == active_only).order_by(Agent.name)
    result = await db.execute(stmt)
    agents = result.scalars().all()
    return {
        "items": [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "prompt_version": a.prompt_version,
                "model_tier": a.model_tier,
                "eval_accuracy": a.eval_accuracy,
            }
            for a in agents
        ],
        "total": len(agents),
    }


@router.get("/{agent_name}", tags=["agents-get"])
async def get_agent(
    agent_name: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_user),
) -> dict:
    """Get agent definition by name."""
    agent = (await db.execute(
        select(Agent).where(Agent.name == agent_name)
    )).scalar_one_or_none()
    if agent is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agent not found")
    return agent.__dict__
