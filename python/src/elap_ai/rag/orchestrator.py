"""RAG Orchestrator - Coordina embeddings, vector DB y agentes."""

from typing import Any, Optional

from elap_ai.embeddings.client import EmbeddingsClient
from elap_ai.embeddings.models import EmbeddingModel
from elap_ai.vectordb.manager import VectorDBManager, Vector
from elap_ai.vectordb.models import SearchResult


class RAGOrchestrator:
    """Coordina RAG (Retrieval-Augmented Generation)."""

    def __init__(
        self,
        embeddings_client: Optional[EmbeddingsClient] = None,
        vectordb_manager: Optional[VectorDBManager] = None,
    ) -> None:
        """Inicializar RAG orchestrator.

        Args:
            embeddings_client: Cliente de embeddings
            vectordb_manager: Manager de vector DB
        """
        self.embeddings = embeddings_client or EmbeddingsClient()
        self.vectordb = vectordb_manager or VectorDBManager()

    async def index_text(self, text_id: str, text: str, metadata: Optional[dict[str, Any]] = None) -> None:
        """Indexar un texto.

        Args:
            text_id: ID único del texto
            text: Contenido del texto
            metadata: Metadata adicional
        """
        # Generar embedding
        embedding = await self.embeddings.embed(text)

        # Insertar en vector DB
        vector = Vector(
            id=text_id,
            vector=embedding,
            metadata=metadata or {},
            text=text,
        )
        await self.vectordb.insert(vector)

    async def index_batch(self, documents: dict[str, str]) -> None:
        """Indexar múltiples documentos.

        Args:
            documents: Dict de {doc_id: contenido}
        """
        for doc_id, content in documents.items():
            await self.index_text(doc_id, content)

    async def retrieve(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.0,
    ) -> list[SearchResult]:
        """Recuperar documentos relevantes.

        Args:
            query: Texto a buscar
            limit: Número de resultados
            threshold: Umbral de similaridad

        Returns:
            Lista de documentos relevantes
        """
        # Generar embedding para la query
        query_embedding = await self.embeddings.embed(query)

        # Buscar en vector DB
        return await self.vectordb.search(query_embedding, limit, threshold)

    async def augment_context(self, query: str, limit: int = 3) -> str:
        """Generar contexto aumentado para una query.

        Args:
            query: Pregunta o query
            limit: Documentos a incluir

        Returns:
            Contexto formateado con documentos relevantes
        """
        results = await self.retrieve(query, limit)

        context_parts = ["=== CONTEXTO RECUPERADO ===\n"]
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[{i}] (similitud: {result.similarity:.2%})\n{result.text}\n"
            )

        return "\n".join(context_parts)

    async def health_check(self) -> dict[str, bool]:
        """Verificar salud de componentes.

        Returns:
            Estado de cada componente
        """
        return {
            "embeddings": await self.embeddings.health_check(),
            "vectordb": await self.vectordb.health_check(),
        }
