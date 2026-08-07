"""ELAP AI Runtime - Enterprise Local AI Platform."""

__version__ = "0.3.0"

from elap_ai.agent_runtime.agent import Agent, AgentState
from elap_ai.memory.memory import MemoryManager
from elap_ai.embeddings.client import EmbeddingsClient
from elap_ai.vectordb.manager import VectorDBManager
from elap_ai.rag.orchestrator import RAGOrchestrator
from elap_ai.document_generation_service import DocumentGenerationService

__all__ = [
    "Agent",
    "AgentState",
    "MemoryManager",
    "EmbeddingsClient",
    "VectorDBManager",
    "RAGOrchestrator",
    "DocumentGenerationService",
]
