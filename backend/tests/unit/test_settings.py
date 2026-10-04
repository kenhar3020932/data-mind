"""Unit tests for Pydantic settings validation."""

from __future__ import annotations

import os
import pytest

from app.core.settings import Settings


class TestSettings:
    """Test suite for settings validation."""

    def test_secret_key_min_length(self) -> None:
        with pytest.raises(Exception):  # pydantic validation error
            Settings(secret_key="short")

    def test_valid_secret_key(self) -> None:
        settings = Settings(secret_key="a" * 32)
        assert settings.secret_key == "a" * 32

    def test_default_values(self) -> None:
        settings = Settings(
            secret_key="a" * 32,
            database_url="postgresql+asyncpg://user:pass@host/db",
        )
        assert settings.app_name == "DataMind-King"
        assert settings.algorithm == "HS256"
        assert settings.access_token_expire_minutes == 30

    def test_invalid_database_url(self) -> None:
        with pytest.raises(Exception):
            Settings(secret_key="a" * 32, database_url="not-a-url")

    def test_anthropic_key_validation(self) -> None:
        with pytest.raises(Exception):
            Settings(secret_key="a" * 32, anthropic_api_key="invalid-key")

    def test_anthropic_key_accepted(self) -> None:
        settings = Settings(
            secret_key="a" * 32,
            anthropic_api_key="sk-ant-test1234567890abcdefghijklmnopqrstuvwxyz",
        )
        assert settings.anthropic_api_key.startswith("sk-ant-")

    def test_rate_limit_positive(self) -> None:
        settings = Settings(
            secret_key="a" * 32,
            rate_limit_requests=100,
            rate_limit_window_seconds=60,
        )
        assert settings.rate_limit_requests == 100
        assert settings.rate_limit_window_seconds == 60

    def test_sql_gate_defaults(self) -> None:
        settings = Settings(secret_key="a" * 32)
        assert settings.sql_gate_enabled is True
        assert settings.sql_max_query_length == 5000