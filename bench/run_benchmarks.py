#!/usr/bin/env python3
"""Benchmark runner for DataMind-King performance testing.

Runs performance benchmarks across all agent types and reports metrics.
"""
from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class BenchmarkResult:
    """Result from a single benchmark run."""

    def __init__(
        self,
        name: str,
        duration_seconds: float,
        operations: int,
        throughput: float,
        memory_mb: float,
        success: bool,
        error: str | None = None,
    ) -> None:
        self.name = name
        self.duration_seconds = duration_seconds
        self.operations = operations
        self.throughput = throughput  # operations per second
        self.memory_mb = memory_mb
        self.success = success
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "duration_seconds": round(self.duration_seconds, 3),
            "operations": self.operations,
            "throughput_ops_per_sec": round(self.throughput, 2),
            "memory_mb": round(self.memory_mb, 2),
            "success": self.success,
            "error": self.error,
        }


class BenchmarkRunner:
    """Runs performance benchmarks and aggregates results."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or Path(__file__).parent / "results"
        self.results: list[BenchmarkResult] = []

    async def run_benchmark(
        self,
        name: str,
        benchmark_func,
        iterations: int = 100,
    ) -> BenchmarkResult:
        """Run a single benchmark with timing and memory tracking.

        Args:
            name: Benchmark identifier.
            benchmark_func: Async function to benchmark.
            iterations: Number of iterations to run.

        Returns:
            BenchmarkResult with metrics.
        """
        start_time = time.perf_counter()
        start_mem = self._get_memory_mb()

        success = True
        error = None

        for i in range(iterations):
            try:
                await benchmark_func(i)
            except Exception as exc:  # noqa: BLE001
                success = False
                error = str(exc)
                break

        end_time = time.perf_counter()
        end_mem = self._get_memory_mb()

        duration = end_time - start_time
        throughput = iterations / duration if duration > 0 else 0
        memory_delta = end_mem - start_mem

        result = BenchmarkResult(
            name=name,
            duration_seconds=duration,
            operations=iterations,
            throughput=throughput,
            memory_mb=memory_delta,
            success=success,
            error=error,
        )

        self.results.append(result)
        return result

    def _get_memory_mb(self) -> float:
        """Get current process memory usage in MB."""
        try:
            import resource
            # RSS (Resident Set Size) in bytes
            memory_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            # On Linux, ru_maxrss is in KB; on macOS, it's in bytes
            if memory_bytes > 1_000_000:  # Likely already in bytes
                return memory_bytes / (1024 * 1024)
            return memory_bytes / 1024  # Convert KB to MB
        except ImportError:
            return 0.0

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive benchmark report.

        Returns:
            Report dictionary with aggregated metrics.
        """
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        total_duration = sum(r.duration_seconds for r in self.results)
        total_operations = sum(r.operations for r in successful)

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_benchmarks": len(self.results),
            "passed": len(successful),
            "failed": len(failed),
            "total_duration_seconds": round(total_duration, 3),
            "total_operations": total_operations,
            "overall_throughput": round(
                total_operations / total_duration if total_duration > 0 else 0, 2
            ),
            "benchmarks": [r.to_dict() for r in self.results],
        }

        return report

    def save_report(self, filename: str | None = None) -> Path:
        """Save benchmark report to JSON file.

        Args:
            filename: Output filename (optional).

        Returns:
            Path to saved report.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_report_{timestamp}.json"

        report_path = self.output_dir / filename
        report = self.generate_report()

        report_path.write_text(json.dumps(report, indent=2))

        return report_path


async def benchmark_sql_agent(runner: BenchmarkRunner) -> None:
    """Benchmark SQL agent query execution."""
    from app.agents.sql.agent import SQLAgent
    from app.agents.base import TaskBrief

    agent = SQLAgent()
    brief = TaskBrief(
        task_id="bench-sql",
        org_id="test-org",
        context={"query": "SELECT 1"},
    )

    ack = await agent.acknowledge(brief)
    if ack.accepted:
        await runner.run_benchmark(
            "sql_agent_execute",
            lambda i: agent.execute(brief, ack),
            iterations=50,
        )


async def benchmark_data_quality_agent(runner: BenchmarkRunner) -> None:
    """Benchmark data quality profiling."""
    from app.agents.data_quality.agent import DataQualityAgent
    from app.agents.base import TaskBrief

    agent = DataQualityAgent()
    brief = TaskBrief(
        task_id="bench-dq",
        org_id="test-org",
        context={
            "dataset_id": "test_dataset",
            "profile_level": "quick",
        },
    )

    ack = await agent.acknowledge(brief)
    if ack.accepted:
        await runner.run_benchmark(
            "data_quality_profile",
            lambda i: agent.execute(brief, ack),
            iterations=50,
        )


async def main() -> None:
    """Run all benchmarks and generate report."""
    runner = BenchmarkRunner()

    print("=" * 60)
    print("DataMind-King Performance Benchmarks")
    print("=" * 60)
    print()

    # Run benchmarks
    await benchmark_sql_agent(runner)
    await benchmark_data_quality_agent(runner)

    # Generate and save report
    report_path = runner.save_report()
    report = runner.generate_report()

    print(f"\nBenchmarks Completed: {report['passed']}/{report['total_benchmarks']} passed")
    print(f"Total Duration: {report['total_duration_seconds']:.3f}s")
    print(f"Overall Throughput: {report['overall_throughput']:.2f} ops/sec")
    print(f"\nReport saved to: {report_path}")

    if report["failed"] > 0:
        print(f"\n⚠️  {report['failed']} benchmark(s) failed!")
        for r in runner.results:
            if not r.success:
                print(f"  - {r.name}: {r.error}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
