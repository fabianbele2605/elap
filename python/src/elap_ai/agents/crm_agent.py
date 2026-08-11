"""CRM Agent - Nivel Comercial con datos REALES"""

import logging
from typing import Dict, Any

from elap_ai.data_agent_mixin import DataAgentMixin

logger = logging.getLogger(__name__)


class CRMAgent(DataAgentMixin):
    """Agente CRM - Gestión de relaciones con clientes con datos REALES"""

    def __init__(self, theme: str = "andina_foods"):
        super().__init__()
        self.theme = theme
        logger.info(f"CRMAgent initialized with theme: {theme} - usando datos REALES")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta CRM"""
        logger.info(f"Processing CRM query: {query[:50]}...")

        query_lower = query.lower()

        # ==================== DATOS REALES ====================
        # Palabras clave para consultas de clientes
        cliente_keywords = ["cliente", "cartera", "vencida", "deuda", "principal", "top"]

        if any(kw in query_lower for kw in cliente_keywords):
            logger.info("👥 Detectada pregunta sobre clientes - usando datos REALES")

            try:
                top_clientes = await self.obtener_top_clientes(limite=15)

                if top_clientes:
                    respuesta = """👥 **GESTIÓN DE CARTERA DE CLIENTES (DATOS REALES)**
==================================================================

📊 **TOP 15 CLIENTES POR VENTAS 2025**

"""
                    for idx, cliente in enumerate(top_clientes, 1):
                        venta_2025 = cliente.get('ventas_2025', 0)
                        venta_2024 = cliente.get('ventas_2024', 0)
                        cartera = cliente.get('cartera_vencida', 0)

                        # Calcular crecimiento
                        crecimiento = ((venta_2025 - venta_2024) / venta_2024 * 100) if venta_2024 > 0 else 0
                        flecha = "📈" if crecimiento > 0 else "📉"

                        respuesta += f"{idx}. **{cliente['nombre']}** ({cliente['ciudad']})\n"
                        respuesta += f"   2025: ${venta_2025:,.0f} {flecha} {crecimiento:+.1f}%\n"
                        if cartera > 0:
                            respuesta += f"   ⚠️ Cartera Vencida: ${cartera:,.0f}\n"
                        respuesta += "\n"

                    # Análisis de riesgo
                    clientes_en_riesgo = [c for c in top_clientes if c.get('cartera_vencida', 0) > 0]
                    if clientes_en_riesgo:
                        respuesta += f"\n🚨 **CLIENTES EN RIESGO**: {len(clientes_en_riesgo)} de {len(top_clientes)}"

                    respuesta += "\n\n✅ Datos actualizados desde PostgreSQL."

                    return {
                        "intent": "cliente_query",
                        "message": respuesta
                    }
            except Exception as e:
                logger.error(f"Error obteniendo datos de clientes: {e}")

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
            respuesta = await ollama.generar("glm4:9b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en CRMAgent: {e}")
            return "👥 Gestor CRM operativo. Administra relaciones y base de clientes."
