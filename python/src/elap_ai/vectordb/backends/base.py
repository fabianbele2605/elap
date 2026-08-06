"""Backend base para Vector DB."""

from abc import ABC, abstractmethod
from typing import Any

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

    @abstractmethod
    async def clear(self) -> None:
        """Limpiar todos los vectores."""
        pass
