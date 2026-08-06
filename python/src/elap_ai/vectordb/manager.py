"""Manager para Vector DB (Qdrant)."""

from typing import Any, Optional
from abc import ABC, abstractmethod

from elap_ai.vectordb.models import Vector, SearchResult


class VectorDBBackend(ABC):
    """Backend abstracto para Vector DB."""

    @abstractmethod
    async def insert(self, vector: Vector) -> None:
        """Insertar vector."""
        pass

    @abstractmethod
    async def search(
        self, query_vector: list[float], limit: int = 10, threshold: float = 0.0
    ) -> list[SearchResult]:
        """Buscar vectores similares."""
        pass

    @abstractmethod
    async def delete(self, vector_id: str) -> None:
        """Eliminar vector."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verificar conexión."""
        pass


class InMemoryVectorDB(VectorDBBackend):
    """Vector DB en memoria (para testing)."""

    def __init__(self) -> None:
        """Inicializar."""
        self.vectors: dict[str, Vector] = {}

    async def insert(self, vector: Vector) -> None:
        """Insertar vector."""
        self.vectors[vector.id] = vector

    async def search(
        self, query_vector: list[float], limit: int = 10, threshold: float = 0.0
    ) -> list[SearchResult]:
        """Buscar vectores similares (cosine similarity)."""
        results: list[SearchResult] = []

        for vector in self.vectors.values():
            similarity = self._cosine_similarity(query_vector, vector.vector)
            if similarity >= threshold:
                results.append(
                    SearchResult(
                        id=vector.id,
                        text=vector.text,
                        similarity=similarity,
                        metadata=vector.metadata,
                    )
                )

        # Ordenar por similarity descendente
        results.sort(key=lambda r: r.similarity, reverse=True)
        return results[:limit]

    async def delete(self, vector_id: str) -> None:
        """Eliminar vector."""
        if vector_id in self.vectors:
            del self.vectors[vector_id]

    async def health_check(self) -> bool:
        """Siempre disponible."""
        return True

    @staticmethod
    def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Calcular similitud coseno."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)


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
