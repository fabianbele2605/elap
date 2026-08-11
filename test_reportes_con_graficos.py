#!/usr/bin/env python3
"""Test de reportes con gráficos Chart.js interactivos

Demuestra cómo agregar gráficos a los reportes de los 5 agentes
"""

import sys
from pathlib import Path

sys.path.insert(0, '/home/fabian/Escritorio/agenteC/python/src')

from elap_ai.templates.report_generator import ReportGenerator, ReportData, KPICard
from elap_ai.templates.report_generator_with_charts import (
    create_financial_charts,
    create_hr_charts,
    create_sales_charts,
    generate_html_with_charts,
    CHART_STYLES
)


def generate_finance_report_with_charts():
    """Genera reporte financiero con gráficos"""
    print("📊 Generando reporte financiero con gráficos...")

    # Crear reporte base
    kpi_cards = [
        KPICard("Ingresos Totales", "$21,200 MM", "↑ 12% vs 2025", "positive", "💰"),
        KPICard("Utilidad Neta", "$1,260 MM", "↑ 8% vs 2025", "positive", "📈"),
        KPICard("Margen Neto", "5.9%", "↑ 0.4pp vs sector", "positive", "📊"),
        KPICard("ROE", "18.2%", "Sobresaliente", "positive", "🎯"),
    ]

    report_data = ReportData(
        title="📊 Análisis Financiero Ejecutivo - CON GRÁFICOS",
        subtitle="Dashboard interactivo con visualización de datos",
        agent_name="CFO Assistant",
        kpi_cards=kpi_cards,
        executive_summary="Análisis de ingresos, márgenes y distribución por línea de negocio con gráficos interactivos.",
        sections=[
            {
                'title': '💼 Análisis Financiero 2026',
                'content': 'Andina Foods consolidó utilidad neta de $1,260MM con margen del 5.9%. Análisis detallado en gráficos interactivos.',
            }
        ],
        recommendations=[
            "Optimizar rotación de inventarios",
            "Expandir a mercados Caribe",
            "Mejorar eficiencia operativa"
        ],
        next_steps_short=["Revisar gráficos", "Validar números"],
        next_steps_medium=["Implementar mejoras", "Monitorear KPIs"]
    )

    # Generar HTML base
    generator = ReportGenerator()
    base_html = generator.generate_html(report_data)

    # Agregar estilos para gráficos
    base_html = base_html.replace("</head>", f"{CHART_STYLES}</head>")

    # Crear gráficos específicos para finanzas
    charts = create_financial_charts()

    # Inyectar gráficos
    final_html = generate_html_with_charts(base_html, charts)

    # Guardar
    reports_dir = Path('/tmp/elap_reports_with_charts')
    reports_dir.mkdir(parents=True, exist_ok=True)

    filepath = reports_dir / 'cfo_con_graficos.html'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"   ✅ Guardado: file://{filepath}")
    print(f"   📊 Incluye 3 gráficos interactivos (Chart.js)")
    return str(filepath)


def generate_hr_report_with_charts():
    """Genera reporte HR con gráficos"""
    print("👥 Generando reporte HR con gráficos...")

    kpi_cards = [
        KPICard("Empleados Activos", "187", "↑ 5% vs 2025", "positive", "👤"),
        KPICard("Rotación Anual", "2.5%", "↓ 2% vs sector", "positive", "📊"),
        KPICard("Antigüedad Promedio", "5.2 años", "Estable", "positive", "📅"),
        KPICard("Capacitaciones", "45 hrs/persona", "↑ 15%", "positive", "🎓"),
    ]

    report_data = ReportData(
        title="👥 Reporte de Recursos Humanos - CON GRÁFICOS",
        subtitle="Dashboard de personal con visualización interactiva",
        agent_name="HR Agent",
        kpi_cards=kpi_cards,
        executive_summary="Análisis de personal: 187 empleados, rotación 2.5%, antigüedad 5.2 años. Gráficos interactivos incluidos.",
        sections=[
            {
                'title': '📋 Análisis de Equipo',
                'content': 'Equipo estable con baja rotación y buena antigüedad. Inversión en capacitación: 45 horas/persona.',
            }
        ],
        recommendations=[
            "Mejorar retención de talento",
            "Fortalecer desarrollo",
            "Aumentar flexibilidad laboral"
        ],
        next_steps_short=["Revisar datos", "Identificar brechas"],
        next_steps_medium=["Ejecutar planes", "Monitorear"]
    )

    generator = ReportGenerator()
    base_html = generator.generate_html(report_data)
    base_html = base_html.replace("</head>", f"{CHART_STYLES}</head>")

    charts = create_hr_charts()
    final_html = generate_html_with_charts(base_html, charts)

    reports_dir = Path('/tmp/elap_reports_with_charts')
    reports_dir.mkdir(parents=True, exist_ok=True)

    filepath = reports_dir / 'hr_con_graficos.html'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"   ✅ Guardado: file://{filepath}")
    print(f"   📊 Incluye 3 gráficos interactivos (Chart.js)")
    return str(filepath)


