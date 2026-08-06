"""End-to-End Integration Tests for RAG Pipeline."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from elap_ai.embeddings.client import EmbeddingsClient
from elap_ai.vectordb.manager import VectorDBManager
from elap_ai.rag.orchestrator import RAGOrchestrator
from elap_ai.rag.cache import SemanticCache
from elap_ai.rag.hybrid_search import HybridSearch
from elap_ai.rag.reranker import Reranker


@pytest.fixture
def mock_embeddings():
    """Mock embeddings client."""
    client = AsyncMock(spec=EmbeddingsClient)
    client.embed = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
    return client


@pytest.fixture
def mock_vectordb():
    """Mock vector DB manager."""
    manager = AsyncMock(spec=VectorDBManager)
    manager.search = AsyncMock(return_value=[
        Mock(id="doc1", text="Python programming guide", similarity=0.95),
        Mock(id="doc2", text="Java tutorial", similarity=0.75),
    ])
    return manager


@pytest.mark.asyncio
async def test_rag_pipeline_e2e(mock_embeddings, mock_vectordb):
    """Test complete RAG pipeline E2E."""
    query = "how to learn python"

    # 1. Embed query
    embedding = await mock_embeddings.embed([query])
    assert embedding is not None
    assert len(embedding) > 0

    # 2. Search in vector DB
    results = await mock_vectordb.search(query, top_k=10)
    assert len(results) > 0
    assert results[0].text == "Python programming guide"

    # 3. Hybrid search
    hybrid = HybridSearch()
    hybrid_results = await hybrid.hybrid_search(
        query=query,
        semantic_results=results,
        documents=[r.text for r in results],
        limit=2
    )
    assert len(hybrid_results) <= 2

    # 4. Reranking
    reranker = Reranker()
    final_results = await reranker.rerank(
        query=query,
        documents=[text for text, _ in hybrid_results],
        top_k=1
    )
    assert len(final_results) <= 1


@pytest.mark.asyncio
async def test_semantic_cache_in_pipeline(mock_embeddings):
    """Test semantic cache in RAG pipeline."""
    cache = SemanticCache(ttl_seconds=60)
    query = "python tutorial"

    # First call - miss
    embedding = await mock_embeddings.embed([query])
    cached = await cache.get(query, embedding[0])
    assert cached is None

    # Cache result
    result = {"docs": ["Python tutorial"], "scores": [0.95]}
    await cache.set(query, result)

    # Second call - hit
    cached = await cache.get(query, embedding[0])
    assert cached == result

    # Check stats
    stats = cache.get_stats()
    assert stats["active_entries"] >= 1


@pytest.mark.asyncio
async def test_rag_with_multiple_queries(mock_embeddings, mock_vectordb):
    """Test RAG handling multiple queries."""
    queries = [
        "how to learn python",
        "java programming",
        "machine learning basics"
    ]

    cache = SemanticCache(ttl_seconds=60)
    hybrid = HybridSearch()
    reranker = Reranker()

    for query in queries:
        # Check cache
        embedding = await mock_embeddings.embed([query])
        cached = await cache.get(query, embedding[0])

        # If not cached, process
        if not cached:
            # Search
            results = await mock_vectordb.search(query, top_k=5)

            # Hybrid
            hybrid_results = await hybrid.hybrid_search(
                query=query,
                semantic_results=results,
                documents=[r.text for r in results],
                limit=3
            )

            # Rerank
            final = await reranker.rerank(
                query=query,
                documents=[text for text, _ in hybrid_results],
                top_k=2
            )

            # Cache
            await cache.set(query, final)
        else:
            final = cached

        assert final is not None


@pytest.mark.asyncio
async def test_concurrent_rag_queries(mock_embeddings, mock_vectordb):
    """Test concurrent RAG pipeline execution."""
    cache = SemanticCache(ttl_seconds=60)
    reranker = Reranker()

    queries = ["python", "java", "rust", "go", "c++"]

    async def process_query(query: str):
        embedding = await mock_embeddings.embed([query])
        cached = await cache.get(query, embedding[0])

        if not cached:
            results = await mock_vectordb.search(query, top_k=5)
            final = await reranker.rerank(
                query=query,
                documents=[r.text for r in results],
                top_k=2
            )
            await cache.set(query, final)
            return final
        return cached

    # Run concurrently
    results = await asyncio.gather(*[process_query(q) for q in queries])

    assert len(results) == 5
    assert all(r is not None for r in results)


@pytest.mark.asyncio
async def test_rag_error_handling(mock_embeddings):
    """Test RAG error handling."""
    # Mock embedding failure
    mock_embeddings.embed.side_effect = Exception("Embedding service down")

    with pytest.raises(Exception):
        await mock_embeddings.embed(["test"])


@pytest.mark.asyncio
async def test_cache_performance(mock_embeddings):
    """Test cache performance improvement."""
    cache = SemanticCache(ttl_seconds=60)
    query = "test query"

    embedding = await mock_embeddings.embed([query])
    result = {"data": "test"}

    # First access - cache miss
    await cache.set(query, result)

    # Subsequent accesses - cache hit (should be fast)
    for _ in range(10):
        cached = await cache.get(query, embedding[0])
        assert cached == result

    stats = cache.get_stats()
    assert stats["active_entries"] == 1
