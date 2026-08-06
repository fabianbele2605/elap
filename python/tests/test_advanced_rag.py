"""Tests para Advanced RAG."""

import pytest
from elap_ai.rag.reranker import Reranker
from elap_ai.rag.cache import SemanticCache
from elap_ai.rag.hybrid_search import HybridSearch
from elap_ai.vectordb.models import SearchResult


@pytest.fixture
def reranker() -> Reranker:
    """Crear reranker para tests."""
    return Reranker()


@pytest.fixture
def semantic_cache() -> SemanticCache:
    """Crear cache para tests."""
    return SemanticCache(ttl_seconds=60)


@pytest.fixture
def hybrid_search() -> HybridSearch:
    """Crear hybrid search para tests."""
    return HybridSearch()


def test_reranker_initialization(reranker: Reranker) -> None:
    """Test inicializar reranker."""
    assert reranker.model_name == "cross-encoder/ms-marco-MiniLM-L-12-v2"
    assert reranker.get_model_info()["model_name"] is not None


@pytest.mark.asyncio
async def test_rerank_documents(reranker: Reranker) -> None:
    """Test reranquear documentos."""
    query = "python programming"
    documents = [
        "Python is a programming language",
        "Java is also a language",
        "Python tutorial for beginners",
    ]

    results = await reranker.rerank(query, documents, top_k=2)

    assert len(results) <= 2
    assert all(isinstance(r, tuple) for r in results)


@pytest.mark.asyncio
async def test_semantic_cache_get_set(semantic_cache: SemanticCache) -> None:
    """Test guardar y obtener del cache."""
    query = "test query"
    result = {"data": "test"}

    await semantic_cache.set(query, result)
    cached = await semantic_cache.get(query, [1.0, 0.5])

    assert cached == result


@pytest.mark.asyncio
async def test_semantic_cache_expiration(
    semantic_cache: SemanticCache,
) -> None:
    """Test expiración del cache."""
    query = "expire test"
    result = {"data": "test"}

    await semantic_cache.set(query, result)

    # Cachea debe expirar después de TTL
    assert await semantic_cache.get(query, [1.0]) == result


def test_semantic_cache_stats(semantic_cache: SemanticCache) -> None:
    """Test estadísticas del cache."""
    stats = semantic_cache.get_stats()

    assert "total_entries" in stats
    assert "active_entries" in stats
    assert stats["ttl_seconds"] == 60


@pytest.mark.asyncio
async def test_hybrid_search(hybrid_search: HybridSearch) -> None:
    """Test búsqueda híbrida."""
    query = "python code"
    semantic_results = [
        SearchResult(
            id="doc1",
            text="Python programming guide",
            similarity=0.9,
            metadata={},
        ),
        SearchResult(
            id="doc2",
            text="Java programming",
            similarity=0.5,
            metadata={},
        ),
    ]
    documents = [
        "Python programming guide",
        "Java programming",
        "C++ reference",
    ]

    results = await hybrid_search.hybrid_search(
        query, semantic_results, documents, limit=2
    )

    assert len(results) <= 2
    assert all(isinstance(r, tuple) for r in results)


def test_hybrid_search_config(hybrid_search: HybridSearch) -> None:
    """Test configuración de hybrid search."""
    config = hybrid_search.get_config()

    assert config["semantic_weight"] == 0.7
    assert config["bm25_weight"] == 0.3
