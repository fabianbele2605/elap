"""Script para generar plantillas base en Word"""

from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def add_header_footer(doc, theme_color):
    """Agrega header y footer a documento"""
    section = doc.sections[0]

    # Header
    header = section.header
    header_para = header.paragraphs[0]
    header_para.text = "{{empresa_nombre}}"
    header_para.style = "Header"
    header_run = header_para.runs[0]
    header_run.font.size = Pt(10)
    header_run.font.color.rgb = theme_color

    # Footer
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.text = "Documento confidencial - {{fecha_generacion}}"
    footer_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    footer_run = footer_para.runs[0]
    footer_run.font.size = Pt(9)
    footer_run.font.color.rgb = RGBColor(128, 128, 128)


def set_page_margins(doc, top=2.54, bottom=2.54, left=2.54, right=2.54):
    """Configura márgenes de página en cm"""
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(top / 2.54)
        section.bottom_margin = Inches(bottom / 2.54)
        section.left_margin = Inches(left / 2.54)
        section.right_margin = Inches(right / 2.54)


def create_contract_template():
    """Crea plantilla de contrato"""
    print("📄 Creando plantilla de contrato...")

    doc = Document()
    theme_color = RGBColor(45, 80, 22)  # Verde Andina
    set_page_margins(doc)
    add_header_footer(doc, theme_color)

    # Título
    title = doc.add_paragraph()
    title_run = title.add_run("CONTRATO DE TRABAJO")
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = theme_color
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    # Espacios
    doc.add_paragraph()

    # Sección 1: Información básica
    info = doc.add_paragraph()
    info_run = info.add_run("1. INFORMACIÓN GENERAL")
    info_run.font.size = Pt(12)
    info_run.font.bold = True
    info_run.font.color.rgb = theme_color

    # Tabla de información
    table = doc.add_table(rows=6, cols=2)
    table.style = "Light Grid Accent 1"

    # Encabezados
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Campo"
    hdr_cells[1].text = "Valor"

    # Datos
    rows_data = [
        ("Empresa", "{{empresa}}"),
        ("Empleado", "{{empleado}}"),
        ("Cargo", "{{cargo}}"),
        ("Fecha de Inicio", "{{fecha_inicio}}"),
        ("Salario Mensual", "${{salario}}")
    ]

    for idx, (label, value) in enumerate(rows_data, 1):
        cells = table.rows[idx].cells
        cells[0].text = label
        cells[1].text = value

    doc.add_paragraph()

    # Sección 2: Beneficios
    benef = doc.add_paragraph()
    benef_run = benef.add_run("2. BENEFICIOS INCLUIDOS")
    benef_run.font.size = Pt(12)
    benef_run.font.bold = True
    benef_run.font.color.rgb = theme_color

    doc.add_paragraph(
        "El empleado tendrá derecho a los siguientes beneficios:",
        style="List Bullet"
    )

    # Beneficios dinámicos (docxtpl)
    for_para = doc.add_paragraph("{%for beneficio in beneficios%}")
    for_para.paragraph_format.left_indent = Inches(0.5)
    for_para.add_run("• {{beneficio}}").font.size = Pt(11)
    doc.add_paragraph("{%endfor%}")

    doc.add_paragraph()

    # Sección 3: Responsabilidades
    resp = doc.add_paragraph()
    resp_run = resp.add_run("3. RESPONSABILIDADES PRINCIPALES")
    resp_run.font.size = Pt(12)
    resp_run.font.bold = True
    resp_run.font.color.rgb = theme_color

    for_resp = doc.add_paragraph("{%for responsabilidad in responsabilidades%}")
    for_resp.paragraph_format.left_indent = Inches(0.5)
    for_resp.add_run("• {{responsabilidad}}").font.size = Pt(11)
    doc.add_paragraph("{%endfor%}")

    doc.add_paragraph()

    # Sección 4: Contenido generado por IA
    ia_sec = doc.add_paragraph()
    ia_run = ia_sec.add_run("4. TÉRMINOS Y CONDICIONES")
    ia_run.font.size = Pt(12)
    ia_run.font.bold = True
    ia_run.font.color.rgb = theme_color

    ia_content = doc.add_paragraph("{{ai_content}}")
    ia_content.paragraph_format.line_spacing = 1.15

    doc.add_paragraph()
    doc.add_paragraph()

    # Firmas
    sig_para = doc.add_paragraph()
    sig_para.add_run("FIRMAS Y ACEPTACIÓN").font.bold = True
    sig_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    doc.add_paragraph()

    # Tabla de firmas
    sig_table = doc.add_table(rows=3, cols=2)
    sig_table.style = "Table Grid"

    sig_cells = sig_table.rows[0].cells
    sig_cells[0].text = "Por la Empresa"
    sig_cells[1].text = "Por el Empleado"

    # Líneas para firma
    for row in sig_table.rows[1:]:
        for cell in row.cells:
            cell.text = "_" * 40

    # Guardar
    template_path = Path(__file__).parent / "word" / "contract_template.docx"
    template_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(template_path))
    print(f"✅ Plantilla de contrato creada: {template_path}")


