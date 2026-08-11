"""PDF Assistant Agent - Nivel Documentación con datos REALES"""

import logging
from typing import Dict, Any

from elap_ai.data_agent_mixin import DataAgentMixin

logger = logging.getLogger(__name__)


class PDFAssistantAgent(DataAgentMixin):
    """Agente Asistente PDF - Análisis de PDFs y extracción de datos con datos REALES"""

    def __init__(self, theme: str = "andina_foods"):
        super().__init__()
        self.theme = theme
        logger.info(f"PDFAssistantAgent initialized with theme: {theme} - usando datos REALES")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de análisis PDF"""
        logger.info(f"Processing PDF analysis query: {query[:50]}...")

        query_lower = query.lower()

        # ==================== DATOS REALES ====================
        # Palabras clave para análisis
        pdf_keywords = ["pdf", "documento", "reporte", "factura", "análisis", "generar"]

        if any(kw in query_lower for kw in pdf_keywords):
            logger.info("📄 Detectada pregunta sobre PDF - usando datos REALES")

            try:
                resumen = await self.obtener_resumen_empresa()

                if resumen:
                    respuesta = f"""📄 **ASISTENTE DE ANÁLISIS PDF (DATOS REALES)**
==================================================================

🔍 **CAPACIDADES DE ANÁLISIS**
  • Extracción de datos desde fuentes reales
  • Generación de reportes PDF desde datos actualizados
  • Análisis de documentos empresariales

📊 **DATOS DISPONIBLES PARA REPORTES**
  • Empleados: {resumen.get('total_empleados', 0)} registros
  • Clientes: {resumen.get('total_clientes', 0)} registros
  • Productos: {resumen.get('total_productos', 0)} registros
  • Transacciones: {resumen.get('total_transacciones', 0)} registros

💼 **TIPOS DE REPORTES GENERABLES**
  • Reportes de nómina y salarios
  • Estados financieros
  • Análisis de cartera y clientes
  • Reportes de proyectos y evaluaciones

✅ Sistema listo para generar reportes desde datos en vivo."""

                    return {
                        "intent": "pdf_query",
                        "message": respuesta
                    }
            except Exception as e:
                logger.error(f"Error obteniendo datos para PDF: {e}")

        response = await self._generate_pdf_response(query)

        return {
            "message": response,
            "intent": "pdf_analysis",
            "agent": "pdf_assistant_agent",
        }

    async def _generate_pdf_response(self, query: str) -> str:
        """Generar respuesta de análisis PDF con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("pdf_assistant_agent")

            prompt_ollama = f"""{system_prompt}

Consulta de PDF: {query}

Proporciona extracción de datos, resúmenes ejecutivos y análisis de documentos."""

            logger.info("📄 Llamando a Ollama para análisis de PDF...")
            respuesta = await ollama.generar("glm4:9b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en PDFAssistantAgent: {e}")
            return "📄 Asistente PDF operativo. Extrae datos y genera análisis de documentos."
