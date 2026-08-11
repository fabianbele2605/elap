"""
Generadores de documentos profesionales: PDF, Word, Excel
Soporta exportación de respuestas de agentes en múltiples formatos
Incluye gráficas, métricas, visualizaciones profesionales y QA automático
"""

import os
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import logging
from pathlib import Path
import re
import io

from docx import Document as DocxDocument
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
import weasyprint

# Gráficas y visualizaciones
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontProperties

# Validadores y reportes QA
from .document_validators import DocumentValidator
from .document_qa_reporter import DocumentQAReporter

logger = logging.getLogger(__name__)


class DataExtractor:
    """Extrae datos estructurados de respuestas de agentes"""

    @staticmethod
    def extract_metrics(content: str) -> Dict[str, float]:
        """Extrae métricas numéricas del contenido

        Busca patrones como:
        - "Ventas: $2.5M" → {"Ventas": 2.5}
        - "Q1: $1.2M, Q2: $1.5M" → {"Q1": 1.2, "Q2": 1.5}
        """
        metrics = {}

        # Patrón único que captura todo
        pattern = r'([A-Za-z0-9\s]+):\s*\$?([0-9.,]+)\s*([MKB%])?'

        matches = re.findall(pattern, content)
        for match in matches:
            if len(match) >= 2:
                label = match[0].strip()
                value_str = match[1].replace(',', '')
                unit = match[2] if len(match) > 2 else ''

                try:
                    num = float(value_str)

                    # Aplicar multiplicadores
                    if unit == 'M':
                        num *= 1000000
                    elif unit == 'K':
                        num *= 1000
                    elif unit == '%':
                        num = num  # mantener como está

                    # Evitar duplicados, usar el valor más grande
                    if label not in metrics or num > metrics[label]:
                        metrics[label] = num

                except ValueError:
                    continue

        return metrics

    @staticmethod
    def extract_table_data(content: str) -> Tuple[List[str], List[List]]:
        """Extrae datos de tablas del contenido

        Busca tablas markdown:
        | Header1 | Header2 |
        |---------|---------|
        | Val1    | Val2    |
        """
        lines = content.split('\n')
        headers = []
        rows = []

        in_table = False
        for line in lines:
            if '|' in line:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]

                if not in_table:
                    in_table = True
                    headers = cells
                elif '---' not in line[0]:
                    rows.append(cells)

        return headers, rows


class ChartGenerator:
    """Genera gráficas profesionales con matplotlib y estilos mejorados"""

    def __init__(self, color_primary: str = "#1e3c72"):
        self.color_primary = color_primary
        self.color_secondary = "#2a5298"
        self.colors = [ColorPalette.PRIMARY, ColorPalette.SECONDARY, ColorPalette.ACCENT,
                       ColorPalette.SUCCESS, ColorPalette.WARNING]

        # Configurar matplotlib con estilos profesionales
        plt.style.use('seaborn-v0_8-darkgrid')

    def generate_bar_chart(self, labels: List[str], values: List[float], title: str = "Análisis") -> bytes:
        """Genera gráfica de barras profesional

        Returns: PNG bytes para insertar en documentos
        """
        fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')

        # Crear barras con gradiente de colores
        bars = ax.bar(labels, values, color=self.colors[:len(labels)],
                      edgecolor='white', linewidth=2, alpha=0.85)

        # Agregar valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:,.0f}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax.set_title(title, fontsize=18, fontweight='bold', color=ColorPalette.PRIMARY, pad=20)
        ax.set_xlabel("Categorías", fontsize=13, fontweight='600')
        ax.set_ylabel("Valores", fontsize=13, fontweight='600')
        ax.grid(axis='y', alpha=0.2, linestyle='--')
        ax.set_axisbelow(True)

        # Mejorar estilo
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(labelsize=11)

        # Guardar como PNG en memoria
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()

        return buf.getvalue()

    def generate_line_chart(self, labels: List[str], values: List[float], title: str = "Tendencia") -> bytes:
        """Genera gráfica de líneas profesional"""
        fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')

        ax.plot(labels, values, marker='o', linewidth=3, markersize=10,
               color=ColorPalette.SECONDARY, markerfacecolor=ColorPalette.ACCENT,
               markeredgewidth=2, markeredgecolor='white')

        ax.fill_between(range(len(labels)), values, alpha=0.15, color=ColorPalette.PRIMARY)

        ax.set_title(title, fontsize=18, fontweight='bold', color=ColorPalette.PRIMARY, pad=20)
        ax.set_xlabel("Período", fontsize=13, fontweight='600')
        ax.set_ylabel("Valores", fontsize=13, fontweight='600')

        # Agregar valores en puntos
        for i, (label, value) in enumerate(zip(labels, values)):
            ax.text(i, value + max(values) * 0.02, f'{value:,.0f}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax.grid(True, alpha=0.2, linestyle='--')
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(labelsize=11)
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        plt.close()

        return buf.getvalue()

    def generate_pie_chart(self, labels: List[str], values: List[float], title: str = "Distribución") -> bytes:
        """Genera gráfica de pie profesional"""
        fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')

        colors = self.colors[:len(labels)]
        explode = [0.08 if i == 0 else 0.02 for i in range(len(labels))]

        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                           colors=colors, explode=explode,
                                           startangle=90, textprops={'fontsize': 12, 'weight': 'bold'})

        # Mejorar estilo de textos
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')

        ax.set_title(title, fontsize=18, fontweight='bold', color=ColorPalette.PRIMARY, pad=20)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        plt.close()

        return buf.getvalue()


