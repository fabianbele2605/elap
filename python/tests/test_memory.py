"""Tests for Memory Management."""

import pytest
from datetime import datetime
from elap_ai.memory.memory import Memory, MemoryManager, MemoryType


@pytest.fixture
def memory_manager() -> MemoryManager:
    """Create memory manager for testing."""
    return MemoryManager(max_short_term=10, max_long_term=100)


def test_memory_creation() -> None:
    """Test memory entry creation."""
    memory = Memory(
        id="mem_1",
        content="Test memory",
        memory_type=MemoryType.SHORT_TERM,
    )

    assert memory.id == "mem_1"
    assert memory.content == "Test memory"
    assert memory.memory_type == MemoryType.SHORT_TERM
    assert memory.relevance == 1.0


def test_add_short_term_memory(memory_manager: MemoryManager) -> None:
    """Test adding short-term memory."""
    memory = Memory(
        id="short_1",
        content="Immediate task",
        memory_type=MemoryType.SHORT_TERM,
    )

    memory_manager.add_memory(memory)

    assert len(memory_manager.short_term) == 1
    assert memory_manager.short_term[0].id == "short_1"


def test_add_long_term_memory(memory_manager: MemoryManager) -> None:
    """Test adding long-term memory."""
    memory = Memory(
        id="long_1",
        content="Important knowledge",
        memory_type=MemoryType.LONG_TERM,
    )

    memory_manager.add_memory(memory)

    assert len(memory_manager.long_term) == 1
    assert memory_manager.long_term[0].id == "long_1"


def test_recall_memory(memory_manager: MemoryManager) -> None:
    """Test recalling memories."""
    # Add memories
    memory_manager.add_memory(Memory(
        id="mem_1",
        content="Python programming language",
        memory_type=MemoryType.LONG_TERM,
    ))
    memory_manager.add_memory(Memory(
        id="mem_2",
        content="Rust system language",
        memory_type=MemoryType.LONG_TERM,
    ))

    # Recall with query
    results = memory_manager.recall("Python", limit=5)

    assert len(results) == 1
    assert results[0].id == "mem_1"


def test_short_term_capacity(memory_manager: MemoryManager) -> None:
    """Test short-term memory capacity limit."""
    # Add more than max_short_term
    for i in range(15):
        memory = Memory(
            id=f"short_{i}",
            content=f"Short memory {i}",
            memory_type=MemoryType.SHORT_TERM,
        )
        memory_manager.add_memory(memory)

    # Should only keep max_short_term
    assert len(memory_manager.short_term) == 10


def test_memory_relevance_sorting(memory_manager: MemoryManager) -> None:
    """Test sorting by relevance."""
    # Add memories with different relevance
    memory_manager.add_memory(Memory(
        id="low",
        content="Low relevance",
        memory_type=MemoryType.LONG_TERM,
        relevance=0.2,
    ))
    memory_manager.add_memory(Memory(
        id="high",
        content="High relevance",
        memory_type=MemoryType.LONG_TERM,
        relevance=0.9,
    ))

    results = memory_manager.recall("relevance", limit=5)

    # Should return highest relevance first
    assert results[0].relevance >= results[-1].relevance


def test_clear_short_term(memory_manager: MemoryManager) -> None:
    """Test clearing short-term memory."""
    # Add short-term memory
    memory_manager.add_memory(Memory(
        id="short",
        content="Temporary",
        memory_type=MemoryType.SHORT_TERM,
    ))

    assert len(memory_manager.short_term) == 1

    # Clear
    memory_manager.clear_short_term()

    assert len(memory_manager.short_term) == 0


def test_memory_summary(memory_manager: MemoryManager) -> None:
    """Test memory summary."""
    memory_manager.add_memory(Memory(
        id="short",
        content="Short",
        memory_type=MemoryType.SHORT_TERM,
    ))
    memory_manager.add_memory(Memory(
        id="long",
        content="Long",
        memory_type=MemoryType.LONG_TERM,
    ))

    summary = memory_manager.summarize()

    assert summary["short_term_count"] == 1
    assert summary["long_term_count"] == 1
    assert summary["total_memories"] == 2
