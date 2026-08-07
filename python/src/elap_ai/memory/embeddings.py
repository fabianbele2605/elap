"""Embedding generation using sentence-transformers."""

from typing import Optional


class EmbeddingService:
    """Generates embeddings for text using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding service.

        Args:
            model_name: sentence-transformers model to use
        """
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        """Lazily load model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError:
                raise ImportError("sentence-transformers required: pip install sentence-transformers")

            self._model = SentenceTransformer(self.model_name)

        return self._model

    def embed(self, text: str) -> list[float]:
        """
        Generate embedding for single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (list of floats)
        """
        model = self._get_model()
        embedding = model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        model = self._get_model()
        embeddings = model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()

    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0-1)
        """
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
        except ImportError:
            raise ImportError("scikit-learn required: pip install scikit-learn")

        emb1 = self.embed(text1)
        emb2 = self.embed(text2)

        similarity = cosine_similarity([emb1], [emb2])[0][0]
        return float(similarity)
