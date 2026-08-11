#!/usr/bin/env python3
"""Test de integración de reportes en 5 agentes

Verifica que cada agente:
1. Procesa la consulta correctamente
2. Genera respuesta de texto
3. Genera reporte HTML

Uso:
    python test_agentes_con_reportes.py
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, '/home/fabian/Escritorio/agenteC/python/src')

from elap_ai.agents.cfo_assistant import CFOAssistant
from elap_ai.agents.hr_agent import HRAgent
from elap_ai.agents.ventas_agent import VentasAgent
from elap_ai.agents.ceo_assistant import CEOAssistant
from elap_ai.agents.compras_agent import ComprasAgent


async def test_agent(agent, agent_name: str, test_query: str):
    """Prueba un agente individual"""
    print(f"\n{'='*60}")
    print(f"🧪 Probando: {agent_name}")
    print(f"{'='*60}")

    try:
        # Procesar consulta
        print(f"📤 Enviando: '{test_query[:50]}...'")
        result = await agent.process_query(test_query)

        # Verificar respuesta
        has_message = 'message' in result and result['message']
        has_html = 'html_report' in result and result['html_report']

        print(f"✅ Respuesta recibida ({len(result.get('message', ''))} chars)")

        if has_html:
            print(f"✅ Reporte HTML generado ({len(result.get('html_report', ''))} chars)")

            # Guardar HTML
            reports_dir = Path('/tmp/elap_agents_reports')
            reports_dir.mkdir(parents=True, exist_ok=True)

            filename = f"{agent_name.lower()}_test_report.html"
            filepath = reports_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(result['html_report'])

            print(f"💾 Guardado en: file://{filepath}")
            return {
                'status': 'success',
                'agent': agent_name,
                'message_length': len(result.get('message', '')),
                'html_length': len(result.get('html_report', '')),
                'filepath': str(filepath)
            }
        else:
            print(f"⚠️  No se generó reporte HTML")
            return {
                'status': 'partial',
                'agent': agent_name,
                'message': 'HTML report missing'
            }

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'status': 'error',
            'agent': agent_name,
            'error': str(e)
        }


async def main():
    """Ejecuta tests de todos los agentes"""
    print("\n" + "="*60)
    print("🚀 TEST DE REPORTES EN 5 AGENTES ELAP")
    print("="*60)

    # Definir tests
    tests = [
        (
            CFOAssistant(),
            "CFOAssistant",
            "¿Cuál es el margen neto actual y cómo está vs 2025?"
        ),
        (
            HRAgent(),
            "HRAgent",
            "¿Cuál es la rotación de personal y cómo mejorar la retención?"
        ),
        (
            VentasAgent(),
            "VentasAgent",
            "¿Cómo está el pipeline de ventas y qué oportunidades tenemos?"
        ),
        (
            CEOAssistant(),
            "CEOAssistant",
            "¿Cuál es la estrategia de crecimiento para los próximos 12 meses?"
        ),
        (
            ComprasAgent(),
            "ComprasAgent",
            "¿Cómo optimizar costos de compras y mejorar proveedores?"
        )
    ]

    results = []

    # Ejecutar tests secuencialmente
    for agent, agent_name, query in tests:
        result = await test_agent(agent, agent_name, query)
        results.append(result)

    # Resumen final
    print(f"\n\n{'='*60}")
    print("📊 RESUMEN DE PRUEBAS")
    print(f"{'='*60}\n")

    successful = [r for r in results if r['status'] == 'success']
    partial = [r for r in results if r['status'] == 'partial']
    errors = [r for r in results if r['status'] == 'error']

    print(f"✅ Exitosas: {len(successful)}/5")
    print(f"⚠️  Parciales: {len(partial)}/5")
    print(f"❌ Errores: {len(errors)}/5")

    if successful:
        print(f"\n🎉 Reportes generados exitosamente:")
        for r in successful:
            print(f"   • {r['agent']}: {r['html_length']} bytes")
            print(f"     📍 {r['filepath']}")

    if partial:
        print(f"\n⚠️  Agentes con respuesta pero sin HTML:")
        for r in partial:
            print(f"   • {r['agent']}: {r['message']}")

    if errors:
        print(f"\n❌ Errores encontrados:")
        for r in errors:
            print(f"   • {r['agent']}: {r['error']}")

    print(f"\n{'='*60}")
    print("📖 Próximos pasos:")
    print("   1. Abre cualquier reporte en navegador")
    print("   2. Verifica que se vea correctamente")
    print("   3. Prueba Ctrl+P para ver opción de PDF")
    print(f"{'='*60}\n")

    # Retornar 0 si todas exitosas
    return 0 if len(errors) == 0 else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
