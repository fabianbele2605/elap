"""Task Router Agent - Nivel Sistema"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TaskRouter:
    """Agente Enrutador de Tareas - Enruta tareas a agentes apropiados y descompone complejas"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        logger.info(f"TaskRouter initialized with theme: {theme}")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de enrutamiento de tareas"""
        logger.info(f"Processing task routing query: {query[:50]}...")

        response = await self._generate_routing_response(query)

        return {
            "message": response,
            "intent": "task_routing",
            "agent": "task_router",
        }

    async def _generate_routing_response(self, query: str) -> str:
        """Generar respuesta de enrutamiento de tareas con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("task_router")

            prompt_ollama = f"""{system_prompt}

Consulta de Tarea: {query}

Proporciona análisis de ruta, descomposición de tareas y asignación óptima de agentes."""

            logger.info("🔀 Llamando a Ollama para enrutamiento de tareas...")
            respuesta = await ollama.generar("glm4:9b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en TaskRouter: {e}")
            return "🔀 Enrutador de Tareas operativo. Descompone y distribuye trabajo entre agentes."