def create_invoice_template():
    """Crea plantilla de factura"""
    print("📊 Creando plantilla de factura...")

    doc = Document()
    theme_color = RGBColor(45, 80, 22)
    set_page_margins(doc)

    # Título
    title = doc.add_paragraph()
    title_run = title.add_run("FACTURA")
    title_run.font.size = Pt(20)
    title_run.font.bold = True
    title_run.font.color.rgb = theme_color
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    doc.add_paragraph()

    # Información general
    info_table = doc.add_table(rows=4, cols=2)
    info_table.style = "Light Grid"

    data = [
        ("Número de Factura", "{{numero}}"),
        ("Fecha de Emisión", "{{fecha_emision}}"),
        ("Cliente", "{{cliente}}"),
        ("Fecha de Vencimiento", "{{fecha_vencimiento}}")
    ]

    for idx, (label, value) in enumerate(data):
        cells = info_table.rows[idx].cells
        cells[0].text = label
        cells[1].text = value

    doc.add_paragraph()

    # Tabla de items
    items_title = doc.add_paragraph()
    items_title_run = items_title.add_run("DETALLE DE PRODUCTOS/SERVICIOS")
    items_title_run.font.bold = True
    items_title_run.font.color.rgb = theme_color

    items_table = doc.add_table(rows=1, cols=4)
    items_table.style = "Light Grid Accent 1"

    hdr_cells = items_table.rows[0].cells
    hdr_cells[0].text = "Descripción"
    hdr_cells[1].text = "Precio Unitario"
    hdr_cells[2].text = "Cantidad"
    hdr_cells[3].text = "Total"

    # Items dinámicos
    for_items = doc.add_paragraph("{%for item in items%}")
    for_items.style = "Normal"

    # Crear fila con variables
    item_row = items_table.add_row()
    item_row.cells[0].text = "{{item.descripcion}}"
    item_row.cells[1].text = "${{item.precio_unitario}}"
    item_row.cells[2].text = "{{item.cantidad}}"
    item_row.cells[3].text = "${{item.total}}"

    doc.add_paragraph("{%endfor%}")

    doc.add_paragraph()

    # Totales
    total_table = doc.add_table(rows=3, cols=2)
    total_table.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT

    total_cells = total_table.rows[0].cells
    total_cells[0].text = "SUBTOTAL:"
    total_cells[1].text = "${{subtotal}}"

    tax_cells = total_table.rows[1].cells
    tax_cells[0].text = "IMPUESTO (19%):"
    tax_cells[1].text = "${{impuesto}}"

    final_cells = total_table.rows[2].cells
    final_cells[0].text = "TOTAL:"
    final_run = final_cells[1].paragraphs[0].add_run("${{total}}")
    final_run.font.bold = True
    final_run.font.size = Pt(12)

    doc.add_paragraph()

    # Condiciones
    cond = doc.add_paragraph()
    cond_run = cond.add_run("CONDICIONES DE PAGO")
    cond_run.font.bold = True
    cond_run.font.color.rgb = theme_color

    cond_text = doc.add_paragraph("{{condiciones_pago}}")
    cond_text.paragraph_format.line_spacing = 1.15

    # Guardar
    template_path = Path(__file__).parent / "word" / "invoice_template.docx"
    template_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(template_path))
    print(f"✅ Plantilla de factura creada: {template_path}")


