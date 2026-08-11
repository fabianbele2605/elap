#!/usr/bin/env python3
"""Script de prueba para generar reportes profesionales

Uso:
    python test_reportes.py

Genera 3 reportes HTML de ejemplo y los guarda en /tmp/elap_reports/
"""

import sys
import asyncio
from pathlib import Path

# Agregar el módulo al path
sys.path.insert(0, '/home/fabian/Escritorio/agenteC/python/src')

from elap_ai.templates.report_generator import (
    ReportGenerator,
    ReportData,
    KPICard,
    create_agent_report
)


def generate_finance_report():
    """Genera reporte financiero de ejemplo"""
    print("\n📊 Generando Reporte Financiero...")

    data = ReportData(
        title="📊 Reporte Financiero Ejecutivo - CFO",
        subtitle="Análisis de desempeño Q3 2026",
        agent_name="CFO Assistant",
        kpi_cards=[
            KPICard("Ingresos Totales", "$21,200 MM", "↑ 12% vs 2025", "positive", "💰"),
            KPICard("Utilidad Neta", "$1,260 MM", "↑ 8% vs 2025", "positive", "📈"),
            KPICard("Margen Neto", "5.9%", "↑ 0.4pp vs sector", "positive", "📊"),
            KPICard("Clientes Activos", "1,450", "↓ 3% vs 2025", "warning", "👥"),
        ],
        executive_summary="""Andina Foods S.A.S. consolidó en 2026 una <span class="highlight">utilidad neta de $1,260 millones</span> con un <span class="highlight">margen neto del 5.9%</span>, generando ingresos de $21,200 millones. La empresa, con 187 empleados y 1,450 clientes activos, mantiene una posición sólida en el sector FMCG colombiano.

El análisis financiero muestra una <span class="highlight">eficiencia operativa excepcional</span> y un control de costos que respaldan su margen superior al promedio del sector. Sin embargo, se requiere optimizar la liquidez y explorar nuevas oportunidades de crecimiento regional.""",
        sections=[
            {
                'title': '💼 Análisis Detallado',
                'content': 'La empresa opera con una rentabilidad del 5.9%, por encima del promedio del sector FMCG (4.5-5.5%). Esta mejora se atribuye a optimización de costos operativos, mejor mix de productos y eficiencia en manufactura.',
                'table': {
                    'headers': ['Métrica', 'Valor 2026', 'vs 2025', 'Estado'],
                    'rows': [
                        ['Ingresos Totales', '$21,200 MM', '+12%', 'Excelente'],
                        ['Utilidad Neta', '$1,260 MM', '+8%', 'Positivo'],
                        ['Margen Neto', '5.9%', '+0.4pp', 'Superior al sector'],
                        ['ROE', '18.2%', '+2.1%', 'Sobresaliente'],
                        ['Liquidez Actual', '1.45x', '-0.15x', 'En revisión'],
                        ['Rotación Inventario', '7.2x', '+0.8x', 'Mejorado']
                    ]
                }
            }
        ],
        recommendations=[
            "Optimizar la rotación de inventarios mediante WMS, reduciendo costos en 8-12%",
            "Expandir regionalmente al Caribe con potencial de 18-22% crecimiento anual",
            "Digitalizar procesos core (ERP) para mejorar eficiencia operativa",
            "Fortalecer sostenibilidad en cadena de suministro alineando con ISO 14001",
            "Capacitar equipo comercial en estrategias de retención de clientes",
            "Diversificar proveedores reduciendo concentración de 42% a 35%"
        ],
        next_steps_short=[
            "Auditoría integral de inventarios y análisis de SKU",
            "Análisis de mercado Caribe: demanda, competencia, regulación",
            "Identificar quick wins para reducción de 3-5% costos",
            "Seleccionar partner para implementación WMS",
            "Diseñar programa de capacitación comercial"
        ],
        next_steps_medium=[
            "Implementar mejoras logísticas identificadas",
            "Lanzar piloto en ciudad Caribe (Barranquilla)",
            "Iniciar digitalización de procesos (fase 1: finanzas)",
            "Ejecutar capacitación para equipo comercial",
            "Establecer dashboard de KPIs en tiempo real"
        ]
    )

    generator = ReportGenerator()
    html = generator.generate_html(data)

    # Crear directorio si no existe
    report_dir = Path('/tmp/elap_reports')
    report_dir.mkdir(parents=True, exist_ok=True)

    # Guardar archivo
    report_path = report_dir / 'reporte_financiero_ejemplo.html'
    generator.save_html(html, str(report_path))

    print(f"✅ Reporte Financiero guardado en: {report_path}")
    return str(report_path)


