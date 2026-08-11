"""CMO Assistant Agent - Nivel Dirección con datos REALES"""

import logging
from typing import Dict, Any

from elap_ai.data_agent_mixin import DataAgentMixin

logger = logging.getLogger(__name__)


class CMOAssistant(DataAgentMixin):
    """Agente Asistente del CMO - Estrategia de marketing y posicionamiento con datos REALES"""

    def __init__(self, theme: str = "andina_foods"):
        super().__init__()
        self.theme = theme
        logger.info(f"CMOAssistant initialized with theme: {theme} - usando datos REALES")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de marketing"""
        logger.info(f"Processing CMO query: {query[:50]}...")

        query_lower = query.lower()

        # ==================== DATOS REALES ====================
        # Palabras clave para análisis de marketing/clientes
        marketing_keywords = ["cliente", "canal", "venta", "mercado", "producto", "estrategia", "posicionamiento"]

        if any(kw in query_lower for kw in marketing_keywords):
            logger.info("📈 Detectada pregunta de marketing - usando datos REALES")

            try:
                datos_ingresos = await self.obtener_ingresos_por_canal()
                top_clientes = await self.obtener_top_clientes(limite=10)

                if "error" not in datos_ingresos and top_clientes:
                    respuesta = """📈 **ANÁLISIS DE MERCADO Y POSICIONAMIENTO (DATOS REALES)**
==================================================================

📊 **COMPOSICIÓN DE INGRESOS POR CANAL**
"""
                    total = datos_ingresos.get('ingresos_totales', 0)
                    for canal, monto in datos_ingresos.get('canales_top_3', []):
                        pct = (monto / total * 100) if total > 0 else 0
                        respuesta += f"\n  • {canal}: {pct:.1f}% (${monto:,.0f})"

                    respuesta += f"""

👥 **SEGMENTACIÓN DE CLIENTES TOP 10**
  • Total Clientes Analizados: {len(top_clientes)}
  • Ingresos Concentrados: {(top_clientes[0]['ventas_2025'] / total * 100):.1f}% en cliente principal

📊 **CARTERA VENCIDA (RIESGO)**
"""
                    cartera_total = sum(c.get('cartera_vencida', 0) for c in top_clientes)
                    respuesta += f"  • Total Cartera Vencida: ${cartera_total:,.0f}\n"

                    respuesta += "\n✅ Análisis basado en datos actualizados de PostgreSQL."

                    return {
                        "intent": "marketing_analysis",
                        "message": respuesta
                    }
            except Exception as e:
                logger.error(f"Error obteniendo datos de marketing: {e}")

        response = await self._generate_cmo_response(query)

        return {
            "message": response,
            "intent": "marketing_strategy",
            "agent": "cmo_assistant",
        }

    async def _generate_cmo_response(self, query: str) -> str:
        """Generar respuesta del CMO con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("cmo_assistant")

            prompt_ollama = f"""{system_prompt}

Consulta de Marketing: {query}

Proporciona estrategia de marketing con canales, mensajes y ROI."""

            logger.info("📢 Llamando a Ollama para estrategia del CMO con deepseek-r1...")
            respuesta = await ollama.generar("deepseek-r1:7b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en CMOAssistant: {e}")
            return "📢 Asistente del CMO operativo. Desarrolla estrategias de posicionamiento y campañas."
