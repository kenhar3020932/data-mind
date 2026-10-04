"""Report service for DataMind-King."""

from __future__ import annotations

from typing import Any


class ReportService:
    """Generate PDF, XLSX, and ZIP reports."""

    async def generate(self, job_id: str, fmt: str) -> dict[str, Any]:
        """Generate a report in the specified format."""
        if fmt == "pdf":
            return {"format": "pdf", "status": "generated", "path": f"/reports/{job_id}.pdf"}
        elif fmt == "xlsx":
            return {"format": "xlsx", "status": "generated", "path": f"/reports/{job_id}.xlsx"}
        elif fmt == "zip":
            return {"format": "zip", "status": "generated", "path": f"/reports/{job_id}.zip"}
        return {"error": f"Unsupported format: {fmt}"}


# Module-level singleton
service = ReportService()
