"""Customer Service Agent - Nivel Comercial con datos REALES"""

import logging
from typing import Dict, Any

from elap_ai.data_agent_mixin import DataAgentMixin

logger = logging.getLogger(__name__)


class CustomerServiceAgent(DataAgentMixin):
    """Agente de Atención al Cliente - Soporte y resolución de problemas con datos REALES"""

    def __init__(self, theme: str = "andina_foods"):
        super().__init__()
        self.theme = theme
        logger.info(f"CustomerServiceAgent initialized with theme: {theme} - usando datos REALES")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de atención al cliente"""
        logger.info(f"Processing customer service query: {query[:50]}...")

        query_lower = query.lower()

        # ==================== DATOS REALES ====================
        # Palabras clave para consultas sobre PQRS/Quejas
        pqrs_keywords = ["pqrs", "queja", "reclamo", "reclamación", "problema", "error", "servicio", "incidente", "ticket"]

        if any(kw in query_lower for kw in pqrs_keywords):
            logger.info("📋 Detectada pregunta sobre PQRS - usando datos REALES")

            try:
                datos = await self.obtener_pqrs_abiertos()

                if "error" not in datos:
                    respuesta = """📋 **ESTADO DE PQRS Y QUEJAS (DATOS REALES)**
===============================================================

"""
                    respuesta += f"📊 **Total PQRS**: {datos.get('total_pqrs', 0)}\n"
                    respuesta += f"🔴 **Abiertos**: {datos.get('abiertos', 0)}\n\n"

                    respuesta += "**Por Estado:**\n"
                    for estado, cantidad in datos.get('por_estado', {}).items():
                        respuesta += f"  • {estado}: {cantidad}\n"

                    respuesta += "\n**Categorías:**\n"
                    for categoria, cantidad in datos.get('por_categoria', {}).items():
                        respuesta += f"  • {categoria}: {cantidad}\n"

                    if datos.get('categoria_mas_frecuente'):
                        respuesta += f"\n⚠️ **Categoría más frecuente**: {datos['categoria_mas_frecuente']}\n"

                    respuesta += "\n✅ Datos obtenidos de PostgreSQL en tiempo real."

                    return {
                        "intent": "pqrs_query",
                        "message": respuesta
                    }
            except Exception as e:
                logger.error(f"Error obteniendo datos de PQRS: {e}")

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
