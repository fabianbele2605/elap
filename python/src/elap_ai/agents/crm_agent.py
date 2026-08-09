"""CRM Agent - Nivel Comercial"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CRMAgent:
    """Agente CRM - Gestión de relaciones con clientes"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        logger.info(f"CRMAgent initialized with theme: {theme}")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta CRM"""
        logger.info(f"Processing CRM query: {query[:50]}...")

        response = await self._generate_crm_response(query)

        return {
            "message": response,
            "intent": "customer_relationship",
            "agent": "crm_agent",
        }

    async def _generate_crm_response(self, query: str) -> str:
        """Generar respuesta CRM con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("crm_agent")

            prompt_ollama = f"""{system_prompt}

Consulta CRM: {query}

Proporciona gestión de clientes, segmentación y estrategias de retención."""

            logger.info("👥 Llamando a Ollama para gestión CRM...")
            respuesta = await ollama.generar("qwen3:8b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en CRMAgent: {e}")
            return "👥 Gestor CRM operativo. Administra relaciones y base de clientes."
