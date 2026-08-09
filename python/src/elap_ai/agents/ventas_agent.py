"""Ventas Agent - Nivel Comercial"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class VentasAgent:
    """Agente de Ventas - Gestión de ventas y prospectos"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        logger.info(f"VentasAgent initialized with theme: {theme}")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de ventas"""
        logger.info(f"Processing sales query: {query[:50]}...")

        response = await self._generate_sales_response(query)

        return {
            "message": response,
            "intent": "sales_management",
            "agent": "ventas_agent",
        }

    async def _generate_sales_response(self, query: str) -> str:
        """Generar respuesta de ventas con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("ventas_agent")

            prompt_ollama = f"""{system_prompt}

Consulta de Ventas: {query}

Proporciona estrategia de ventas, propuestas comerciales e identificación de prospectos."""

            logger.info("📈 Llamando a Ollama para gestión de ventas...")
            respuesta = await ollama.generar("qwen3:8b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en VentasAgent: {e}")
            return "📈 Especialista en Ventas operativo. Gestiona oportunidades y pipeline comercial."
