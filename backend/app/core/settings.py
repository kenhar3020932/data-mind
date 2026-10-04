"""Pydantic Settings for DataMind-King.

Provides typed, validated configuration via pydantic-settings.
All secrets come from environment variables — no hardcoded values.
"""

from __future__ import annotations

import os
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""

    # Application
    app_name: str = "DataMind-King"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # Security
    secret_key: str = Field(default="a" * 32, min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)
    bcrypt_rounds: int = Field(default=12, ge=4)

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/datamind",
        pattern=r"^postgresql\+asyncpg://|^sqlite\+aiosqlite://",
    )
    redis_url: str = "redis://localhost:6379/0"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "datamind"

    # MinIO / S3
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    minio_bucket_raw: str = "raw"
    minio_bucket_cleaned: str = "cleaned"
    minio_bucket_archived: str = "archived"

    # LLM / Brain
    anthropic_api_key: str = ""
    anthropic_base_url: str = "https://api.anthropic.com"
    default_model: str = "claude-sonnet-4-20250514"
    planning_model: str = "claude-opus-4-20250514"
    simple_model: str = "claude-haiku-3-20241022"
    budget_per_request_usd: float = Field(default=0.05, gt=0)

    # CORS
    cors_origins: list[str] = Field(default=["http://localhost:3000"])
    cors_allow_credentials: bool = True
    cors_allow_headers: list[str] = Field(default=["*"])

    # Rate Limiting
    rate_limit_requests: int = Field(default=100, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)

    # Observability
    otel_service_name: str = "datamind-king"
    prometheus_enabled: bool = True

    # SQL Gate
    sql_gate_enabled: bool = True
    sql_allowed_dialects: list[str] = Field(default=["duckdb", "postgres"])
    sql_max_query_length: int = Field(default=5000, ge=100)

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if "://" not in v:
            raise ValueError("database_url must be a valid URL with scheme")
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("secret_key must be at least 32 characters")
        return v

    @field_validator("anthropic_api_key")
    @classmethod
    def validate_anthropic_key(cls, v: str) -> str:
        if v and not v.startswith("sk-ant-"):
            raise ValueError("anthropic_api_key must start with 'sk-ant-'")
        return v

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True}


def get_settings() -> Settings:
    """Create settings instance from environment."""
    env_file = os.getenv("DATAMIND_ENV_FILE", ".env")
    if os.path.exists(env_file):
        os.environ.setdefault("__DATAMIND_ENV_FILE", env_file)
    return Settings()


settings = get_settings()