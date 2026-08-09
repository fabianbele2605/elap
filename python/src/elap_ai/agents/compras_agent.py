"""Compras Agent - Nivel Administración"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ComprasAgent:
    """Agente de Compras - Gestión de compras y proveedores"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        logger.info(f"ComprasAgent initialized with theme: {theme}")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de compras"""
        logger.info(f"Processing procurement query: {query[:50]}...")

        response = await self._generate_procurement_response(query)

        return {
            "message": response,
            "intent": "procurement_management",
            "agent": "compras_agent",
        }

    async def _generate_procurement_response(self, query: str) -> str:
        """Generar respuesta de compras con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("compras_agent")

            prompt_ollama = f"""{system_prompt}

Consulta de Compras: {query}

Proporciona gestión de compras, cotizaciones y negociación con proveedores."""

            logger.info("🛒 Llamando a Ollama para gestión de compras...")
            respuesta = await ollama.generar("qwen3:8b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en ComprasAgent: {e}")
            return "🛒 Especialista en Compras operativo. Gestiona proveedores y optimiza costos."
