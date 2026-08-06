"""Semantic Cache - Cache de queries similares."""

from typing import Any, Optional
from datetime import datetime, timedelta
import hashlib


class SemanticCache:
    """Cache semántico para resultados de búsqueda."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        """Inicializar cache.

        Args:
            ttl_seconds: Time to live de cache
        """
        self.ttl = ttl_seconds
        self.cache: dict[str, tuple[Any, datetime]] = {}
        self.similarity_threshold = 0.95

    def _hash_query(self, query: str) -> str:
        """Hash de query."""
        return hashlib.sha256(query.encode()).hexdigest()[:16]

    async def get(self, query: str, embedding: list[float]) -> Optional[Any]:
        """Obtener resultado del cache.

        Args:
            query: Query
            embedding: Embedding de la query

        Returns:
            Resultado cached o None
        """
        cache_key = self._hash_query(query)

        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return result
            else:
                del self.cache[cache_key]

        return None

    async def set(self, query: str, result: Any) -> None:
        """Guardar resultado en cache.

        Args:
            query: Query
            result: Resultado
        """
        cache_key = self._hash_query(query)
        self.cache[cache_key] = (result, datetime.now())

    def clear(self) -> None:
        """Limpiar cache."""
        self.cache.clear()

    def get_stats(self) -> dict[str, Any]:
        """Estadísticas del cache."""
        now = datetime.now()
        active = sum(
            1 for _, timestamp in self.cache.values()
            if now - timestamp < timedelta(seconds=self.ttl)
        )
        return {
            "total_entries": len(self.cache),
            "active_entries": active,
            "ttl_seconds": self.ttl,
        }
