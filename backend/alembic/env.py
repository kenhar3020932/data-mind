"""Alembic configuration for DataMind-King migrations."""

from __future__ import annotations

from alembic.config import Config
from sqlalchemy import engine_from_config, pool

from app.core.db import engine
from app.models.base import Base

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in '离线' mode."""
    url = settings.database_url
    config.set_main_option("sqlalchemy.url", url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    config = Config("backend/alembic.ini")
    config.set_main_option("sqlalchemy.url", engine.url)
    context.configure(
        connection=engine.sync_engine,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
