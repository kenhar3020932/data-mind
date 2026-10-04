"""Dagster orchestration for DataMind-King.

Defines pipelines for data ingestion, analysis, and report generation.
"""

from __future__ import annotations

from typing import Any

from dagster import job, op, repository, DailyTimezoneBaseSensorDefinition, FailureConfig


@op
def ingest_dataset(dataset_id: str, org_id: str) -> dict[str, Any]:
    """Ingest a dataset from MinIO."""
    # In production: call ingest_service.ingest()
    return {
        "dataset_id": dataset_id,
        "org_id": org_id,
        "status": "ingested",
        "row_count": 1000,
    }


@op
def profile_dataset(dataset_id: str) -> dict[str, Any]:
    """Profile a dataset for quality metrics."""
    # In production: call data_quality_agent
    return {
        "dataset_id": dataset_id,
        "completeness": 0.95,
        "uniqueness": 0.98,
        "issues_found": 3,
    }


@op
def run_analysis(dataset_id: str, query: str) -> dict[str, Any]:
    """Run analysis on a dataset."""
    # In production: call brain controller
    return {
        "dataset_id": dataset_id,
        "query": query,
        "result": {"insights": ["Trend detected"]},
        "confidence": 0.87,
    }


@op
def generate_report(job_id: str, fmt: str) -> dict[str, Any]:
    """Generate a report in specified format."""
    # In production: call report_engine.generate()
    return {
        "job_id": job_id,
        "format": fmt,
        "url": f"/reports/{job_id}.{fmt}",
    }


@job
def ingestion_pipeline() -> None:
    """Pipeline for data ingestion and profiling."""
    result = ingest_dataset("ds-123", "org-1")
    profiled = profile_dataset(result["dataset_id"])
    return profiled


@job
def analysis_pipeline(dataset_id: str, query: str) -> dict[str, Any]:
    """Pipeline for running analysis on a dataset."""
    result = run_analysis(dataset_id, query)
    report = generate_report("job-1", "pdf")
    return {"result": result, "report": report}


def create_daily_sensor() -> DailyTimezoneBaseSensorDefinition:
    """Create a daily sensor for scheduled pipelines."""
    return DailyTimezoneBaseSensorDefinition(
        name="daily_ingestion_sensor",
        job=ingestion_pipeline,
        cron_schedule="0 2 * * *",  # Run at 2 AM daily
    )


def get_repository() -> Any:
    """Get Dagster repository definition."""
    return repository(
        name="datamind_king",
        jobs=[ingestion_pipeline, analysis_pipeline],
        sensors=[create_daily_sensor()],
    )