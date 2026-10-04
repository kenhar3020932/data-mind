#!/usr/bin/env python3
"""Generate API client code from FastAPI app routes.

Extracts route information and generates TypeScript client code
for frontend API consumption.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def extract_routes(app) -> list[dict[str, Any]]:
    """Extract route information from FastAPI app.

    Args:
        app: FastAPI application instance.

    Returns:
        List of route dictionaries.
    """
    routes = []

    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            route_info = {
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, "name", ""),
            }

            # Extract endpoint info
            if hasattr(route, "endpoint"):
                endpoint = route.endpoint
                if hasattr(endpoint, "__annotations__"):
                    route_info["parameters"] = list(endpoint.__annotations__.keys())

            routes.append(route_info)

    return routes


def generate_typescript_client(routes: list[dict[str, Any]], output_path: Path) -> None:
    """Generate TypeScript API client from route information.

    Args:
        routes: List of route dictionaries.
        output_path: Path to write the generated client.
    """
    lines = [
        '"""Auto-generated API client - DO NOT EDIT MANUALLY."""',
        'export interface ApiRoute {',
        '  path: string;',
        '  methods: string[];',
        '  name: string;',
        '}',
        "",
        "export const API_BASE = '/api/v1';",
        "",
        "export const routes: ApiRoute[] = [",
    ]

    for route in routes:
        methods_str = ", ".join(route["methods"])
        lines.append(f"  {{ path: '{route['path']}', methods: ['{methods_str}'], name: '{route['name']}' }},")

    lines.extend([
        "];",
        "",
        "// Client methods",
        "export class ApiClient {",
        "  private baseUrl: string;",
        "",
        "  constructor(baseUrl: string = API_BASE) {",
        "    this.baseUrl = baseUrl;",
        "  }",
        "",
    ])

    # Generate method stubs for each route
    for route in routes:
        if route["methods"]:
            method = route["methods"][0].lower()
            path_params = [p for p in route["path"].split("/") if p.startswith("{")]
            param_list = ", ".join(path_params)
            lines.append(f"  {method}{route['name'].title()}({param_list}): Promise<any> {{")
            lines.append(f"    return fetch(`${{this.baseUrl}}{route['path']}`).then(r => r.json());")
            lines.append("  }")
            lines.append("")

    lines.append("}")

    output_path.write_text("\n".join(lines))


def main() -> None:
    """Generate API client from FastAPI application."""
    from app.main import app  # noqa: PLC0415

    project_root = Path(__file__).parent.parent
    output_dir = project_root / "frontend" / "src" / "lib" / "api-client"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract routes
    print("Extracting routes from FastAPI app...")
    routes = extract_routes(app)
    print(f"Found {len(routes)} routes")

    # Generate TypeScript client
    output_path = output_dir / "routes.ts"
    generate_typescript_client(routes, output_path)
    print(f"✓ Generated {output_path}")

    # Also generate JSON spec
    spec_path = output_dir / "api-spec.json"
    spec_path.write_text(json.dumps(routes, indent=2))
    print(f"✓ Generated {spec_path}")

    print("\nAPI client generation complete!")


if __name__ == "__main__":
    main()
