"""Word (.docx) Generator - Manejo profesional de templates con items dinámicos"""

import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from copy import deepcopy
import zipfile
import shutil
import tempfile

logger = logging.getLogger(__name__)

try:
    from docxtpl import DocxTemplate
except ImportError:
    logger.warning("docxtpl no instalado. Instala con: pip install docxtpl")
    DocxTemplate = None

try:
    from docx import Document
    from docx.shared import Pt, RGBColor
except ImportError:
    logger.warning("python-docx no instalado. Instala con: pip install python-docx")
    Document = None


class WordGenerator:
    """Genera documentos Word profesionales con templates"""

    def __init__(self, theme: Dict[str, Any], language: str = "es"):
        self.theme = theme
        self.language = language
        self.templates_dir = Path(__file__).parent.parent / "templates" / "word"

    def generate(self, document_type: str, data: Dict[str, Any], output_path: Path) -> None:
        """Genera documento Word de forma profesional"""
        if not DocxTemplate:
            logger.error("docxtpl no instalado")
            raise ImportError("docxtpl required")

        template_path = self._get_template_path(document_type)
        if not template_path.exists():
            self._create_default_template(template_path, document_type)

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if document_type == "invoice" and "items" in data and data["items"]:
                self._generate_invoice_with_items(template_path, data, output_path)
            else:
                doc = DocxTemplate(str(template_path))
                context = self._prepare_context(data, document_type)
                doc.render(context)
                doc.save(str(output_path))
                logger.info(f"Word document generated: {output_path}")

        except Exception as e:
            logger.error(f"Error generating Word document: {e}")
            raise

    def _generate_invoice_with_items(self, template_path: Path, data: Dict[str, Any], output_path: Path) -> None:
        """Genera factura con items dinámicos"""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "temp.docx"

            # Paso 1: Crear versión limpia sin variables {{item.*}}
            self._clean_template_for_docxtpl(template_path, temp_path)

            # Paso 2: Renderizar con docxtpl (sin variables item)
            doc = DocxTemplate(str(temp_path))
            context = self._prepare_context(data, "invoice")
            context_clean = {k: v for k, v in context.items() if k != "items"}
            doc.render(context_clean)

            # Paso 3: Guardar intermedio
            intermediate_path = Path(tmpdir) / "intermediate.docx"
            doc.save(str(intermediate_path))

            # Paso 4: Agregar items dinámicos con python-docx
            self._add_invoice_items_to_table(str(intermediate_path), data["items"], str(output_path))
            logger.info(f"Invoice with {len(data['items'])} items generated: {output_path}")

    def _clean_template_for_docxtpl(self, input_path: Path, output_path: Path) -> None:
        """Crea versión limpia reemplazando {{item.*}} temporalmente"""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_extract = Path(tmpdir) / "extracted"
                with zipfile.ZipFile(input_path, 'r') as zip_ref:
                    zip_ref.extractall(tmp_extract)

                # Leer y limpiar document.xml
                doc_xml_path = tmp_extract / "word" / "document.xml"
                with open(doc_xml_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Reemplazar {{item.*}} con placeholders
                content = content.replace("{{item.descripcion}}", "ITEM_DESC_PLACEHOLDER")
                content = content.replace("{{item.precio_unitario}}", "ITEM_PRICE_PLACEHOLDER")
                content = content.replace("{{item.cantidad}}", "ITEM_QTY_PLACEHOLDER")
                content = content.replace("{{item.subtotal}}", "ITEM_SUBTOTAL_PLACEHOLDER")

                with open(doc_xml_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                # Recomprimir
                shutil.make_archive(str(output_path)[:-5], 'zip', tmp_extract)
                zip_path = Path(str(output_path)[:-5] + ".zip")
                if zip_path.exists():
                    zip_path.rename(output_path)

        except Exception as e:
            logger.error(f"Error cleaning template: {e}")
            shutil.copy(input_path, output_path)

    def _add_invoice_items_to_table(self, doc_path: str, items: list, output_path: str) -> None:
        """Agrega items dinámicos a tabla clonando filas"""
        try:
            doc = Document(doc_path)

            if len(doc.tables) < 2:
                doc.save(output_path)
                return

            items_table = doc.tables[1]

            # Encontrar fila con placeholders
            template_row_idx = None
            for idx, row in enumerate(items_table.rows):
                row_text = " ".join([cell.text for cell in row.cells])
                if "ITEM_DESC_PLACEHOLDER" in row_text or "ITEM_PRICE_PLACEHOLDER" in row_text:
                    template_row_idx = idx
                    break

            if template_row_idx is None:
                doc.save(output_path)
                return

            tbl = items_table._element
            template_row = items_table.rows[template_row_idx]._element

            # Clonar fila para cada item
            for item in items:
                new_row = deepcopy(template_row)

                # Reemplazar placeholders
                for t_elem in new_row.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"):
                    if t_elem.text:
                        if "ITEM_DESC_PLACEHOLDER" in t_elem.text:
                            t_elem.text = str(item.get("descripcion", ""))
                        elif "ITEM_PRICE_PLACEHOLDER" in t_elem.text:
                            t_elem.text = str(item.get("precio_unitario", ""))
                        elif "ITEM_QTY_PLACEHOLDER" in t_elem.text:
                            t_elem.text = str(item.get("cantidad", ""))
                        elif "ITEM_SUBTOTAL_PLACEHOLDER" in t_elem.text:
                            t_elem.text = str(item.get("subtotal", ""))

                tbl.insert(tbl.index(template_row) + 1, new_row)

            # Eliminar fila template
            tbl.remove(template_row)

            doc.save(output_path)

        except Exception as e:
            logger.error(f"Error adding items: {e}")
            doc = Document(doc_path)
            doc.save(output_path)

    def _get_template_path(self, document_type: str) -> Path:
        templates = {
            "contract": "contract_template.docx",
            "report": "report_template.docx",
            "invoice": "invoice_template.docx",
            "job_offer": "job_offer_template.docx",
        }
        return self.templates_dir / templates.get(document_type, "default_template.docx")

    def _prepare_context(self, data: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        context = {
            "empresa_nombre": self.theme.get("name", "Empresa"),
            "footer_text": self.theme.get("footer_text", ""),
            "primary_color": self.theme.get("primary_color", "#003366"),
            "fecha_generacion": datetime.now().strftime("%d de %B de %Y"),
            "fecha_hoy": datetime.now().strftime("%Y-%m-%d"),
            "fecha_hoy_corta": datetime.now().strftime("%d/%m/%Y"),
            **data
        }

        if document_type == "invoice":
            context = self._prepare_invoice_context(context)

        return context

    def _prepare_invoice_context(self, context: Dict) -> Dict:
        if "items" in context and isinstance(context["items"], list):
            for item in context["items"]:
                cantidad = float(item.get("cantidad", 1))
                precio = float(item.get("precio_unitario", 0))
                subtotal = cantidad * precio
                item["subtotal"] = f"${subtotal:,.0f}"
                item["precio_unitario"] = f"${precio:,.0f}"
                item["cantidad"] = int(cantidad)

            subtotal_total = sum(float(item.get("precio_unitario", "0").replace("$", "").replace(",", "")) * item.get("cantidad", 1) for item in context["items"])
            context["subtotal"] = f"${subtotal_total:,.0f}"
            context["impuesto"] = f"${subtotal_total * 0.19:,.0f}"
            context["total"] = f"${subtotal_total * 1.19:,.0f}"
        else:
            context["subtotal"] = "$0"
            context["impuesto"] = "$0"
            context["total"] = "$0"

        return context

    def _create_default_template(self, template_path: Path, document_type: str) -> None:
        if not Document:
            return

        template_path.parent.mkdir(parents=True, exist_ok=True)
        doc = Document()

        title = doc.add_paragraph()
        title_run = title.add_run(f"Template: {document_type.upper()}")
        title_run.font.size = Pt(16)
        title_run.font.bold = True

        doc.add_paragraph("Template por defecto")
        doc.save(str(template_path))
