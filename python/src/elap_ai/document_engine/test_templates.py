"""Test de plantillas con docxtpl"""

import sys
from pathlib import Path

# Agregar path para importar desde el paquete
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from elap_ai.document_engine import DocumentEngine


def test_contract_template():
    """Prueba generación de contrato con plantilla"""
    print("🧪 Probando plantilla de contrato...")

    engine = DocumentEngine(theme="andina_foods", language="es")

    contract_data = {
        "empresa": "Andina Foods S.A.",
        "empleado": "Juan Carlos Pérez García",
        "cargo": "Gerente Regional de Ventas",
        "salario": 5000000,
        "fecha_inicio": "1 de septiembre de 2026",
        "beneficios": [
            "Seguro médico integral para el empleado y familia",
            "Bonificación anual según desempeño",
            "Plan de pensión complementaria",
            "Capacitación y desarrollo profesional",
            "Política flexible de horarios"
        ],
        "responsabilidades": [
            "Gestionar y liderar equipo de ventas regional",
            "Alcanzar metas de ingresos y presupuesto",
            "Desarrollar nuevos clientes y mantener relaciones",
            "Reportar semanalmente al Director General",
            "Implementar estrategias comerciales aprobadas"
        ],
        "ai_content": """El presente contrato establece una relación laboral de tiempo completo entre
Andina Foods S.A. y el empleado mencionado. El empleado se compromete a desempeñar sus funciones
de manera profesional, ética y dentro de los horarios establecidos.

Andina Foods proporciona los beneficios enumerados anteriormente y garantiza un ambiente de trabajo
seguro, respetuoso e inclusivo. El empleado tendrá derecho a los beneficios legales vigentes en la
República de Colombia.

Este contrato estará vigente de manera indefinida y podrá ser terminado por cualquiera de las partes
con treinta (30) días de notificación previa por escrito, o inmediatamente por justa causa conforme
a la ley laboral colombiana."""
    }

    try:
        path = engine.generate_word("contract", contract_data, "test_contrato.docx")
        print(f"✅ Contrato generado: {path}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_invoice_template():
    """Prueba generación de factura con plantilla"""
    print("🧪 Probando plantilla de factura...")

    engine = DocumentEngine(theme="andina_foods")

    invoice_data = {
        "numero": "FAC-2026-001",
        "empresa": "Andina Foods S.A.",
        "cliente": "Supermercados La Prosperidad SAS",
        "fecha_emision": "15 de agosto de 2026",
        "fecha_vencimiento": "15 de septiembre de 2026",
        "items": [
            {
                "descripcion": "Pasta de tomate 500g - Caja x 24 unidades",
                "precio_unitario": 45000,
                "cantidad": 5
            },
            {
                "descripcion": "Conservas de frutas 400g - Caja x 12 unidades",
                "precio_unitario": 35000,
                "cantidad": 3
            },
            {
                "descripcion": "Granos secos variados 1kg - Caja x 10 unidades",
                "precio_unitario": 55000,
                "cantidad": 2
            }
        ],
        "condiciones_pago": """Pago a 30 días neto. Se aplica descuento del 5% por pago de contado.
Envíos a cargo del cliente. Devoluciones únicamente dentro de 8 días de recibida la mercancía."""
    }

    try:
        path = engine.generate_word("invoice", invoice_data, "test_factura.docx")
        print(f"✅ Factura generada: {path}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_report_template():
    """Prueba generación de reporte con plantilla"""
    print("🧪 Probando plantilla de reporte...")

    engine = DocumentEngine(theme="andina_foods")

    report_data = {
        "titulo": "Reporte de Desempeño Trimestral Q3 2026",
        "empresa": "Andina Foods S.A.",
        "periodo": "Julio - Septiembre 2026",
        "seccion_ejecutiva": """Durante el tercer trimestre de 2026, Andina Foods experimentó un crecimiento
notable del 15% en ventas comparado con el trimestre anterior. Los productos estrella fueron las conservas
de frutas y la pasta de tomate, que representaron el 60% del volumen total de ventas. La satisfacción
del cliente se mantuvo en 92%, reflejando la calidad de nuestros productos y servicios.""",
        "metricas": {
            "Ventas Totales": "$2,450,000",
            "Crecimiento YoY": "+15%",
            "Nuevos Clientes": "23",
            "Tasa de Retención": "92%",
            "Margen Bruto": "42%",
            "Empleados Activos": "450"
        },
        "contenido_ia": """Análisis detallado del mercado indica que la demanda de productos orgánicos
y de origen local aumentó significativamente en el segmento retail. Los consumidores muestran preferencia
por productos con certificación ambiental. Recomendamos expandir la línea de productos orgánicos y
fortalecer la presencia en tiendas online para capturar el crecimiento del e-commerce en alimentos,
que presentó un crecimiento del 28% este trimestre.""",
        "conclusiones": """El trimestre fue muy exitoso. Recomendamos: (1) continuar con la estrategia
de marketing digital, (2) invertir en certificaciones ambientales, (3) explorar nuevos mercados
regionales en la zona cafetera, y (4) fortalecer relaciones con distribuidores mayoristas."""
    }

    try:
        path = engine.generate_word("report", report_data, "test_reporte.docx")
        print(f"✅ Reporte generado: {path}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Iniciando pruebas de plantillas corporativas...\n")

    results = []
    results.append(("Contrato", test_contract_template()))
    print()
    results.append(("Factura", test_invoice_template()))
    print()
    results.append(("Reporte", test_report_template()))

    print("\n" + "="*50)
    print("📊 RESULTADOS DE PRUEBAS")
    print("="*50)

    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{name:15} {status}")

    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 ¡Todas las pruebas pasaron!")
        print("\n💾 Documentos generados:")
        print("   - test_contrato.docx")
        print("   - test_factura.docx")
        print("   - test_reporte.docx")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores.")
