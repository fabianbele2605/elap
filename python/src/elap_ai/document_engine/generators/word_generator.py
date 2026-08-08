"""Word (.docx) Generator usando docxtpl"""

import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from docxtpl import DocxTemplate
except ImportError:
    logger.warning("docxtpl no instalado. Instala con: pip install docxtpl")
    DocxTemplate = None


class WordGenerator:
    """Genera documentos Word profesionales con templates"""

    def __init__(self, theme: Dict[str, Any], language: str = "es"):
        """
        Args:
            theme: Configuración del tema corporativo
            language: Idioma (es, en)
        """
        self.theme = theme
        self.language = language
        self.templates_dir = Path(__file__).parent.parent / "templates" / "word"

    def generate(self, document_type: str, data: Dict[str, Any], output_path: Path) -> None:
        """
        Genera documento Word usando docxtpl

        Args:
            document_type: Tipo de documento (contract, report, invoice)
            data: Datos para rellenar template
            output_path: Ruta de salida
        """
        if not DocxTemplate:
            logger.error("docxtpl no instalado. Instala con: pip install docxtpl")
            raise ImportError("docxtpl required")

        # Obtener template según tipo de documento
        template_path = self._get_template_path(document_type)

        if not template_path.exists():
            logger.warning(f"Template no encontrado: {template_path}. Creando default...")
            self._create_default_template(template_path, document_type)

        try:
            # Cargar template con docxtpl
            doc = DocxTemplate(str(template_path))

            # Preparar contexto con datos
            context = self._prepare_context(data, document_type)

            # Renderizar variables {{ }} en el template
            doc.render(context)

            # Crear directorio si no existe
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Guardar documento
            doc.save(str(output_path))
            logger.info(f"Word document generated: {output_path}")

        except Exception as e:
            logger.error(f"Error generating Word document: {e}")
            raise

    def _get_template_path(self, document_type: str) -> Path:
        """Obtiene ruta del template según tipo"""
        templates = {
            "contract": "contract_template.docx",
            "report": "report_template.docx",
            "invoice": "invoice_template.docx",
            "hr_document": "hr_document_template.docx",
        }
        template_name = templates.get(document_type, "default_template.docx")
        return self.templates_dir / template_name

    def _prepare_context(self, data: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        """Prepara contexto para renderizar template con docxtpl"""
        # Contexto base
        context = {
            # Datos del tema corporativo
            "empresa_nombre": self.theme.get("name", "Empresa"),
            "footer_text": self.theme.get("footer_text", ""),
            "primary_color": self.theme.get("primary_color", "#003366"),

            # Fechas
            "fecha_generacion": datetime.now().strftime("%d de %B de %Y"),
            "fecha_hoy": datetime.now().strftime("%Y-%m-%d"),
            "fecha_hoy_corta": datetime.now().strftime("%d/%m/%Y"),

            # Incluir todos los datos del usuario
            **data
        }

        # Procesamiento específico según tipo de documento
        if document_type == "contract":
            context = self._prepare_contract_context(context)
        elif document_type == "report":
            context = self._prepare_report_context(context)
        elif document_type == "invoice":
            context = self._prepare_invoice_context(context)

        return context

    def _prepare_contract_context(self, context: Dict) -> Dict:
        """Prepara contexto para contrato con docxtpl"""
        # docxtpl puede iterar listas directamente con {% for %}
        # Solo asegurarse de que existan
        if "beneficios" not in context:
            context["beneficios"] = []

        if "responsabilidades" not in context:
            context["responsabilidades"] = []

        return context

    def _prepare_report_context(self, context: Dict) -> Dict:
        """Prepara contexto para reporte con docxtpl"""
        # docxtpl puede iterar dicts directamente
        if "metricas" not in context:
            context["metricas"] = {}

        return context

    def _prepare_invoice_context(self, context: Dict) -> Dict:
        """Prepara contexto para factura con docxtpl"""
        # Calcular totales de items
        if "items" in context and isinstance(context["items"], list):
            for item in context["items"]:
                cantidad = float(item.get("cantidad", 0))
                precio = float(item.get("precio_unitario", 0))
                item["total"] = cantidad * precio

            # Calcular totales
            subtotal = sum(item.get("total", 0) for item in context["items"])
            context["subtotal"] = f"{subtotal:,.2f}"

            impuesto = subtotal * 0.19
            context["impuesto"] = f"{impuesto:,.2f}"

            total = subtotal + impuesto
            context["total"] = f"{total:,.2f}"

        return context

    def _create_default_template(self, template_path: Path, document_type: str) -> None:
        """Crea template por defecto si no existe"""
        try:
            from docx import Document
            from docx.shared import Pt, RGBColor, Inches
        except ImportError:
            logger.error("python-docx no instalado")
            return

        # Crear directorio si no existe
        template_path.parent.mkdir(parents=True, exist_ok=True)

        # Crear documento base
        doc = Document()

        # Agregar título
        title = doc.add_paragraph()
        title_run = title.add_run(f"Template: {document_type.upper()}")
        title_run.font.size = Pt(16)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(45, 80, 22)  # Verde Andina

        # Agregar descripción
        desc = doc.add_paragraph("Este es un template por defecto. Personaliza según necesites.")
        desc.style = "Heading 2"

        # Agregar campos de ejemplo
        if document_type == "contract":
            doc.add_paragraph("Empresa: {{empresa}}")
            doc.add_paragraph("Empleado: {{empleado}}")
            doc.add_paragraph("Cargo: {{cargo}}")
            doc.add_paragraph("Salario: {{salario}}")

        # Guardar
        doc.save(str(template_path))
        logger.info(f"Default template created: {template_path}")
