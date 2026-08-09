"""CFO Assistant Agent - Nivel Dirección"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CFOAssistant:
    """Agente Asistente del CFO - Gestión financiera y presupuestaria"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        logger.info(f"CFOAssistant initialized with theme: {theme}")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta financiera ejecutiva"""
        logger.info(f"Processing CFO query: {query[:50]}...")

        response = await self._generate_cfo_response(query)

        return {
            "message": response,
            "intent": "financial_direction",
            "agent": "cfo_assistant",
        }

    async def _generate_cfo_response(self, query: str) -> str:
        """Generar respuesta del CFO con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("cfo_assistant")

            prompt_ollama = f"""{system_prompt}

Consulta Financiera: {query}

Proporciona análisis financiero riguroso con números y recomendaciones."""

            logger.info("💼 Llamando a Ollama para análisis del CFO...")
            respuesta = await ollama.generar("deepseek:8b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en CFOAssistant: {e}")
            return "💼 Asistente del CFO operativo. Controla presupuestos, flujos y análisis financiero."
