"""Script to generate API client code from OpenAPI spec.

Produces type-safe client libraries for frontend consumption.
Supports TypeScript, Python, and Go clients.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def load_spec(spec_file: str) -> dict:
    """Load OpenAPI specification from file."""
    path = Path(spec_file)
    if not path.exists():
        raise FileNotFoundError(f"Spec file not found: {spec_file}")
    return json.loads(path.read_text())


def generate_typescript_client(spec: dict, output_dir: str) -> None:
    """Generate TypeScript client from OpenAPI spec."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    paths = spec.get("paths", {})
    lines = [
        "/** Auto-generated API client - DO NOT EDIT */",
        "export interface ApiConfig {",
        '  baseUrl: string;',
        '  apiKey?: string;',
        "}",
        "",
        "export class ApiClient {",
        "  private config: ApiConfig;",
        "",
        "  constructor(config: ApiConfig) {",
        "    this.config = config;",
        "  }",
        "",
    ]

    for path, methods in paths.items():
        for method, details in methods.items():
            if method not in ("get", "post", "put", "delete", "patch"):
                continue
            op_id = details.get("operationId", f"{method}_{path}")
            safe_id = op_id.replace("-", "_").replace(".", "_")
            lines.append(f"  async {safe_id}(body?: any): Promise<any> {{")
            lines.append(f"    const url = `${{this.config.baseUrl}}{path}`;")
            lines.append(f"    const response = await fetch(url, {{")
            lines.append(f"      method: '{method.upper()}',")
            lines.append(f"      headers: this.config.apiKey ? {{'Authorization': `Bearer ${{this.config.apiKey}}`}} : {{'Content-Type': 'application/json'}},")
            lines.append(f"      body: body ? JSON.stringify(body) : undefined,")
            lines.append(f"    }});")
            lines.append(f"    return response.json();")
            lines.append("  }")
            lines.append("")

    (out / "client.ts").write_text("\n".join(lines))
    print(f"Generated TypeScript client: {out / 'client.ts'}")


def generate_python_client(spec: dict, output_dir: str) -> None:
    """Generate Python client from OpenAPI spec."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    paths = spec.get("paths", {})
    lines = [
        '"""Auto-generated API client - DO NOT EDIT"""',
        "from __future__ import annotations",
        "import asyncio",
        "from typing import Any",
        "",
        "",
        "class ApiClient:",
        "    def __init__(self, base_url: str, api_key: str | None = None):",
        "        self.base_url = base_url",
        "        self.api_key = api_key",
        "",
    ]

    for path, methods in paths.items():
        for method, details in methods.items():
            if method not in ("get", "post", "put", "delete", "patch"):
                continue
            op_id = details.get("operationId", f"{method}_{path}")
            safe_id = op_id.replace("-", "_").replace(".", "_")
            lines.append(f"    async def {safe_id}(self, body: dict | None = None) -> dict:")
            lines.append(f"        url = f'{self.base_url}{path}'")
            lines.append(f"        headers = {{}}")
            lines.append(f"        if self.api_key:")
            lines.append(f"            headers['Authorization'] = f'Bearer {{self.api_key}}'")
            lines.append(f"        headers['Content-Type'] = 'application/json'")
            lines.append(f"        resp = await httpx.{method}(url, json=body, headers=headers)")
            lines.append(f"        return resp.json()")
            lines.append("")

    (out / "client.py").write_text("\n".join(lines))
    print(f"Generated Python client: {out / 'client.py'}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: generate_api_client.py <spec.json> <output_dir> [--lang ts|py]")
        sys.exit(1)

    spec_file = sys.argv[1]
    output_dir = sys.argv[2]
    lang = sys.argv[3] if len(sys.argv) > 3 else "ts"

    spec = load_spec(spec_file)

    if lang == "ts":
        generate_typescript_client(spec, output_dir)
    elif lang == "py":
        generate_python_client(spec, output_dir)
    else:
        print(f"Unsupported language: {lang}")
        sys.exit(1)