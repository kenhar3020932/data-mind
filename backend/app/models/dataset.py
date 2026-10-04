"""Dataset model for DataMind-King."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, JSON, String, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Dataset(Base, TimestampMixin):
    """Dataset table tracking uploaded and ingested data assets."""
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    row_count: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    schema_: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    dialect: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)
