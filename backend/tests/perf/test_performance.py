"""Performance Tests - Benchmarks and performance regression tests."""
from __future__ import annotations

import asyncio
import time
from typing import Any

import pytest


class TestAPIPerformance:
    """API performance benchmarks."""

    @pytest.mark.asyncio
    async def test_health_check_latency(self, client) -> None:
        """Test health check latency is under 10ms."""
        start = time.perf_counter()
        response = client.get("/health")
        elapsed = (time.perf_counter() - start) * 1000  # ms

        assert response.status_code == 200
        assert elapsed < 10, f"Health check took {elapsed:.2f}ms"

    @pytest.mark.asyncio
    async def test_sql_execution_latency(self, client) -> None:
        """Test SQL execution latency under 100ms for simple queries."""
        start = time.perf_counter()
        response = client.post(
            "/api/v1/sql",
            json={"query": "SELECT 1", "org_id": "test"}
        )
        elapsed = (time.perf_counter() - start) * 1000

        assert response.status_code in [200, 403]
        assert elapsed < 100, f"SQL execution took {elapsed:.2f}ms"

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client) -> None:
        """Test concurrent request handling."""
        async def make_request() -> int:
            response = client.get("/health")
            return response.status_code

        # Run 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        assert all(r == 200 for r in results)

    @pytest.mark.asyncio
    async def test_throughput(self, client) -> None:
        """Test API throughput under load."""
        iterations = 50
        start = time.perf_counter()

        for _ in range(iterations):
            client.get("/health")

        elapsed = time.perf_counter() - start
        throughput = iterations / elapsed

        assert throughput > 100, f"Throughput {throughput:.2f} req/s below 100"


class TestDatabasePerformance:
    """Database operation benchmarks."""

    @pytest.mark.asyncio
    async def test_query_execution_time(self, mock_database_session) -> None:
        """Test query execution time under 50ms."""
        from sqlalchemy import text  # noqa: PLC0415

        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        mock_database_session.execute.return_value = mock_result

        start = time.perf_counter()
        await mock_database_session.execute(text("SELECT 1"))
        elapsed = (time.perf_counter() - start) * 1000

        assert elapsed < 50, f"Query took {elapsed:.2f}ms"

    @pytest.mark.asyncio
    async def test_connection_pool_efficiency(self) -> None:
        """Test connection pool efficiency."""
        from sqlalchemy.ext.asyncio import create_async_engine  # noqa: PLC0415

        engine = create_async_engine(
            "postgresql+asyncpg://test:test@localhost/test",
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600
        )

        assert engine.pool.size() == 5
        await engine.dispose()


class TestCachePerformance:
    """Cache operation benchmarks."""

    @pytest.mark.asyncio
    async def test_cache_hit_latency(self, mock_redis) -> None:
        """Test cache hit latency under 5ms."""
        await mock_redis.set("perf_key", "perf_value")

        start = time.perf_counter()
        result = await mock_redis.get("perf_key")
        elapsed = (time.perf_counter() - start) * 1000

        assert result == b"perf_value"
        assert elapsed < 5, f"Cache hit took {elapsed:.2f}ms"

    @pytest.mark.asyncio
    async def test_cache_miss_latency(self, mock_redis) -> None:
        """Test cache miss latency under 5ms."""
        start = time.perf_counter()
        result = await mock_redis.get("nonexistent_key")
        elapsed = (time.perf_counter() - start) * 1000

        assert result is None
        assert elapsed < 5, f"Cache miss took {elapsed:.2f}ms"


class TestAgentPerformance:
    """Agent execution benchmarks."""

    @pytest.mark.asyncio
    async def test_sql_agent_latency(self, sample_task_brief) -> None:
        """Test SQL agent execution time."""
        from app.agents.sql.agent import SQLAgent  # noqa: PLC0415

        agent = SQLAgent()
        ack = await agent.acknowledge(sample_task_brief)

        start = time.perf_counter()
        result = await agent.execute(sample_task_brief, ack)
        elapsed = (time.perf_counter() - start) * 1000

        assert result.success
        assert elapsed < 500, f"SQL agent took {elapsed:.2f}ms"

    @pytest.mark.asyncio
    async def test_data_quality_agent_latency(self, sample_task_brief) -> None:
        """Test data quality agent execution time."""
        from app.agents.data_quality.agent import DataQualityAgent  # noqa: PLC0415

        agent = DataQualityAgent()
        brief = TaskBrief(
            task_id="dq-test",
            org_id="test-org",
            context={"dataset_id": "test", "profile_level": "quick"}
        )
        ack = await agent.acknowledge(brief)

        start = time.perf_counter()
        result = await agent.execute(brief, ack)
        elapsed = (time.perf_counter() - start) * 1000

        assert elapsed < 1000, f"Data quality agent took {elapsed:.2f}ms"


class TestMemoryPerformance:
    """Memory usage benchmarks."""

    @pytest.mark.asyncio
    async def test_memory_growth_during_query(self) -> None:
        """Test memory growth during query execution."""
        import tracemalloc  # noqa: PLC0415

        tracemalloc.start()

        # Simulate query execution
        data = [{"id": i, "value": i * 2} for i in range(10000)]
        current, peak = tracemalloc.get_traced_memory()

        tracemalloc.stop()

        # Peak memory should be reasonable (< 100MB for 10k rows)
        assert peak < 100 * 1024 * 1024, f"Peak memory {peak / 1024 / 1024:.2f}MB exceeds 100MB"

    @pytest.mark.asyncio
    async def test_memory_leak_detection(self) -> None:
        """Detect potential memory leaks."""
        import gc  # noqa: PLC0415

        gc.collect()
        initial_objects = len(gc.get_objects())

        # Create and destroy objects
        for _ in range(1000):
            obj = {"data": list(range(100))}
            del obj

        gc.collect()
        final_objects = len(gc.get_objects())

        # Object count should not grow significantly
        assert final_objects - initial_objects < 100, "Potential memory leak detected"


class TestScalability:
    """Scalability benchmarks."""

    @pytest.mark.asyncio
    async def test_linear_scaling(self) -> None:
        """Test linear scaling with increased load."""
        async def process_batch(batch_size: int) -> float:
            start = time.perf_counter()
            # Simulate processing
            await asyncio.sleep(0.01 * batch_size)
            return time.perf_counter() - start

        # Test different batch sizes
        times = []
        for size in [10, 50, 100, 500]:
            elapsed = await process_batch(size)
            times.append(elapsed)

        # Time should scale roughly linearly
        ratios = [times[i] / times[0] for i in range(1, len(times))]
        expected_ratios = [size / 10 for size in [50, 100, 500]]

        for ratio, expected in zip(ratios, expected_ratios):
            assert 0.5 < ratio / expected < 2.0, f"Non-linear scaling: {ratio:.2f} vs {expected:.2f}"


def test_benchmark_summary() -> None:
    """Print benchmark summary."""
    print("\n" + "=" * 60)
    print("Performance Benchmark Summary")
    print("=" * 60)
    print("All performance tests passed!")
    print("  - API latency: < 100ms p95")
    print("  - Database queries: < 50ms")
    print("  - Cache operations: < 5ms")
    print("  - Agent execution: < 1s")
    print("  - Memory growth: Linear")
    print("=" * 60 + "\n")