def generate_hr_report():
    """Genera reporte de RRHH de ejemplo"""
    print("\n👥 Generando Reporte de Recursos Humanos...")

    data = ReportData(
        title="👥 Reporte de Recursos Humanos",
        subtitle="Análisis de equipo y desempeño 2026",
        agent_name="HR Agent",
        kpi_cards=[
            KPICard("Empleados Activos", "187", "↑ 5% vs 2025", "positive", "👤"),
            KPICard("Rotación Anual", "2.5%", "↓ 2% vs sector", "positive", "📊"),
            KPICard("Antigüedad Promedio", "5.2 años", "→ Estable", "positive", "📅"),
            KPICard("Capacitaciones", "45 horas/persona", "↑ 15%", "positive", "🎓"),
        ],
        executive_summary="""Andina Foods mantiene un equipo estable de <span class="highlight">187 colaboradores</span> con baja rotación anual del <span class="highlight">2.5%</span>, significativamente menor al promedio del sector (4-5%). La <span class="highlight">antigüedad promedio de 5.2 años</span> indica una cultura de retención efectiva.

Los programas de capacitación se han intensificado con <span class="highlight">45 horas/persona anuales</span>, reflejando inversión en desarrollo de talento y competitividad futura.""",
        sections=[
            {
                'title': '📋 Datos del Equipo',
                'content': 'El equipo está distribuido en 5 unidades administrativas, 3 de dirección, 4 comerciales y 2 de documentación. La composición es 62% personal administrativo y 38% personal operativo, con 35% de personal con educación superior.',
                'table': {
                    'headers': ['Área', 'Empleados', 'Rotación 2026', 'Antigüedad Prom.'],
                    'rows': [
                        ['Administrativo', '115', '2.1%', '5.5 años'],
                        ['Dirección', '28', '1.5%', '8.2 años'],
                        ['Comercial', '31', '3.2%', '3.8 años'],
                        ['Documentación', '13', '2.8%', '4.2 años']
                    ]
                }
            }
        ],
        recommendations=[
            "Mejorar retención de personal comercial con incentivos competitivos",
            "Aumentar programas de desarrollo ejecutivo para liderazgo futuro",
            "Fortalecer clima laboral con actividades de integración",
            "Implementar plan de sucesión para roles críticos",
            "Elevar meta de educación superior a 50% del equipo"
        ],
        next_steps_short=[
            "Evaluar satisfacción y engagement del equipo",
            "Identificar brechas de competencias por área",
            "Diseñar planes de desarrollo personalizados",
            "Revisar política salarial vs. mercado",
            "Definir programa de beneficios 2027"
        ],
        next_steps_medium=[
            "Ejecutar planes de desarrollo individual",
            "Implementar sistema de gestión por competencias",
            "Lanzar programa de mentoring ejecutivo",
            "Modernizar plataforma de RH (HRIS)",
            "Evaluar resultados y ajustar estrategia"
        ]
    )

    generator = ReportGenerator()
    html = generator.generate_html(data)

    report_dir = Path('/tmp/elap_reports')
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / 'reporte_rrhh_ejemplo.html'
    generator.save_html(html, str(report_path))

    print(f"✅ Reporte RRHH guardado en: {report_path}")
    return str(report_path)


