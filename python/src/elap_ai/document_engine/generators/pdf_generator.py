"""PDF Generator usando WeasyPrint o Borb"""

import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Genera documentos PDF profesionales"""

    def __init__(self, theme: Dict[str, Any], language: str = "es"):
        self.theme = theme
        self.language = language

    def generate(self, document_type: str, data: Dict[str, Any], output_path: Path) -> None:
        """Genera PDF desde HTML template"""
        try:
            from weasyprint import HTML, CSS
        except ImportError:
            logger.error("WeasyPrint no instalado. Instala con: pip install weasyprint")
            self._generate_with_borb(document_type, data, output_path)
            return

        # Generar HTML
        html_content = self._generate_html(document_type, data)

        # Convertir a PDF
        HTML(string=html_content).write_pdf(str(output_path))
        logger.info(f"PDF document saved: {output_path}")

    def _generate_with_borb(self, document_type: str, data: Dict[str, Any], output_path: Path) -> None:
        """Fallback a Borb si WeasyPrint no está disponible"""
        try:
            from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, Title
        except ImportError:
            logger.error("Borb no instalado. Instala con: pip install borb")
            return

        doc = Document()
        page = Page()
        layout = SingleColumnLayout(page)

        # Agregar título
        layout.add(Title(data.get("titulo", document_type.upper())))

        # Agregar contenido
        if "contenido_ia" in data:
            layout.add(Paragraph(data["contenido_ia"]))

        doc.add_pages([page])
        doc.save(str(output_path))
        logger.info(f"PDF document saved with Borb: {output_path}")

    def _generate_html(self, document_type: str, data: Dict[str, Any]) -> str:
        """Genera HTML para convertir a PDF"""
        primary_color = self.theme.get("primary_color", "#003366")
        secondary_color = self.theme.get("secondary_color", "#0099FF")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: {self.theme.get('font_family', 'Calibri')};
                    color: {self.theme.get('text_color', '#333333')};
                    margin: {self.theme.get('margins', {}).get('top', 2.54)}cm;
                }}
                h1 {{
                    color: {primary_color};
                    font-size: {self.theme.get('font_size_title', 18)}pt;
                    border-bottom: 3px solid {primary_color};
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: {secondary_color};
                    font-size: {self.theme.get('font_size_heading', 14)}pt;
                }}
                p {{
                    font-size: {self.theme.get('font_size_body', 11)}pt;
                    line-height: 1.6;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid {primary_color};
                    padding-bottom: 20px;
                }}
                .footer {{
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #ccc;
                    text-align: center;
                    font-size: 10pt;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{data.get('titulo', 'Documento')}</h1>
                <p><strong>{self.theme.get('name', 'Empresa')}</strong></p>
                <p>{data.get('empresa', '')}</p>
            </div>

            {self._render_content(document_type, data)}

            <div class="footer">
                <p>{self.theme.get('footer_text', '')}</p>
                <p>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
        </body>
        </html>
        """
        return html

    def _render_content(self, document_type: str, data: Dict[str, Any]) -> str:
        """Renderiza contenido según tipo de documento"""
        if document_type == "contract":
            return self._render_contract(data)
        elif document_type == "report":
            return self._render_report(data)
        elif document_type == "invoice":
            return self._render_invoice(data)
        else:
            return f"<p>{data.get('contenido_ia', '')}</p>"

    def _render_contract(self, data: Dict) -> str:
        beneficios = "<br>".join([f"• {b}" for b in data.get("beneficios", [])])
        return f"""
        <h2>Contrato de Trabajo</h2>
        <p><strong>Empresa:</strong> {data.get('empresa', '')}</p>
        <p><strong>Empleado:</strong> {data.get('empleado', '')}</p>
        <p><strong>Cargo:</strong> {data.get('cargo', '')}</p>
        <p><strong>Salario:</strong> ${data.get('salario', 0):,.2f}</p>
        <p><strong>Fecha Inicio:</strong> {data.get('fecha_inicio', '')}</p>

        <h3>Beneficios</h3>
        <p>{beneficios}</p>

        <h3>Contenido</h3>
        <p>{data.get('ai_content', '')}</p>
        """

    def _render_report(self, data: Dict) -> str:
        return f"""
        <h2>{data.get('titulo', 'Reporte')}</h2>
        <p><strong>Período:</strong> {data.get('periodo', '')}</p>
        <h3>Resumen Ejecutivo</h3>
        <p>{data.get('seccion_ejecutiva', '')}</p>
        <h3>Análisis Detallado</h3>
        <p>{data.get('contenido_ia', '')}</p>
        <h3>Conclusiones</h3>
        <p>{data.get('conclusiones', '')}</p>
        """

    def _render_invoice(self, data: Dict) -> str:
        items_html = ""
        for item in data.get("items", []):
            items_html += f"""
            <tr>
                <td>{item.get('descripcion', '')}</td>
                <td>${item.get('precio_unitario', 0):,.2f}</td>
                <td>{item.get('cantidad', 0)}</td>
                <td>${item.get('cantidad', 0) * item.get('precio_unitario', 0):,.2f}</td>
            </tr>
            """

        return f"""
        <h2>FACTURA #{data.get('numero', '')}</h2>
        <p><strong>Fecha:</strong> {data.get('fecha_emision', '')}</p>
        <p><strong>Cliente:</strong> {data.get('cliente', '')}</p>

        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background-color: #f0f0f0;">
                <th>Descripción</th>
                <th>Precio</th>
                <th>Cantidad</th>
                <th>Total</th>
            </tr>
            {items_html}
        </table>

        <p style="text-align: right; margin-top: 20px;">
            <strong>Subtotal:</strong> ${data.get('subtotal', 0):,.2f}<br>
            <strong>Total:</strong> ${data.get('total', 0):,.2f}
        </p>
        """
