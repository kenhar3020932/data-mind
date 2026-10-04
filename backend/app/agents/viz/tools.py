"""Visualization Agent Tools for DataMind-King - Ultra God Mode Edition.

Intelligent chart selection, accessible Vega-Lite generation, and 
comprehensive data validation with design system integration.
"""

from __future__ import annotations

import logging
from typing import Any, Literal

logger = logging.getLogger(__name__)

# Design System Tokens (Neural Data Glass)
DESIGN_TOKENS = {
    "colors": {
        "primary": "#3B82F6",
        "secondary": "#10B981",
        "accent": "#F59E0B",
        "danger": "#EF4444",
        "neutral": "#6B7280",
        "background": "#FFFFFF",
        "text": "#111827",
    },
    "font_family": "Inter, system-ui, sans-serif",
    "border_radius": 8,
}

# Colorblind-friendly palette (Okabe-Ito inspired)
COLORBLIND_PALETTE = [
    "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#06B6D4"
]


def analyze_data_characteristics(data: list[dict[str, Any]]) -> dict[str, Any]:
    """Deeply analyze data to determine column types and relationships."""
    if not data:
        return {"type": "empty", "columns": [], "row_count": 0}
    
    first_row = data[0]
    columns = list(first_row.keys())
    row_count = len(data)
    
    # Detect column types
    numeric_cols = []
    categorical_cols = []
    temporal_cols = []
    
    for col in columns:
        sample_val = first_row[col]
        if isinstance(sample_val, (int, float)):
            numeric_cols.append(col)
        elif isinstance(sample_val, str):
            # Simple heuristic for dates
            if any(pattern in sample_val for pattern in ["-", "/", "T", "202", "201"]):
                temporal_cols.append(col)
            else:
                categorical_cols.append(col)
    
    return {
        "type": "structured",
        "columns": columns,
        "row_count": row_count,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "temporal_cols": temporal_cols,
        "is_time_series": len(temporal_cols) > 0 and len(numeric_cols) > 0,
        "is_comparison": len(categorical_cols) > 0 and len(numeric_cols) > 0,
        "is_distribution": len(numeric_cols) >= 2,
    }


def select_chart_type(data_chars: dict, user_preference: str = "auto") -> str:
    """Intelligently select the best chart type based on data characteristics."""
    if user_preference != "auto":
        return user_preference
    
    if data_chars["row_count"] == 0:
        return "empty_state"
    
    if data_chars["is_time_series"]:
        return "line"
    elif data_chars["is_comparison"]:
        if len(data_chars["categorical_cols"]) == 1 and len(data_chars["numeric_cols"]) == 1:
            return "bar"
        elif len(data_chars["numeric_cols"]) == 2:
            return "scatter"
    elif data_chars["is_distribution"]:
        return "histogram"
    elif len(data_chars["numeric_cols"]) == 1 and len(data_chars["categorical_cols"]) == 1:
        # Check if categorical has few unique values for pie
        return "pie" if len(set(row[data_chars["categorical_cols"][0]] for row in data_chars.get("data", [])[:10])) < 6 else "bar"
    
    return "table"  # Fallback