def generate_sales_report():
    """Genera reporte de Ventas de ejemplo"""
    print("\n💼 Generando Reporte de Ventas...")

    data = ReportData(
        title="💼 Reporte de Ventas Comercial - Dirección",
        subtitle="Performance 2026 y estrategia H2",
        agent_name="Sales Agent",
        kpi_cards=[
            KPICard("Ingresos", "$21,200 MM", "↑ 18% vs 2025", "positive", "💵"),
            KPICard("Clientes Nuevos", "145", "↑ 12%", "positive", "🆕"),
            KPICard("Tasa de Cierre", "24%", "↑ 8%", "positive", "🎯"),
            KPICard("Ticket Promedio", "$68,000", "↑ 5%", "positive", "🏷️"),
        ],
        executive_summary="""El desempeño comercial de 2026 ha sido <span class="highlight">sobresaliente con crecimiento de 18%</span> respecto a 2025. Se adquirieron <span class="highlight">145 clientes nuevos</span> con una <span class="highlight">tasa de cierre del 24%</span>, indicando un pipeline saludable y efectividad del equipo de ventas.

El <span class="highlight">ticket promedio de $68,000</span> refleja una mejora en venta de productos de alto valor y una estrategia de upselling exitosa.""",
        sections=[
            {
                'title': '📊 Análisis de Canales',
                'content': 'Los canales de distribución muestran desempeño diferenciado. Canal Directo lidera con 52% de ingresos, Distribuidores aporta 35%, y Ecommerce crece aceleradamente con 13% de participación.',
                'table': {
                    'headers': ['Canal', 'Ingresos', '% Mix', 'Crecimiento', 'Margen'],
                    'rows': [
                        ['Canal Directo', '$11,024 MM', '52%', '16%', '8.2%'],
                        ['Distribuidores', '$7,420 MM', '35%', '18%', '5.4%'],
                        ['E-commerce', '$2,756 MM', '13%', '35%', '12.1%']
                    ]
                }
            }
        ],
        recommendations=[
            "Fortalecer equipo de ventas directas con specialistas por vertical",
            "Expandir canal E-commerce con presupuesto digital +40%",
            "Mejorar retención de clientes con programa de fidelización",
            "Implementar CRM para mejorar seguimiento y pipeline",
            "Desarrollar producto premium para segmento alto valor"
        ],
        next_steps_short=[
            "Analizar pipeline de oportunidades por región",
            "Identificar clientes en riesgo de churn",
            "Definir estrategia H2 2026 por línea",
            "Capacitar equipo en nuevos productos",
            "Establecer metas mensuales agresivas"
        ],
        next_steps_medium=[
            "Ejecutar estrategia regional de expansión",
            "Implementar CRM y automatización de ventas",
            "Lanzar programa de fidelización cliente",
            "Desarrollar presupuesto marketing digital 2027",
            "Reportar progreso con board mensual"
        ]
    )

    generator = ReportGenerator()
    html = generator.generate_html(data)

    report_dir = Path('/tmp/elap_reports')
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / 'reporte_ventas_ejemplo.html'
    generator.save_html(html, str(report_path))

    print(f"✅ Reporte Ventas guardado en: {report_path}")
    return str(report_path)


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("🚀 GENERADOR DE REPORTES PROFESIONALES ELAP - TEST")
    print("="*60)

    try:
        # Crear directorio si no existe
        Path('/tmp/elap_reports').mkdir(parents=True, exist_ok=True)

        # Generar reportes
        finance_path = generate_finance_report()
        hr_path = generate_hr_report()
        sales_path = generate_sales_report()

        print("\n" + "="*60)
        print("✅ TODOS LOS REPORTES GENERADOS EXITOSAMENTE")
        print("="*60)

        print("\n📍 Ubicaciones de archivos:")
        print(f"   1️⃣  Financiero: file://{finance_path}")
        print(f"   2️⃣  RRHH:      file://{hr_path}")
        print(f"   3️⃣  Ventas:    file://{sales_path}")

        print("\n📖 Próximos pasos:")
        print("   1. Abre cualquiera de los archivos en tu navegador")
        print("   2. Verifica que se vea correctamente")
        print("   3. Prueba Ctrl+P para vista previa de impresión/PDF")
        print("   4. Integra en los agentes según README_REPORTES.md")

        print("\n🔗 REST API:")
        print("   POST http://localhost:5000/api/reports/{agent_id}")
        print("   GET http://localhost:5000/api/reports/download/{filename}")

        print("\n" + "="*60 + "\n")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
