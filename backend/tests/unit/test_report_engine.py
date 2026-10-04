"""Unit tests for ReportEngine."""

from __future__ import annotations

import pytest

from app.services.report_engine import ReportEngine


class TestReportEngine:
    """Test suite for ReportEngine."""

    def setup_method(self) -> None:
        self.engine = ReportEngine()
        self.sample_data = {
            'confidence': 0.85,
            'duration_ms': 1500,
            'cost_usd': 0.05,
            'metrics': {
                'rows_processed': 1000,
                'columns': 10,
                'queries_executed': 5,
            },
            'results': [{'a': 1, 'b': 2}],
        }

    def test_generate_pdf(self) -> None:
        """Test PDF report generation."""
        content = self.engine.generate_pdf('job-123', self.sample_data)
        assert isinstance(content, bytes)
        assert b'DataMind-King Analysis Report' in content
        assert b'job-123' in content

    def test_generate_xlsx(self) -> None:
        """Test Excel report generation."""
        content = self.engine.generate_xlsx('job-123', self.sample_data)
        assert isinstance(content, bytes)
        assert len(content) > 0

    def test_generate_zip(self) -> None:
        """Test ZIP report generation."""
        content = self.engine.generate_zip('job-123', self.sample_data)
        assert isinstance(content, bytes)
        assert len(content) > 0

    def test_generate_pdf_format(self) -> None:
        """Test PDF format selection."""
        content, mime = self.engine.generate('job-123', 'pdf', self.sample_data)
        assert mime == 'application/pdf'
        assert isinstance(content, bytes)

    def test_generate_xlsx_format(self) -> None:
        """Test XLSX format selection."""
        content, mime = self.engine.generate('job-123', 'xlsx', self.sample_data)
        assert mime == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def test_generate_zip_format(self) -> None:
        """Test ZIP format selection."""
        content, mime = self.engine.generate('job-123', 'zip', self.sample_data)
        assert mime == 'application/zip'

    def test_generate_invalid_format(self) -> None:
        """Test invalid format raises error."""
        with pytest.raises(ValueError, match="Unsupported format"):
            self.engine.generate('job-123', 'invalid', self.sample_data)