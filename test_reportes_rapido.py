#!/usr/bin/env python3
"""Test rápido de generación de reportes (sin Ollama)

Verifica que los 5 agentes pueden generar reportes HTML
usando respuestas mockeadas (sin esperar a Ollama)
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, '/home/fabian/Escritorio/agenteC/python/src')

from elap_ai.templates.report_generator import ReportGenerator, ReportData, KPICard


async def generate_mock_reports():
    """Genera reportes para cada tipo de agente sin Ollama"""

    reports = {
        'CFOAssistant': {
            'title': '📊 Análisis Financiero Ejecutivo - CFO',
            'subtitle': 'Análisis detallado y recomendaciones estratégicas',
            'agent_name': 'CFO Assistant',
            'kpi_cards': [
                KPICard("Ingresos Totales", "$21,200 MM", "↑ 12% vs 2025", "positive", "💰"),
                KPICard("Utilidad Neta", "$1,260 MM", "↑ 8% vs 2025", "positive", "📈"),
                KPICard("Margen Neto", "5.9%", "↑ 0.4pp vs sector", "positive", "📊"),
                KPICard("ROE", "18.2%", "Sobresaliente", "positive", "🎯"),
            ],
            'executive_summary': 'Análisis financiero de 2026: Andina Foods consolidó una utilidad neta de $1,260 millones con margen neto del 5.9%, generando ingresos de $21,200 millones. La empresa mantiene posición sólida en sector FMCG.',
            'recommendations': [
                "Optimizar estructura de costos operativos",
                "Mejorar rotación de inventarios",
                "Fortalecer gestión de flujo de caja"
            ],
            'next_steps_short': ["Revisar análisis CFO", "Identificar optimizaciones"],
            'next_steps_medium': ["Implementar mejoras", "Monitorear KPIs"]
        },
        'HRAgent': {
            'title': '👥 Reporte de Recursos Humanos',
            'subtitle': 'Análisis de personal y recomendaciones',
            'agent_name': 'HR Agent',
            'kpi_cards': [
                KPICard("Empleados Activos", "187", "↑ 5% vs 2025", "positive", "👤"),
                KPICard("Rotación Anual", "2.5%", "↓ 2% vs sector", "positive", "📊"),
                KPICard("Antigüedad Promedio", "5.2 años", "Estable", "positive", "📅"),
                KPICard("Capacitaciones", "45 hrs/persona", "↑ 15%", "positive", "🎓"),
            ],
            'executive_summary': 'Equipo estable de 187 colaboradores con baja rotación del 2.5%, significativamente menor al promedio sector. Inversión en desarrollo: 45 horas/persona anuales.',
            'recommendations': [
                "Mejorar retención de talento crítico",
                "Fortalecer programas de desarrollo",
                "Aumentar flexibilidad laboral"
            ],
            'next_steps_short': ["Revisar satisfacción", "Identificar brechas"],
            'next_steps_medium': ["Ejecutar planes", "Monitorear KPIs"]
        },
        'VentasAgent': {
            'title': '💼 Reporte de Ventas Comercial',
            'subtitle': 'Performance y estrategia comercial',
            'agent_name': 'Sales Agent',
            'kpi_cards': [
                KPICard("Ingresos", "$21,200 MM", "↑ 18% vs 2025", "positive", "💵"),
                KPICard("Clientes Nuevos", "145", "↑ 12%", "positive", "🆕"),
                KPICard("Tasa Cierre", "24%", "↑ 8%", "positive", "🎯"),
                KPICard("Ticket Promedio", "$68,000", "↑ 5%", "positive", "🏷️"),
            ],
            'executive_summary': 'Desempeño comercial sobresaliente con crecimiento de 18%. Adquisición de 145 clientes nuevos con tasa de cierre del 24% e incremento en ticket promedio.',
            'recommendations': [
                "Mejorar pipeline con prospectación activa",
                "Aumentar clientes de alto valor",
                "Optimizar ciclo de ventas"
            ],
            'next_steps_short': ["Analizar pipeline", "Identificar riesgos"],
            'next_steps_medium': ["Ejecutar plan", "Implementar CRM"]
        },
        'CEOAssistant': {
            'title': '🏢 Reporte Ejecutivo - Dirección General',
            'subtitle': 'Perspectiva estratégica integral del negocio',
            'agent_name': 'CEO Assistant',
            'kpi_cards': [
                KPICard("Ingresos Anuales", "$21,200 MM", "↑ 12%", "positive", "📊"),
                KPICard("Utilidad Operacional", "$1,260 MM", "↑ 8%", "positive", "💰"),
                KPICard("ROE", "18.2%", "Sobresaliente", "positive", "📈"),
                KPICard("Crecimiento Proyectado", "15%", "2027", "positive", "🚀"),
            ],
            'executive_summary': 'Perspectiva estratégica: Andina Foods posiciona para crecimiento acelerado. Ingresos $21.2B, margen 5.9%, ROE 18.2%. Oportunidades en expansión regional y diversificación.',
            'recommendations': [
                "Ejecutar plan de expansión regional",
                "Fortalecer innovación y desarrollo",
                "Mejorar eficiencia operativa"
            ],
            'next_steps_short': ["Validar estrategia", "Comunicar a junta"],
            'next_steps_medium': ["Ejecutar iniciativas", "Asignar recursos"]
        },
        'ComprasAgent': {
            'title': '🛒 Reporte de Procura y Compras',
            'subtitle': 'Análisis de eficiencia y gestión de proveedores',
            'agent_name': 'Procurement Agent',
            'kpi_cards': [
                KPICard("Ahorro Logrado", "$180 MM", "↑ 8%", "positive", "💸"),
                KPICard("Proveedores Activos", "65", "↑ 5", "positive", "🤝"),
                KPICard("Tiempo Entrega", "32 días", "↓ 8 días", "positive", "⏱️"),
                KPICard("Cumplimiento", "98%", "Excelente", "positive", "✅"),
            ],
            'executive_summary': 'Gestión eficiente de procura: Ahorro de $180MM, 65 proveedores activos, tiempo entrega 32 días, cumplimiento 98%. Base proveedores optimizada.',
            'recommendations': [
                "Consolidar base de proveedores críticos",
                "Implementar long-term agreements",
                "Mejorar logística y distribución"
            ],
            'next_steps_short': ["Revisar proveedores", "Identificar ahorros"],
            'next_steps_medium': ["Ejecutar renegociaciones", "Automatizar"]
        }
    }

    print("\n" + "="*60)
    print("🚀 GENERANDO REPORTES - VERSION RÁPIDA (SIN OLLAMA)")
    print("="*60 + "\n")

    generator = ReportGenerator()
    reports_dir = Path('/tmp/elap_agents_reports')
    reports_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for agent_name, data_dict in reports.items():
        print(f"📝 Generando reporte: {agent_name}...")

        try:
            # Crear ReportData
            report_data = ReportData(
                title=data_dict['title'],
                subtitle=data_dict['subtitle'],
                agent_name=data_dict['agent_name'],
                kpi_cards=data_dict['kpi_cards'],
                executive_summary=data_dict['executive_summary'],
                sections=[
                    {
                        'title': '📊 Análisis Detallado',
                        'content': data_dict['executive_summary'],
                    }
                ],
                recommendations=data_dict['recommendations'],
                next_steps_short=data_dict['next_steps_short'],
                next_steps_medium=data_dict['next_steps_medium']
            )

            # Generar HTML
            html = generator.generate_html(report_data)

            # Guardar archivo
            filename = f"{agent_name.lower()}_reporte.html"
            filepath = reports_dir / filename
            generator.save_html(html, str(filepath))

            size_kb = len(html) / 1024

            print(f"   ✅ {filename}: {size_kb:.1f} KB")

            results.append({
                'agent': agent_name,
                'status': 'success',
                'filepath': str(filepath),
                'size': len(html)
            })

        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'agent': agent_name,
                'status': 'error',
                'error': str(e)
            })

    # Resumen
    print("\n" + "="*60)
    print("✅ REPORTES GENERADOS EXITOSAMENTE")
    print("="*60 + "\n")

    for r in results:
        agent = r['agent']
        if r['status'] == 'success':
            print(f"✅ {agent}")
            print(f"   📍 file://{r['filepath']}")
            print(f"   📊 Tamaño: {r['size']/1024:.1f} KB\n")
        else:
            print(f"❌ {agent}: {r.get('error')}\n")

    print("="*60)
    print("📖 Próximos pasos:")
    print("   1. Abre cualquier reporte en navegador")
    print("   2. Verifica diseño responsive")
    print("   3. Prueba Ctrl+P para PDF")
    print(f"\n📊 Total: {len(results)} reportes generados")
    print("="*60 + "\n")

    return 0


if __name__ == "__main__":
    exit(asyncio.run(generate_mock_reports()))
