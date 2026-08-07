"""Vector database integration using chromadb."""

from typing import Optional, Any
from .embeddings import EmbeddingService


class VectorStore:
    """Wrapper around chromadb for document storage and retrieval."""

    def __init__(self, db_path: str = "./data/chromadb"):
        """
        Initialize vector store.

        Args:
            db_path: Path to chromadb storage directory
        """
        self.db_path = db_path
        self._client = None
        self._collections = {}
        self._embedding_service = EmbeddingService()

    def _get_client(self):
        """Lazily initialize chromadb client."""
        if self._client is None:
            try:
                import chromadb
            except ImportError:
                raise ImportError("chromadb required: pip install chromadb")

            self._client = chromadb.PersistentClient(path=self.db_path)

        return self._client

    def create_collection(self, name: str, metadata: Optional[dict] = None) -> None:
        """
        Create or get a collection.

        Args:
            name: Collection name
            metadata: Optional metadata dict
        """
        client = self._get_client()
        collection = client.get_or_create_collection(
            name=name,
            metadata=metadata or {}
        )
        self._collections[name] = collection

    def add_documents(
        self,
        collection_name: str,
        documents: list[str],
        metadata: Optional[list[dict]] = None,
        ids: Optional[list[str]] = None,
    ) -> None:
        """
        Add documents to collection.

        Args:
            collection_name: Name of collection
            documents: List of document texts
            metadata: List of metadata dicts (one per document)
            ids: List of document IDs (auto-generated if not provided)
        """
        if collection_name not in self._collections:
            self.create_collection(collection_name)

        collection = self._collections[collection_name]

        # Generate embeddings
        embeddings = self._embedding_service.embed_batch(documents)

        # Auto-generate IDs if not provided
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]

        # Add to collection
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadata or [{}] * len(documents),
        )

    def search(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            collection_name: Collection to search
            query: Query text
            top_k: Number of results to return

        Returns:
            List of results with documents, distances, metadatas
        """
        if collection_name not in self._collections:
            return []

        collection = self._collections[collection_name]

        # Generate query embedding
        query_embedding = self._embedding_service.embed(query)

        # Query collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        # Format results
        formatted_results = []
        if results["documents"]:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "distance": results["distances"][0][i],
                    "metadata": results["metadatas"][0][i],
                })

        return formatted_results

    def delete_collection(self, collection_name: str) -> None:
        """
        Delete a collection.

        Args:
            collection_name: Collection to delete
        """
        if collection_name in self._collections:
            client = self._get_client()
            client.delete_collection(name=collection_name)
            del self._collections[collection_name]

    def list_collections(self) -> list[str]:
        """
        List all collections.

        Returns:
            List of collection names
        """
        client = self._get_client()
        collections = client.list_collections()
        return [c.name for c in collections]

    def get_collection_stats(self, collection_name: str) -> dict[str, Any]:
        """
        Get statistics about a collection.

        Args:
            collection_name: Collection name

        Returns:
            Stats dict with count, metadata
        """
        if collection_name not in self._collections:
            return {}

        collection = self._collections[collection_name]
        count = collection.count()

        return {
            "name": collection_name,
            "count": count,
        }
