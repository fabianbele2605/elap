"""Cliente de embeddings con Ollama."""

import asyncio
from typing import Any, Optional
import aiohttp
from pydantic import BaseModel, Field

from elap_ai.embeddings.models import EmbeddingModel, NOMIC_EMBED


class EmbeddingsClient:
    """Cliente para generar embeddings con Ollama."""

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: Optional[EmbeddingModel] = None,
    ) -> None:
        """Inicializar cliente de embeddings.

        Args:
            ollama_url: URL de servidor Ollama
            model: Modelo de embedding a usar (default: NOMIC_EMBED)
        """
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model or NOMIC_EMBED
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "EmbeddingsClient":
        """Context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        if self.session:
            await self.session.close()

    async def embed(self, text: str) -> list[float]:
        """Generar embedding para un texto.

        Args:
            text: Texto a embedir

        Returns:
            Vector de embedding

        Raises:
            RuntimeError: Si falla la conexión a Ollama
        """
        if not self.session:
            async with aiohttp.ClientSession() as session:
                return await self._embed_with_session(session, text)
        return await self._embed_with_session(self.session, text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generar embeddings para múltiples textos.

        Args:
            texts: Lista de textos

        Returns:
            Lista de vectores de embedding
        """
        tasks = [self.embed(text) for text in texts]
        return await asyncio.gather(*tasks)

    async def _embed_with_session(
        self, session: aiohttp.ClientSession, text: str
    ) -> list[float]:
        """Generar embedding con sesión existente."""
        url = f"{self.ollama_url}/api/embed"
        payload = {
            "model": self.model.name,
            "input": text,
        }

        try:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    raise RuntimeError(
                        f"Ollama error: {resp.status} - {await resp.text()}"
                    )
                data = await resp.json()
                return data.get("embeddings", [[]])[0]
        except asyncio.TimeoutError:
            raise RuntimeError("Timeout connecting to Ollama")
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Failed to connect to Ollama: {e}")

    async def health_check(self) -> bool:
        """Verificar conexión con Ollama.

        Returns:
            True si Ollama está disponible
        """
        url = f"{self.ollama_url}/api/tags"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """Listar modelos disponibles en Ollama.

        Returns:
            Lista de nombres de modelos
        """
        url = f"{self.ollama_url}/api/tags"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = data.get("models", [])
                        return [m.get("name", "") for m in models]
            return []
        except Exception:
            return []
