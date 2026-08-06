"""Hybrid Search - BM25 + Semantic."""

from typing import Optional
from elap_ai.vectordb.models import SearchResult


class HybridSearch:
    """Combina BM25 (keyword) + Semantic (embedding)."""

    def __init__(self, semantic_weight: float = 0.7, bm25_weight: float = 0.3) -> None:
        """Inicializar hybrid search.

        Args:
            semantic_weight: Peso de búsqueda semántica (0-1)
            bm25_weight: Peso de búsqueda BM25 (0-1)
        """
        self.semantic_weight = semantic_weight
        self.bm25_weight = bm25_weight

    def _bm25_score(self, query: str, document: str) -> float:
        """Calcular BM25 score (simplified)."""
        query_terms = query.lower().split()
        doc_terms = document.lower().split()

        # Contar matches
        matches = sum(1 for term in query_terms if term in doc_terms)
        doc_relevance = matches / max(len(query_terms), 1)

        return min(1.0, doc_relevance * 2)  # Normalizar a [0, 1]

    async def hybrid_search(
        self,
        query: str,
        semantic_results: list[SearchResult],
        documents: list[str],
        limit: int = 5,
    ) -> list[tuple[str, float]]:
        """Búsqueda híbrida.

        Args:
            query: Query
            semantic_results: Resultados de búsqueda semántica
            documents: Todos los documentos
            limit: Top k resultados

        Returns:
            Lista de (documento, score combinado)
        """
        scores: dict[str, float] = {}

        # Scores semánticos
        for result in semantic_results:
            scores[result.text] = result.similarity * self.semantic_weight

        # Scores BM25
        for doc in documents:
            bm25 = self._bm25_score(query, doc)
            if doc in scores:
                scores[doc] += bm25 * self.bm25_weight
            else:
                scores[doc] = bm25 * self.bm25_weight

        # Ordenar
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:limit]

    def get_config(self) -> dict:
        """Configuración actual."""
        return {
            "semantic_weight": self.semantic_weight,
            "bm25_weight": self.bm25_weight,
        }
