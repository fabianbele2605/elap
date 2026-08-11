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

        # Generar reporte HTML profesional
        html_report = await self._generate_html_report(response, query)

        return {
            "message": response,
            "html_report": html_report,
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
            respuesta = await ollama.generar("glm4:9b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en CEOAssistant: {e}")
            return "👔 Asistente Ejecutivo operativo. Analiza estrategia y oportunidades de crecimiento."

    async def _generate_html_report(self, response: str, query: str) -> str:
        """Generar reporte HTML ejecutivo"""
        try:
            from ..templates.report_generator import ReportGenerator, ReportData, KPICard

            query_lower = query.lower()

            # KPIs según tipo de consulta
            if "estrategia" in query_lower or "crecimiento" in query_lower:
                kpi_cards = [
                    KPICard("Crecimiento Anual", "12%", "vs sector: 8%", "positive", "📈"),
                    KPICard("Mercados Nuevos", "2", "En desarrollo", "positive", "🌎"),
                    KPICard("Inversión R&D", "$420 MM", "↑ 18%", "positive", "🔬"),
                    KPICard("ROIC", "22%", "Excepcional", "positive", "💰"),
                ]
            elif "riesgo" in query_lower or "oportunidad" in query_lower:
                kpi_cards = [
                    KPICard("Matriz Riesgos", "Actualizada", "Q3 2026", "positive", "⚠️"),
                    KPICard("Oportunidades", "8", "Identificadas", "positive", "🎯"),
                    KPICard("Contingencia", "$800 MM", "Disponible", "positive", "💵"),
                    KPICard("Exposición", "Moderada", "Controlada", "positive", "✅"),
                ]
            else:
                # KPIs genéricos ejecutivos
                kpi_cards = [
                    KPICard("Ingresos Anuales", "$21,200 MM", "↑ 12%", "positive", "📊"),
                    KPICard("Utilidad Operacional", "$1,260 MM", "↑ 8%", "positive", "💰"),
                    KPICard("ROE", "18.2%", "Sobresaliente", "positive", "📈"),
                    KPICard("Crecimiento Proyectado", "15%", "2027", "positive", "🚀"),
                ]

            # Crear reporte
            report_data = ReportData(
                title="🏢 Reporte Ejecutivo - Dirección General",
                subtitle="Perspectiva estratégica integral del negocio",
                agent_name="CEO Assistant",
                kpi_cards=kpi_cards,
                executive_summary=response[:600],
                sections=[
                    {
                        'title': '📋 Análisis Estratégico',
                        'content': response,
                    }
                ],
                recommendations=[
                    "Ejecutar plan de expansión regional",
                    "Fortalecer innovación y desarrollo",
                    "Mejorar eficiencia operativa",
                    "Desarrollar liderazgo futuro",
                    "Maximizar valor para stakeholders"
                ],
                next_steps_short=[
                    "Revisar análisis estratégico",
                    "Validar supuestos con CFO",
                    "Comunicar a junta directiva",
                    "Definir prioridades ejecutivas"
                ],
                next_steps_medium=[
                    "Ejecutar iniciativas estratégicas",
                    "Asignar recursos y presupuestos",
                    "Monitorear KPIs clave",
                    "Reportar a accionistas"
                ]
            )

            # Generar HTML
            generator = ReportGenerator()
            html = generator.generate_html(report_data)

            logger.info("✅ Reporte HTML generado por CEOAssistant")
            return html

        except Exception as e:
            logger.error(f"Error generando reporte CEO: {e}")
            return ""
