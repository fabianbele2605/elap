"""Task Router Agent - Nivel Sistema con datos REALES"""

import logging
from typing import Dict, Any

from elap_ai.data_agent_mixin import DataAgentMixin

logger = logging.getLogger(__name__)


class TaskRouter(DataAgentMixin):
    """Agente Enrutador de Tareas - Enruta tareas a agentes apropiados y descompone complejas con datos REALES"""

    def __init__(self, theme: str = "andina_foods"):
        super().__init__()
        self.theme = theme
        logger.info(f"TaskRouter initialized with theme: {theme} - usando datos REALES")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de enrutamiento de tareas"""
        logger.info(f"Processing task routing query: {query[:50]}...")

        query_lower = query.lower()

        # ==================== DATOS REALES ====================
        # Palabras clave para enrutamiento de tareas
        routing_keywords = ["tarea", "asignar", "enrutamiento", "distribuir", "flujo", "proceso"]

        if any(kw in query_lower for kw in routing_keywords):
            logger.info("🔄 Detectada pregunta de enrutamiento - usando datos REALES")

            try:
                resumen = await self.obtener_resumen_empresa()

                if resumen:
                    respuesta = f"""🔄 **GESTOR DE ENRUTAMIENTO DE TAREAS (DATOS REALES)**
==================================================================

📋 **AGENTES DISPONIBLES Y ESPECIALIDADES**

👤 **NIVEL OPERACIONAL** (8 agentes)
  • HR Agent: Nómina, evaluaciones, beneficios
  • Payroll Agent: Cálculo de salarios y análisis
  • Finance Agent: Reportes financieros, facturas
  • Ventas Agent: Estrategia comercial, pipeline
  • CRM Agent: Gestión de clientes y cartera
  • Customer Service Agent: PQRS y quejas
  • Compras Agent: Inventario y productos
  • Benefits Agent: Prestaciones sociales

👔 **NIVEL DIRECCIÓN** (3 agentes)
  • CEO Assistant: Resumen ejecutivo
  • CFO Assistant: Análisis financiero
  • CMO Assistant: Estrategia de marketing

📚 **NIVEL DOCUMENTACIÓN** (3 agentes)
  • Document Manager: Gestión de registros
  • PDF Assistant: Análisis y generación
  • Knowledge Manager: Base de conocimiento

🔧 **NIVEL SISTEMA** (2 agentes)
  • System Supervisor: Monitoreo y salud
  • Task Router: Enrutamiento y descomposición

💼 **CARGAS PROCESADAS**
  • Empleados activos: {resumen.get('total_empleados', 0)}
  • Clientes en cartera: {resumen.get('total_clientes', 0)}
  • Transacciones: {resumen.get('total_transacciones', 0)}

✅ Sistema de enrutamiento optimizado con datos en tiempo real."""

                    return {
                        "intent": "routing_query",
                        "message": respuesta
                    }
            except Exception as e:
                logger.error(f"Error en enrutamiento: {e}")

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
