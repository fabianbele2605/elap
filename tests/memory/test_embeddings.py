"""Tests for EmbeddingService."""

import pytest
from elap_ai.memory.embeddings import EmbeddingService


def test_embedding_service_initialization():
    """Test EmbeddingService can be created."""
    service = EmbeddingService(model_name="all-MiniLM-L6-v2")
    assert service.model_name == "all-MiniLM-L6-v2"


@pytest.mark.asyncio
async def test_single_embedding():
    """Test embedding a single text."""
    service = EmbeddingService()

    text = "Este es un texto de prueba"
    embedding = service.embed(text)

    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)


@pytest.mark.asyncio
async def test_batch_embeddings():
    """Test embedding multiple texts."""
    service = EmbeddingService()

    texts = [
        "Primer texto",
        "Segundo texto",
        "Tercer texto"
    ]
    embeddings = service.embed_batch(texts)

    assert isinstance(embeddings, list)
    assert len(embeddings) == 3
    assert all(isinstance(emb, list) for emb in embeddings)


@pytest.mark.asyncio
async def test_embedding_consistency():
    """Test that same text produces same embedding."""
    service = EmbeddingService()

    text = "Texto consistente para prueba"
    emb1 = service.embed(text)
    emb2 = service.embed(text)

    assert emb1 == emb2


@pytest.mark.asyncio
async def test_similarity_calculation():
    """Test similarity between texts."""
    service = EmbeddingService()

    # Similar texts should have higher similarity
    sim_similar = service.similarity(
        "El gato es negro",
        "El gato es oscuro"
    )

    # Different texts should have lower similarity
    sim_different = service.similarity(
        "El gato es negro",
        "Los números son importantes"
    )

    assert sim_similar > sim_different
    assert 0 <= sim_similar <= 1
    assert 0 <= sim_different <= 1


@pytest.mark.asyncio
async def test_embedding_dimensions():
    """Test embedding vector dimensions."""
    service = EmbeddingService(model_name="all-MiniLM-L6-v2")

    embedding = service.embed("Test text")

    # all-MiniLM-L6-v2 produces 384-dimensional vectors
    assert len(embedding) == 384