class ColorPalette:
    """Paleta de colores profesional consistente"""
    PRIMARY = "#1e3c72"      # Azul marino
    SECONDARY = "#2a5298"    # Azul más claro
    ACCENT = "#e8735d"       # Naranja (importante)
    SUCCESS = "#27ae60"      # Verde (positivo)
    WARNING = "#f39c12"      # Naranja (precaución)
    LIGHT = "#ecf0f1"        # Gris claro
    LIGHTER = "#f8f9fa"      # Gris muy claro
    DARK = "#2c3e50"         # Gris oscuro (texto)
    WHITE = "#ffffff"        # Blanco


class DocumentGenerator:
    """Genera documentos profesionales en PDF, Word, Excel con portadas, TOC y gráficas"""

    def __init__(self, output_dir: str = "/tmp/elap_documents"):
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.company_name = "Andina Foods S.A.S."
        self.company_color = ColorPalette.PRIMARY
        self.colors = ColorPalette

        # Herramientas para gráficas y datos
        self.extractor = DataExtractor()
        self.chart_gen = ChartGenerator(color_primary=self.company_color)

        # Validador y reportero QA
        self.validator = DocumentValidator()

    def _run_qa_check(self, filepath: str, agent_name: str, document_type: str) -> Dict:
        """Ejecuta validación QA automática después de generar documento"""
        try:
            qa_report = self.validator.generate_qa_report(filepath, agent_name, document_type)

            # Guardar reporte
            report_path = filepath.replace(Path(filepath).suffix, '_QA_REPORT')
            reporter = DocumentQAReporter(qa_report)
            reporter.save_report(report_path)

            # Log del resultado
            status = qa_report.get('status', 'UNKNOWN')
            score = qa_report.get('overall_score', 0)
            logger.info(f"📊 QA CHECK: {status} | Score: {score}% | {filepath}")

            return qa_report

        except Exception as e:
            logger.error(f"❌ Error en QA check: {e}")
            return {"status": "ERROR", "error": str(e)}

    def _generate_pdf_toc(self, content: str) -> str:
        """Genera tabla de contenidos desde encabezados en el contenido"""
        toc_items = []
        for line in content.split('\n'):
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
                toc_items.append(('h1', title))
            elif line.startswith('## '):
                title = line.replace('## ', '').strip()
                toc_items.append(('h2', title))
            elif line.startswith('### '):
                title = line.replace('### ', '').strip()
                toc_items.append(('h3', title))

        if not toc_items:
            return ""

        toc_html = """
        <div class="toc-section">
            <h2>📑 Tabla de Contenidos</h2>
            <ul class="toc-list">
        """

        for level, title in toc_items:
            indent = {'h1': '0', 'h2': '20', 'h3': '40'}[level]
            toc_html += f'<li style="margin-left: {indent}px">{title}</li>'

        toc_html += """
            </ul>
        </div>
        """
        return toc_html

    def generate_pdf(
        self,
        agent_name: str,
        title: str,
        content: str,
        timestamp: Optional[str] = None,
        include_charts: bool = True
    ) -> str:
        """Genera PDF PROFESIONAL con portada, TOC, números de página y gráficas"""
        try:
            timestamp = timestamp or datetime.now().strftime("%d de %B de %Y")

            # Generar tabla de contenidos simple
            toc_html = self._generate_pdf_toc(content)

            # Extraer datos y generar gráficas si está habilitado
            charts_html = ""
            if include_charts:
                metrics = self.extractor.extract_metrics(content)
                headers, rows = self.extractor.extract_table_data(content)

                # Si hay datos, generar gráficas
                if metrics and len(metrics) >= 2:
                    labels = list(metrics.keys())[:8]  # Máx 8 items
                    values = list(metrics.values())[:8]

                    # Generar gráfica de barras
                    try:
                        chart_png = self.chart_gen.generate_bar_chart(labels, values, title)
                        import base64
                        chart_b64 = base64.b64encode(chart_png).decode('utf-8')
                        charts_html = f"""
                        <div class="chart-section">
                            <h3>📊 Análisis Visual</h3>
                            <img src="data:image/png;base64,{chart_b64}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        </div>
                        """
                    except Exception as e:
                        logger.warning(f"Error generando gráfica: {e}")

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

                    body {{
                        font-family: 'Segoe UI', 'Trebuchet MS', sans-serif;
                        color: {ColorPalette.DARK};
                        background: white;
                        line-height: 1.8;
                    }}

                    @page {{
                        margin: 2.5cm;
                        @bottom-center {{
                            content: "Página " counter(page) " de " counter(pages);
                            font-size: 10pt;
                            color: {ColorPalette.SECONDARY};
                        }}
                    }}

                    @page :first {{
                        margin: 0;
                        @bottom-center {{
                            content: "";
                        }}
                    }}

                    .page-container {{
                        max-width: 210mm;
                        margin: 0 auto;
                        background: white;
                    }}

                    .header {{
                        background: linear-gradient(135deg, {ColorPalette.PRIMARY} 0%, {ColorPalette.SECONDARY} 100%);
                        color: white;
                        padding: 50px 40px;
                        margin-bottom: 35px;
                        box-shadow: 0 6px 12px rgba(0,0,0,0.12);
                        border-radius: 4px;
                    }}

                    .header h1 {{
                        font-size: 36px;
                        margin-bottom: 15px;
                        font-weight: 700;
                        letter-spacing: 0.3px;
                    }}

                    .header p {{
                        font-size: 15px;
                        opacity: 0.95;
                        margin: 8px 0;
                    }}

                    .metadata {{
                        display: grid;
                        grid-template-columns: 1fr 1fr 1fr;
                        gap: 25px;
                        background: {ColorPalette.LIGHT};
                        padding: 25px 40px;
                        margin-bottom: 35px;
                        border-left: 6px solid {ColorPalette.PRIMARY};
                        border-radius: 4px;
                    }}

                    .metadata-item {{
                        display: flex;
                        flex-direction: column;
                    }}

                    .metadata-item strong {{
                        color: {ColorPalette.PRIMARY};
                        font-size: 13px;
                        text-transform: uppercase;
                        letter-spacing: 1.2px;
                        font-weight: 700;
                    }}

                    .metadata-item p {{
                        margin-top: 8px;
                        color: {ColorPalette.DARK};
                        font-size: 15px;
                        font-weight: 500;
                    }}

                    .content {{
                        padding: 0 40px;
                        font-size: 15px;
                    }}

                    .content h2 {{
                        color: white;
                        background: linear-gradient(135deg, {ColorPalette.PRIMARY} 0%, {ColorPalette.SECONDARY} 100%);
                        padding: 16px 20px;
                        margin: 30px 0 18px 0;
                        font-size: 20px;
                        font-weight: 700;
                        border-radius: 4px;
                        letter-spacing: 0.3px;
                    }}

                    .content h3 {{
                        color: {ColorPalette.PRIMARY};
                        margin: 25px 0 12px 0;
                        font-size: 17px;
                        font-weight: 700;
                        border-bottom: 3px solid {ColorPalette.ACCENT};
                        padding-bottom: 8px;
                    }}

                    .content h4 {{
                        color: {ColorPalette.SECONDARY};
                        margin: 18px 0 10px 0;
                        font-size: 15px;
                        font-weight: 600;
                    }}

                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 25px 0;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
                        border-radius: 4px;
                        overflow: hidden;
                    }}

                    thead tr {{
                        background: linear-gradient(135deg, {ColorPalette.PRIMARY} 0%, {ColorPalette.SECONDARY} 100%);
                        color: white;
                    }}

                    th {{
                        padding: 18px;
                        text-align: left;
                        font-weight: 700;
                        font-size: 14px;
                        letter-spacing: 0.4px;
                    }}

                    td {{
                        padding: 14px 18px;
                        border-bottom: 1px solid {ColorPalette.LIGHT};
                        font-size: 14px;
                    }}

                    tbody tr:nth-child(odd) {{
                        background: {ColorPalette.LIGHTER};
                    }}

                    tbody tr:nth-child(even) {{
                        background: white;
                    }}

                    ul, ol {{
                        margin: 18px 0 18px 35px;
                    }}

                    li {{
                        margin: 10px 0;
                        color: {ColorPalette.DARK};
                        font-size: 14px;
                    }}

                    p {{
                        margin: 12px 0;
                        text-align: justify;
                        color: {ColorPalette.DARK};
                    }}

                    .section {{
                        margin: 25px 0;
                        padding: 20px;
                        background: {ColorPalette.LIGHTER};
                        border-left: 5px solid {ColorPalette.ACCENT};
                        border-radius: 4px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    }}

                    .highlight {{
                        background: {ColorPalette.WARNING};
                        color: white;
                        padding: 4px 8px;
                        border-radius: 3px;
                        font-weight: 600;
                    }}

                    .footer {{
                        border-top: 3px solid {ColorPalette.LIGHT};
                        padding: 25px 40px;
                        margin-top: 45px;
                        text-align: center;
                        color: {ColorPalette.SECONDARY};
                        font-size: 12px;
                        background: {ColorPalette.LIGHTER};
                        border-radius: 4px;
                    }}

                    .footer p {{
                        margin: 5px 0;
                        font-weight: 500;
                    }}

                    strong {{
                        color: {ColorPalette.PRIMARY};
                        font-weight: 700;
                    }}

                    .chart-section {{
                        margin: 30px 0;
                        padding: 20px;
                        background: #f8f9fa;
                        border-radius: 8px;
                        border-left: 4px solid {self.company_color};
                    }}

                    .chart-section h3 {{
                        color: {self.company_color};
                        margin-bottom: 15px;
                        font-size: 16px;
                    }}

                    .chart-section img {{
                        max-width: 100%;
                        height: auto;
                        border-radius: 6px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    }}

                    .metrics-grid {{
                        display: grid;
                        grid-template-columns: 1fr 1fr 1fr;
                        gap: 15px;
                        margin: 20px 0;
                    }}

                    .metric-box {{
                        background: {self.company_color};
                        color: white;
                        padding: 15px;
                        border-radius: 6px;
                        text-align: center;
                    }}

                    .metric-value {{
                        font-size: 24px;
                        font-weight: bold;
                    }}

                    .metric-label {{
                        font-size: 12px;
                        opacity: 0.9;
                        margin-top: 5px;
                    }}
                    /* PORTADA */
                    .cover-page {{
                        page-break-after: always;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        min-height: 297mm;
                        background: linear-gradient(135deg, {ColorPalette.PRIMARY} 0%, {ColorPalette.SECONDARY} 100%);
                        color: white;
                        text-align: center;
                        padding: 40px;
                    }}

                    .cover-page h1 {{
                        font-size: 48px;
                        font-weight: 800;
                        margin-bottom: 20px;
                    }}

                    .cover-page .subtitle {{
                        font-size: 24px;
                        margin-bottom: 40px;
                        opacity: 0.95;
                    }}

                    .cover-page .company {{
                        font-size: 18px;
                        margin-bottom: 60px;
                        opacity: 0.9;
                        text-transform: uppercase;
                        letter-spacing: 2px;
                    }}

                    .cover-page .metadata-cover {{
                        margin-top: auto;
                        font-size: 13px;
                        opacity: 0.85;
                    }}

                    .toc-section {{
                        page-break-after: always;
                        padding: 60px 40px;
                    }}

                    .toc-section h2 {{
                        color: {ColorPalette.PRIMARY};
                        font-size: 28px;
                        margin-bottom: 30px;
                        border-bottom: 3px solid {ColorPalette.ACCENT};
                        padding-bottom: 15px;
                    }}

                    .toc-list {{
                        list-style: none;
                    }}

                    .toc-list li {{
                        margin: 10px 0;
                        font-size: 14px;
                        color: {ColorPalette.DARK};
                    }}
                </style>
            </head>
            <body>
                <!-- PORTADA PROFESIONAL -->
                <div class="cover-page">
                    <h1>{title}</h1>
                    <div style="width: 60px; height: 3px; background: white; margin: 30px auto; opacity: 0.7;"></div>
                    <p class="subtitle">Reporte Profesional</p>
                    <p class="company">{self.company_name}</p>
                    <div class="metadata-cover">
                        <p><strong>Agente:</strong> {agent_name}</p>
                        <p><strong>Fecha:</strong> {timestamp}</p>
                        <p><strong>Clasificación:</strong> Confidencial</p>
                    </div>
                </div>

                <!-- TABLA DE CONTENIDOS -->
                {toc_html}

                <div class="page-container">
                    <div class="header">
                        <h1>{title}</h1>
                        <p>{self.company_name}</p>
                    </div>

                    <div class="metadata">
                        <div class="metadata-item">
                            <strong>👤 Agente</strong>
                            <p>{agent_name}</p>
                        </div>
                        <div class="metadata-item">
                            <strong>📅 Fecha</strong>
                            <p>{timestamp}</p>
                        </div>
                        <div class="metadata-item">
                            <strong>📄 Tipo</strong>
                            <p>Documento Profesional</p>
                        </div>
                    </div>

                    <div class="content">
                        {content.replace(chr(10), '<br>')}
                    </div>

                    {charts_html}

                    <div class="footer">
                        <p><strong>Documento Confidencial</strong></p>
                        <p>Generado por ELAP Intelligence System</p>
                        <p>&copy; 2026 {self.company_name}. Todos los derechos reservados.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            filename = f"{agent_name}_{int(datetime.now().timestamp())}.pdf"
            filepath = os.path.join(self.output_dir, filename)

            weasyprint.HTML(string=html_content).write_pdf(filepath)
            logger.info(f"✅ PDF generado: {filepath}")

            # Ejecutar QA check automático
            qa_report = self._run_qa_check(filepath, agent_name, "pdf")

            return filepath

        except Exception as e:
            logger.error(f"❌ Error generando PDF: {e}")
            raise

    def generate_word(
        self,
        agent_name: str,
        title: str,
        content: str,
        timestamp: Optional[str] = None,
        include_charts: bool = True
    ) -> str:
        """Genera Word profesional con gráficas desde respuesta de agente"""
        try:
            timestamp = timestamp or datetime.now().strftime("%d de %B de %Y")

            doc = DocxDocument()

            # Estilos y colores
            company_color = RGBColor(30, 60, 114)
            light_color = RGBColor(232, 244, 248)

            # Título
            title_para = doc.add_heading(title, level=1)
            title_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            title_format = title_para.runs[0]
            title_format.font.color.rgb = company_color
            title_format.font.size = Pt(24)

            # Subtítulo
            subtitle = doc.add_paragraph(self.company_name)
            subtitle.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            subtitle_format = subtitle.runs[0]
            subtitle_format.font.color.rgb = RGBColor(100, 100, 100)
            subtitle_format.font.size = Pt(12)

            doc.add_paragraph()  # Espacio

            # Metadata profesional
            meta_table = doc.add_table(rows=3, cols=2)
            meta_table.style = 'Light Grid Accent 1'

            meta_items = [
                ("👤 Agente", agent_name),
                ("📅 Fecha", timestamp),
                ("🏢 Empresa", self.company_name)
            ]

            for i, (label, value) in enumerate(meta_items):
                row = meta_table.rows[i]
                row.cells[0].text = label
                row.cells[1].text = value

                # Estilo de celdas
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.size = Pt(11)
                            if i % 2 == 0:
                                run.font.bold = True
                                run.font.color.rgb = RGBColor(30, 60, 114)

            doc.add_paragraph()  # Espacio

            # Separador
            separator = doc.add_paragraph("_" * 80)
            separator_format = separator.runs[0]
            separator_format.font.color.rgb = RGBColor(200, 200, 200)

            doc.add_paragraph()  # Espacio

            # Contenido principal
            # Dividir contenido por líneas y aplicar formato
            content_lines = content.split('\n')
            for line in content_lines:
                if line.strip():
                    para = doc.add_paragraph(line)
                    para.paragraph_format.line_spacing = 1.5
                    para.paragraph_format.space_after = Pt(6)

                    # Detectar encabezados
                    if line.startswith('#'):
                        for run in para.runs:
                            run.font.bold = True
                            run.font.size = Pt(12)
                            run.font.color.rgb = company_color
                    else:
                        for run in para.runs:
                            run.font.size = Pt(11)

            doc.add_paragraph()  # Espacio
            doc.add_paragraph()  # Espacio

            # Agregar gráficas si está habilitado
            if include_charts:
                try:
                    metrics = self.extractor.extract_metrics(content)
                    if metrics and len(metrics) >= 2:
                        labels = list(metrics.keys())[:8]
                        values = list(metrics.values())[:8]

                        # Separador visual
                        chart_header = doc.add_heading("📊 Análisis Visual", level=2)
                        chart_header.runs[0].font.color.rgb = RGBColor(30, 60, 114)

                        # Generar y insertar gráfica de barras
                        chart_png = self.chart_gen.generate_bar_chart(labels, values, title)
                        chart_bytes = io.BytesIO(chart_png)

                        doc.add_picture(chart_bytes, width=Inches(5.5))
                        last_paragraph = doc.paragraphs[-1]
                        last_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

                        doc.add_paragraph()  # Espacio
                except Exception as e:
                    logger.warning(f"Error agregando gráfica a Word: {e}")

            # Separador final
            final_sep = doc.add_paragraph("_" * 80)
            final_sep_format = final_sep.runs[0]
            final_sep_format.font.color.rgb = RGBColor(200, 200, 200)

            # Footer profesional
            footer_para = doc.add_paragraph("Documento Confidencial")
            footer_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            footer_run = footer_para.runs[0]
            footer_run.font.size = Pt(10)
            footer_run.font.color.rgb = company_color
            footer_run.font.bold = True

            footer_para2 = doc.add_paragraph("Generado por ELAP Intelligence System")
            footer_para2.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            footer_run2 = footer_para2.runs[0]
            footer_run2.font.size = Pt(9)
            footer_run2.font.color.rgb = RGBColor(150, 150, 150)

            footer_para3 = doc.add_paragraph(f"© 2026 {self.company_name}. Todos los derechos reservados.")
            footer_para3.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            footer_run3 = footer_para3.runs[0]
            footer_run3.font.size = Pt(8)
            footer_run3.font.color.rgb = RGBColor(150, 150, 150)

            filename = f"{agent_name}_{int(datetime.now().timestamp())}.docx"
            filepath = os.path.join(self.output_dir, filename)
            doc.save(filepath)

            logger.info(f"✅ Word generado: {filepath}")

            # Ejecutar QA check automático
            qa_report = self._run_qa_check(filepath, agent_name, "word")

            return filepath

        except Exception as e:
            logger.error(f"❌ Error generando Word: {e}")
            raise

    def generate_excel(
        self,
        agent_name: str,
        title: str,
        content: str,
        timestamp: Optional[str] = None,
        include_charts: bool = True
    ) -> str:
        """Genera Excel PROFESIONAL AVANZADO con múltiples hojas, gráficas y KPIs"""
        try:
            timestamp = timestamp or datetime.now().strftime("%d de %B de %Y")

            wb = Workbook()
            wb.remove(wb.active)

            company_color = "1E3C72"
            light_blue = "E8F4F8"
            light_gray = "F8F9FA"
            kpi_color = "2A5298"

            header_fill = PatternFill(start_color=company_color, end_color=company_color, fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=14, name="Calibri")
            kpi_fill = PatternFill(start_color=kpi_color, end_color=kpi_color, fill_type="solid")
            kpi_font = Font(bold=True, color="FFFFFF", size=12, name="Calibri")

            border_thin = Border(
                left=Side(style='thin', color='CCCCCC'),
                right=Side(style='thin', color='CCCCCC'),
                top=Side(style='thin', color='CCCCCC'),
                bottom=Side(style='thin', color='CCCCCC')
            )

            center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
            left_align = Alignment(horizontal='left', vertical='top', wrap_text=True)

            # ===== HOJA 1: RESUMEN EJECUTIVO =====
            ws_resumen = wb.create_sheet("📊 Resumen", 0)

            ws_resumen.merge_cells('A1:E1')
            ws_resumen['A1'] = title
            ws_resumen['A1'].font = header_font
            ws_resumen['A1'].fill = header_fill
            ws_resumen['A1'].alignment = center_align
            ws_resumen.row_dimensions[1].height = 35

            ws_resumen['A3'] = "👤 Agente"
            ws_resumen['B3'] = agent_name
            ws_resumen['C3'] = "📅 Fecha"
            ws_resumen['D3'] = timestamp
            ws_resumen['E3'] = "🏢 Empresa"
            ws_resumen['A4'] = self.company_name

            for col in ['A', 'B', 'C', 'D', 'E']:
                ws_resumen[f'{col}3'].font = Font(bold=True, color=company_color, size=10)

            metrics = self.extractor.extract_metrics(content)

            if metrics:
                kpi_row = 6
                ws_resumen.merge_cells(f'A{kpi_row}:E{kpi_row}')
                ws_resumen[f'A{kpi_row}'] = "🎯 MÉTRICAS CLAVE"
                ws_resumen[f'A{kpi_row}'].font = Font(bold=True, size=12, color=company_color)

                kpi_row += 1
                col_idx = 1
                for label, value in list(metrics.items())[:5]:
                    cell = ws_resumen.cell(row=kpi_row, column=col_idx)
                    cell.value = f"{label}\n{value:,.0f}"
                    cell.fill = kpi_fill
                    cell.font = kpi_font
                    cell.alignment = center_align
                    ws_resumen.column_dimensions[chr(64 + col_idx)].width = 18
                    col_idx += 1

            # ===== HOJA 2: DATOS DETALLADOS =====
            ws_datos = wb.create_sheet("📋 Datos", 1)

            ws_datos.merge_cells('A1:D1')
            ws_datos['A1'] = "Análisis Detallado"
            ws_datos['A1'].font = header_font
            ws_datos['A1'].fill = header_fill
            ws_datos['A1'].alignment = center_align
            ws_datos.row_dimensions[1].height = 25

            content_lines = content.split('\n')
            row = 3
            for i, line in enumerate(content_lines):
                if line.strip():
                    ws_datos.merge_cells(f'A{row}:D{row}')
                    ws_datos[f'A{row}'] = line
                    ws_datos[f'A{row}'].font = Font(size=10, name="Calibri")
                    ws_datos[f'A{row}'].alignment = left_align
                    ws_datos[f'A{row}'].border = border_thin

                    if i % 2 == 0:
                        ws_datos[f'A{row}'].fill = PatternFill(start_color=light_gray, end_color=light_gray, fill_type="solid")

                    ws_datos.row_dimensions[row].height = None
                    row += 1

            ws_datos.column_dimensions['A'].width = 80

            # ===== HOJA 3: GRÁFICAS =====
            if include_charts and metrics:
                ws_charts = wb.create_sheet("📈 Gráficas", 2)

                ws_charts.merge_cells('A1:E1')
                ws_charts['A1'] = "VISUALIZACIONES Y ANÁLISIS"
                ws_charts['A1'].font = header_font
                ws_charts['A1'].fill = header_fill
                ws_charts['A1'].alignment = center_align
                ws_charts.row_dimensions[1].height = 25

                labels = list(metrics.keys())[:8]
                values = list(metrics.values())[:8]

                data_row = 3
                ws_charts['A3'] = "Categoría"
                ws_charts['B3'] = "Valor"
                ws_charts['A3'].fill = header_fill
                ws_charts['B3'].fill = header_fill
                ws_charts['A3'].font = Font(bold=True, color="FFFFFF")
                ws_charts['B3'].font = Font(bold=True, color="FFFFFF")

                for i, (label, value) in enumerate(zip(labels, values)):
                    row_num = data_row + 1 + i
                    ws_charts[f'A{row_num}'] = label
                    ws_charts[f'B{row_num}'] = value
                    ws_charts[f'B{row_num}'].fill = PatternFill(start_color=light_blue, end_color=light_blue, fill_type="solid")
                    ws_charts[f'B{row_num}'].border = border_thin

                # Gráfica de barras
                chart_bar = BarChart()
                chart_bar.type = "col"
                chart_bar.style = 10
                chart_bar.title = "Análisis Comparativo"
                chart_bar.y_axis.title = 'Valores'
                chart_bar.x_axis.title = 'Categorías'

                data = Reference(ws_charts, min_col=2, min_row=data_row, max_row=data_row + len(values))
                cats = Reference(ws_charts, min_col=1, min_row=data_row + 1, max_row=data_row + len(values))

                chart_bar.add_data(data, titles_from_data=True)
                chart_bar.set_categories(cats)
                ws_charts.add_chart(chart_bar, "D3")

                # Gráfica de líneas
                if len(values) >= 3:
                    chart_line = LineChart()
                    chart_line.title = "Tendencia"
                    chart_line.y_axis.title = 'Valores'

                    chart_line.add_data(data, titles_from_data=True)
                    chart_line.set_categories(cats)
                    ws_charts.add_chart(chart_line, "D20")

                # Gráfica pie
                if len(values) >= 2:
                    chart_pie = PieChart()
                    chart_pie.title = "Distribución"

                    chart_pie.add_data(data, titles_from_data=True)
                    chart_pie.set_categories(cats)
                    ws_charts.add_chart(chart_pie, "M3")

                ws_charts.column_dimensions['A'].width = 20
                ws_charts.column_dimensions['B'].width = 15

            # Configuración de página para todas las hojas
            for ws in wb.sheetnames:
                ws_obj = wb[ws]
                ws_obj.print_options.horizontalCentered = True
                ws_obj.page_setup.paperSize = ws_obj.PAPERSIZE_LETTER
                ws_obj.page_margins.left = 0.5
                ws_obj.page_margins.right = 0.5
                ws_obj.page_margins.top = 0.75
                ws_obj.page_margins.bottom = 0.75

            filename = f"{agent_name}_{int(datetime.now().timestamp())}.xlsx"
            filepath = os.path.join(self.output_dir, filename)
            wb.save(filepath)

            logger.info(f"✅ Excel AVANZADO generado: {filepath}")

            # Ejecutar QA check automático
            qa_report = self._run_qa_check(filepath, agent_name, "excel")

            return filepath

        except Exception as e:
            logger.error(f"❌ Error generando Excel: {e}")
            raise

    def generate_all(
        self,
        agent_name: str,
        title: str,
        content: str,
        timestamp: Optional[str] = None
    ) -> dict:
        """Genera los 3 formatos (PDF, Word, Excel) simultáneamente"""
        return {
            "pdf": self.generate_pdf(agent_name, title, content, timestamp),
            "word": self.generate_word(agent_name, title, content, timestamp),
            "excel": self.generate_excel(agent_name, title, content, timestamp)
        }
