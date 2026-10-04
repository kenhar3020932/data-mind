"""Security Agent Schemas for DataMind-King - Ultra God Mode Edition.

Defines structured schemas for security findings, scan inputs,
and comprehensive audit outputs with CWE mapping and remediation tracking.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class SecurityFinding(BaseModel):
    """A single security finding with Ultra God Mode details."""
    finding_id: str = Field(default_factory=lambda: f"find-{uuid.uuid4().hex[:8]}")
    
    # Core Details
    severity: Literal["critical", "high", "medium", "low", "info"] = Field(..., description="Severity level")
    category: Literal[
        "sql_injection", "xss", "ssrf", "hardcoded_secret", "auth_bypass", 
        "weak_crypto", "tenant_isolation_violation", "prompt_injection_risk",
        "dependency_vulnerability", "misconfiguration", "general_vulnerability"
    ] = Field(..., description="Vulnerability category")
    
    title: str = Field(..., min_length=1, max_length=200, description="Short title of the finding")
    description: str = Field(..., min_length=1, max_length=2000, description="Detailed description")
    
    # Location & Context
    file_path: str | None = Field(None, description="Path to the affected file")
    line_number: int | None = Field(None, ge=1, description="Line number in the file")
    code_snippet: str | None = Field(None, max_length=500, description="Relevant code snippet")
    
    # Standards & Compliance
    cwe_id: str | None = Field(None, pattern=r"^CWE-\d+$", description="Common Weakness Enumeration ID")
    owasp_top_10: str | None = Field(None, description="Related OWASP Top 10 category")
    
    # Remediation
    remediation: str = Field(..., min_length=1, max_length=1000, description="How to fix this issue")
    auto_fixable: bool = Field(default=False, description="Can this be fixed automatically?")
    
    # Metadata
    scanner_source: str = Field(..., description="Which scanner found this (e.g., bandit, semgrep)")
    confidence_in_finding: float = Field(ge=0.0, le=1.0, default=0.9, description="Scanner's confidence")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ScanScope(BaseModel):
    """Defines what to scan."""
    target_path: str = Field(..., min_length=1, description="Path to file or directory")
    include_sast: bool = Field(default=True, description="Static Application Security Testing")
    include_sca: bool = Field(default=True, description="Software Composition Analysis")
    include_secrets: bool = Field(default=True, description="Secrets detection (gitleaks)")
    include_custom_checks: bool = Field(default=True, description="Tenant isolation & prompt injection checks")
    excluded_paths: list[str] = Field(default_factory=list, description="Paths to ignore")


class SecurityScanInput(BaseModel):
    """Input schema for Security Audit Agent - Ultra God Mode Edition."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    org_id: str = Field(..., min_length=1, max_length=36, description="Tenant ID")
    
    # Scope
    scope: ScanScope
    
    # Configuration
    fail_on_severity: Literal["critical", "high", "medium", "low"] = Field(
        default="high", 
        description="Fail the scan if findings of this severity or higher are found"
    )
    max_findings_limit: int = Field(default=1000, ge=1, le=10000, description="Stop after this many findings")
    
    # Audit
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SeveritySummary(BaseModel):
    """Aggregated counts by severity."""
    critical: int = Field(ge=0, default=0)
    high: int = Field(ge=0, default=0)
    medium: int = Field(ge=0, default=0)
    low: int = Field(ge=0, default=0)
    info: int = Field(ge=0, default=0)
    total: int = Field(ge=0, default=0)

    @model_validator(mode="after")
    def calculate_total(self) -> "SeveritySummary":
        self.total = self.critical + self.high + self.medium + self.low + self.info
        return self


class ScannerStatus(BaseModel):
    """Status of an individual scanner."""
    scanner_name: str
    status: Literal["success", "error", "timeout", "missing"]
    findings_count: int = 0
    error_message: str | None = None
    duration_ms: float = 0.0


class SecurityScanOutput(BaseModel):
    """Output schema for Security Audit Agent - Ultra God Mode Edition."""
    success: bool
    task_id: str
    
    # Results
    findings: list[SecurityFinding] = Field(default_factory=list)
    severity_summary: SeveritySummary = Field(default_factory=SeveritySummary)
    
    # Risk Assessment
    overall_risk_level: Literal["critical", "high", "medium", "low", "safe"] = Field(default="safe")
    recommendation: str | None = None
    
    # Performance & Metrics
    scan_duration_ms: float = Field(ge=0.0, default=0.0)
    scanners_run: list[ScannerStatus] = Field(default_factory=list)
    files_scanned: int = 0
    lines_of_code_scanned: int = 0
    
    # Quality
    confidence: float = Field(ge=0.0, le=1.0, description="Evidence-based confidence in the audit")
    
    # Error Handling
    error: str | None = None
    partial_results: bool = False
    
    # Audit
    completed_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("severity_summary", mode="before")
    @classmethod
    def sync_severity_summary(cls, v: Any, info: Any) -> SeveritySummary:
        """Auto-calculate severity summary from findings."""
        findings = info.data.get("findings", [])
        if not findings and isinstance(v, dict):
            return SeveritySummary(**v)
        
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for f in findings:
            sev = f.severity if hasattr(f, 'severity') else f.get('severity', 'info')
            if sev in counts:
                counts[sev] += 1
        
        return SeveritySummary(**counts)

    @field_validator("overall_risk_level", mode="before")
    @classmethod
    def determine_risk_level(cls, v: Any, info: Any) -> str:
        """Auto-determine risk level based on findings."""
        summary = info.data.get("severity_summary")
        if not summary:
            return "safe"
        
        if hasattr(summary, 'critical'):
            if summary.critical > 0: return "critical"
            if summary.high > 2: return "high"
            if summary.high > 0 or summary.medium > 5: return "medium"
            if summary.low > 0: return "low"
        return "safe"
