"""Agent registry model for DataMind-King."""

from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Agent(Base):
    """Agent definition table for the agent fleet."""
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    prompt_version: Mapped[str] = mapped_column(String(20), default="v1.0", nullable=False)
    model_tier: Mapped[str] = mapped_column(String(20), default="sonnet", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    tool_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    eval_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_eval_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    config_: Mapped[dict | None] = mapped_column(JSON, nullable=True)
