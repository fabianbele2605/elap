"""Tests para Embeddings Client."""

import pytest
from elap_ai.embeddings.client import EmbeddingsClient
from elap_ai.embeddings.models import (
    EmbeddingModel,
    EmbeddingModelType,
    NOMIC_EMBED,
)


def test_embedding_model_creation() -> None:
    """Test crear modelo de embedding."""
    model = EmbeddingModel(
        name="test-model",
        model_type=EmbeddingModelType.NOMIC_EMBED_TEXT,
        dimension=768,
    )

    assert model.name == "test-model"
    assert model.dimension == 768


def test_embedding_model_invalid_dimension() -> None:
    """Test validación de dimensión."""
    with pytest.raises(ValueError):
        EmbeddingModel(
            name="invalid",
            model_type=EmbeddingModelType.NOMIC_EMBED_TEXT,
            dimension=-1,
        )


def test_client_initialization() -> None:
    """Test inicializar cliente."""
    client = EmbeddingsClient(model=NOMIC_EMBED)

    assert client.model == NOMIC_EMBED
    assert client.ollama_url == "http://localhost:11434"


def test_client_custom_url() -> None:
    """Test cliente con URL customizada."""
    client = EmbeddingsClient(ollama_url="http://example.com:11434/")

    assert client.ollama_url == "http://example.com:11434"


@pytest.mark.asyncio
async def test_health_check() -> None:
    """Test health check (puede fallar si Ollama no está corriendo)."""
    client = EmbeddingsClient()
    health = await client.health_check()

    # Este test puede ser True o False dependiendo si Ollama está corriendo
    assert isinstance(health, bool)


@pytest.mark.asyncio
async def test_list_models() -> None:
    """Test listar modelos (puede estar vacío si Ollama no está corriendo)."""
    client = EmbeddingsClient()
    models = await client.list_models()

    assert isinstance(models, list)
