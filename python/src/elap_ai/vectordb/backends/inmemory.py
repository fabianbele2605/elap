"""Backend in-memory para Vector DB."""

from typing import Any

from elap_ai.vectordb.backends.base import VectorDBBackend
from elap_ai.vectordb.models import Vector, SearchResult


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

    async def clear(self) -> None:
        """Limpiar todos los vectores."""
        self.vectors.clear()

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
