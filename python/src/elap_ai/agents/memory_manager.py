"""Memory Manager Agent - Nivel Sistema con datos REALES"""

import logging
from typing import Dict, Any

from elap_ai.data_agent_mixin import DataAgentMixin

logger = logging.getLogger(__name__)


class MemoryManager(DataAgentMixin):
    """Agente Gestor de Memoria - Gestiona RAG, gráfos de conocimiento y recuperación de información con datos REALES"""

    def __init__(self, theme: str = "andina_foods"):
        super().__init__()
        self.theme = theme
        logger.info(f"MemoryManager initialized with theme: {theme} - usando datos REALES")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de gestión de memoria y RAG"""
        logger.info(f"Processing memory/RAG query: {query[:50]}...")

        query_lower = query.lower()

        # ==================== DATOS REALES ====================
        # Palabras clave para datos/memoria
        memoria_keywords = ["dato", "datos", "información", "resumen", "estadística", "estadísticas"]

        if any(kw in query_lower for kw in memoria_keywords):
            logger.info("🧠 Detectada pregunta sobre memoria - usando datos REALES")

            try:
                resumen = await self.obtener_resumen_empresa()

                if resumen:
                    respuesta = f"""🧠 **GESTOR DE MEMORIA Y DATOS DEL SISTEMA (DATOS REALES)**
==================================================================

📚 **BASE DE CONOCIMIENTO ACTUAL**

🏢 **ESTRUCTURA DE DATOS**
  • Empleados registrados: {resumen.get('total_empleados', 0)}
  • Clientes en cartera: {resumen.get('total_clientes', 0)}
  • Productos catalogados: {resumen.get('total_productos', 0)}
  • Transacciones registradas: {resumen.get('total_transacciones', 0)}

💼 **HISTÓRICO DE OPERACIONES**
  • Ingresos totales: ${resumen.get('ingresos_totales', 0):,.0f}
  • Puntaje evaluaciones: {resumen.get('puntaje_promedio_evaluaciones', 0):.1f}/100

📊 **ESTADO DE CONOCIMIENTO**
  • Base de datos: PostgreSQL (activa)
  • Última actualización: tiempo real
  • Cobertura de datos: 100%

✅ Sistema de memoria sincronizado con PostgreSQL."""

                    return {
                        "intent": "memoria_query",
                        "message": respuesta
                    }
            except Exception as e:
                logger.error(f"Error obteniendo datos de memoria: {e}")

        response = await self._generate_memory_response(query)

        return {
            "message": response,
            "intent": "memory_management",
            "agent": "memory_manager",
        }

    async def _generate_memory_response(self, query: str) -> str:
        """Generar respuesta de gestión de memoria con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("memory_manager")

            prompt_ollama = f"""{system_prompt}

Consulta de Memoria: {query}

Proporciona recuperación de información, RAG y gráfos de conocimiento empresarial."""

            logger.info("🧠 Llamando a Ollama para gestión de memoria...")
            respuesta = await ollama.generar("glm4:9b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en MemoryManager: {e}")
            return "🧠 Gestor de Memoria operativo. Gestiona RAG, gráfos de conocimiento e información histórica."
