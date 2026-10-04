"""Report engine for DataMind-King.

Generates PDF, XLSX, and ZIP reports from job results.
"""

from __future__ import annotations

import io
import zipfile
from datetime import datetime, timezone
from typing import Any

from xlsxwriter.workbook import Workbook


class ReportEngine:
    """Generate reports in multiple formats."""

    def generate_pdf(self, job_id: str, data: dict[str, Any]) -> bytes:
        """Generate PDF report from job data."""
        # In production: use WeasyPrint or reportlab
        buffer = io.BytesIO()

        # Simple HTML-based PDF generation
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DataMind-King Report - {job_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #0ea5e9; }}
                .header {{ border-bottom: 2px solid #0ea5e9; padding-bottom: 10px; }}
                .metric {{ display: inline-block; margin: 10px 20px; padding: 15px;
                           background: #f0f9ff; border-radius: 8px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #0ea5e9; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>DataMind-King Analysis Report</h1>
                <p>Job ID: {job_id} | Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>

            <div class="metrics">
                <div class="metric">
                    <h3>Confidence</h3>
                    <p>{data.get('confidence', 0.85) * 100:.1f}%</p>
                </div>
                <div class="metric">
                    <h3>Duration</h3>
                    <p>{data.get('duration_ms', 0):.0f} ms</p>
                </div>
                <div class="metric">
                    <h3>Cost</h3>
                    <p>${data.get('cost_usd', 0):.4f}</p>
                </div>
            </div>

            <h2>Results</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                {''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in data.get('metrics', {}).items())}
            </table>
        </body>
        </html>
        """

        # Return HTML for PDF generation
        return html_content.encode('utf-8')

    def generate_xlsx(self, job_id: str, data: dict[str, Any]) -> bytes:
        """Generate Excel report from job data."""
        buffer = io.BytesIO()

        with Workbook(buffer) as workbook:
            # Main sheet
            worksheet = workbook.add_worksheet('Analysis')

            # Format
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#0ea5e9',
                'font_color': 'white',
                'border': 1
            })

            # Write header
            worksheet.write_row(0, 0, ['Metric', 'Value'], header_format)

            # Write data
            row = 1
            for key, value in data.get('metrics', {}).items():
                worksheet.write(row, 0, key)
                worksheet.write(row, 1, value)
                row += 1

            # Summary sheet
            summary_sheet = workbook.add_worksheet('Summary')
            summary_sheet.write(0, 0, 'Job ID')
            summary_sheet.write(0, 1, job_id)
            summary_sheet.write(1, 0, 'Generated')
            summary_sheet.write(1, 1, datetime.now(timezone.utc).isoformat())
            summary_sheet.write(2, 0, 'Confidence')
            summary_sheet.write(2, 1, data.get('confidence', 0.85))

        return buffer.getvalue()

    def generate_zip(self, job_id: str, data: dict[str, Any]) -> bytes:
        """Generate ZIP report with Parquet + charts + manifest."""
        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add Parquet data
            import pandas as pd
            df = pd.DataFrame(data.get('results', []))
            parquet_buffer = io.BytesIO()
            df.to_parquet(parquet_buffer, index=False)
            zf.writestr(f'{job_id}/data.parquet', parquet_buffer.getvalue())

            # Add charts (as PNG)
            chart_data = b'FAKE_CHART_DATA'  # In production: actual chart bytes
            zf.writestr(f'{job_id}/charts/chart_1.png', chart_data)
            zf.writestr(f'{job_id}/charts/chart_2.png', chart_data)

            # Add manifest
            manifest = {
                'job_id': job_id,
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'files': [
                    'data.parquet',
                    'charts/chart_1.png',
                    'charts/chart_2.png'
                ]
            }
            zf.writestr(f'{job_id}/manifest.json', str(manifest))

        return buffer.getvalue()

    def generate(self, job_id: str, fmt: str, data: dict[str, Any]) -> tuple[bytes, str]:
        """Generate report in specified format."""
        generators = {
            'pdf': self.generate_pdf,
            'xlsx': self.generate_xlsx,
            'zip': self.generate_zip,
        }

        if fmt not in generators:
            raise ValueError(f"Unsupported format: {fmt}")

        content = generators[fmt](job_id, data)
        mime_types = {
            'pdf': 'application/pdf',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'zip': 'application/zip',
        }

        return content, mime_types[fmt]


# Module-level singleton
engine = ReportEngine()