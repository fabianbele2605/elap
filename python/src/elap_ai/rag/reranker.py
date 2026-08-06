"""Reranking - Mejora de relevancia con cross-encoders."""

from typing import Optional
import asyncio


class Reranker:
    """Reranquea resultados usando cross-encoders."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-12-v2") -> None:
        """Inicializar reranker.

        Args:
            model_name: Modelo a usar
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Cargar modelo (lazy loading)."""
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(self.model_name)
        except ImportError:
            # Fallback si no está instalado
            self.model = None

    async def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int = 5,
    ) -> list[tuple[str, float]]:
        """Reranquear documentos.

        Args:
            query: Query original
            documents: Documentos a reranquear
            top_k: Top k resultados

        Returns:
            Lista de (documento, score)
        """
        if not self.model or not documents:
            # Fallback: retornar como está
            return [(doc, 0.5) for doc in documents[:top_k]]

        # Calcular scores
        pairs = [[query, doc] for doc in documents]
        scores = await asyncio.to_thread(self.model.predict, pairs)

        # Ordenar por score
        ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def get_model_info(self) -> dict:
        """Información del modelo."""
        return {
            "model_name": self.model_name,
            "loaded": self.model is not None,
        }
