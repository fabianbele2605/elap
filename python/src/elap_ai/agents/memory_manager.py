"""Memory Manager Agent - Nivel Sistema"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MemoryManager:
    """Agente Gestor de Memoria - Gestiona RAG, gráfos de conocimiento y recuperación de información"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        logger.info(f"MemoryManager initialized with theme: {theme}")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de gestión de memoria y RAG"""
        logger.info(f"Processing memory/RAG query: {query[:50]}...")

        response = await self._generate_memory_response(query)

        return {
            "message": response,
            "intent": "memory_management",
            "agent": "memory_manager",
        }

    async def _generate_memory_response(self, query: str) -> str:
        """Generar respuesta de gestión de memoria con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("memory_manager")

            prompt_ollama = f"""{system_prompt}

Consulta de Memoria: {query}

Proporciona recuperación de información, RAG y gráfos de conocimiento empresarial."""

            logger.info("🧠 Llamando a Ollama para gestión de memoria...")
            respuesta = await ollama.generar("qwen3:8b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en MemoryManager: {e}")
            return "🧠 Gestor de Memoria operativo. Gestiona RAG, gráfos de conocimiento e información histórica."