def generate_sales_report_with_charts():
    """Genera reporte de ventas con gráficos"""
    print("💼 Generando reporte de Ventas con gráficos...")

    kpi_cards = [
        KPICard("Ingresos", "$21,200 MM", "↑ 18% vs 2025", "positive", "💵"),
        KPICard("Clientes Nuevos", "145", "↑ 12%", "positive", "🆕"),
        KPICard("Tasa Cierre", "24%", "↑ 8%", "positive", "🎯"),
        KPICard("Ticket Promedio", "$68,000", "↑ 5%", "positive", "🏷️"),
    ]

    report_data = ReportData(
        title="💼 Reporte de Ventas - CON GRÁFICOS",
        subtitle="Dashboard comercial con análisis interactivo",
        agent_name="Sales Agent",
        kpi_cards=kpi_cards,
        executive_summary="Desempeño comercial: Ingresos $21.2B (+18%), 145 clientes nuevos, tasa cierre 24%. Análisis por canal y línea.",
        sections=[
            {
                'title': '📊 Análisis Comercial',
                'content': 'Pipeline saludable, distribución equilibrada entre canales. E-commerce con crecimiento acelerado.',
            }
        ],
        recommendations=[
            "Mejorar pipeline",
            "Aumentar clientes altos",
            "Optimizar ciclo ventas"
        ],
        next_steps_short=["Analizar pipeline", "Identificar riesgos"],
        next_steps_medium=["Ejecutar plan", "Implementar CRM"]
    )

    generator = ReportGenerator()
    base_html = generator.generate_html(report_data)
    base_html = base_html.replace("</head>", f"{CHART_STYLES}</head>")

    charts = create_sales_charts()
    final_html = generate_html_with_charts(base_html, charts)

    reports_dir = Path('/tmp/elap_reports_with_charts')
    reports_dir.mkdir(parents=True, exist_ok=True)

    filepath = reports_dir / 'ventas_con_graficos.html'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"   ✅ Guardado: file://{filepath}")
    print(f"   📊 Incluye 3 gráficos interactivos (Chart.js)")
    return str(filepath)


def main():
    """Genera todos los reportes con gráficos"""
    print("\n" + "="*60)
    print("🚀 GENERADOR DE REPORTES CON GRÁFICOS CHART.JS")
    print("="*60 + "\n")

    filepaths = [
        generate_finance_report_with_charts(),
        generate_hr_report_with_charts(),
        generate_sales_report_with_charts(),
    ]

    print("\n" + "="*60)
    print("✅ TODOS LOS REPORTES GENERADOS CON GRÁFICOS")
    print("="*60 + "\n")

    print("📊 Gráficos incluidos:")
    print("   ✅ Gráficos de línea (tendencias)")
    print("   ✅ Gráficos de pastel (distribución)")
    print("   ✅ Gráficos de barras (comparativas)")
    print("   ✅ Totalmente interactivos (Chart.js 3.9)")
    print("\n")

    print("📍 Ubicaciones:")
    for fp in filepaths:
        print(f"   🔗 file://{fp}")

    print("\n" + "="*60)
    print("📖 Próximos pasos:")
    print("   1. Abre cualquier reporte en navegador")
    print("   2. Interactúa con los gráficos")
    print("   3. Pasa mouse para ver tooltips")
    print("   4. Clic en leyenda para show/hide series")
    print("="*60 + "\n")

    return 0


if __name__ == "__main__":
    exit(main())
