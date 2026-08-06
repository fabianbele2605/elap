"""Manager para Vector DB."""

from typing import Any, Optional

from elap_ai.vectordb.backends.base import VectorDBBackend
from elap_ai.vectordb.backends.inmemory import InMemoryVectorDB
from elap_ai.vectordb.models import Vector, SearchResult


class VectorDBManager:
    """Manager para Vector DB."""

    def __init__(self, backend: Optional[VectorDBBackend] = None) -> None:
        """Inicializar manager.

        Args:
            backend: Backend a usar (default: InMemoryVectorDB)
        """
        self.backend = backend or InMemoryVectorDB()
        self.vector_count = 0

    async def insert(self, vector: Vector) -> None:
        """Insertar vector."""
        await self.backend.insert(vector)
        self.vector_count += 1

    async def insert_batch(self, vectors: list[Vector]) -> None:
        """Insertar múltiples vectores."""
        for vector in vectors:
            await self.insert(vector)

    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        threshold: float = 0.0,
    ) -> list[SearchResult]:
        """Buscar vectores similares."""
        return await self.backend.search(query_vector, limit, threshold)

    async def delete(self, vector_id: str) -> None:
        """Eliminar vector."""
        await self.backend.delete(vector_id)
        self.vector_count = max(0, self.vector_count - 1)

    async def health_check(self) -> bool:
        """Verificar conexión."""
        return await self.backend.health_check()

    def get_stats(self) -> dict[str, Any]:
        """Obtener estadísticas."""
        return {
            "vector_count": self.vector_count,
            "backend": self.backend.__class__.__name__,
        }
