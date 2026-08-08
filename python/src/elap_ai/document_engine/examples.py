"""Ejemplos de uso del Document Engine"""

from document_engine import DocumentEngine


def example_contract():
    """Ejemplo: Generar contrato"""
    engine = DocumentEngine(theme="andina_foods", language="es")

    contract_data = {
        "empresa": "Andina Foods",
        "empleado": "Juan Pérez García",
        "cargo": "Gerente de Ventas",
        "salario": 5000000,
        "fecha_inicio": "2026-09-01",
        "fecha_vigencia": "Indefinido",
        "beneficios": [
            "Seguro médico completo",
            "Bonificación anual",
            "Plan de pensiones",
            "Capacitación continua",
            "Política flexible de horarios"
        ],
        "responsabilidades": [
            "Gestionar equipo de ventas",
            "Alcanzar metas de ingresos",
            "Desarrollar nuevos clientes",
            "Reportar al Director General"
        ],
        "ai_content": """
        El presente contrato establece una relación laboral entre Andina Foods y Juan Pérez García.

        El empleado se compromete a desempeñar sus funciones de manera profesional y dentro de los
        horarios establecidos. Andina Foods proporciona los beneficios enumerados anteriormente
        y garantiza un ambiente de trabajo seguro y respetuoso.

        Este contrato estará vigente de manera indefinida y podrá ser terminado por cualquiera
        de las partes con treinta (30) días de notificación previa.
        """
    }

    # Generar en diferentes formatos
    word_path = engine.generate_word("contract", contract_data, "contrato_juan_perez.docx")
    pdf_path = engine.generate_pdf("contract", contract_data, "contrato_juan_perez.pdf")
    html_content = engine.generate_html("contract", contract_data)

    print(f"✅ Contrato Word: {word_path}")
    print(f"✅ Contrato PDF: {pdf_path}")
    print(f"✅ Contrato HTML generado")


def example_invoice():
    """Ejemplo: Generar factura"""
    engine = DocumentEngine(theme="andina_foods")

    invoice_data = {
        "numero": "FAC-2026-001",
        "empresa": "Andina Foods",
        "cliente": "Supermercados La Prosperidad",
        "fecha_emision": "2026-08-15",
        "fecha_vencimiento": "2026-09-15",
        "items": [
            {
                "descripcion": "Pasta de tomate 500g (caja x 24)",
                "precio_unitario": 45000,
                "cantidad": 5
            },
            {
                "descripcion": "Conservas de frutas 400g (caja x 12)",
                "precio_unitario": 35000,
                "cantidad": 3
            },
            {
                "descripcion": "Granos secos variados 1kg (caja x 10)",
                "precio_unitario": 55000,
                "cantidad": 2
            }
        ],
        "condiciones_pago": "Pago a 30 días. Se aplica descuento del 5% por pago de contado."
    }

    excel_path = engine.generate_excel("invoice", invoice_data, "factura_2026_001.xlsx")
    pdf_path = engine.generate_pdf("invoice", invoice_data, "factura_2026_001.pdf")

    print(f"✅ Factura Excel: {excel_path}")
    print(f"✅ Factura PDF: {pdf_path}")


def example_report():
    """Ejemplo: Generar reporte"""
    engine = DocumentEngine(theme="andina_foods")

    report_data = {
        "titulo": "Reporte Trimestral de Ventas",
        "empresa": "Andina Foods",
        "periodo": "Q3 2026",
        "seccion_ejecutiva": """
        Durante el tercer trimestre de 2026, Andina Foods experimentó un crecimiento
        del 15% en ventas comparado con el trimestre anterior. Los productos estrella
        fueron las conservas de frutas y la pasta de tomate, que representaron el 60%
        del volumen total de ventas.
        """,
        "metricas": {
            "Ventas Totales": "$2,450,000",
            "Crecimiento YoY": "+15%",
            "Nuevos Clientes": 23,
            "Tasa de Retención": "92%",
            "Margen Bruto": "42%"
        },
        "contenido_ia": """
        Análisis detallado de mercado indica que la demanda de productos orgánicos
        aumentó significativamente en el segmento retail. Recomendamos expandir
        la línea de productos orgánicos y fortalecer la presencia en tiendas
        online para capturar el crecimiento del e-commerce en alimentos.
        """,
        "conclusiones": """
        El trimestre fue muy exitoso. Recomendamos continuar con la estrategia
        actual, invertir en marketing digital y explorar nuevos mercados regionales.
        """
    }

    word_path = engine.generate_word("report", report_data, "reporte_q3_2026.docx")
    excel_path = engine.generate_excel("report", report_data, "reporte_q3_2026.xlsx")
    ppt_path = engine.generate_powerpoint("report", report_data, "reporte_q3_2026.pptx")

    print(f"✅ Reporte Word: {word_path}")
    print(f"✅ Reporte Excel: {excel_path}")
    print(f"✅ Reporte PowerPoint: {ppt_path}")


if __name__ == "__main__":
    print("📄 Generando ejemplos de documentos...\n")

    print("1️⃣  Generando Contrato...")
    example_contract()

    print("\n2️⃣  Generando Factura...")
    example_invoice()

    print("\n3️⃣  Generando Reporte...")
    example_report()

    print("\n✅ ¡Todos los documentos generados exitosamente!")
