"""Security Agent Tools for DataMind-King - Ultra God Mode Edition.

Advanced security scanning tools with AST-based analysis, entropy calculation,
context-aware detection, and comprehensive vulnerability identification.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Literal

import sqlglot
from sqlglot import exp


def calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of a string (higher = more random/secret-like)."""
    if not text:
        return 0.0
    
    counter = Counter(text)
    length = len(text)
    entropy = 0.0
    
    for count in counter.values():
        probability = count / length
        if probability > 0:
            entropy -= probability * math.log2(probability)
    
    return entropy


def check_hardcoded_secrets(text: str, file_path: str | None = None) -> list[dict[str, Any]]:
    """
    Advanced secret detection with entropy analysis and context awareness.
    
    Args:
        text: Source code text to scan
        file_path: Optional file path for context (to skip test files, etc.)
        
    Returns:
        List of findings with type, line, entropy, and remediation
    """
    findings = []
    
    # Skip test files and example files
    if file_path and any(skip in file_path.lower() for skip in ['test', 'example', 'sample', '.env.example']):
        return findings
    
    # High-entropy patterns (likely real secrets)
    secret_patterns = [
        {
            "pattern": r"(?i)(password|passwd|pwd)\s*=\s*['\"]([^'\"]{8,})['\"]",
            "type": "password",
            "cwe": "CWE-798",
            "severity": "critical",
            "min_entropy": 3.5,
        },
        {
            "pattern": r"(?i)(api[_-]?key|apikey)\s*=\s*['\"]([^'\"]{16,})['\"]",
            "type": "api_key",
            "cwe": "CWE-798",
            "severity": "critical",
            "min_entropy": 4.0,
        },
        {
            "pattern": r"(?i)(secret|secret[_-]?key)\s*=\s*['\"]([^'\"]{16,})['\"]",
            "type": "secret_key",
            "cwe": "CWE-798",
            "severity": "critical",
            "min_entropy": 4.0,
        },
        {
            "pattern": r"(?i)(token|auth[_-]?token|access[_-]?token)\s*=\s*['\"]([^'\"]{20,})['\"]",
            "type": "token",
            "cwe": "CWE-798",
            "severity": "high",
            "min_entropy": 3.8,
        },
        {
            "pattern": r"(AKIA[0-9A-Z]{16})",  # AWS Access Key
            "type": "aws_access_key",
            "cwe": "CWE-798",
            "severity": "critical",
            "min_entropy": 0.0,  # Always flag AWS keys
        },
        {
            "pattern": r"(-----BEGIN (RSA|PRIVATE|EC) KEY-----)",
            "type": "private_key",
            "cwe": "CWE-321",
            "severity": "critical",
            "min_entropy": 0.0,
        },
        {
            "pattern": r"(?i)(connection[_-]?string|database[_-]?url)\s*=\s*['\"]([^'\"]{20,})['\"]",
            "type": "connection_string",
            "cwe": "CWE-798",
            "severity": "critical",
            "min_entropy": 3.5,
        },
    ]
    
    for config in secret_patterns:
        pattern = config["pattern"]
        matches = re.finditer(pattern, text)
        
        for match in matches:
            # Extract the secret value (group 2 if exists, else group 1)
            secret_value = match.group(2) if match.lastindex >= 2 else match.group(1)
            
            # Calculate entropy
            entropy = calculate_entropy(secret_value)
            
            # Check if entropy meets threshold
            if entropy >= config["min_entropy"]:
                line_number = text[:match.start()].count("\n") + 1
                
                findings.append({
                    "type": config["type"],
                    "line": line_number,
                    "severity": config["severity"],
                    "cwe": config["cwe"],
                    "entropy": round(entropy, 2),
                    "match_preview": secret_value[:8] + "..." if len(secret_value) > 8 else secret_value,
                    "remediation": f"Move {config['type']} to environment variables or a secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault).",
                    "auto_fixable": False,
                })
    
    return findings


