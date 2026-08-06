"""Tests para Vector DB Manager."""

import pytest
from elap_ai.vectordb.manager import VectorDBManager, InMemoryVectorDB
from elap_ai.vectordb.models import Vector, SearchResult


@pytest.fixture
def vector_db() -> VectorDBManager:
    """Crear manager para tests."""
    return VectorDBManager()


@pytest.fixture
def sample_vectors() -> list[Vector]:
    """Crear vectores de ejemplo."""
    return [
        Vector(
            id="vec_1",
            vector=[1.0, 0.0, 0.0],
            text="Python programming",
            metadata={"category": "programming"},
        ),
        Vector(
            id="vec_2",
            vector=[0.0, 1.0, 0.0],
            text="Rust systems language",
            metadata={"category": "programming"},
        ),
        Vector(
            id="vec_3",
            vector=[0.0, 0.0, 1.0],
            text="Web development",
            metadata={"category": "web"},
        ),
    ]


@pytest.mark.asyncio
async def test_insert_vector(vector_db: VectorDBManager) -> None:
    """Test insertar vector."""
    vector = Vector(
        id="test_1",
        vector=[1.0, 2.0, 3.0],
        text="Test vector",
        metadata={},
    )

    await vector_db.insert(vector)

    assert vector_db.vector_count == 1


@pytest.mark.asyncio
async def test_insert_batch(
    vector_db: VectorDBManager, sample_vectors: list[Vector]
) -> None:
    """Test insertar múltiples vectores."""
    await vector_db.insert_batch(sample_vectors)

    assert vector_db.vector_count == 3


@pytest.mark.asyncio
async def test_search(
    vector_db: VectorDBManager, sample_vectors: list[Vector]
) -> None:
    """Test búsqueda de vectores."""
    await vector_db.insert_batch(sample_vectors)

    # Buscar con vector similar al primero
    results = await vector_db.search([1.0, 0.0, 0.0], limit=2)

    assert len(results) > 0
    # El primer resultado debería ser el más similar
    assert results[0].similarity > 0.5


@pytest.mark.asyncio
async def test_search_with_threshold(
    vector_db: VectorDBManager, sample_vectors: list[Vector]
) -> None:
    """Test búsqueda con threshold."""
    await vector_db.insert_batch(sample_vectors)

    results = await vector_db.search([1.0, 0.0, 0.0], threshold=0.99)

    # Solo debe devolver resultados muy similares
    assert all(r.similarity >= 0.99 for r in results)


@pytest.mark.asyncio
async def test_delete(vector_db: VectorDBManager) -> None:
    """Test eliminar vector."""
    vector = Vector(
        id="delete_me",
        vector=[1.0, 2.0],
        text="To delete",
        metadata={},
    )

    await vector_db.insert(vector)
    assert vector_db.vector_count == 1

    await vector_db.delete("delete_me")
    assert vector_db.vector_count == 0


@pytest.mark.asyncio
async def test_health_check(vector_db: VectorDBManager) -> None:
    """Test health check."""
    health = await vector_db.health_check()

    assert health is True


def test_stats(vector_db: VectorDBManager) -> None:
    """Test obtener estadísticas."""
    stats = vector_db.get_stats()

    assert "vector_count" in stats
    assert "backend" in stats
    assert stats["vector_count"] == 0


def test_in_memory_cosine_similarity() -> None:
    """Test cálculo de similitud coseno."""
    db = InMemoryVectorDB()

    # Vectores idénticos
    sim1 = db._cosine_similarity([1.0, 0.0], [1.0, 0.0])
    assert abs(sim1 - 1.0) < 0.01

    # Vectores ortogonales
    sim2 = db._cosine_similarity([1.0, 0.0], [0.0, 1.0])
    assert abs(sim2 - 0.0) < 0.01

    # Vectores opuestos
    sim3 = db._cosine_similarity([1.0, 0.0], [-1.0, 0.0])
    assert abs(sim3 - (-1.0)) < 0.01
