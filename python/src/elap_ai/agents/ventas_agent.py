"""Ventas Agent - Nivel Comercial"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class VentasAgent:
    """Agente de Ventas - Gestión de ventas y prospectos"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        logger.info(f"VentasAgent initialized with theme: {theme}")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de ventas"""
        logger.info(f"Processing sales query: {query[:50]}...")

        response = await self._generate_sales_response(query)

        # Generar reporte HTML profesional
        html_report = await self._generate_html_report(response, query)

        return {
            "message": response,
            "html_report": html_report,
            "intent": "sales_management",
            "agent": "ventas_agent",
        }

    async def _generate_sales_response(self, query: str) -> str:
        """Generar respuesta de ventas con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("ventas_agent")

            prompt_ollama = f"""{system_prompt}

Consulta de Ventas: {query}

Proporciona estrategia de ventas, propuestas comerciales e identificación de prospectos."""

            logger.info("📈 Llamando a Ollama para gestión de ventas...")
            respuesta = await ollama.generar("glm4:9b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en VentasAgent: {e}")
            return "📈 Especialista en Ventas operativo. Gestiona oportunidades y pipeline comercial."

    async def _generate_html_report(self, response: str, query: str) -> str:
        """Generar reporte HTML profesional desde respuesta de ventas"""
        try:
            from ..templates.report_generator import ReportGenerator, ReportData, KPICard

            query_lower = query.lower()

            # KPIs según tipo de consulta
            if "pipeline" in query_lower or "oportunidad" in query_lower:
                kpi_cards = [
                    KPICard("Pipeline Abierto", "$8,500 MM", "↑ 18% vs 2025", "positive", "💵"),
                    KPICard("Tasa Cierre", "24%", "↑ 8% anual", "positive", "🎯"),
                    KPICard("Ciclo Venta", "32 días", "↓ 5 días", "positive", "⏱️"),
                    KPICard("Propuestas Activas", "156", "En evaluación", "positive", "📋"),
                ]
            elif "cliente" in query_lower or "prospect" in query_lower:
                kpi_cards = [
                    KPICard("Clientes Nuevos", "145", "↑ 12%", "positive", "🆕"),
                    KPICard("Retención", "97%", "Excelente", "positive", "✅"),
                    KPICard("Lifetime Value", "$850K", "↑ 15%", "positive", "💰"),
                    KPICard("NPS Score", "72", "Bueno", "positive", "📊"),
                ]
            else:
                # KPIs genéricos de ventas
                kpi_cards = [
                    KPICard("Ingresos", "$21,200 MM", "↑ 18% vs 2025", "positive", "💵"),
                    KPICard("Clientes Nuevos", "145", "↑ 12%", "positive", "🆕"),
                    KPICard("Tasa Cierre", "24%", "↑ 8%", "positive", "🎯"),
                    KPICard("Ticket Promedio", "$68,000", "↑ 5%", "positive", "🏷️"),
                ]

            # Crear reporte
            report_data = ReportData(
                title="💼 Reporte de Ventas Comercial",
                subtitle="Performance y estrategia comercial",
                agent_name="Sales Agent",
                kpi_cards=kpi_cards,
                executive_summary=response[:600],
                sections=[
                    {
                        'title': '📊 Análisis de Desempeño Comercial',
                        'content': response,
                    }
                ],
                recommendations=[
                    "Mejorar pipeline con prospectación activa",
                    "Aumentar clientes de alto valor",
                    "Optimizar ciclo de ventas",
                    "Fortalecer retención de clientes",
                    "Implementar CRM para seguimiento"
                ],
                next_steps_short=[
                    "Analizar pipeline por segmento",
                    "Identificar clientes en riesgo",
                    "Definir estrategia por línea",
                    "Capacitar equipo comercial"
                ],
                next_steps_medium=[
                    "Ejecutar plan de expansión",
                    "Implementar CRM y automatización",
                    "Lanzar programa de fidelización",
                    "Reportar progreso mensual"
                ]
            )

            # Generar HTML
            generator = ReportGenerator()
            html = generator.generate_html(report_data)

            logger.info("✅ Reporte HTML generado por VentasAgent")
            return html

        except Exception as e:
            logger.error(f"Error generando reporte Ventas: {e}")
            return ""
