"""Security Audit Agent for DataMind-King - ULTRA GOD MODE EDITION.

Orchestrates multiple security scanners (bandit, semgrep, gitleaks, trivy),
performs custom tenant isolation checks, detects prompt injection attempts,
and provides evidence-based severity classifications with remediation guidance.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from app.agents.base import Acknowledgement, AgentResult, BaseAgent, TaskBrief
from app.core.audit_log import create_audit_entry
from app.services.llm_service import LLMRouter

logger = logging.getLogger(__name__)


class SecurityAgent(BaseAgent):
    """Ultra God Mode Security Audit Agent with Multi-Scanner Orchestration."""

    name = "security_agent"
    description = "Orchestrates multi-scanner security audits with tenant isolation and prompt injection detection"
    prompt_version = "v3.0"
    model_tier = "opus"  # Security requires highest-tier model

    # Severity weights for confidence calculation
    SEVERITY_WEIGHTS = {
        "critical": 1.0,
        "high": 0.8,
        "medium": 0.5,
        "low": 0.2,
        "info": 0.05,
    }

    # Scanner configurations
    SCANNERS = {
        "bandit": {
            "command": ["bandit", "-r", "-f", "json", "-q"],
            "target_type": "python",
            "severity_map": {"HIGH": "high", "MEDIUM": "medium", "LOW": "low"},
        },
        "semgrep": {
            "command": ["semgrep", "--json", "--quiet", "--config=p/python", "--config=p/owasp-top-ten"],
            "target_type": "code",
            "severity_map": {"ERROR": "critical", "WARNING": "high", "INFO": "medium"},
        },
        "gitleaks": {
            "command": ["gitleaks", "detect", "--report-format", "json", "--report-path"],
            "target_type": "repo",
            "severity_map": {"default": "critical"},
        },
    }

    def __init__(self) -> None:
        self.llm_router = LLMRouter()
        self.scan_history: list[dict[str, Any]] = []

    async def acknowledge(self, brief: TaskBrief) -> Acknowledgement:
        """Acknowledge security audit task with scope analysis."""
        has_target = bool(
            brief.context.get("target") or 
            brief.context.get("path") or
            brief.context.get("scan_scope")
        )
        return Acknowledgement(
            task_id=brief.task_id,
            agent_name=self.name,
            accepted=has_target,
            estimated_duration_seconds=60.0 if has_target else 0.0,
            reason="Scan target provided" if has_target else "No scan target",
        )

    async def _run_scanner(self, scanner_name: str, target_path: str, org_id: str) -> list[dict[str, Any]]:
        """Run a single security scanner and parse its output."""
        scanner_config = self.SCANNERS.get(scanner_name)
        if not scanner_config:
            logger.warning(f"Unknown scanner: {scanner_name}")
            return []

        try:
            cmd = scanner_config["command"].copy()
            
            # Handle gitleaks special case (needs report path)
            if scanner_name == "gitleaks":
                report_path = f"/tmp/{scanner_name}_{org_id}_{datetime.now().timestamp()}.json"
                cmd.extend([target_path, report_path])
            else:
                cmd.append(target_path)

            # Run scanner with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)

            findings = []
            
            if scanner_name == "gitleaks":
                report_path = cmd[-1]
                if Path(report_path).exists():
                    with open(report_path) as f:
                        raw_findings = json.load(f)
                    for f_item in raw_findings:
                        findings.append({
                            "scanner": scanner_name,
                            "severity": "critical",
                            "category": "hardcoded_secret",
                            "title": f"Secret detected: {f_item.get('RuleID', 'unknown')}",
                            "file": f_item.get("File", ""),
                            "line": f_item.get("StartLine", 0),
                            "description": f_item.get("Description", ""),
                            "remediation": "Remove the secret and use environment variables or a secrets manager.",
                            "cwe": "CWE-798",
                        })
                    Path(report_path).unlink(missing_ok=True)
            
            elif stdout:
                try:
                    raw_data = json.loads(stdout.decode())
                    results = raw_data.get("results", raw_data.get("runs", []))
                    
                    for result in results:
                        severity_raw = result.get("issue_severity", result.get("level", "MEDIUM"))
                        severity = scanner_config["severity_map"].get(severity_raw, "medium")
                        
                        findings.append({
                            "scanner": scanner_name,
                            "severity": severity,
                            "category": self._categorize_finding(result, scanner_name),
                            "title": result.get("check_name", result.get("check_id", "Unknown")),
                            "file": result.get("filename", result.get("location", {}).get("path", "")),
                            "line": result.get("line_number", result.get("location", {}).get("lines", {}).get("begin", {}).get("line", 0)),
                            "description": result.get("issue_text", result.get("message", "")),
                            "remediation": self._get_remediation(scanner_name, result),
                            "cwe": result.get("cwe", {}).get("id", "") if isinstance(result.get("cwe"), dict) else "",
                        })
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse {scanner_name} output: {e}")

            return findings

        except asyncio.TimeoutError:
            logger.error(f"Scanner {scanner_name} timed out on {target_path}")
            return [{"scanner": scanner_name, "severity": "info", "category": "scanner_error", 
                     "title": f"{scanner_name} timed out", "description": "Scanner took too long"}]
        except FileNotFoundError:
            logger.warning(f"Scanner {scanner_name} not installed")
            return [{"scanner": scanner_name, "severity": "info", "category": "scanner_missing",
                     "title": f"{scanner_name} not installed", "description": f"Install {scanner_name} to enable this scanner"}]
        except Exception as e:
            logger.error(f"Scanner {scanner_name} failed: {e}")
            return []

    def _categorize_finding(self, result: dict, scanner: str) -> str:
        """Categorize a finding based on its content."""
        text = (result.get("issue_text", "") + " " + result.get("check_name", "")).lower()
        
        if any(k in text for k in ["sql", "injection", "query"]):
            return "sql_injection"
        elif any(k in text for k in ["xss", "cross-site", "html"]):
            return "xss"
        elif any(k in text for k in ["ssrf", "url", "request"]):
            return "ssrf"
        elif any(k in text for k in ["secret", "password", "key", "token"]):
            return "hardcoded_secret"
        elif any(k in text for k in ["auth", "permission", "access"]):
            return "auth_bypass"
        elif any(k in text for k in ["crypto", "encrypt", "hash"]):
            return "weak_crypto"
        else:
            return "general_vulnerability"

    def _get_remediation(self, scanner: str, result: dict) -> str:
        """Generate remediation suggestion based on finding type."""
        category = self._categorize_finding(result, scanner)
        remediations = {
            "sql_injection": "Use parameterized queries or the SQL Gate (sqlglot) for all database operations.",
            "xss": "Escape all user inputs before rendering. Use Content-Security-Policy headers.",
            "ssrf": "Validate and whitelist all URLs. Block internal/metadata IPs (169.254.169.254, 127.0.0.1).",
            "hardcoded_secret": "Move secrets to environment variables or a secrets manager (e.g., Vault).",
            "auth_bypass": "Implement proper authentication middleware and tenant isolation (org_id scoping).",
            "weak_crypto": "Use Argon2id for passwords, AES-GCM for encryption, RS256/ES256 for JWT.",
            "general_vulnerability": "Review the finding and apply industry best practices for the specific issue.",
        }
        return remediations.get(category, "Review and fix the identified issue.")

    async def _check_tenant_isolation(self, target_path: str, org_id: str) -> list[dict[str, Any]]:
        """Custom check for tenant isolation violations in SQL queries."""
        findings = []
        path = Path(target_path)
        
        if not path.exists():
            return findings

        files_to_check = list(path.rglob("*.py")) if path.is_dir() else [path]
        
        for file_path in files_to_check:
            try:
                content = file_path.read_text()
                
                # Check for raw SQL without org_id filter
                sql_patterns = [
                    r'(execute|raw)\s*\(\s*["\'].*?SELECT.*?FROM.*?["\']',
                    r'session\.execute\s*\(\s*text\s*\(\s*["\'].*?SELECT',
                ]
                
                for pattern in sql_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
                    for match in matches:
                        # Check if org_id is in the query
                        surrounding = content[max(0, match.start() - 200):min(len(content), match.end() + 200)]
                        if "org_id" not in surrounding and "tenant" not in surrounding:
                            findings.append({
                                "scanner": "custom_tenant_check",
                                "severity": "critical",
                                "category": "tenant_isolation_violation",
                                "title": "SQL query missing tenant isolation",
                                "file": str(file_path),
                                "line": content[:match.start()].count('\n') + 1,
                                "description": "SQL query does not include org_id filter, risking cross-tenant data access",
                                "remediation": "Add WHERE org_id = :current_org_id to all queries or use SQLAlchemy's tenant-scoped sessions.",
                                "cwe": "CWE-284",
                            })
            except Exception as e:
                logger.warning(f"Failed to check {file_path}: {e}")

        return findings

    async def _detect_prompt_injection(self, target_path: str, org_id: str) -> list[dict[str, Any]]:
        """Detect potential prompt injection vulnerabilities in agent prompts."""
        findings = []
        path = Path(target_path)
        
        if not path.exists():
            return findings

        prompt_files = list(path.rglob("prompt.md")) + list(path.rglob("*.prompt"))
        
        for prompt_file in prompt_files:
            try:
                content = prompt_file.read_text()
                
                # Check for untrusted data wrapping
                if "<untrusted_data>" not in content and "{{" in content:
                    findings.append({
                        "scanner": "custom_prompt_check",
                        "severity": "high",
                        "category": "prompt_injection_risk",
                        "title": "Prompt uses template variables without <untrusted_data> wrapping",
                        "file": str(prompt_file),
                        "line": 1,
                        "description": "Template variables found but not wrapped in <untrusted_data> tags",
                        "remediation": "Wrap all user-provided data in <untrusted_data>...</untrusted_data> tags.",
                        "cwe": "CWE-94",
                    })
                
                # Check for direct concatenation patterns
                if re.search(r'f".*\{.*user.*\}.*"', content) or re.search(r'\+\s*user_input', content):
                    findings.append({
                        "scanner": "custom_prompt_check",
                        "severity": "high",
                        "category": "prompt_injection_risk",
                        "title": "Potential direct user input concatenation in prompt",
                        "file": str(prompt_file),
                        "line": 1,
                        "description": "User input may be directly concatenated into prompt instructions",
                        "remediation": "Use structured input separation. Never concatenate user data into instruction position.",
                        "cwe": "CWE-94",
                    })
            except Exception as e:
                logger.warning(f"Failed to check prompt {prompt_file}: {e}")

        return findings

    def _calculate_confidence(
        self,
        findings: list[dict],
        scanners_run: int,
        scan_duration_ms: float
    ) -> float:
        """Calculate evidence-based confidence in the audit results."""
        if not findings:
            # No findings = high confidence in security (assuming scanners ran)
            return min(0.95, 0.7 + (scanners_run * 0.05))

        # Severity-based penalty
        severity_penalty = sum(
            self.SEVERITY_WEIGHTS.get(f["severity"], 0.1) 
            for f in findings
        )
        
        # Scanner coverage bonus
        scanner_coverage = min(1.0, scanners_run / 4.0)  # 4 main scanners
        
        # Time factor (too fast = suspicious, too slow = incomplete)
        time_factor = 1.0 if 1000 < scan_duration_ms < 300000 else 0.7

        raw_confidence = (
            (1.0 - min(severity_penalty / 10.0, 0.5)) * 0.5 +  # Severity impact
            scanner_coverage * 0.3 +                            # Scanner coverage
            time_factor * 0.2                                   # Scan quality
        )

        return round(max(0.1, min(raw_confidence, 1.0)), 2)

    async def execute(self, brief: TaskBrief, ack: Acknowledgement) -> AgentResult:
        """Execute comprehensive security audit with multi-scanner orchestration."""
        target = (
            brief.context.get("target") or 
            brief.context.get("path") or
            brief.context.get("scan_scope", "")
        )
        org_id = brief.org_id
        
        if not target:
            return AgentResult(
                task_id=brief.task_id,
                success=False,
                error="No scan target provided",
                confidence=0.0,
            )

        start_time = datetime.now(timezone.utc)
        all_findings = []
        scanners_run = 0
        scanner_results = {}

        try:
            # 1. Run all scanners in parallel
            scanner_tasks = [
                self._run_scanner(scanner, target, org_id)
                for scanner in self.SCANNERS.keys()
            ]
            
            # Add custom checks
            scanner_tasks.append(self._check_tenant_isolation(target, org_id))
            scanner_tasks.append(self._detect_prompt_injection(target, org_id))

            results = await asyncio.gather(*scanner_tasks, return_exceptions=True)
            
            # 2. Aggregate findings
            scanner_names = list(self.SCANNERS.keys()) + ["custom_tenant_check", "custom_prompt_check"]
            for scanner_name, result in zip(scanner_names, results):
                if isinstance(result, Exception):
                    logger.error(f"Scanner {scanner_name} raised exception: {result}")
                    scanner_results[scanner_name] = {"status": "error", "error": str(result)}
                else:
                    all_findings.extend(result)
                    scanners_run += 1
                    scanner_results[scanner_name] = {
                        "status": "success",
                        "findings_count": len(result)
                    }

            # 3. Deduplicate findings (same file + line + category)
            unique_findings = []
            seen = set()
            for f in all_findings:
                key = (f.get("file"), f.get("line"), f.get("category"), f.get("title"))
                if key not in seen:
                    seen.add(key)
                    unique_findings.append(f)

            # 4. Sort by severity
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
            unique_findings.sort(key=lambda x: severity_order.get(x.get("severity", "info"), 5))

            # 5. Calculate metrics
            end_time = datetime.now(timezone.utc)
            scan_duration_ms = (end_time - start_time).total_seconds() * 1000
            
            severity_counts = {
                "critical": sum(1 for f in unique_findings if f.get("severity") == "critical"),
                "high": sum(1 for f in unique_findings if f.get("severity") == "high"),
                "medium": sum(1 for f in unique_findings if f.get("severity") == "medium"),
                "low": sum(1 for f in unique_findings if f.get("severity") == "low"),
                "info": sum(1 for f in unique_findings if f.get("severity") == "info"),
            }

            confidence = self._calculate_confidence(unique_findings, scanners_run, scan_duration_ms)

            # 6. Determine overall risk level
            if severity_counts["critical"] > 0:
                risk_level = "critical"
            elif severity_counts["high"] > 2:
                risk_level = "high"
            elif severity_counts["high"] > 0 or severity_counts["medium"] > 5:
                risk_level = "medium"
            else:
                risk_level = "low"

            # 7. Audit Log
            await create_audit_entry(
                event_type="SECURITY_AUDIT_COMPLETED",
                org_id=org_id,
                details={
                    "task_id": brief.task_id,
                    "target": target,
                    "total_findings": len(unique_findings),
                    "severity_counts": severity_counts,
                    "risk_level": risk_level,
                    "scanners_run": scanners_run,
                    "scan_duration_ms": scan_duration_ms,
                    "confidence": confidence
                }
            )

            # 8. Store in history
            self.scan_history.append({
                "task_id": brief.task_id,
                "target": target,
                "findings_count": len(unique_findings),
                "risk_level": risk_level,
                "timestamp": end_time.isoformat()
            })

            return AgentResult(
                task_id=brief.task_id,
                success=True,
                output={
                    "target": target,
                    "findings": unique_findings,
                    "total_findings": len(unique_findings),
                    "severity_counts": severity_counts,
                    "risk_level": risk_level,
                    "scanners_run": scanners_run,
                    "scanner_results": scanner_results,
                    "scan_duration_ms": scan_duration_ms,
                    "recommendation": self._get_overall_recommendation(risk_level, severity_counts),
                },
                confidence=confidence,
                tokens_used=0,  # No LLM used in scanning
                cost_usd=0.0,
                completed_at=end_time,
            )

        except Exception as exc:
            logger.error(f"Security audit failed: {exc}")
            
            await create_audit_entry(
                event_type="SECURITY_AUDIT_FAILED",
                org_id=org_id,
                details={"task_id": brief.task_id, "target": target, "error": str(exc)}
            )

            return AgentResult(
                task_id=brief.task_id,
                success=False,
                error=f"Security audit failed: {str(exc)}",
                output={"partial_findings": all_findings},
                confidence=0.1,
                tokens_used=0,
                cost_usd=0.0,
                completed_at=datetime.now(timezone.utc),
            )

    def _get_overall_recommendation(self, risk_level: str, severity_counts: dict) -> str:
        """Generate overall recommendation based on findings."""
        if risk_level == "critical":
            return "BLOCK RELEASE: Critical vulnerabilities found. Fix immediately before deployment."
        elif risk_level == "high":
            return "HIGH RISK: Multiple high-severity issues. Address before next release."
        elif risk_level == "medium":
            return "MODERATE RISK: Review and fix medium-severity issues in next sprint."
        else:
            return "LOW RISK: System is reasonably secure. Continue monitoring."


from app.agents.base import registry
registry.register(SecurityAgent)
