"""Document Manager Agent - Nivel Documentación con datos REALES"""

import logging
from typing import Dict, Any

from elap_ai.data_agent_mixin import DataAgentMixin

logger = logging.getLogger(__name__)


class DocumentManagerAgent(DataAgentMixin):
    """Agente Gestor Documental - Administra documentos y archivos con datos REALES"""

    def __init__(self, theme: str = "andina_foods"):
        super().__init__()
        self.theme = theme
        logger.info(f"DocumentManagerAgent initialized with theme: {theme} - usando datos REALES")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de gestión documental"""
        logger.info(f"Processing document management query: {query[:50]}...")

        query_lower = query.lower()

        # ==================== DATOS REALES ====================
        # Palabras clave para documentos
        documento_keywords = ["documento", "archivo", "transacción", "factura", "comprobante", "registro"]

        if any(kw in query_lower for kw in documento_keywords):
            logger.info("📄 Detectada pregunta sobre documentos - usando datos REALES")

            try:
                transacciones = await self.obtener_datos_reales("transactions", limite=100)

                if transacciones:
                    respuesta = f"""📄 **GESTIÓN DE DOCUMENTOS Y REGISTROS (DATOS REALES)**
==================================================================

📊 **RESUMEN DE TRANSACCIONES DOCUMENTADAS**
  • Total de Transacciones: {len(transacciones)}
  • Documentos Registrados: {len(transacciones)}

📋 **ÚLTIMAS TRANSACCIONES**

"""
                    # Mostrar últimas 10 transacciones
                    for idx, trans in enumerate(transacciones[-10:], 1):
                        fecha = trans.get('fecha', 'N/A')
                        canal = trans.get('canal', 'Desconocido')
                        valor = trans.get('valor_total', 0)
                        respuesta += f"{idx}. [{fecha}] {canal}: ${valor:,.0f}\n"

                    respuesta += "\n✅ Registros desde PostgreSQL en tiempo real."

                    return {
                        "intent": "documento_query",
                        "message": respuesta
                    }
            except Exception as e:
                logger.error(f"Error obteniendo datos de documentos: {e}")

        response = await self._generate_document_response(query)

        return {
            "message": response,
            "intent": "document_management",
            "agent": "document_manager_agent",
        }

    async def _generate_document_response(self, query: str) -> str:
        """Generar respuesta de gestión documental con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("document_manager_agent")

            prompt_ollama = f"""{system_prompt}

Consulta Documental: {query}

Proporciona clasificación, organización y políticas de retención documental."""

            logger.info("📑 Llamando a Ollama para gestión documental...")
            respuesta = await ollama.generar("glm4:9b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en DocumentManagerAgent: {e}")
            return "📑 Gestor Documental operativo. Clasifica y organiza documentos empresariales."
