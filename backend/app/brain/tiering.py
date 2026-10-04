"""Model tiering for DataMind-King.

Routes tasks to appropriate LLM tiers based on complexity:
- Opus: Complex planning, critique, security audit
- Sonnet: Agent supervision, code generation
- Haiku/FreeLLM: Classification, simple SQL, summarization
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class ModelTier(str, Enum):
    """Available LLM tiers."""
    OPUS = "opus"
    SONNET = "sonnet"
    HAIKU = "haiku"
    FREE = "free_llm"


class ModelTiering:
    """Route tasks to appropriate model tiers."""

    _TIER_MAP: dict[str, ModelTier] = {
        "planning": ModelTier.OPUS,
        "critique": ModelTier.OPUS,
        "security": ModelTier.OPUS,
        "supervision": ModelTier.SONNET,
        "code_generation": ModelTier.SONNET,
        "sql": ModelTier.HAIKU,
        "classification": ModelTier.HAIKU,
        "summarization": ModelTier.HAIKU,
        "simple_query": ModelTier.FREE,
    }

    def select_tier(self, task_type: str) -> ModelTier:
        """Select the appropriate tier for a task type."""
        return self._TIER_MAP.get(task_type, ModelTier.SONNET)

    def select_model(self, tier: ModelTier) -> str:
        """Get the model ID for a tier."""
        models = {
            ModelTier.OPUS: "claude-opus-4-20250514",
            ModelTier.SONNET: "claude-sonnet-4-20250514",
            ModelTier.HAIKU: "claude-haiku-3-20241022",
            ModelTier.FREE: "free-llm-placeholder",
        }
        return models[tier]


# Module-level singleton
tiering = ModelTiering()
