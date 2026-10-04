"""Memory system for DataMind-King.

Implements working, episodic, and semantic memory types.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class MemoryEntry:
    """A single memory entry."""
    timestamp: datetime
    entry_type: str  # "working", "episodic", "semantic"
    content: dict[str, Any]
    relevance_score: float = 1.0


class WorkingMemory:
    """Short-term working memory for active tasks."""

    def __init__(self, max_entries: int = 100) -> None:
        self._entries: deque[MemoryEntry] = deque(maxlen=max_entries)

    def add(self, content: dict[str, Any], entry_type: str = "working") -> None:
        self._entries.append(MemoryEntry(
            timestamp=datetime.now(timezone.utc),
            entry_type=entry_type,
            content=content,
        ))

    def get_recent(self, n: int = 10) -> list[dict[str, Any]]:
        return [e.content for e in list(self._entries)[-n:]]

    def clear(self) -> None:
        self._entries.clear()


class EpisodicMemory:
    """Long-term episodic memory for past interactions."""

    def __init__(self) -> None:
        self._episodes: list[MemoryEntry] = []

    def store(self, episode: dict[str, Any]) -> None:
        self._episodes.append(MemoryEntry(
            timestamp=datetime.now(timezone.utc),
            entry_type="episodic",
            content=episode,
        ))

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        # Simple keyword search
        results = [
            e.content for e in self._episodes
            if query.lower() in str(e.content).lower()
        ]
        return results[-limit:]


class SemanticMemory:
    """Structured knowledge base for reusable facts."""

    def __init__(self) -> None:
        self._facts: dict[str, Any] = {}

    def add_fact(self, key: str, value: Any) -> None:
        self._facts[key] = value

    def get_fact(self, key: str) -> Any:
        return self._facts.get(key)

    def update_fact(self, key: str, value: Any) -> None:
        self._facts[key] = value


class BrainMemory:
    """Combined memory system for the brain."""

    def __init__(self) -> None:
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()

    def store_episode(self, episode: dict[str, Any]) -> None:
        """Store an episode in both episodic and working memory."""
        self.episodic.store(episode)
        self.working.add(episode, "episodic")

    def get_context(self) -> dict[str, Any]:
        """Get current context from all memory stores."""
        return {
            "working": self.working.get_recent(5),
            "recent_episodes": self.episodic.search("", limit=3),
        }


# Module-level singleton
memory = BrainMemory()
