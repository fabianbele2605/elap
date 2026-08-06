"""Modelos para Vector DB."""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Vector:
    """Vector con metadata."""

    id: str
    vector: list[float]
    metadata: dict[str, Any]
    text: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convertir a diccionario."""
        return {
            "id": self.id,
            "vector": self.vector,
            "metadata": self.metadata,
            "text": self.text,
        }


@dataclass
class SearchResult:
    """Resultado de búsqueda en vector DB."""

    id: str
    text: str
    similarity: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convertir a diccionario."""
        return {
            "id": self.id,
            "text": self.text,
            "similarity": self.similarity,
            "metadata": self.metadata,
        }
