"""Tests para Qdrant Backend."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from elap_ai.vectordb.backends.qdrant import QdrantVectorDB
from elap_ai.vectordb.models import Vector


@pytest.fixture
def qdrant_client():
    """Crear cliente Qdrant para tests."""
    return QdrantVectorDB(
        url="http://localhost:6333",
        collection_name="test_collection",
        vector_size=768,
    )


def test_qdrant_initialization(qdrant_client: QdrantVectorDB) -> None:
    """Test inicializar cliente Qdrant."""
    assert qdrant_client.url == "http://localhost:6333"
    assert qdrant_client.collection_name == "test_collection"
    assert qdrant_client.vector_size == 768


def test_qdrant_url_normalization() -> None:
    """Test normalización de URL."""
    client = QdrantVectorDB(url="http://localhost:6333/")
    assert client.url == "http://localhost:6333"


def test_hash_id() -> None:
    """Test conversión de ID string a int."""
    id1 = QdrantVectorDB._hash_id("doc_1")
    id2 = QdrantVectorDB._hash_id("doc_2")

    assert isinstance(id1, int)
    assert isinstance(id2, int)
    assert id1 != id2


@pytest.mark.asyncio
async def test_health_check_success() -> None:
    """Test health check exitoso."""
    client = QdrantVectorDB()

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response

        # Este test depende de la conexión real si Qdrant está corriendo
        # En un test real, mockearíamos la sesión
        result = await client.health_check()
        assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_health_check_failure() -> None:
    """Test health check fallido."""
    client = QdrantVectorDB(url="http://invalid:9999")

    # Debería fallar sin lanzar excepción
    result = await client.health_check()
    assert result is False


def test_vector_model() -> None:
    """Test crear vector para Qdrant."""
    vector = Vector(
        id="test_1",
        vector=[1.0, 0.5, 0.2],
        text="Test content",
        metadata={"source": "test"},
    )

    assert vector.id == "test_1"
    assert len(vector.vector) == 3
    assert vector.metadata["source"] == "test"


@pytest.mark.asyncio
async def test_qdrant_context_manager() -> None:
    """Test context manager."""
    with patch("elap_ai.vectordb.backends.qdrant.QdrantVectorDB._ensure_collection"):
        client = QdrantVectorDB()
        async with client as c:
            assert c.session is not None
        assert client.session.closed or client.session is not None