def check_sql_injection(query: str, dialect: str = "postgres") -> dict[str, Any]:
    """
    Advanced SQL injection detection using AST parsing with sqlglot.
    
    Args:
        query: SQL query to analyze
        dialect: SQL dialect (postgres, mysql, duckdb, etc.)
        
    Returns:
        Dict with is_clean, risks, and remediation suggestions
    """
    risks = []
    
    try:
        # Parse the query
        parsed = sqlglot.parse_one(query, read=dialect)
        
        # 1. Check for dangerous functions
        dangerous_funcs = {
            "exec": "CWE-94",
            "execute": "CWE-94",
            "system": "CWE-78",
            "xp_cmdshell": "CWE-78",
            "load_file": "CWE-200",
            "into_outfile": "CWE-200",
            "into_dumpfile": "CWE-200",
        }
        
        for func in parsed.find_all(exp.Func):
            func_name = func.name.lower()
            if func_name in dangerous_funcs:
                risks.append({
                    "type": "dangerous_function",
                    "function": func_name,
                    "cwe": dangerous_funcs[func_name],
                    "severity": "critical",
                    "description": f"Dangerous function '{func_name}' detected",
                    "remediation": "Remove dangerous function calls. Use parameterized queries instead.",
                })
        
        # 2. Check for UNION-based injection
        if list(parsed.find_all(exp.Union)):
            # Check if UNION is used with SELECT (potential injection)
            risks.append({
                "type": "union_injection",
                "cwe": "CWE-89",
                "severity": "high",
                "description": "UNION statement detected - potential for data exfiltration",
                "remediation": "Validate and sanitize all user inputs. Use parameterized queries.",
            })
        
        # 3. Check for stacked queries (multiple statements)
        if ";" in query and query.count(";") > 1:
            risks.append({
                "type": "stacked_queries",
                "cwe": "CWE-89",
                "severity": "high",
                "description": "Multiple SQL statements detected (stacked queries)",
                "remediation": "Disable stacked queries in database configuration. Use single statements only.",
            })
        
        # 4. Check for comment-based injection
        if re.search(r"(--|#|/\*)", query):
            risks.append({
                "type": "comment_injection",
                "cwe": "CWE-89",
                "severity": "medium",
                "description": "SQL comments detected - potential for query manipulation",
                "remediation": "Strip comments from user-supplied SQL. Use allowlist for valid queries.",
            })
        
        # 5. Check for tautologies (1=1, 'a'='a', etc.)
        tautology_patterns = [
            r"1\s*=\s*1",
            r"'\w*'\s*=\s*'\w*'",
            r"true",
            r"or\s+1",
        ]
        
        for pattern in tautology_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                risks.append({
                    "type": "tautology",
                    "cwe": "CWE-89",
                    "severity": "high",
                    "description": "Tautology detected (always-true condition)",
                    "remediation": "Validate input types. Use parameterized queries to prevent injection.",
                })
        
        # 6. Check for time-based blind injection
        time_funcs = ["sleep", "benchmark", "waitfor", "pg_sleep"]
        for func in parsed.find_all(exp.Func):
            if func.name.lower() in time_funcs:
                risks.append({
                    "type": "time_based_injection",
                    "function": func.name.lower(),
                    "cwe": "CWE-89",
                    "severity": "critical",
                    "description": f"Time-based function '{func.name}' detected - potential blind injection",
                    "remediation": "Block time-based functions in SQL gate. Use query timeouts.",
                })
        
    except Exception as e:
        # If parsing fails, it might be malformed SQL (potential injection)
        risks.append({
            "type": "malformed_sql",
            "cwe": "CWE-89",
            "severity": "medium",
            "description": f"SQL parsing failed: {str(e)}",
            "remediation": "Validate SQL syntax before execution. Use SQL parser for validation.",
        })
    
    return {
        "query": query,
        "is_clean": len(risks) == 0,
        "risk_count": len(risks),
        "risks": risks,
        "recommendation": "Use parameterized queries and SQL Gate (sqlglot) for all database operations." if risks else "Query appears safe.",
    }


