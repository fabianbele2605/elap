"""CEO Assistant Agent - Nivel Dirección"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CEOAssistant:
    """Agente Asistente del CEO - Asesoría ejecutiva y estratégica"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        logger.info(f"CEOAssistant initialized with theme: {theme}")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta ejecutiva"""
        logger.info(f"Processing CEO query: {query[:50]}...")

        response = await self._generate_executive_response(query)

        return {
            "message": response,
            "intent": "executive_advisory",
            "agent": "ceo_assistant",
        }

    async def _generate_executive_response(self, query: str) -> str:
        """Generar respuesta ejecutiva con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("ceo_assistant")

            prompt_ollama = f"""{system_prompt}

Consulta Ejecutiva: {query}

Proporciona reporte ejecutivo con resumen, métricas y recomendaciones accionables."""

            logger.info("👔 Llamando a Ollama para asesoría ejecutiva...")
            respuesta = await ollama.generar("qwen3:8b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en CEOAssistant: {e}")
            return "👔 Asistente Ejecutivo operativo. Analiza estrategia y oportunidades de crecimiento."
