"""Sandbox for isolated Python code execution.

In production, this would use gVisor or nsjail. For now, we implement
a strict Python sandbox using restricted evaluation contexts.
"""

from __future__ import annotations

import ast
import sys
import time
from dataclasses import dataclass
from io import StringIO
from typing import Any


@dataclass
class SandboxResult:
    """Result of sandboxed code execution."""

    success: bool
    output: str
    error: str | None
    duration_ms: float
    exit_code: int


class CodeSandbox:
    """Sandbox for executing untrusted Python code."""

    _BLOCKED_MODULES: frozenset[str] = frozenset({
        "os", "sys", "subprocess", "shutil", "socket", "httplib",
        "urllib", "requests", "httpx", "aiohttp", "pickle", "marshal",
        "importlib", "ctypes", "multiprocessing", "threading",
    })

    _BLOCKED_BUILTINS: frozenset[str] = frozenset({
        "eval", "exec", "__import__", "compile", "open",
        "input", "breakpoint",
    })

    def execute(self, code: str, timeout_seconds: float = 5.0) -> SandboxResult:
        """Execute code in a sandboxed environment."""
        start = time.perf_counter()
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        output = ""
        error = None
        exit_code = 0
        success = False

        try:
            self._validate_ast(code)
            local_ns: dict[str, Any] = {}
            global_ns = self._build_safe_globals()
            exec(compile(code, "<sandbox>", "exec"), global_ns, local_ns)  # noqa: S102
            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
            success = True
        except Exception as exc:  # noqa: BLE001
            error = f"{type(exc).__name__}: {exc}"
            exit_code = 1
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        duration_ms = (time.perf_counter() - start) * 1000
        return SandboxResult(
            success=success,
            output=output,
            error=error,
            duration_ms=round(duration_ms, 2),
            exit_code=exit_code,
        )

    def _validate_ast(self, code: str) -> None:
        """Validate AST for dangerous constructs."""
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_level = alias.name.split(".")[0]
                    if top_level in self._BLOCKED_MODULES:
                        raise ValueError(f"Blocked module import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                top_level = (node.module or "").split(".")[0]
                if top_level in self._BLOCKED_MODULES:
                    raise ValueError(f"Blocked import from: {node.module}")

    def _build_safe_globals(self) -> dict[str, Any]:
        """Build a restricted globals dict for sandbox execution."""
        safe_builtins = {
            k: v for k, v in builtins.__dict__.items()
            if k not in self._BLOCKED_BUILTINS
        }
        return {"__builtins__": safe_builtins}


# Module-level singleton
sandbox = CodeSandbox()