def check_xss(vulnerable_text: str, context: Literal["html", "js", "url"] = "html") -> dict[str, Any]:
    """
    Advanced XSS detection with context awareness.
    
    Args:
        vulnerable_text: Text to check for XSS
        context: Where this text will be used (html, js, url)
        
    Returns:
        Dict with is_clean, findings, and remediation
    """
    findings = []
    
    # HTML context patterns
    html_patterns = [
        {
            "pattern": r"<script[^>]*>",
            "type": "script_tag",
            "cwe": "CWE-79",
            "severity": "critical",
            "description": "Script tag detected",
        },
        {
            "pattern": r"javascript\s*:",
            "type": "javascript_protocol",
            "cwe": "CWE-79",
            "severity": "critical",
            "description": "javascript: protocol detected",
        },
        {
            "pattern": r"on(error|load|click|mouseover|focus|blur|submit|change)\s*=",
            "type": "event_handler",
            "cwe": "CWE-79",
            "severity": "high",
            "description": "Event handler attribute detected",
        },
        {
            "pattern": r"<iframe[^>]*>",
            "type": "iframe",
            "cwe": "CWE-79",
            "severity": "high",
            "description": "iframe tag detected",
        },
        {
            "pattern": r"<(object|embed|applet)[^>]*>",
            "type": "embedded_content",
            "cwe": "CWE-79",
            "severity": "high",
            "description": "Embedded content tag detected",
        },
        {
            "pattern": r"<svg[^>]*on\w+\s*=",
            "type": "svg_event",
            "cwe": "CWE-79",
            "severity": "critical",
            "description": "SVG with event handler detected",
        },
        {
            "pattern": r"data\s*:\s*text/html",
            "type": "data_uri",
            "cwe": "CWE-79",
            "severity": "high",
            "description": "data: URI with HTML content detected",
        },
    ]
    
    # JavaScript context patterns
    js_patterns = [
        {
            "pattern": r"eval\s*\(",
            "type": "eval",
            "cwe": "CWE-94",
            "severity": "critical",
            "description": "eval() detected - code execution risk",
        },
        {
            "pattern": r"Function\s*\(",
            "type": "function_constructor",
            "cwe": "CWE-94",
            "severity": "critical",
            "description": "Function constructor detected",
        },
        {
            "pattern": r"setTimeout\s*\(\s*['\"]",
            "type": "setTimeout_string",
            "cwe": "CWE-94",
            "severity": "high",
            "description": "setTimeout with string argument detected",
        },
        {
            "pattern": r"innerHTML\s*=",
            "type": "innerHTML",
            "cwe": "CWE-79",
            "severity": "high",
            "description": "innerHTML assignment detected",
        },
        {
            "pattern": r"document\.write\s*\(",
            "type": "document_write",
            "cwe": "CWE-79",
            "severity": "high",
            "description": "document.write() detected",
        },
    ]
    
    # URL context patterns
    url_patterns = [
        {
            "pattern": r"javascript\s*:",
            "type": "javascript_protocol",
            "cwe": "CWE-79",
            "severity": "critical",
            "description": "javascript: protocol in URL",
        },
        {
            "pattern": r"data\s*:",
            "type": "data_protocol",
            "cwe": "CWE-79",
            "severity": "medium",
            "description": "data: protocol in URL",
        },
    ]
    
    # Select patterns based on context
    patterns = html_patterns if context == "html" else (js_patterns if context == "js" else url_patterns)
    
    for config in patterns:
        if re.search(config["pattern"], vulnerable_text, re.IGNORECASE):
            findings.append({
                "type": config["type"],
                "cwe": config["cwe"],
                "severity": config["severity"],
                "description": config["description"],
                "remediation": _get_xss_remediation(config["type"], context),
            })
    
    return {
        "text": vulnerable_text,
        "context": context,
        "is_clean": len(findings) == 0,
        "risk_count": len(findings),
        "findings": findings,
        "recommendation": _get_xss_overall_recommendation(context) if findings else "Text appears safe for the given context.",
    }


def _get_xss_remediation(xss_type: str, context: str) -> str:
    """Get specific remediation for XSS type."""
    remediations = {
        "script_tag": "Remove script tags. Use Content-Security-Policy to block inline scripts.",
        "javascript_protocol": "Block javascript: URLs. Use allowlist for URL schemes.",
        "event_handler": "Escape HTML entities. Use framework's built-in escaping (e.g., React, Vue).",
        "iframe": "Validate iframe sources. Use sandbox attribute. Implement CSP frame-ancestors.",
        "eval": "Never use eval(). Use JSON.parse() for data, or safe alternatives.",
        "innerHTML": "Use textContent instead. If HTML needed, use DOMPurify library.",
    }
    return remediations.get(xss_type, "Sanitize input and use context-appropriate escaping.")


