"""PDF Assistant Agent - Nivel Documentación"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PDFAssistantAgent:
    """Agente Asistente PDF - Análisis de PDFs y extracción de datos"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        logger.info(f"PDFAssistantAgent initialized with theme: {theme}")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de análisis PDF"""
        logger.info(f"Processing PDF analysis query: {query[:50]}...")

        response = await self._generate_pdf_response(query)

        return {
            "message": response,
            "intent": "pdf_analysis",
            "agent": "pdf_assistant_agent",
        }

    async def _generate_pdf_response(self, query: str) -> str:
        """Generar respuesta de análisis PDF con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("pdf_assistant_agent")

            prompt_ollama = f"""{system_prompt}

Consulta de PDF: {query}

Proporciona extracción de datos, resúmenes ejecutivos y análisis de documentos."""

            logger.info("📄 Llamando a Ollama para análisis de PDF...")
            respuesta = await ollama.generar("qwen3:8b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en PDFAssistantAgent: {e}")
            return "📄 Asistente PDF operativo. Extrae datos y genera análisis de documentos."
