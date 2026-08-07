"""Document generation (PDF, Excel, Word)."""

from typing import Optional, Any
from io import BytesIO
import pandas as pd


class DocumentGenerator:
    """Generates professional documents in multiple formats."""

    @staticmethod
    def generate_pdf_report(
        title: str,
        sections: list[dict[str, Any]],
        company_name: str = "Empresa",
        company_logo: Optional[str] = None,
    ) -> bytes:
        """
        Generate professional PDF report.

        Args:
            title: Report title
            sections: List of sections {title, content, chart_path (optional)}
            company_name: Company name for header
            company_logo: Path to logo image (optional)

        Returns:
            PDF bytes
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
        except ImportError:
            raise ImportError("reportlab required: pip install reportlab")

        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1a1a1a"),
            spaceAfter=12,
            alignment=1,  # Center
        )

        # Header with company name
        elements.append(Paragraph(company_name, styles["Normal"]))
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.3 * inch))

        # Add sections
        for section in sections:
            elements.append(Paragraph(section.get("title", ""), styles["Heading2"]))
            elements.append(Spacer(1, 0.1 * inch))

            content = section.get("content", "")
            if content:
                elements.append(Paragraph(content, styles["Normal"]))
            elements.append(Spacer(1, 0.2 * inch))

            # Add chart if present
            if "chart_path" in section:
                try:
                    img = Image(section["chart_path"], width=5 * inch, height=3 * inch)
                    elements.append(img)
                    elements.append(Spacer(1, 0.3 * inch))
                except Exception:
                    pass

            elements.append(PageBreak())

        # Build PDF
        doc.build(elements)
        return pdf_buffer.getvalue()

    @staticmethod
    def generate_excel_report(
        data: dict[str, Any],
        title: str = "Report",
    ) -> bytes:
        """
        Generate Excel workbook with multiple sheets.

        Args:
            data: Dictionary mapping sheet names to DataFrames or lists
            title: Workbook title (metadata)

        Returns:
            Excel bytes
        """
        output = BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            workbook = writer.book

            # Define formats
            header_format = workbook.add_format({
                "bold": True,
                "bg_color": "#4472C4",
                "font_color": "white",
                "border": 1,
            })

            cell_format = workbook.add_format({
                "border": 1,
                "valign": "vcenter",
            })

            # Write sheets
            for sheet_name, sheet_data in data.items():
                if isinstance(sheet_data, pd.DataFrame):
                    sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)

                    # Format headers
                    worksheet = writer.sheets[sheet_name]
                    for col_num, value in enumerate(sheet_data.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                else:
                    # Handle lists or dicts
                    if isinstance(sheet_data, list) and sheet_data:
                        df = pd.DataFrame(sheet_data)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

        output.seek(0)
        return output.getvalue()

    @staticmethod
    def generate_word_document(
        title: str,
        sections: list[dict[str, Any]],
        company_name: str = "Empresa",
    ) -> bytes:
        """
        Generate Word document (.docx).

        Args:
            title: Document title
            sections: List of {title, content, bullet_points (optional)}
            company_name: Company name

        Returns:
            DOCX bytes
        """
        try:
            from docx import Document
            from docx.shared import Pt, RGBColor, Inches
            from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
        except ImportError:
            raise ImportError("python-docx required: pip install python-docx")

        doc = Document()

        # Add header
        header = doc.add_heading(company_name, 0)
        header.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        title_para = doc.add_heading(title, 1)
        title_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        doc.add_paragraph()

        # Add sections
        for section in sections:
            section_title = section.get("title", "")
            if section_title:
                doc.add_heading(section_title, level=2)

            content = section.get("content", "")
            if content:
                doc.add_paragraph(content)

            bullets = section.get("bullet_points", [])
            for bullet in bullets:
                doc.add_paragraph(bullet, style="List Bullet")

            doc.add_paragraph()

        # Return as bytes
        output = BytesIO()
        doc.save(output)
        output.seek(0)
        return output.getvalue()