def _get_xss_overall_recommendation(context: str) -> str:
    """Get overall XSS remediation recommendation."""
    recommendations = {
        "html": "Use HTML entity encoding. Implement Content-Security-Policy. Use framework auto-escaping.",
        "js": "Never use eval(). Use JSON.parse() for data. Sanitize all user inputs.",
        "url": "Validate URL schemes. Block javascript: and data: protocols. Use allowlist.",
    }
    return recommendations.get(context, "Sanitize all user inputs and use context-appropriate escaping.")


def check_ssrf(url: str) -> dict[str, Any]:
    """
    Check for Server-Side Request Forgery (SSRF) vulnerabilities.
    
    Args:
        url: URL to validate
        
    Returns:
        Dict with is_safe, risks, and remediation
    """
    risks = []
    
    # Block internal/private IPs
    private_ip_patterns = [
        r"127\.0\.0\.1",  # localhost
        r"localhost",
        r"0\.0\.0\.0",
        r"10\.\d+\.\d+\.\d+",  # 10.0.0.0/8
        r"172\.(1[6-9]|2\d|3[01])\.\d+\.\d+",  # 172.16.0.0/12
        r"192\.168\.\d+\.\d+",  # 192.168.0.0/16
        r"169\.254\.\d+\.\d+",  # Link-local (AWS metadata)
        r"::1",  # IPv6 localhost
        r"fc00:",  # IPv6 private
    ]
    
    for pattern in private_ip_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            risks.append({
                "type": "internal_ip",
                "cwe": "CWE-918",
                "severity": "critical",
                "description": f"URL points to internal/private IP: {pattern}",
                "remediation": "Block all internal IPs. Use allowlist for external domains only.",
            })
    
    # Block cloud metadata endpoints
    metadata_patterns = [
        r"169\.254\.169\.254",  # AWS/GCP metadata
        r"metadata\.google",  # GCP metadata
        r"metadata\.azure",  # Azure metadata
    ]
    
    for pattern in metadata_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            risks.append({
                "type": "cloud_metadata",
                "cwe": "CWE-918",
                "severity": "critical",
                "description": "URL points to cloud metadata endpoint",
                "remediation": "Block cloud metadata endpoints. Use IAM roles instead of metadata service.",
            })
    
    # Check for dangerous protocols
    dangerous_protocols = ["file://", "gopher://", "ftp://", "dict://"]
    for protocol in dangerous_protocols:
        if url.lower().startswith(protocol):
            risks.append({
                "type": "dangerous_protocol",
                "protocol": protocol,
                "cwe": "CWE-918",
                "severity": "critical",
                "description": f"Dangerous protocol detected: {protocol}",
                "remediation": "Allow only http:// and https:// protocols. Block all others.",
            })
    
    return {
        "url": url,
        "is_safe": len(risks) == 0,
        "risk_count": len(risks),
        "risks": risks,
        "recommendation": "Implement URL allowlist. Block internal IPs and metadata endpoints." if risks else "URL appears safe.",
    }