def create_report_template():
    """Crea plantilla de reporte"""
    print("📋 Creando plantilla de reporte...")

    doc = Document()
    theme_color = RGBColor(45, 80, 22)
    set_page_margins(doc)
    add_header_footer(doc, theme_color)

    # Título
    title = doc.add_paragraph()
    title_run = title.add_run("{{titulo}}")
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = theme_color
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    # Metadatos
    meta = doc.add_paragraph()
    meta.add_run(f"Empresa: ").font.bold = True
    meta.add_run("{{empresa}}")
    meta.add_run(f"\nPeríodo: ").font.bold = True
    meta.add_run("{{periodo}}")

    doc.add_paragraph()

    # Resumen Ejecutivo
    summary = doc.add_paragraph()
    summary_run = summary.add_run("1. RESUMEN EJECUTIVO")
    summary_run.font.size = Pt(12)
    summary_run.font.bold = True
    summary_run.font.color.rgb = theme_color

    summary_content = doc.add_paragraph("{{seccion_ejecutiva}}")
    summary_content.paragraph_format.line_spacing = 1.15

    doc.add_paragraph()

    # Métricas
    metrics = doc.add_paragraph()
    metrics_run = metrics.add_run("2. MÉTRICAS CLAVE")
    metrics_run.font.size = Pt(12)
    metrics_run.font.bold = True
    metrics_run.font.color.rgb = theme_color

    metrics_table = doc.add_table(rows=1, cols=2)
    metrics_table.style = "Light Grid Accent 1"
    hdr = metrics_table.rows[0].cells
    hdr[0].text = "Métrica"
    hdr[1].text = "Valor"

    # Métricas dinámicas
    for_metrics = doc.add_paragraph("{%for metrica, valor in metricas.items()%}")
    metric_row = metrics_table.add_row()
    metric_row.cells[0].text = "{{metrica}}"
    metric_row.cells[1].text = "{{valor}}"
    doc.add_paragraph("{%endfor%}")

    doc.add_paragraph()

    # Análisis
    analysis = doc.add_paragraph()
    analysis_run = analysis.add_run("3. ANÁLISIS DETALLADO")
    analysis_run.font.size = Pt(12)
    analysis_run.font.bold = True
    analysis_run.font.color.rgb = theme_color

    analysis_content = doc.add_paragraph("{{contenido_ia}}")
    analysis_content.paragraph_format.line_spacing = 1.15

    doc.add_paragraph()

    # Conclusiones
    conclusion = doc.add_paragraph()
    conclusion_run = conclusion.add_run("4. CONCLUSIONES")
    conclusion_run.font.size = Pt(12)
    conclusion_run.font.bold = True
    conclusion_run.font.color.rgb = theme_color

    conclusion_content = doc.add_paragraph("{{conclusiones}}")
    conclusion_content.paragraph_format.line_spacing = 1.15

    # Guardar
    template_path = Path(__file__).parent / "word" / "report_template.docx"
    template_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(template_path))
    print(f"✅ Plantilla de reporte creada: {template_path}")


if __name__ == "__main__":
    print("🔨 Generando plantillas corporativas...\n")
    create_contract_template()
    create_invoice_template()
    create_report_template()
    print("\n✅ ¡Todas las plantillas creadas exitosamente!")
    print("\n💡 Próximos pasos:")
    print("   1. Abre las plantillas en Word")
    print("   2. Personaliza colores, logos y diseño")
    print("   3. Agrega más variables {{como_estas}} si necesitas")
    print("   4. Guarda los cambios")
