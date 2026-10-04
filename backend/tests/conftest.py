"""Shared test fixtures and configuration for DataMind-King tests."""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from pytest_mock import MockerFixture

# Add backend directory to Python path
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.agents.base import Acknowledgement, AgentResult, TaskBrief
from app.core.settings import Settings


# Override settings for testing
@pytest.fixture(autouse=True)
def override_settings() -> None:
    """Override settings with test values."""
    os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    os.environ.setdefault("SECRET_KEY", "test-secret-key-for-development-only")
    os.environ.setdefault("ANTHROPIC_API_KEY", "sk-test-key")
    os.environ.setdefault("MINIO_ENDPOINT", "localhost:9000")
    os.environ.setdefault("MINIO_ACCESS_KEY", "minioadmin")
    os.environ.setdefault("MINIO_SECRET_KEY", "minioadmin")


@pytest.fixture
def settings() -> Settings:
    """Provide test settings."""
    return Settings(
        database_url="postgresql+asyncpg://test:test@localhost:5432/test",
        redis_url="redis://localhost:6379/0",
        secret_key="test-secret-key",
        algorithm="HS256",
        access_token_expire_minutes=30,
    )


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide async HTTP client for testing."""
    from app.main import app  # noqa: PLC0415

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def client() -> AsyncGenerator[TestClient, None]:
    """Provide synchronous test client for API tests."""
    from app.main import app  # noqa: PLC0415
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_task_brief() -> TaskBrief:
    """Provide a sample task brief for testing."""
    return TaskBrief(
        task_id="test-task-001",
        org_id="test-org-001",
        context={
            "task": "Analyze sales data",
            "description": "Analyze sales trends",
            "size_bytes": 100 * 1024 * 1024,  # 100MB
        },
    )


@pytest.fixture
def sample_acknowledgement() -> Acknowledgement:
    """Provide a sample acknowledgement."""
    return Acknowledgement(
        task_id="test-task-001",
        agent_name="test_agent",
        accepted=True,
        estimated_duration_seconds=5.0,
        reason="Test acknowledgement",
    )


@pytest.fixture
def sample_agent_result() -> AgentResult:
    """Provide a sample agent result."""
    return AgentResult(
        task_id="test-task-001",
        success=True,
        output={"result": "success", "data": [1, 2, 3]},
        confidence=0.95,
        tokens_used=150,
        cost_usd=0.003,
        completed_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_llm_router(mocker: MockerFixture) -> MagicMock:
    """Mock LLM router for testing."""
    mock = mocker.patch("app.services.llm_service.LLMRouter")
    mock_instance = mock.return_value
    mock_instance.generate = AsyncMock(return_value='{"result": "test"}')
    return mock_instance


@pytest.fixture
def mock_sql_gate(mocker: MockerFixture) -> MagicMock:
    """Mock SQL gate for testing."""
    from app.core.sql_gate import SQLGate  # noqa: PLC0415

    mock = mocker.patch.object(SQLGate, "validate")
    mock.return_value.is_allowed = True
    mock.return_value.sanitized_query = "SELECT 1"
    return mock


@pytest.fixture
def mock_engine_service(mocker: MockerFixture) -> MagicMock:
    """Mock engine service for testing."""
    from app.services.engine_service import EngineService  # noqa: PLC0415

    mock = mocker.patch.object(EngineService, "execute")
    mock.return_value = {
        "rows": [],
        "columns": [],
        "row_count": 0,
        "engine": "duckdb",
    }
    return mock


@pytest.fixture
def mock_minio_client(mocker: MockerFixture) -> MagicMock:
    """Mock MinIO client for testing."""
    mock = mocker.patch("app.core.minio_service.minio_client")
    mock.list_buckets.return_value = []
    mock.make_bucket.return_value = None
    return mock


@pytest.fixture
def mock_redis(mocker: MockerFixture) -> MagicMock:
    """Mock Redis client for testing."""
    mock = mocker.MagicMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    mock.setex = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_database_session(mocker: MockerFixture) -> AsyncGenerator[MagicMock, None]:
    """Mock database session for testing."""
    from sqlalchemy.ext.asyncio import AsyncSession  # noqa: PLC0415

    mock_session = mocker.MagicMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(return_value=mocker.MagicMock())
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()

    yield mock_session


@pytest.fixture
def sample_user_data() -> dict:
    """Provide sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "org_id": "test-org-001",
    }


@pytest.fixture
def sample_dataset() -> dict:
    """Provide sample dataset metadata."""
    return {
        "id": "ds-test-001",
        "name": "Test Dataset",
        "org_id": "test-org-001",
        "file_type": "parquet",
        "size_bytes": 104857600,  # 100MB
        "row_count": 1000000,
        "status": "processed",
    }


@pytest.fixture
def sample_dashboard_config() -> dict:
    """Provide sample dashboard configuration."""
    return {
        "widgets": [
            {
                "type": "line",
                "title": "Sales Trend",
                "query": "SELECT date, SUM(revenue) FROM sales GROUP BY date",
            },
            {
                "type": "bar",
                "title": "Revenue by Region",
                "query": "SELECT region, SUM(revenue) FROM sales GROUP BY region",
            },
        ],
        "layout": [
            {"x": 0, "y": 0, "w": 12, "h": 6},
            {"x": 12, "y": 0, "w": 12, "h": 6},
        ],
    }


@pytest.fixture
def sample_security_finding() -> dict:
    """Provide sample security finding."""
    return {
        "severity": "medium",
        "confidence": 0.85,
        "description": "Hardcoded credential detected",
        "file_path": "backend/app/config.py",
        "line_number": 42,
        "code": "password = 'hardcoded_secret'",
        "remediation": "Use environment variables for secrets",
    }


@pytest.fixture
def sample_query_context() -> dict:
    """Provide sample query execution context."""
    return {
        "query": "SELECT * FROM users WHERE org_id = 'test-org-001'",
        "org_id": "test-org-001",
        "size_bytes": 50 * 1024 * 1024,  # 50MB
        "complexity": "simple",
        "limit": 1000,
    }


@pytest.fixture
def now() -> datetime:
    """Provide fixed timestamp for testing."""
    return datetime(2024, 10, 5, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_data_dir(tmp_path: pytest.TempPathFixture) -> str:
    """Create temporary test data directory."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    return str(data_dir)


@pytest.fixture
def mock_casbin_enforcer(mocker: MockerFixture) -> MagicMock:
    """Mock Casbin enforcer for RBAC testing."""
    mock = mocker.patch("app.core.rbac.Enforcer")
    mock_instance = mock.return_value
    mock_instance.enforce = MagicMock(return_value=True)
    return mock_instance


@pytest.fixture
def mock_totp_service(mocker: MockerFixture) -> MagicMock:
    """Mock TOTP service for 2FA testing."""
    mock = mocker.patch("app.core.totp.TOTPService")
    mock_instance = mock.return_value
    mock_instance.generate_secret.return_value = "JBSWY3DPEHPK3PXP"
    mock_instance.verify.return_value = True
    mock_instance.get_qr_code.return_value = b"fake_qr_code"
    return mock_instance