def generate_vega_spec(
    chart_type: str, 
    data: list[dict[str, Any]], 
    data_chars: dict,
    options: dict[str, Any]
) -> dict[str, Any]:
    """Generate a complete, accessible Vega-Lite specification."""
    
    # Base config with design system tokens
    base_config = {
        "view": {"stroke": None},
        "axis": {
            "labelFont": DESIGN_TOKENS["font_family"],
            "titleFont": DESIGN_TOKENS["font_family"],
            "labelColor": DESIGN_TOKENS["colors"]["text"],
            "titleColor": DESIGN_TOKENS["colors"]["text"],
        },
        "legend": {
            "labelFont": DESIGN_TOKENS["font_family"],
            "titleFont": DESIGN_TOKENS["font_family"],
        },
        "title": {
            "text": options.get("title", ""),
            "font": DESIGN_TOKENS["font_family"],
            "color": DESIGN_TOKENS["colors"]["text"],
            "fontSize": 16,
            "fontWeight": "bold",
        },
        "background": DESIGN_TOKENS["colors"]["background"],
    }

    # Determine encoding fields
    x_field = data_chars["categorical_cols"][0] if data_chars["categorical_cols"] else (data_chars["temporal_cols"][0] if data_chars["temporal_cols"] else "")
    y_field = data_chars["numeric_cols"][0] if data_chars["numeric_cols"] else ""
    color_field = data_chars["categorical_cols"][1] if len(data_chars["categorical_cols"]) > 1 else None

    spec: dict[str, Any] = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "config": base_config,
        "data": {"values": data},
        "width": "container",
        "height": 400,
        "autosize": {"type": "fit", "contains": "padding"},
    }

    # Chart-specific logic
    if chart_type == "bar":
        spec["mark"] = {"type": "bar", "cornerRadius": [DESIGN_TOKENS["border_radius"], DESIGN_TOKENS["border_radius"], 0, 0]}
        spec["encoding"] = {
            "x": {"field": x_field, "type": "nominal", "axis": {"labelAngle": -45}},
            "y": {"field": y_field, "type": "quantitative"},
            "color": {"field": color_field, "type": "nominal", "scale": {"range": COLORBLIND_PALETTE}} if color_field else {"value": DESIGN_TOKENS["colors"]["primary"]},
        }
    elif chart_type == "line":
        spec["mark"] = {"type": "line", "point": True, "strokeWidth": 2}
        spec["encoding"] = {
            "x": {"field": x_field, "type": "temporal" if data_chars["is_time_series"] else "nominal"},
            "y": {"field": y_field, "type": "quantitative"},
            "color": {"field": color_field, "type": "nominal", "scale": {"range": COLORBLIND_PALETTE}} if color_field else {"value": DESIGN_TOKENS["colors"]["primary"]},
        }
    elif chart_type == "scatter":
        spec["mark"] = {"type": "point", "filled": True, "size": 60}
        spec["encoding"] = {
            "x": {"field": data_chars["numeric_cols"][0], "type": "quantitative"},
            "y": {"field": data_chars["numeric_cols"][1], "type": "quantitative"},
            "color": {"field": color_field, "type": "nominal", "scale": {"range": COLORBLIND_PALETTE}} if color_field else {"value": DESIGN_TOKENS["colors"]["primary"]},
        }
    elif chart_type == "pie":
        spec["mark"] = {"type": "arc", "innerRadius": 50}
        spec["encoding"] = {
            "theta": {"field": y_field, "type": "quantitative", "stack": True},
            "color": {"field": x_field, "type": "nominal", "scale": {"range": COLORBLIND_PALETTE}},
            "tooltip": [{"field": x_field, "type": "nominal"}, {"field": y_field, "type": "quantitative"}],
        }
    elif chart_type == "histogram":
        spec["mark"] = {"type": "bar", "cornerRadius": [DESIGN_TOKENS["border_radius"], DESIGN_TOKENS["border_radius"], 0, 0]}
        spec["encoding"] = {
            "x": {"bin": {"maxbins": 20}, "field": data_chars["numeric_cols"][0], "type": "quantitative"},
            "y": {"aggregate": "count", "type": "quantitative"},
            "color": {"value": DESIGN_TOKENS["colors"]["primary"]},
        }
    else:  # table or empty
        spec["mark"] = {"type": "text", "text": "No suitable chart type found for this data."}
        spec["encoding"] = {}

    # Accessibility: Add ARIA role and description
    spec["description"] = f"Chart showing {options.get('title', 'data analysis')} with {len(data)} data points."
    
    return spec


def validate_chart_data(data: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate chart data for consistency and quality."""
    if not data:
        return {"valid": False, "error": "Empty data", "row_count": 0}

    first_keys = set(data[0].keys())
    inconsistent_rows = [i for i, row in enumerate(data) if set(row.keys()) != first_keys]
    
    # Check for nulls
    null_counts = {col: sum(1 for row in data if row.get(col) is None) for col in first_keys}
    
    return {
        "valid": len(inconsistent_rows) == 0,
        "row_count": len(data),
        "column_count": len(first_keys),
        "inconsistent_rows": inconsistent_rows[:10],
        "keys": list(first_keys),
        "null_counts": null_counts,
        "quality_score": 1.0 - (sum(null_counts.values()) / (len(data) * len(first_keys)) if data else 0)
    }
