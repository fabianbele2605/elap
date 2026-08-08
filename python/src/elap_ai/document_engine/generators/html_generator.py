"""HTML Generator para correos y visualización web"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """Genera HTML profesional para correos y web"""

    def __init__(self, theme: Dict[str, Any], language: str = "es"):
        self.theme = theme
        self.language = language

    def generate(self, document_type: str, data: Dict[str, Any]) -> str:
        """Genera HTML"""
        primary_color = self.theme.get("primary_color", "#003366")
        secondary_color = self.theme.get("secondary_color", "#0099FF")
        font_family = self.theme.get("font_family", "Calibri, Arial, sans-serif")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: {font_family};
                    background-color: #f5f5f5;
                    color: #333333;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
                    color: white;
                    padding: 40px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    font-size: 28px;
                    margin-bottom: 10px;
                }}
                .header p {{
                    font-size: 14px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 30px 20px;
                }}
                .content h2 {{
                    color: {primary_color};
                    font-size: 20px;
                    margin-top: 20px;
                    margin-bottom: 10px;
                    border-bottom: 2px solid {secondary_color};
                    padding-bottom: 10px;
                }}
                .content h3 {{
                    color: {secondary_color};
                    font-size: 16px;
                    margin-top: 15px;
                    margin-bottom: 8px;
                }}
                .content p {{
                    margin-bottom: 15px;
                    text-align: justify;
                }}
                .info-box {{
                    background-color: #f9f9f9;
                    border-left: 4px solid {primary_color};
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 4px;
                }}
                .info-box strong {{
                    color: {primary_color};
                }}
                .button {{
                    display: inline-block;
                    background-color: {primary_color};
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 4px;
                    margin: 10px 0;
                    font-weight: bold;
                }}
                .button:hover {{
                    background-color: {secondary_color};
                }}
                .table-responsive {{
                    overflow-x: auto;
                    margin: 15px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th {{
                    background-color: {primary_color};
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                td {{
                    border-bottom: 1px solid #ddd;
                    padding: 12px;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
                .footer {{
                    background-color: #f0f0f0;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    border-top: 1px solid #ddd;
                }}
                .footer p {{
                    margin: 5px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{data.get('titulo', document_type.upper())}</h1>
                    <p>{self.theme.get('name', 'Empresa')}</p>
                </div>

                <div class="content">
                    {self._render_content(document_type, data)}
                </div>

                <div class="footer">
                    <p>{self.theme.get('footer_text', '')}</p>
                    <p>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def _render_content(self, document_type: str, data: Dict[str, Any]) -> str:
        """Renderiza contenido según tipo"""
        if document_type == "contract":
            return self._render_contract(data)
        elif document_type == "report":
            return self._render_report(data)
        elif document_type == "invoice":
            return self._render_invoice(data)
        else:
            return f"<p>{data.get('contenido_ia', '')}</p>"

    def _render_contract(self, data: Dict) -> str:
        beneficios = "".join([f"<li>{b}</li>" for b in data.get("beneficios", [])])
        return f"""
        <h2>Contrato de Trabajo</h2>
        <div class="info-box">
            <p><strong>Empresa:</strong> {data.get('empresa', '')}</p>
            <p><strong>Empleado:</strong> {data.get('empleado', '')}</p>
            <p><strong>Cargo:</strong> {data.get('cargo', '')}</p>
            <p><strong>Salario Mensual:</strong> ${data.get('salario', 0):,.2f}</p>
            <p><strong>Fecha de Inicio:</strong> {data.get('fecha_inicio', '')}</p>
        </div>

        <h3>Beneficios Incluidos</h3>
        <ul style="margin-left: 20px;">
            {beneficios}
        </ul>

        <h3>Detalles del Acuerdo</h3>
        <p>{data.get('ai_content', '')}</p>
        """

    def _render_report(self, data: Dict) -> str:
        metricas = "".join([
            f"<tr><td>{k}</td><td>{v}</td></tr>"
            for k, v in data.get("metricas", {}).items()
        ])
        return f"""
        <h2>{data.get('titulo', 'Reporte')}</h2>
        <p><strong>Período:</strong> {data.get('periodo', '')}</p>

        <h3>Resumen Ejecutivo</h3>
        <p>{data.get('seccion_ejecutiva', '')}</p>

        <h3>Métricas Clave</h3>
        <div class="table-responsive">
            <table>
                <tr>
                    <th>Métrica</th>
                    <th>Valor</th>
                </tr>
                {metricas}
            </table>
        </div>

        <h3>Análisis Detallado</h3>
        <p>{data.get('contenido_ia', '')}</p>

        <h3>Conclusiones</h3>
        <p>{data.get('conclusiones', '')}</p>
        """

    def _render_invoice(self, data: Dict) -> str:
        items_html = "".join([
            f"""
            <tr>
                <td>{item.get('descripcion', '')}</td>
                <td>${item.get('precio_unitario', 0):,.2f}</td>
                <td>{item.get('cantidad', 0)}</td>
                <td>${item.get('cantidad', 0) * item.get('precio_unitario', 0):,.2f}</td>
            </tr>
            """
            for item in data.get("items", [])
        ])

        subtotal = sum(item.get('cantidad', 0) * item.get('precio_unitario', 0) for item in data.get("items", []))
        impuesto = subtotal * 0.19
        total = subtotal + impuesto

        return f"""
        <h2>FACTURA #{data.get('numero', '')}</h2>
        <div class="info-box">
            <p><strong>Fecha:</strong> {data.get('fecha_emision', '')}</p>
            <p><strong>Cliente:</strong> {data.get('cliente', '')}</p>
            <p><strong>Vencimiento:</strong> {data.get('fecha_vencimiento', '')}</p>
        </div>

        <div class="table-responsive">
            <table>
                <tr>
                    <th>Descripción</th>
                    <th>Precio Unitario</th>
                    <th>Cantidad</th>
                    <th>Total</th>
                </tr>
                {items_html}
            </table>
        </div>

        <div class="info-box" style="text-align: right;">
            <p><strong>Subtotal:</strong> ${subtotal:,.2f}</p>
            <p><strong>Impuesto (19%):</strong> ${impuesto:,.2f}</p>
            <p style="font-size: 18px; color: #FF6B35;">
                <strong>TOTAL: ${total:,.2f}</strong>
            </p>
        </div>

        <h3>Condiciones de Pago</h3>
        <p>{data.get('condiciones_pago', '')}</p>
        """
