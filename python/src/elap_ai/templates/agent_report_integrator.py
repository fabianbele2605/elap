"""Integrador de reportes con agentes ELAP

Permite que cualquier agente genere reportes HTML profesionales.
"""

import asyncio
import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime


class AgentReportIntegrator:
    """Integra generación de reportes con agentes"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def generate_report_from_agent_response(
        self,
        agent_id: str,
        agent_response: str,
        agent_name: str,
        title: str,
        subtitle: str
    ) -> Dict[str, Any]:
        """Genera un reporte basado en la respuesta de un agente"""

        try:
            # Aquí podríamos parsear la respuesta del agente para extraer datos estructurados
            # Por ahora, crearemos un reporte genérico

            payload = {
                "title": title,
                "subtitle": subtitle,
                "executive_summary": agent_response[:500],  # Primeros 500 chars
                "kpi_data": [
                    {
                        "label": "Métrica Principal",
                        "value": "Procesado",
                        "change": "→",
                        "status": "positive",
                        "icon": "📊"
                    }
                ],
                "sections": [
                    {
                        "title": "Análisis del Agente",
                        "content": agent_response
                    }
                ],
                "recommendations": [
                    "Implementar las acciones recomendadas por el agente",
                    "Monitorear los indicadores clave",
                    "Revisar periódicamente los resultados"
                ],
                "next_steps_short": [
                    "Revisar el análisis detallado",
                    "Identificar prioridades",
                    "Asignar responsables"
                ],
                "next_steps_medium": [
                    "Ejecutar plan de acción",
                    "Establecer seguimiento",
                    "Reportar resultados"
                ]
            }

            response = await self.client.post(
                f"{self.base_url}/api/reports/{agent_id}",
                json=payload,
                timeout=30.0
            )

            result = response.json()
            return {
                'status': 'success',
                'report_id': result.get('report_id'),
                'filename': result.get('filename'),
                'html': result.get('html'),
                'url': result.get('url')
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    async def create_finance_report(
        self,
        ingresos: str = "$0",
        utilidad: str = "$0",
        margen: str = "0%",
        clientes: str = "0",
        resumen: str = "",
        analisis: str = "",
        metricas: list = None,
        recomendaciones: list = None
    ) -> Dict[str, Any]:
        """Genera reporte financiero especializado"""

        if metricas is None:
            metricas = [
                ["Ingresos", ingresos, "Positivo"],
                ["Utilidad", utilidad, "Positivo"],
                ["Margen", margen, "Normal"],
                ["Clientes", clientes, "Por revisar"]
            ]

        if recomendaciones is None:
            recomendaciones = [
                "Optimizar rotación de inventarios",
                "Explorar expansión regional",
                "Mejorar eficiencia operativa"
            ]

        payload = {
            "title": "📊 Reporte Financiero Ejecutivo",
            "subtitle": "Análisis de desempeño y recomendaciones estratégicas",
            "executive_summary": resumen or "Análisis financiero del período",
            "kpi_data": [
                {
                    "label": "Ingresos Totales",
                    "value": ingresos,
                    "change": "↑ 12% vs período anterior",
                    "status": "positive",
                    "icon": "💰"
                },
                {
                    "label": "Utilidad Neta",
                    "value": utilidad,
                    "change": "↑ 8% vs período anterior",
                    "status": "positive",
                    "icon": "📈"
                },
                {
                    "label": "Margen Neto",
                    "value": margen,
                    "change": "↑ 0.4pp vs promedio sector",
                    "status": "positive",
                    "icon": "📊"
                },
                {
                    "label": "Clientes Activos",
                    "value": clientes,
                    "change": "→ Estable",
                    "status": "warning",
                    "icon": "👥"
                }
            ],
            "sections": [
                {
                    "title": "💼 Análisis Detallado",
                    "content": analisis or "Análisis financiero pendiente",
                    "table": {
                        "headers": ["Métrica", "Valor", "Estado"],
                        "rows": metricas
                    }
                }
            ],
            "recommendations": recomendaciones,
            "next_steps_short": [
                "Auditoría de inventarios",
                "Análisis de oportunidades",
                "Identificar optimizaciones"
            ],
            "next_steps_medium": [
                "Implementar mejoras",
                "Lanzar iniciativas",
                "Monitorear resultados"
            ]
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/api/reports/finance",
                json=payload,
                timeout=30.0
            )

            result = response.json()
            return {
                'status': 'success',
                'report': result
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    async def create_hr_report(
        self,
        empleados: str = "0",
        rotacion: str = "0%",
        antiguedad: str = "0",
        capacitaciones: str = "0",
        resumen: str = "",
        recomendaciones: list = None
    ) -> Dict[str, Any]:
        """Genera reporte de recursos humanos especializado"""

        if recomendaciones is None:
            recomendaciones = [
                "Mejorar retención de talento",
                "Aumentar programas de capacitación",
                "Fortalecer clima laboral"
            ]

        payload = {
            "title": "👥 Reporte de Recursos Humanos",
            "subtitle": "Análisis de equipo y recomendaciones de gestión",
            "executive_summary": resumen or "Análisis de recursos humanos",
            "kpi_data": [
                {
                    "label": "Empleados Activos",
                    "value": empleados,
                    "change": "↑ 5% vs año anterior",
                    "status": "positive",
                    "icon": "👤"
                },
                {
                    "label": "Rotación Anual",
                    "value": rotacion,
                    "change": "↓ 2% vs sector",
                    "status": "positive",
                    "icon": "📊"
                },
                {
                    "label": "Antigüedad Promedio",
                    "value": antiguedad,
                    "change": "→ Estable",
                    "status": "positive",
                    "icon": "📅"
                },
                {
                    "label": "Capacitaciones",
                    "value": capacitaciones,
                    "change": "↑ 15% anual",
                    "status": "positive",
                    "icon": "🎓"
                }
            ],
            "sections": [],
            "recommendations": recomendaciones,
            "next_steps_short": [
                "Revisar indicadores de personal",
                "Identificar brechas de competencias",
                "Planificar desarrollo"
            ],
            "next_steps_medium": [
                "Ejecutar planes de desarrollo",
                "Implementar retención",
                "Medir resultados"
            ]
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/api/reports/hr",
                json=payload,
                timeout=30.0
            )

            result = response.json()
            return {
                'status': 'success',
                'report': result
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    async def create_sales_report(
        self,
        ingresos: str = "$0",
        clientes_nuevos: str = "0",
        tasa_cierre: str = "0%",
        ticket_promedio: str = "$0",
        resumen: str = "",
        recomendaciones: list = None
    ) -> Dict[str, Any]:
        """Genera reporte de ventas especializado"""

        if recomendaciones is None:
            recomendaciones = [
                "Mejorar pipeline de ventas",
                "Aumentar clientes de alto valor",
                "Optimizar ciclo de ventas"
            ]

        payload = {
            "title": "💼 Reporte de Ventas Comercial",
            "subtitle": "Análisis de desempeño comercial y estrategia",
            "executive_summary": resumen or "Análisis de ventas",
            "kpi_data": [
                {
                    "label": "Ingresos",
                    "value": ingresos,
                    "change": "↑ 18% vs período anterior",
                    "status": "positive",
                    "icon": "💵"
                },
                {
                    "label": "Clientes Nuevos",
                    "value": clientes_nuevos,
                    "change": "↑ 12%",
                    "status": "positive",
                    "icon": "🆕"
                },
                {
                    "label": "Tasa de Cierre",
                    "value": tasa_cierre,
                    "change": "↑ 8%",
                    "status": "positive",
                    "icon": "🎯"
                },
                {
                    "label": "Ticket Promedio",
                    "value": ticket_promedio,
                    "change": "↑ 5%",
                    "status": "positive",
                    "icon": "🏷️"
                }
            ],
            "sections": [],
            "recommendations": recomendaciones,
            "next_steps_short": [
                "Analizar pipeline de oportunidades",
                "Identificar clientes en riesgo",
                "Planificar acciones"
            ],
            "next_steps_medium": [
                "Ejecutar estrategia comercial",
                "Fortalecer relaciones clave",
                "Reportar progreso"
            ]
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/api/reports/sales",
                json=payload,
                timeout=30.0
            )

            result = response.json()
            return {
                'status': 'success',
                'report': result
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }


# Ejemplo de uso
async def demo_report_generation():
    """Demuestra cómo generar reportes"""

    async with AgentReportIntegrator() as integrator:
        # Generar reporte financiero
        finance_report = await integrator.create_finance_report(
            ingresos="$21,200 MM",
            utilidad="$1,260 MM",
            margen="5.9%",
            clientes="1,450",
            resumen="Andina Foods consolidó utilidad neta de $1,260 millones con margen neto del 5.9%",
            analisis="Eficiencia operativa excepcional con control de costos superior al sector",
            recomendaciones=[
                "Optimizar rotación de inventarios",
                "Expandir a mercados Caribe",
                "Digitalizar procesos",
                "Fortalecer sostenibilidad",
                "Capacitar equipo comercial"
            ]
        )

        print("Reporte Financiero:", finance_report)

        # Generar reporte de RRHH
        hr_report = await integrator.create_hr_report(
            empleados="187",
            rotacion="2.5%",
            antiguedad="5.2 años",
            capacitaciones="45 horas/persona",
            resumen="Equipo estable con buena retención y desarrollo",
            recomendaciones=[
                "Fortalecer programas de desarrollo",
                "Mejorar retención ejecutiva",
                "Aumentar diversidad"
            ]
        )

        print("Reporte HR:", hr_report)

        # Generar reporte de Ventas
        sales_report = await integrator.create_sales_report(
            ingresos="$8,500 MM",
            clientes_nuevos="125",
            tasa_cierre="24%",
            ticket_promedio="$68,000",
            resumen="Desempeño comercial sobresaliente con crecimiento en todas las líneas",
            recomendaciones=[
                "Fortalecer equipo comercial",
                "Expandir canal digital",
                "Mejorar retención de clientes"
            ]
        )

        print("Reporte Ventas:", sales_report)


if __name__ == "__main__":
    asyncio.run(demo_report_generation())
