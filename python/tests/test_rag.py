"""Tests para RAG Orchestrator."""

import pytest
from elap_ai.rag.orchestrator import RAGOrchestrator
from elap_ai.vectordb.manager import VectorDBManager, InMemoryVectorDB
from elap_ai.vectordb.models import Vector
from unittest.mock import AsyncMock, patch


@pytest.fixture
def mock_embeddings():
    """Mock del cliente de embeddings."""
    mock = AsyncMock()
    mock.embed = AsyncMock(return_value=[1.0, 0.0, 0.0])
    mock.health_check = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def rag_orchestrator(mock_embeddings):
    """Crear RAG orchestrator con mocks."""
    return RAGOrchestrator(
        embeddings_client=mock_embeddings,
        vectordb_manager=VectorDBManager(),
    )


@pytest.mark.asyncio
async def test_index_text(rag_orchestrator: RAGOrchestrator) -> None:
    """Test indexar un texto."""
    await rag_orchestrator.index_text(
        "doc_1",
        "Machine learning is awesome",
        {"topic": "AI"},
    )

    assert rag_orchestrator.vectordb.vector_count == 1


@pytest.mark.asyncio
async def test_index_batch(rag_orchestrator: RAGOrchestrator) -> None:
    """Test indexar múltiples documentos."""
    documents = {
        "doc_1": "Python programming language",
        "doc_2": "Rust systems programming",
        "doc_3": "JavaScript web development",
    }

    await rag_orchestrator.index_batch(documents)

    assert rag_orchestrator.vectordb.vector_count == 3


@pytest.mark.asyncio
async def test_retrieve(rag_orchestrator: RAGOrchestrator) -> None:
    """Test recuperar documentos."""
    # Indexar documentos
    documents = {
        "doc_1": "Python programming",
        "doc_2": "Rust programming",
    }
    await rag_orchestrator.index_batch(documents)

    # Recuperar
    results = await rag_orchestrator.retrieve("programming", limit=2)

    assert len(results) > 0
    assert all(hasattr(r, "similarity") for r in results)


@pytest.mark.asyncio
async def test_augment_context(rag_orchestrator: RAGOrchestrator) -> None:
    """Test generar contexto aumentado."""
    documents = {
        "doc_1": "Python is great for data science",
        "doc_2": "Machine learning models are powerful",
    }
    await rag_orchestrator.index_batch(documents)

    context = await rag_orchestrator.augment_context("data science", limit=2)

    assert "CONTEXTO RECUPERADO" in context
    assert "similitud:" in context


@pytest.mark.asyncio
async def test_health_check(rag_orchestrator: RAGOrchestrator) -> None:
    """Test health check."""
    health = await rag_orchestrator.health_check()

    assert "embeddings" in health
    assert "vectordb" in health
    assert health["embeddings"] is True
    assert health["vectordb"] is True
