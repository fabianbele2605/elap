"""Core Document Engine - Orquestador central"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentEngine:
    """Orquestador central para generación de documentos profesionales"""

    def __init__(self, theme: str = "default", language: str = "es", output_dir: str = "/tmp/elap_documents"):
        """
        Inicializa Document Engine

        Args:
            theme: Tema corporativo (andina_foods, default, professional)
            language: Idioma (es, en)
            output_dir: Directorio de salida para documentos generados
        """
        self.theme = theme
        self.language = language
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Cargar temas
        self.themes = self._load_themes()
        self.current_theme = self.themes.get(theme, self.themes["default"])

        logger.info(f"DocumentEngine initialized with theme: {theme}")

    def _load_themes(self) -> Dict[str, Dict[str, Any]]:
        """Carga configuración de temas desde YAML"""
        theme_file = Path(__file__).parent / "assets" / "themes.yaml"
        try:
            with open(theme_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config.get("themes", {})
        except Exception as e:
            logger.error(f"Error cargando temas: {e}")
            return {}

    def generate_word(
        self,
        document_type: str,
        data: Dict[str, Any],
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Genera documento Word profesional

        Args:
            document_type: Tipo de documento (contract, report, invoice)
            data: Datos para rellenar template
            output_filename: Nombre del archivo (opcional)

        Returns:
            Path al archivo generado
        """
        from .generators.word_generator import WordGenerator

        if not output_filename:
            output_filename = f"{document_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"

        output_path = self.output_dir / output_filename

        generator = WordGenerator(theme=self.current_theme, language=self.language)
        generator.generate(document_type, data, output_path)

        logger.info(f"Word document generated: {output_path}")
        return output_path

    def generate_pdf(
        self,
        document_type: str,
        data: Dict[str, Any],
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Genera documento PDF profesional

        Args:
            document_type: Tipo de documento
            data: Datos para rellenar
            output_filename: Nombre del archivo

        Returns:
            Path al archivo generado
        """
        from .generators.pdf_generator import PDFGenerator

        if not output_filename:
            output_filename = f"{document_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        output_path = self.output_dir / output_filename

        generator = PDFGenerator(theme=self.current_theme, language=self.language)
        generator.generate(document_type, data, output_path)

        logger.info(f"PDF document generated: {output_path}")
        return output_path

    def generate_excel(
        self,
        document_type: str,
        data: Dict[str, Any],
        output_filename: Optional[str] = None
    ) -> Path:
        """Genera documento Excel"""
        from .generators.excel_generator import ExcelGenerator

        if not output_filename:
            output_filename = f"{document_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        output_path = self.output_dir / output_filename

        generator = ExcelGenerator(theme=self.current_theme, language=self.language)
        generator.generate(document_type, data, output_path)

        logger.info(f"Excel document generated: {output_path}")
        return output_path

    def generate_powerpoint(
        self,
        document_type: str,
        data: Dict[str, Any],
        output_filename: Optional[str] = None
    ) -> Path:
        """Genera presentación PowerPoint"""
        from .generators.powerpoint_generator import PowerPointGenerator

        if not output_filename:
            output_filename = f"{document_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"

        output_path = self.output_dir / output_filename

        generator = PowerPointGenerator(theme=self.current_theme, language=self.language)
        generator.generate(document_type, data, output_path)

        logger.info(f"PowerPoint document generated: {output_path}")
        return output_path

    def generate_html(
        self,
        document_type: str,
        data: Dict[str, Any]
    ) -> str:
        """
        Genera HTML para correos o visualización web

        Returns:
            String HTML
        """
        from .generators.html_generator import HTMLGenerator

        generator = HTMLGenerator(theme=self.current_theme, language=self.language)
        return generator.generate(document_type, data)

    def list_available_themes(self) -> list:
        """Lista temas disponibles"""
        return list(self.themes.keys())

    def set_theme(self, theme: str) -> None:
        """Cambia el tema actual"""
        if theme in self.themes:
            self.theme = theme
            self.current_theme = self.themes[theme]
            logger.info(f"Theme changed to: {theme}")
        else:
            logger.warning(f"Theme not found: {theme}")
