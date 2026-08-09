"""System Supervisor Agent - Nivel Sistema"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SystemSupervisor:
    """Agente Supervisor de Sistema - Monitorea todos los agentes y coordina ejecución"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        logger.info(f"SystemSupervisor initialized with theme: {theme}")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de supervisión del sistema"""
        logger.info(f"Processing system supervision query: {query[:50]}...")

        response = await self._generate_supervisor_response(query)

        return {
            "message": response,
            "intent": "system_supervision",
            "agent": "system_supervisor",
        }

    async def _generate_supervisor_response(self, query: str) -> str:
        """Generar respuesta de supervisión del sistema con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("system_supervisor")

            prompt_ollama = f"""{system_prompt}

Consulta de Sistema: {query}

Proporciona monitoreo, salud de agentes y recomendaciones de coordinación."""

            logger.info("🔍 Llamando a Ollama para supervisión del sistema...")
            respuesta = await ollama.generar("qwen3:8b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en SystemSupervisor: {e}")
            return "🔍 Supervisor de Sistema operativo. Monitorea salud y coordinación de agentes."
