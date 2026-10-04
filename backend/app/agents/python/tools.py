"""Python Agent tools for DataMind-King."""
from __future__ import annotations

import time
from typing import Any


def validate_python_code(code: str) -> dict[str, Any]:
    """Validate Python code for safety before execution.

    Checks for dangerous imports and patterns.
    """
    blocked_modules = {
        "os", "sys", "subprocess", "socket", "requests", "urllib",
        "shutil", "ctypes", "pickle", "importlib", "ftplib",
    }
    blocked_patterns = [
        r"\bos\.",
        r"\bsubprocess\b",
        r"\bopen\s*\(",
        r"\bexec\s*\(",
        r"\beval\s*\(",
        r"\b__import__\b",
        r"\binput\s*\(",
    ]

    warnings: list[str] = []

    for module in blocked_modules:
        if f"import {module}" in code or f"from {module}" in code:
            warnings.append(f"Blocked module import: {module}")

    import re
    for pattern in blocked_patterns:
        if re.search(pattern, code):
            warnings.append(f"Blocked pattern detected: {pattern}")

    # Check for syntax errors
    try:
        compile(code, "<python_agent>", "exec")
        syntax_ok = True
    except SyntaxError as exc:
        syntax_ok = False
        warnings.append(f"Syntax error: {exc}")

    return {
        "valid": len(warnings) == 0 and syntax_ok,
        "warnings": warnings,
        "syntax_ok": syntax_ok,
        "length": len(code),
    }


def execute_code(code: str, timeout: float = 5.0) -> dict[str, Any]:
    """Execute Python code in a restricted environment.

    Uses time module for timeout simulation.
    """
    start_time = time.monotonic()
    output = {"success": False, "stdout": "", "stderr": "", "execution_time_ms": 0.0}

    try:
        # Restricted globals - no builtins that could escape sandbox
        restricted_globals = {
            "__builtins__": {
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "range": range,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "sorted": sorted,
                "min": min,
                "max": max,
                "sum": sum,
                "abs": abs,
                "round": round,
                "pow": pow,
                "isinstance": isinstance,
                "issubclass": issubclass,
                "type": type,
                "True": True,
                "False": False,
                "None": None,
                "print": print,
            }
        }
        exec(code, restricted_globals)  # noqa: S102
        output["success"] = True
        output["stdout"] = "Execution completed"
    except TimeoutError:
        output["stderr"] = f"Execution exceeded {timeout}s timeout"
    except Exception as exc:  # noqa: BLE001
        output["stderr"] = str(exc)

    output["execution_time_ms"] = (time.monotonic() - start_time) * 1000
    return output