def check_path_traversal(file_path: str) -> dict[str, Any]:
    """
    Check for path traversal vulnerabilities.
    
    Args:
        file_path: File path to validate
        
    Returns:
        Dict with is_safe, risks, and remediation
    """
    risks = []
    
    # Check for traversal patterns
    traversal_patterns = [
        r"\.\./",  # Unix traversal
        r"\.\.\\",  # Windows traversal
        r"%2e%2e%2f",  # URL-encoded traversal
        r"%2e%2e/",  # Partial URL encoding
        r"\.\.%2f",  # Partial URL encoding
        r"%252e%252e%252f",  # Double URL encoding
    ]
    
    for pattern in traversal_patterns:
        if re.search(pattern, file_path, re.IGNORECASE):
            risks.append({
                "type": "path_traversal",
                "pattern": pattern,
                "cwe": "CWE-22",
                "severity": "critical",
                "description": "Path traversal pattern detected",
                "remediation": "Use os.path.basename() to extract filename. Validate against allowlist. Use chroot jail.",
            })
    
    # Check for absolute paths (potential issue if user-controlled)
    if file_path.startswith("/") or re.match(r"^[A-Za-z]:\\", file_path):
        risks.append({
            "type": "absolute_path",
            "cwe": "CWE-22",
            "severity": "medium",
            "description": "Absolute path detected - ensure it's not user-controlled",
            "remediation": "Use relative paths. If absolute needed, validate against allowlist.",
        })
    
    return {
        "path": file_path,
        "is_safe": len(risks) == 0,
        "risk_count": len(risks),
        "risks": risks,
        "recommendation": "Sanitize file paths. Use os.path.basename() and validate against allowlist." if risks else "Path appears safe.",
    }


def check_weak_crypto(text: str) -> list[dict[str, Any]]:
    """
    Check for weak cryptographic algorithms and practices.
    
    Args:
        text: Source code to scan
        
    Returns:
        List of findings with type, algorithm, and remediation
    """
    findings = []
    
    # Weak hash algorithms
    weak_hashes = {
        "md5": {"cwe": "CWE-328", "severity": "high", "replacement": "SHA-256 or SHA-3"},
        "sha1": {"cwe": "CWE-328", "severity": "high", "replacement": "SHA-256 or SHA-3"},
        "md4": {"cwe": "CWE-328", "severity": "critical", "replacement": "SHA-256 or SHA-3"},
    }
    
    for algo, config in weak_hashes.items():
        pattern = rf"(?i)(hashlib\.)?{algo}\s*\("
        if re.search(pattern, text):
            findings.append({
                "type": "weak_hash",
                "algorithm": algo.upper(),
                "cwe": config["cwe"],
                "severity": config["severity"],
                "description": f"Weak hash algorithm {algo.upper()} detected",
                "remediation": f"Replace {algo.upper()} with {config['replacement']}.",
            })
    
    # Weak encryption algorithms
    weak_encryption = {
        "des": {"cwe": "CWE-326", "severity": "critical", "replacement": "AES-256"},
        "rc4": {"cwe": "CWE-326", "severity": "critical", "replacement": "AES-256-GCM"},
        "blowfish": {"cwe": "CWE-326", "severity": "high", "replacement": "AES-256"},
    }
    
    for algo, config in weak_encryption.items():
        pattern = rf"(?i){algo}"
        if re.search(pattern, text):
            findings.append({
                "type": "weak_encryption",
                "algorithm": algo.upper(),
                "cwe": config["cwe"],
                "severity": config["severity"],
                "description": f"Weak encryption algorithm {algo.upper()} detected",
                "remediation": f"Replace {algo.upper()} with {config['replacement']}.",
            })
    
    # Weak password hashing
    weak_password_hash = {
        "md5": {"cwe": "CWE-916", "severity": "critical", "replacement": "Argon2id"},
        "sha1": {"cwe": "CWE-916", "severity": "critical", "replacement": "Argon2id"},
        "sha256": {"cwe": "CWE-916", "severity": "high", "replacement": "Argon2id or bcrypt"},
    }
    
    for algo, config in weak_password_hash.items():
        pattern = rf"(?i)(password|passwd|pwd).*{algo}"
        if re.search(pattern, text):
            findings.append({
                "type": "weak_password_hash",
                "algorithm": algo.upper(),
                "cwe": config["cwe"],
                "severity": config["severity"],
                "description": f"Weak password hashing with {algo.upper()} detected",
                "remediation": f"Use {config['replacement']} for password hashing.",
            })
    
    # Hardcoded IV/salt
    if re.search(r"(?i)(iv|salt|nonce)\s*=\s*['\"][^'\"]{8,}['\"]", text):
        findings.append({
            "type": "hardcoded_iv",
            "cwe": "CWE-329",
            "severity": "high",
            "description": "Hardcoded IV/salt/nonce detected",
            "remediation": "Generate random IV/salt for each encryption operation. Never reuse.",
        })
    
    return findings
