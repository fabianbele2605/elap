"""Ejemplo: Integración completa - Agentes generan documentos con IA"""

import asyncio
import sys
from pathlib import Path

# Agregar path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from elap_ai.agents.hr_agent import HRAgent
from elap_ai.agents.finance_agent import FinanceAgent


async def example_hr_generates_contract():
    """Ejemplo 1: Agente RRHH genera contrato"""
    print("\n" + "="*70)
    print("📄 EJEMPLO 1: AGENTE RRHH GENERA CONTRATO")
    print("="*70)

    # Inicializar agente
    hr_agent = HRAgent(theme="andina_foods")

    # Contenido generado por Ollama
    ollama_generated_content = """
El presente contrato establece una relación laboral entre Andina Foods S.A.
y el empleado mencionado. El empleado se compromete a desempeñar sus funciones
de manera profesional y ética.

Andina Foods proporciona los beneficios enumerados y garantiza un ambiente de
trabajo seguro. El contrato tendrá vigencia indefinida y podrá ser terminado
con treinta (30) días de notificación previa por escrito.
    """

    # Generar contrato
    result = await hr_agent.generate_contract(
        empresa="Andina Foods S.A.",
        empleado="Juan Carlos Pérez García",
        cargo="Gerente Regional de Ventas",
        salario=5000000,
        fecha_inicio="01/09/2026",
        beneficios=[
            "Seguro médico completo",
            "Bonificación anual",
            "Plan de pensión",
            "Capacitación y desarrollo"
        ],
        responsabilidades=[
            "Gestionar equipo de ventas",
            "Alcanzar metas de ingresos",
            "Desarrollar nuevos clientes",
            "Reportar al Director General"
        ],
        ai_content=ollama_generated_content,
        output_format="word"
    )

    print(f"\n✅ Status: {result['status']}")
    print(f"📝 Empleado: {result['employee']}")
    print(f"🏢 Empresa: {result['company']}")
    if result['status'] == 'success':
        print(f"📍 Path: {result['path']}")
        print(f"💬 {result['message']}")
    else:
        print(f"❌ Error: {result.get('error')}")


async def example_finance_generates_invoice():
    """Ejemplo 2: Agente Finanzas genera factura"""
    print("\n" + "="*70)
    print("🧾 EJEMPLO 2: AGENTE FINANZAS GENERA FACTURA")
    print("="*70)

    # Inicializar agente
    finance_agent = FinanceAgent(theme="andina_foods")

    # Generar factura
    result = await finance_agent.generate_invoice(
        numero="FAC-2026-001",
        empresa_emisor="Andina Foods S.A.",
        cliente="Supermercados La Prosperidad SAS",
        fecha_emision="15/08/2026",
        fecha_vencimiento="15/09/2026",
        items=[
            {
                "descripcion": "Pasta de tomate 500g - Caja x 24",
                "precio_unitario": 45000,
                "cantidad": 5
            },
            {
                "descripcion": "Conservas de frutas 400g - Caja x 12",
                "precio_unitario": 35000,
                "cantidad": 3
            },
            {
                "descripcion": "Granos secos variados 1kg - Caja x 10",
                "precio_unitario": 55000,
                "cantidad": 2
            }
        ],
        condiciones_pago="Pago a 30 días. Descuento 5% por pago de contado.",
        output_format="word"
    )

    print(f"\n✅ Status: {result['status']}")
    print(f"🧾 Factura: {result['invoice_number']}")
    print(f"👤 Cliente: {result['client']}")
    print(f"💰 Total: {result['total']}")
    if result['status'] == 'success':
        print(f"📍 Path: {result['path']}")
        print(f"💬 {result['message']}")
    else:
        print(f"❌ Error: {result.get('error')}")


async def example_finance_generates_report():
    """Ejemplo 3: Agente Finanzas genera reporte"""
    print("\n" + "="*70)
    print("📊 EJEMPLO 3: AGENTE FINANZAS GENERA REPORTE")
    print("="*70)

    # Inicializar agente
    finance_agent = FinanceAgent(theme="andina_foods")

    # Contenido generado por Ollama
    ollama_analysis = """
Durante el Q3 2026, Andina Foods experimentó un crecimiento del 15% en ventas.
Los productos estrella fueron las conservas de frutas (40%) y pasta de tomate (20%).

El análisis de mercado muestra demanda creciente de productos orgánicos. Se recomienda
expandir esta línea en un 25% durante Q4. La satisfacción del cliente se mantiene
en 92%, reflejando calidad consistente.

El margen bruto mejoró de 40% (Q2) a 42% (Q3), principalmente por optimización
de costos logísticos. Se proyecta estabilidad para Q4.
    """

    # Generar reporte
    result = await finance_agent.generate_report(
        titulo="Reporte Financiero Q3 2026",
        empresa="Andina Foods S.A.",
        periodo="Julio - Septiembre 2026",
        resumen_ejecutivo="""
Trimestre exitoso con crecimiento de 15% en ventas. Nuevos clientes: 23.
Tasa de retención: 92%. Margen bruto: 42% (mejora de 2 puntos).
        """,
        metricas={
            "Ventas Totales": "$2,450,000",
            "Crecimiento YoY": "+15%",
            "Nuevos Clientes": "23",
            "Tasa de Retención": "92%",
            "Margen Bruto": "42%",
            "Empleados": "450"
        },
        analisis=ollama_analysis,
        conclusiones="""
Recomendamos continuar con la estrategia actual, expandir línea orgánica,
fortalecer presencia online e invertir en certificaciones ambientales.
        """,
        output_format="word"
    )

    print(f"\n✅ Status: {result['status']}")
    print(f"📊 Reporte: {result['title']}")
    print(f"📅 Período: {result['period']}")
    if result['status'] == 'success':
        print(f"📍 Path: {result['path']}")
        print(f"💬 {result['message']}")
    else:
        print(f"❌ Error: {result.get('error')}")


async def main():
    """Ejecuta todos los ejemplos"""
    print("\n" + "="*70)
    print("🚀 FASE 4C: INTEGRACIÓN COMPLETA - AGENTES + DOCUMENT ENGINE")
    print("="*70)

    try:
        # Ejecutar ejemplos en paralelo
        await asyncio.gather(
            example_hr_generates_contract(),
            example_finance_generates_invoice(),
            example_finance_generates_report()
        )

        print("\n" + "="*70)
        print("✅ TODOS LOS EJEMPLOS COMPLETADOS EXITOSAMENTE")
        print("="*70)
        print("\n📁 Documentos generados:")
        print("   ├── contrato_Juan_Carlos_Pérez_García.docx")
        print("   ├── factura_FAC-2026-001.docx")
        print("   └── reporte_Reporte_Financiero_Q3_2026.docx")
        print("\n💡 Próximos pasos:")
        print("   1. Abre los documentos en Word")
        print("   2. Verifica que contengan datos personalizados")
        print("   3. Revisa que los temas corporativos se aplicaron")
        print("   4. Prueba con otros temas: 'default', 'professional'")

    except Exception as e:
        print(f"\n❌ Error durante ejecución: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
