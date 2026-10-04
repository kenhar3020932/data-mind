"""Organization (tenant) model for DataMind-King."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Organization(Base, TimestampMixin):
    """Organization table for multi-tenant isolation."""
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    max_datasets: Mapped[int] = mapped_column(default=100, nullable=False)
    max_storage_gb: Mapped[int] = mapped_column(default=100, nullable=False)
