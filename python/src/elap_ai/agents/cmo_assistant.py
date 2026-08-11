"""CMO Assistant Agent - Nivel Dirección"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CMOAssistant:
    """Agente Asistente del CMO - Estrategia de marketing y posicionamiento"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        logger.info(f"CMOAssistant initialized with theme: {theme}")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de marketing"""
        logger.info(f"Processing CMO query: {query[:50]}...")

        response = await self._generate_cmo_response(query)

        return {
            "message": response,
            "intent": "marketing_strategy",
            "agent": "cmo_assistant",
        }

    async def _generate_cmo_response(self, query: str) -> str:
        """Generar respuesta del CMO con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("cmo_assistant")

            prompt_ollama = f"""{system_prompt}

Consulta de Marketing: {query}

Proporciona estrategia de marketing con canales, mensajes y ROI."""

            logger.info("📢 Llamando a Ollama para estrategia del CMO...")
            respuesta = await ollama.generar("glm4:9b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en CMOAssistant: {e}")
            return "📢 Asistente del CMO operativo. Desarrolla estrategias de posicionamiento y campañas."
