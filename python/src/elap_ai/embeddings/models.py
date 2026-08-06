"""Modelos de embeddings."""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class EmbeddingModelType(str, Enum):
    """Tipos de modelos de embedding."""
    NOMIC_EMBED_TEXT = "nomic-embed-text"
    MXBAI_EMBED_LARGE = "mxbai-embed-large"
    ALL_MINILM = "all-minilm"


@dataclass
class EmbeddingModel:
    """Modelo de embedding."""

    name: str
    model_type: EmbeddingModelType
    dimension: int
    description: str = ""

    def __post_init__(self) -> None:
        """Validar modelo."""
        if self.dimension <= 0:
            raise ValueError("Dimension must be positive")


# Modelos predefinidos
NOMIC_EMBED = EmbeddingModel(
    name="nomic-embed-text",
    model_type=EmbeddingModelType.NOMIC_EMBED_TEXT,
    dimension=768,
    description="Nomic Embed Text - 768 dimensions"
)

MXBAI_EMBED = EmbeddingModel(
    name="mxbai-embed-large",
    model_type=EmbeddingModelType.MXBAI_EMBED_LARGE,
    dimension=1024,
    description="Mixedbread AI Embed Large - 1024 dimensions"
)

ALL_MINILM_EMBED = EmbeddingModel(
    name="all-minilm",
    model_type=EmbeddingModelType.ALL_MINILM,
    dimension=384,
    description="All-MiniLM - 384 dimensions (lightweight)"
)
