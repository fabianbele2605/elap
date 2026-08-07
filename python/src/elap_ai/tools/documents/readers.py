"""Document readers for multiple formats."""

from typing import Optional, Any
import pandas as pd


class DocumentReader:
    """Reads and extracts text from multiple document formats."""

    @staticmethod
    def read_pdf(file_path: str) -> tuple[str, list[dict]]:
        """
        Read PDF and extract text and tables.

        Args:
            file_path: Path to PDF file

        Returns:
            Tuple of (full_text, tables_list)
        """
        try:
            import pdfplumber
        except ImportError:
            raise ImportError("pdfplumber required: pip install pdfplumber")

        text_parts = []
        tables = []

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract text
                text = page.extract_text()
                if text:
                    text_parts.append(text)

                # Extract tables
                for table in page.extract_tables() or []:
                    tables.append({
                        "page": page_num,
                        "data": table
                    })

        return "\n".join(text_parts), tables

    @staticmethod
    def read_excel(file_path: str) -> dict[str, pd.DataFrame]:
        """
        Read Excel file and return all sheets.

        Args:
            file_path: Path to Excel file

        Returns:
            Dictionary mapping sheet names to DataFrames
        """
        return pd.read_excel(file_path, sheet_name=None)

    @staticmethod
    def read_csv(file_path: str) -> pd.DataFrame:
        """
        Read CSV file.

        Args:
            file_path: Path to CSV file

        Returns:
            DataFrame
        """
        return pd.read_csv(file_path)

    @staticmethod
    def read_word(file_path: str) -> str:
        """
        Read Word document (.docx).

        Args:
            file_path: Path to Word file

        Returns:
            Extracted text
        """
        try:
            from docx import Document
        except ImportError:
            raise ImportError("python-docx required: pip install python-docx")

        doc = Document(file_path)
        text_parts = []

        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)

        # Also get tables
        for table in doc.tables:
            for row in table.rows:
                cells = [cell.text for cell in row.cells]
                text_parts.append(" | ".join(cells))

        return "\n".join(text_parts)

    @staticmethod
    def extract_images_from_pdf(file_path: str) -> list[str]:
        """
        Extract images from PDF.

        Args:
            file_path: Path to PDF file

        Returns:
            List of extracted image file paths
        """
        try:
            import pdfplumber
            from PIL import Image
            import io
        except ImportError:
            raise ImportError("pdfplumber and Pillow required")

        image_paths = []

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                for img_num, img in enumerate(page.images, 1):
                    try:
                        img_file = page.extract_image(img["srcsize"])
                        if img_file:
                            output_path = f"/tmp/pdf_img_{page_num}_{img_num}.png"
                            with open(output_path, "wb") as f:
                                f.write(img_file)
                            image_paths.append(output_path)
                    except Exception:
                        continue

        return image_paths

    @staticmethod
    def ocr_image(image_path: str) -> str:
        """
        Extract text from image using OCR.

        Args:
            image_path: Path to image file

        Returns:
            Extracted text
        """
        try:
            import easyocr
        except ImportError:
            raise ImportError("easyocr required: pip install easyocr")

        reader = easyocr.Reader(["es", "en"])
        results = reader.readtext(image_path)

        # Extract text from results
        text_parts = [line[1] for line in results]
        return " ".join(text_parts)
