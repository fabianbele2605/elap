"""Memory Management - Short-term and Long-term."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, ConfigDict


class MemoryType(str, Enum):
    """Memory type classification."""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"


class Memory(BaseModel):
    """Single memory entry."""

    id: str = Field(..., description="Memory unique identifier")
    content: str = Field(..., description="Memory content")
    memory_type: MemoryType = Field(..., description="Type of memory")
    timestamp: datetime = Field(default_factory=datetime.now)
    relevance: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(use_enum_values=False)


class MemoryManager:
    """Manage agent memory (short-term and long-term)."""

    def __init__(self, max_short_term: int = 50, max_long_term: int = 1000) -> None:
        """Initialize memory manager.

        Args:
            max_short_term: Maximum short-term memories to keep
            max_long_term: Maximum long-term memories to keep
        """
        self.max_short_term = max_short_term
        self.max_long_term = max_long_term

        self.short_term: list[Memory] = []
        self.long_term: list[Memory] = []

    def add_memory(self, memory: Memory) -> None:
        """Add memory to appropriate store."""
        if memory.memory_type == MemoryType.SHORT_TERM:
            self.short_term.append(memory)
            # Keep only recent short-term memories
            if len(self.short_term) > self.max_short_term:
                self.short_term.pop(0)
        else:
            self.long_term.append(memory)
            # Keep only relevant long-term memories
            if len(self.long_term) > self.max_long_term:
                # Remove least relevant
                self.long_term.sort(key=lambda m: m.relevance)
                self.long_term.pop(0)

    def recall(self, query: str, limit: int = 5) -> list[Memory]:
        """Recall memories matching query.

        Args:
            query: Search query
            limit: Maximum memories to return

        Returns:
            List of relevant memories
        """
        # Simple keyword matching (can be enhanced with embeddings)
        results: list[Memory] = []

        for memory in self.short_term + self.long_term:
            if query.lower() in memory.content.lower():
                results.append(memory)

        # Sort by relevance and recency
        results.sort(
            key=lambda m: (m.relevance, m.timestamp),
            reverse=True
        )

        return results[:limit]

    def clear_short_term(self) -> None:
        """Clear short-term memory."""
        self.short_term.clear()

    def summarize(self) -> dict[str, Any]:
        """Get memory summary."""
        return {
            "short_term_count": len(self.short_term),
            "long_term_count": len(self.long_term),
            "total_memories": len(self.short_term) + len(self.long_term),
            "short_term_capacity": self.max_short_term,
            "long_term_capacity": self.max_long_term,
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert memory to dictionary."""
        return {
            "short_term": [m.model_dump() for m in self.short_term],
            "long_term": [m.model_dump() for m in self.long_term],
        }
