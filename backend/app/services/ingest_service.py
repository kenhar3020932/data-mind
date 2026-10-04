"""Data ingestion and normalization service for DataMind-King."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from ..services.minio_service import MinIOService, get_dataset_path

minio = MinIOService()


@dataclass
class DatasetProfile:
    """Profile of a dataset after ingestion."""
    row_count: int
    column_count: int
    column_names: list[str]
    column_types: dict[str, str]
    file_size_bytes: int
    checksum: str
    ingestion_time_ms: float


class IngestService:
    """Handle data ingestion and normalization to Parquet."""

    async def ingest(
        self,
        org_id: str,
        dataset_id: str,
        source_path: str,
        file_size_bytes: int,
    ) -> DatasetProfile:
        """Ingest data from source and normalize to Parquet."""
        start_time = datetime.now(timezone.utc)

        # Read source data (CSV, JSON, Excel, etc.)
        # In production: detect format and use appropriate parser
        import pandas as pd
        df = self._read_source(source_path)

        # Generate Parquet schema
        schema = pa.Schema.from_pandas(df)

        # Write to MinIO as Parquet
        parquet_path = get_dataset_path(org_id, dataset_id, "normalized.parquet")

        table = pa.Table.from_pandas(df, schema=schema)
        parquet_buffer = pq.BytesIO()
        pq.write_table(table, parquet_buffer)
        parquet_bytes = parquet_buffer.getvalue()

        minio.upload_stream(
            bucket="cleaned",
            object_name=parquet_path,
            data=parquet_bytes,
            mime_type="application/vnd.apache.parquet",
        )

        # Compute checksum
        checksum = hashlib.sha256(parquet_bytes).hexdigest()

        # Build profile
        profile = DatasetProfile(
            row_count=len(df),
            column_count=len(df.columns),
            column_names=list(df.columns),
            column_types={col: str(df[col].dtype) for col in df.columns},
            file_size_bytes=len(parquet_bytes),
            checksum=checksum,
            ingestion_time_ms=(datetime.now(timezone.utc) - start_time).total_seconds() * 1000,
        )

        return profile

    def _read_source(self, path: str) -> Any:
        """Read source data from various formats."""
        import pandas as pd

        if path.endswith(".csv"):
            return pd.read_csv(path)
        elif path.endswith(".json"):
            return pd.read_json(path)
        elif path.endswith((".xlsx", ".xls")):
            return pd.read_excel(path)
        elif path.endswith(".parquet"):
            return pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported file format: {path}")


# Module-level singleton
service = IngestService()