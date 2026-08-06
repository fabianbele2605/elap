"""Backend Qdrant para Vector DB."""

import asyncio
from typing import Any, Optional
import aiohttp

from elap_ai.vectordb.backends.base import VectorDBBackend
from elap_ai.vectordb.models import Vector, SearchResult


class QdrantVectorDB(VectorDBBackend):
    """Vector DB con Qdrant."""

    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection_name: str = "default",
        vector_size: int = 768,
    ) -> None:
        """Inicializar cliente Qdrant.

        Args:
            url: URL del servidor Qdrant
            collection_name: Nombre de la colección
            vector_size: Dimensión de los vectores
        """
        self.url = url.rstrip("/")
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "QdrantVectorDB":
        """Context manager entry."""
        self.session = aiohttp.ClientSession()
        await self._ensure_collection()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        if self.session:
            await self.session.close()

    async def insert(self, vector: Vector) -> None:
        """Insertar vector."""
        if not self.session:
            async with aiohttp.ClientSession() as session:
                await self._insert_with_session(session, vector)
        else:
            await self._insert_with_session(self.session, vector)

    async def _insert_with_session(
        self, session: aiohttp.ClientSession, vector: Vector
    ) -> None:
        """Insertar con sesión existente."""
        url = f"{self.url}/collections/{self.collection_name}/points"
        payload = {
            "points": [
                {
                    "id": self._hash_id(vector.id),
                    "vector": vector.vector,
                    "payload": {
                        "id": vector.id,
                        "text": vector.text,
                        "metadata": vector.metadata,
                    },
                }
            ]
        }

        async with session.put(url, json=payload) as resp:
            if resp.status not in (200, 201):
                raise RuntimeError(f"Qdrant error: {resp.status}")

    async def search(
        self, query_vector: list[float], limit: int = 10, threshold: float = 0.0
    ) -> list[SearchResult]:
        """Buscar vectores similares."""
        if not self.session:
            async with aiohttp.ClientSession() as session:
                return await self._search_with_session(session, query_vector, limit, threshold)
        return await self._search_with_session(self.session, query_vector, limit, threshold)

    async def _search_with_session(
        self,
        session: aiohttp.ClientSession,
        query_vector: list[float],
        limit: int = 10,
        threshold: float = 0.0,
    ) -> list[SearchResult]:
        """Buscar con sesión existente."""
        url = f"{self.url}/collections/{self.collection_name}/points/search"
        payload = {
            "vector": query_vector,
            "limit": limit,
            "score_threshold": threshold,
            "with_payload": True,
        }

        async with session.post(url, json=payload) as resp:
            if resp.status != 200:
                return []

            data = await resp.json()
            results: list[SearchResult] = []

            for point in data.get("result", []):
                payload = point.get("payload", {})
                results.append(
                    SearchResult(
                        id=payload.get("id", ""),
                        text=payload.get("text", ""),
                        similarity=point.get("score", 0.0),
                        metadata=payload.get("metadata", {}),
                    )
                )

            return results

    async def delete(self, vector_id: str) -> None:
        """Eliminar vector."""
        if not self.session:
            async with aiohttp.ClientSession() as session:
                await self._delete_with_session(session, vector_id)
        else:
            await self._delete_with_session(self.session, vector_id)

    async def _delete_with_session(
        self, session: aiohttp.ClientSession, vector_id: str
    ) -> None:
        """Eliminar con sesión existente."""
        url = f"{self.url}/collections/{self.collection_name}/points/delete"
        payload = {"points": [self._hash_id(vector_id)]}

        async with session.post(url, json=payload) as resp:
            if resp.status not in (200, 201):
                raise RuntimeError(f"Qdrant error: {resp.status}")

    async def health_check(self) -> bool:
        """Verificar conexión."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.url}/health") as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def clear(self) -> None:
        """Limpiar colección."""
        if not self.session:
            async with aiohttp.ClientSession() as session:
                await self._clear_with_session(session)
        else:
            await self._clear_with_session(self.session)

    async def _clear_with_session(self, session: aiohttp.ClientSession) -> None:
        """Limpiar con sesión existente."""
        url = f"{self.url}/collections/{self.collection_name}/delete"
        async with session.delete(url) as resp:
            if resp.status not in (200, 201):
                raise RuntimeError(f"Qdrant error: {resp.status}")

    async def _ensure_collection(self) -> None:
        """Asegurar que la colección existe."""
        if not self.session:
            return

        url = f"{self.url}/collections/{self.collection_name}"
        async with self.session.get(url) as resp:
            if resp.status == 404:
                # Crear colección
                create_url = f"{self.url}/collections/{self.collection_name}"
                payload = {
                    "vectors": {
                        "size": self.vector_size,
                        "distance": "Cosine",
                    }
                }
                async with self.session.put(create_url, json=payload) as create_resp:
                    if create_resp.status not in (200, 201):
                        raise RuntimeError("Failed to create Qdrant collection")

    @staticmethod
    def _hash_id(vector_id: str) -> int:
        """Convertir ID string a int para Qdrant."""
        return int(hash(vector_id) % (10 ** 8))
