"""Customer Service Agent - Nivel Comercial"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CustomerServiceAgent:
    """Agente de Atención al Cliente - Soporte y resolución de problemas"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        logger.info(f"CustomerServiceAgent initialized with theme: {theme}")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de atención al cliente"""
        logger.info(f"Processing customer service query: {query[:50]}...")

        response = await self._generate_service_response(query)

        return {
            "message": response,
            "intent": "customer_support",
            "agent": "customer_service_agent",
        }

    async def _generate_service_response(self, query: str) -> str:
        """Generar respuesta de atención con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("customer_service_agent")

            prompt_ollama = f"""{system_prompt}

Consulta de Cliente: {query}

Proporciona soporte empático, resolución de problemas y escalamiento si es necesario."""

            logger.info("💬 Llamando a Ollama para atención al cliente...")
            respuesta = await ollama.generar("glm4:9b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en CustomerServiceAgent: {e}")
            return "💬 Equipo de Atención al Cliente operativo. Resuelve consultas y problemas."
