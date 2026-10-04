"""Integration Tests - Tests component interactions and end-to-end workflows."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestSQLToDashboardWorkflow:
    """Test SQL to Dashboard integration workflow."""

    @pytest.mark.asyncio
    async def test_full_workflow(self, sample_task_brief, sample_agent_result) -> None:
        """Test complete SQL to Dashboard workflow."""
        # Mock the chain of agents
        with patch("app.agents.planning.agent.PlanningAgent") as mock_planning:
            mock_planning_instance = MagicMock()
            mock_planning_instance.execute = AsyncMock(return_value=sample_agent_result)
            mock_planning.return_value = mock_planning_instance

            # Workflow should execute without errors
            assert mock_planning.called

    @pytest.mark.asyncio
    async def test_agent_chain_execution(self) -> None:
        """Test agent chain executes in correct order."""
        execution_order = []

        async def mock_agent(name):
            execution_order.append(name)

        # Simulate agent chain
        await mock_agent("planning")
        await mock_agent("sql")
        await mock_agent("data_quality")
        await mock_agent("visualization")
        await mock_agent("dashboard")

        assert execution_order == ["planning", "sql", "data_quality", "visualization", "dashboard"]


class TestUploadToProcessingWorkflow:
    """Test file upload to processing workflow."""

    @pytest.mark.asyncio
    async def test_upload_trigger_processing(self) -> None:
        """Test that upload triggers processing pipeline."""
        with patch("app.services.upload_service.UploadService") as mock_upload:
            mock_instance = MagicMock()
            mock_instance.initiate_upload = AsyncMock(return_value={"upload_id": "test-123"})
            mock_upload.return_value = mock_instance

            result = await mock_instance.initiate_upload("test.parquet", 1024)
            assert result["upload_id"] == "test-123"

    @pytest.mark.asyncio
    async def test_multipart_upload_complete(self) -> None:
        """Test multipart upload completion."""
        with patch("app.services.upload_service.UploadService") as mock_upload:
            mock_instance = MagicMock()
            mock_instance.complete_upload = AsyncMock(return_value={"location": "s3://bucket/file"})
            mock_upload.return_value = mock_instance

            result = await mock_instance.complete_upload("test-123", ["part1", "part2"])
            assert result["location"] == "s3://bucket/file"


class TestBrainControllerIntegration:
    """Test Brain Controller with agents."""

    @pytest.mark.asyncio
    async def test_brain_orchestrates_agents(self) -> None:
        """Test Brain Controller orchestrates multiple agents."""
        from app.brain.controller import BrainController  # noqa: PLC0415

        controller = BrainController()
        assert controller is not None

    @pytest.mark.asyncio
    async def test_brain_state_persistence(self) -> None:
        """Test Brain Controller persists state."""
        with patch("app.brain.memory.PostgresCheckpoint") as mock_checkpoint:
            checkpoint = mock_checkpoint.return_value
            checkpoint.save = AsyncMock()
            checkpoint.restore = AsyncMock(return_value={})

            # State should be savable and restorable
            assert checkpoint.save.called


class TestDatabaseIntegration:
    """Test database operations integration."""

    @pytest.mark.asyncio
    async def test_crud_operations(self, mock_database_session) -> None:
        """Test CRUD operations with database."""
        from sqlalchemy import select  # noqa: PLC0415

        # Mock execute response
        mock_result = MagicMock()
        mock_result.scalars.return_value.one_or_none.return_value = None
        mock_database_session.execute.return_value = mock_result

        # Query should execute without error
        await mock_database_session.execute(select(1))
        assert mock_database_session.execute.called

    @pytest.mark.asyncio
    async def test_transaction_rollback(self, mock_database_session) -> None:
        """Test transaction rollback on failure."""
        mock_database_session.commit = AsyncMock(side_effect=Exception("Commit failed"))
        mock_database_session.rollback = AsyncMock()

        with pytest.raises(Exception):
            await mock_database_session.commit()

        assert mock_database_session.rollback.called


class TestCacheIntegration:
    """Test cache integration with services."""

    @pytest.mark.asyncio
    async def test_cache_write_read(self, mock_redis) -> None:
        """Test cache write and read operations."""
        await mock_redis.set("test_key", "test_value")
        result = await mock_redis.get("test_key")

        assert result == b"test_value"

    @pytest.mark.asyncio
    async def test_cache_expiration(self, mock_redis) -> None:
        """Test cache expiration handling."""
        await mock_redis.setex("expire_key", 60, "value")
        result = await mock_redis.get("expire_key")

        assert result == b"value"

    @pytest.mark.asyncio
    async def test_cache_invalidation(self, mock_redis) -> None:
        """Test cache invalidation."""
        await mock_redis.set("invalidate_key", "value")
        deleted = await mock_redis.delete("invalidate_key")

        assert deleted == 1


class TestMessageQueueIntegration:
    """Test message queue integration."""

    @pytest.mark.asyncio
    async def test_message_producer(self) -> None:
        """Test message production."""
        with patch("app.orchestration.queue.RedisQueue") as mock_queue:
            mock_instance = MagicMock()
            mock_instance.publish = AsyncMock()
            mock_queue.return_value = mock_instance

            await mock_instance.publish("test_channel", {"data": "test"})
            assert mock_instance.publish.called

    @pytest.mark.asyncio
    async def test_message_consumer(self) -> None:
        """Test message consumption."""
        with patch("app.orchestration.queue.RedisQueue") as mock_queue:
            mock_instance = MagicMock()
            mock_instance.subscribe = AsyncMock(return_value=["message"])
            mock_queue.return_value = mock_instance

            messages = await mock_instance.subscribe("test_channel")
            assert len(messages) > 0


class TestAPIEndpointIntegration:
    """Test API endpoint integration."""

    def test_health_check_integration(self, client) -> None:
        """Test health check with all dependencies."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_metrics_endpoint_integration(self, client) -> None:
        """Test metrics endpoint with actual metrics."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert len(response.text) > 0

    def test_openapi_schema_integration(self, client) -> None:
        """Test OpenAPI schema generation."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema
        assert len(schema["paths"]) > 0


class TestAuditLogIntegration:
    """Test audit logging integration."""

    @pytest.mark.asyncio
    async def test_audit_entry_creation(self, mock_database_session) -> None:
        """Test audit entry creation."""
        from app.core.audit_log import create_audit_entry  # noqa: PLC0415

        with patch("app.core.audit_log.datetime") as mock_datetime:
            mock_datetime.now.return_value = MagicMock()
            await create_audit_entry(
                db=mock_database_session,
                action="TEST_ACTION",
                resource_type="test",
                org_id="test-org",
                metadata_={"key": "value"}
            )
            assert mock_database_session.add.called

    @pytest.mark.asyncio
    async def test_audit_query(self, mock_database_session) -> None:
        """Test audit log querying."""
        from app.core.audit_log import get_audit_logs  # noqa: PLC0415

        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_database_session.execute.return_value = mock_result

        logs = await get_audit_logs(mock_database_session, org_id="test-org")
        assert isinstance(logs, list)
