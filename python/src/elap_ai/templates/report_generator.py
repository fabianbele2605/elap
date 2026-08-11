"""Generador dinámico de reportes HTML profesionales con datos de agentes"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import json
from dataclasses import dataclass


@dataclass
class KPICard:
    """Tarjeta KPI para reportes"""
    label: str
    value: str
    change: str
    status: str  # 'positive', 'warning', 'alert'
    icon: str = "📊"


@dataclass
class ReportData:
    """Estructura de datos para un reporte"""
    title: str
    subtitle: str
    agent_name: str
    kpi_cards: List[KPICard]
    executive_summary: str
    sections: List[Dict[str, Any]]
    recommendations: List[str]
    next_steps_short: List[str]
    next_steps_medium: List[str]
    generated_date: Optional[str] = None
    company: str = "Andina Foods S.A.S."


class ReportGenerator:
    """Genera reportes HTML profesionales para agentes ELAP"""

    def __init__(self):
        self.template_path = "/home/fabian/Escritorio/agenteC/python/src/elap_ai/templates/professional_report.html"

    def generate_html(self, data: ReportData) -> str:
        """Genera HTML a partir de datos estructurados"""

        if not data.generated_date:
            data.generated_date = datetime.now().strftime("%d de %B de %Y")

        # Build KPI cards HTML
        kpi_html = self._build_kpi_cards(data.kpi_cards)

        # Build sections HTML
        sections_html = self._build_sections(data.sections)

        # Build recommendations
        recommendations_html = self._build_recommendations(data.recommendations)

        # Build next steps
        next_steps_html = self._build_next_steps(
            data.next_steps_short,
            data.next_steps_medium
        )

        # Generate final HTML
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Ejecutivo - {data.company}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}

        /* Header */
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
            font-weight: 600;
        }}

        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}

        .header-meta {{
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
            font-size: 14px;
            opacity: 0.8;
        }}

        /* KPI Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .kpi-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 5px solid #2a5298;
            transition: transform 0.3s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}

        .kpi-card.positive {{
            border-left-color: #27ae60;
        }}

        .kpi-card.warning {{
            border-left-color: #f39c12;
        }}

        .kpi-card.alert {{
            border-left-color: #e74c3c;
        }}

        .kpi-label {{
            font-size: 13px;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }}

        .kpi-value {{
            font-size: 32px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 5px;
        }}

        .kpi-change {{
            font-size: 13px;
            color: #27ae60;
        }}

        .kpi-change.negative {{
            color: #e74c3c;
        }}

        /* Section */
        .section {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .section h2 {{
            font-size: 22px;
            color: #1e3c72;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #2a5298;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .section h3 {{
            font-size: 16px;
            color: #2c3e50;
            margin-top: 20px;
            margin-bottom: 10px;
        }}

        /* Table */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        thead {{
            background: #f8f9fa;
        }}

        th {{
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #2c3e50;
            border-bottom: 2px solid #e0e0e0;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        /* Status Badges */
        .badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .badge.success {{
            background: #d5f4e6;
            color: #27ae60;
        }}

        .badge.warning {{
            background: #fef5e7;
            color: #f39c12;
        }}

        .badge.alert {{
            background: #fadbd8;
            color: #e74c3c;
        }}

        /* List */
        .recommendation-list {{
            list-style: none;
            margin: 20px 0;
        }}

        .recommendation-list li {{
            padding: 12px 0;
            padding-left: 30px;
            position: relative;
            border-bottom: 1px solid #ecf0f1;
        }}

        .recommendation-list li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #27ae60;
            font-weight: bold;
            font-size: 18px;
        }}

        /* Chart Placeholder */
        .chart-container {{
            background: #f8f9fa;
            border: 2px dashed #bdc3c7;
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            color: #7f8c8d;
            margin: 20px 0;
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        /* Footer */
        .footer {{
            background: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin-top: 40px;
            font-size: 12px;
        }}

        /* Utilities */
        .highlight {{
            background: #fff9e6;
            padding: 2px 6px;
            border-radius: 3px;
            color: #d68910;
            font-weight: 600;
        }}

        .metric-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}

        /* Print Styles */
        @media print {{
            body {{
                background: white;
            }}
            .section {{
                page-break-inside: avoid;
                box-shadow: none;
                border: 1px solid #ddd;
            }}
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 24px;
            }}

            .kpi-grid {{
                grid-template-columns: 1fr;
            }}

            .metric-row {{
                grid-template-columns: 1fr;
            }}

            .header-meta {{
                flex-direction: column;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>{data.title}</h1>
            <p>{data.subtitle}</p>
            <div class="header-meta">
                <span>{data.company}</span>
                <span id="report-date">Generado: {data.generated_date}</span>
                <span>Agente: {data.agent_name}</span>
            </div>
        </div>

        <!-- KPI Cards -->
        <div class="kpi-grid">
            {kpi_html}
        </div>

        <!-- Resumen Ejecutivo -->
        <div class="section">
            <h2>📋 Resumen Ejecutivo</h2>
            <p>{data.executive_summary}</p>
        </div>

        <!-- Secciones Dinámicas -->
        {sections_html}

        <!-- Recomendaciones -->
        <div class="section">
            <h2>🎯 Recomendaciones Estratégicas</h2>
            <ol class="recommendation-list">
                {recommendations_html}
            </ol>
        </div>

        <!-- Próximos Pasos -->
        <div class="section">
            <h2>📅 Próximos Pasos</h2>
            <div class="metric-row">
                <div>
                    <h3>Corto Plazo (1-3 meses)</h3>
                    <ul class="recommendation-list">
                        {next_steps_html.split("|||")[0]}
                    </ul>
                </div>
                <div>
                    <h3>Mediano Plazo (3-6 meses)</h3>
                    <ul class="recommendation-list">
                        {next_steps_html.split("|||")[1]}
                    </ul>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>🔒 Documento Confidencial - {data.company} | Generado por ELAP Intelligence System</p>
            <p>Para descarga en PDF o más detalles, contacte al equipo respectivo</p>
        </div>
    </div>
</body>
</html>"""

        return html

    def _build_kpi_cards(self, kpi_cards: List[KPICard]) -> str:
        """Construye HTML para tarjetas KPI"""
        html = ""
        for card in kpi_cards:
            html += f"""
            <div class="kpi-card {card.status}">
                <div class="kpi-label">{card.icon} {card.label}</div>
                <div class="kpi-value">{card.value}</div>
                <div class="kpi-change {'negative' if card.change.startswith('↓') else ''}">{card.change}</div>
            </div>"""
        return html

    def _build_sections(self, sections: List[Dict[str, Any]]) -> str:
        """Construye secciones dinámicas HTML"""
        html = ""
        for section in sections:
            html += f"""
        <div class="section">
            <h2>{section.get('title', 'Sección')}</h2>
"""

            # Contenido de texto
            if 'content' in section:
                html += f"            <p>{section['content']}</p>\n"

            # Tabla si existe
            if 'table' in section:
                html += self._build_table(section['table'])

            html += "        </div>\n"

        return html

    def _build_table(self, table_data: Dict[str, Any]) -> str:
        """Construye tabla HTML"""
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])

        html = "<table>\n<thead>\n<tr>\n"
        for header in headers:
            html += f"<th>{header}</th>\n"
        html += "</tr>\n</thead>\n<tbody>\n"

        for row in rows:
            html += "<tr>\n"
            for value in row:
                html += f"<td>{value}</td>\n"
            html += "</tr>\n"

        html += "</tbody>\n</table>\n"
        return html

    def _build_recommendations(self, recommendations: List[str]) -> str:
        """Construye lista de recomendaciones"""
        html = ""
        for rec in recommendations:
            html += f"<li>{rec}</li>\n"
        return html

    def _build_next_steps(self, short_term: List[str], medium_term: List[str]) -> str:
        """Construye pasos siguientes"""
        short_html = ""
        for step in short_term:
            short_html += f"<li>{step}</li>\n"

        medium_html = ""
        for step in medium_term:
            medium_html += f"<li>{step}</li>\n"

        return f"{short_html}|||{medium_html}"

    def save_html(self, html: str, filepath: str) -> str:
        """Guarda HTML a archivo"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return filepath


# Factory function para crear reportes de diferentes agentes
def create_agent_report(agent_name: str, agent_data: Dict[str, Any]) -> ReportData:
    """Crea un reporte adaptado al tipo de agente"""

    agent_name_lower = agent_name.lower()

    if 'finance' in agent_name_lower or 'cfo' in agent_name_lower:
        return _create_finance_report(agent_data)
    elif 'hr' in agent_name_lower or 'rrhh' in agent_name_lower:
        return _create_hr_report(agent_data)
    elif 'sales' in agent_name_lower or 'ventas' in agent_name_lower:
        return _create_sales_report(agent_data)
    elif 'ceo' in agent_name_lower:
        return _create_executive_report(agent_data)
    elif 'procurement' in agent_name_lower or 'compras' in agent_name_lower:
        return _create_procurement_report(agent_data)
    else:
        return _create_generic_report(agent_name, agent_data)


def _create_finance_report(data: Dict[str, Any]) -> ReportData:
    """Crea reporte financiero"""
    return ReportData(
        title="📊 Reporte Financiero Ejecutivo",
        subtitle="Análisis de desempeño y recomendaciones estratégicas",
        agent_name="CFO Assistant / Finanzas",
        kpi_cards=[
            KPICard("Ingresos Totales", data.get('ingresos', '$0'), "↑ 12% vs 2024", "positive", "💰"),
            KPICard("Utilidad Neta", data.get('utilidad', '$0'), "↑ 8% vs 2024", "positive", "📈"),
            KPICard("Margen Neto", data.get('margen', '0%'), "↑ 0.4pp vs sector", "positive", "📊"),
            KPICard("Clientes Activos", data.get('clientes', '0'), "↓ 3% vs 2024", "warning", "👥"),
        ],
        executive_summary=data.get('resumen', 'Análisis financiero del período'),
        sections=[
            {
                'title': '💼 Análisis Detallado',
                'content': data.get('analisis', 'Análisis pendiente'),
                'table': {
                    'headers': ['Métrica', 'Valor', 'Estado'],
                    'rows': data.get('metricas', [])
                }
            }
        ],
        recommendations=data.get('recomendaciones', []),
        next_steps_short=data.get('corto_plazo', []),
        next_steps_medium=data.get('mediano_plazo', [])
    )


def _create_hr_report(data: Dict[str, Any]) -> ReportData:
    """Crea reporte de recursos humanos"""
    return ReportData(
        title="👥 Reporte de Recursos Humanos",
        subtitle="Análisis de equipo y recomendaciones de gestión",
        agent_name="HR Agent / Recursos Humanos",
        kpi_cards=[
            KPICard("Empleados Activos", data.get('empleados', '0'), "↑ 5% vs 2024", "positive", "👤"),
            KPICard("Rotación Anual", data.get('rotacion', '0%'), "↓ 2% vs 2024", "positive", "📊"),
            KPICard("Promedio Antigüedad", data.get('antiguedad', '0'), "→ Estable", "positive", "📅"),
            KPICard("Capacitaciones", data.get('capacitaciones', '0'), "↑ 15%", "positive", "🎓"),
        ],
        executive_summary=data.get('resumen', 'Análisis de recursos humanos'),
        sections=[
            {
                'title': '📋 Datos del Equipo',
                'content': data.get('analisis', 'Análisis pendiente'),
            }
        ],
        recommendations=data.get('recomendaciones', []),
        next_steps_short=data.get('corto_plazo', []),
        next_steps_medium=data.get('mediano_plazo', [])
    )


def _create_sales_report(data: Dict[str, Any]) -> ReportData:
    """Crea reporte comercial/ventas"""
    return ReportData(
        title="💼 Reporte de Ventas Comercial",
        subtitle="Análisis de desempeño comercial y estrategia",
        agent_name="Sales Agent / Ventas",
        kpi_cards=[
            KPICard("Ingresos", data.get('ingresos', '$0'), "↑ 18% vs 2024", "positive", "💵"),
            KPICard("Clientes Nuevos", data.get('clientes_nuevos', '0'), "↑ 12%", "positive", "🆕"),
            KPICard("Tasa Cierre", data.get('tasa_cierre', '0%'), "↑ 8%", "positive", "🎯"),
            KPICard("Ticket Promedio", data.get('ticket', '$0'), "↑ 5%", "positive", "🏷️"),
        ],
        executive_summary=data.get('resumen', 'Análisis de ventas'),
        sections=[],
        recommendations=data.get('recomendaciones', []),
        next_steps_short=data.get('corto_plazo', []),
        next_steps_medium=data.get('mediano_plazo', [])
    )


def _create_executive_report(data: Dict[str, Any]) -> ReportData:
    """Crea reporte ejecutivo CEO"""
    return ReportData(
        title="🏢 Reporte Ejecutivo - Dirección General",
        subtitle="Perspectiva estratégica integral del negocio",
        agent_name="CEO Assistant / Dirección Ejecutiva",
        kpi_cards=[
            KPICard("Ingresos Anuales", data.get('ingresos', '$0'), "↑ 15%", "positive", "📊"),
            KPICard("Utilidad Operacional", data.get('utilidad', '$0'), "↑ 10%", "positive", "💰"),
            KPICard("ROE", data.get('roe', '0%'), "↑ 3%", "positive", "📈"),
            KPICard("Crecimiento Proyectado", data.get('crecimiento', '0%'), "→ En curso", "positive", "🚀"),
        ],
        executive_summary=data.get('resumen', 'Análisis ejecutivo'),
        sections=[],
        recommendations=data.get('recomendaciones', []),
        next_steps_short=data.get('corto_plazo', []),
        next_steps_medium=data.get('mediano_plazo', [])
    )


def _create_procurement_report(data: Dict[str, Any]) -> ReportData:
    """Crea reporte de procura/compras"""
    return ReportData(
        title="🛒 Reporte de Procura y Compras",
        subtitle="Análisis de eficiencia y gestión de proveedores",
        agent_name="Procurement Agent / Compras",
        kpi_cards=[
            KPICard("Ahorro Logrado", data.get('ahorro', '$0'), "↑ 8%", "positive", "💸"),
            KPICard("Proveedores Activos", data.get('proveedores', '0'), "↑ 5", "positive", "🤝"),
            KPICard("Tiempo Entrega", data.get('tiempo_entrega', '0'), "↓ 10%", "positive", "⏱️"),
            KPICard("Cumplimiento", data.get('cumplimiento', '0%'), "→ 98%", "positive", "✅"),
        ],
        executive_summary=data.get('resumen', 'Análisis de procura'),
        sections=[],
        recommendations=data.get('recomendaciones', []),
        next_steps_short=data.get('corto_plazo', []),
        next_steps_medium=data.get('mediano_plazo', [])
    )


def _create_generic_report(agent_name: str, data: Dict[str, Any]) -> ReportData:
    """Crea reporte genérico"""
    return ReportData(
        title=f"📋 Reporte - {agent_name}",
        subtitle="Análisis y recomendaciones",
        agent_name=agent_name,
        kpi_cards=[
            KPICard("Métrica 1", data.get('metrica_1', '-'), "→", "positive", "📊"),
            KPICard("Métrica 2", data.get('metrica_2', '-'), "→", "positive", "📈"),
            KPICard("Métrica 3", data.get('metrica_3', '-'), "→", "positive", "📋"),
            KPICard("Métrica 4", data.get('metrica_4', '-'), "→", "positive", "✅"),
        ],
        executive_summary=data.get('resumen', 'Análisis pendiente'),
        sections=[],
        recommendations=data.get('recomendaciones', []),
        next_steps_short=data.get('corto_plazo', []),
        next_steps_medium=data.get('mediano_plazo', [])
    )
