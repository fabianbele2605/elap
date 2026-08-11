"""Document Manager Agent - Nivel Documentación"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DocumentManagerAgent:
    """Agente Gestor Documental - Administra documentos y archivos"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        logger.info(f"DocumentManagerAgent initialized with theme: {theme}")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de gestión documental"""
        logger.info(f"Processing document management query: {query[:50]}...")

        response = await self._generate_document_response(query)

        return {
            "message": response,
            "intent": "document_management",
            "agent": "document_manager_agent",
        }

    async def _generate_document_response(self, query: str) -> str:
        """Generar respuesta de gestión documental con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("document_manager_agent")

            prompt_ollama = f"""{system_prompt}

Consulta Documental: {query}

Proporciona clasificación, organización y políticas de retención documental."""

            logger.info("📑 Llamando a Ollama para gestión documental...")
            respuesta = await ollama.generar("glm4:9b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en DocumentManagerAgent: {e}")
            return "📑 Gestor Documental operativo. Clasifica y organiza documentos empresariales."
