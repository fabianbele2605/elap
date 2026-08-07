"""Tests for DocumentGenerator and ChartGenerator."""

import pytest
import tempfile
from pathlib import Path
from elap_ai.tools.documents import DocumentGenerator, ChartGenerator


def test_generator_initialization():
    """Test generators can be instantiated."""
    gen_doc = DocumentGenerator()
    gen_chart = ChartGenerator()

    assert gen_doc is not None
    assert gen_chart is not None


def test_generate_pdf_report():
    """Test PDF report generation."""
    sections = [
        {
            "title": "Resumen",
            "content": "Este es un reporte de prueba"
        },
        {
            "title": "Detalles",
            "content": "Información adicional del reporte"
        }
    ]

    pdf_bytes = DocumentGenerator.generate_pdf_report(
        title="Reporte de Prueba",
        sections=sections,
        company_name="Empresa de Prueba"
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert b"PDF" in pdf_bytes[:10] or b"%PDF" in pdf_bytes[:10]


def test_generate_excel_report():
    """Test Excel workbook generation."""
    import pandas as pd

    data = {
        "Ventas": pd.DataFrame({
            "Mes": ["Enero", "Febrero", "Marzo"],
            "Cantidad": [100, 150, 200]
        }),
        "Gastos": pd.DataFrame({
            "Mes": ["Enero", "Febrero", "Marzo"],
            "Cantidad": [50, 60, 70]
        })
    }

    excel_bytes = DocumentGenerator.generate_excel_report(
        data=data,
        title="Reporte Financiero"
    )

    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 0


def test_generate_word_document():
    """Test Word document generation."""
    sections = [
        {
            "title": "Introducción",
            "content": "Contenido de introducción"
        },
        {
            "title": "Metodología",
            "content": "Descripción de metodología",
            "bullet_points": ["Punto 1", "Punto 2", "Punto 3"]
        }
    ]

    docx_bytes = DocumentGenerator.generate_word_document(
        title="Documento de Prueba",
        sections=sections,
        company_name="Test Company"
    )

    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 0


def test_bar_chart_generation():
    """Test bar chart generation."""
    data = {
        "Producto A": 100,
        "Producto B": 150,
        "Producto C": 120
    }

    chart_path = ChartGenerator.bar_chart(
        data=data,
        title="Ventas por Producto"
    )

    assert isinstance(chart_path, str)
    assert Path(chart_path).exists()
    assert chart_path.endswith(".png")

    # Cleanup
    Path(chart_path).unlink(missing_ok=True)


def test_line_chart_generation():
    """Test line chart generation."""
    data = {
        "Serie 1": [10, 20, 30, 40, 50],
        "Serie 2": [15, 25, 35, 45, 55]
    }
    x_labels = ["Ene", "Feb", "Mar", "Abr", "May"]

    chart_path = ChartGenerator.line_chart(
        data=data,
        x_labels=x_labels,
        title="Evolución de Ventas"
    )

    assert Path(chart_path).exists()
    assert chart_path.endswith(".png")

    Path(chart_path).unlink(missing_ok=True)


def test_pie_chart_generation():
    """Test pie chart generation."""
    data = {
        "Ventas": 40,
        "Gastos": 35,
        "Otros": 25
    }

    chart_path = ChartGenerator.pie_chart(
        data=data,
        title="Distribución de Recursos"
    )

    assert Path(chart_path).exists()
    assert chart_path.endswith(".png")

    Path(chart_path).unlink(missing_ok=True)


def test_histogram_generation():
    """Test histogram generation."""
    data = [10, 20, 20, 30, 30, 30, 40, 40, 40, 40, 50]

    chart_path = ChartGenerator.histogram(
        data=data,
        title="Distribución de Valores",
        bins=5
    )

    assert Path(chart_path).exists()
    assert chart_path.endswith(".png")

    Path(chart_path).unlink(missing_ok=True)


def test_scatter_plot_generation():
    """Test scatter plot generation."""
    x_data = [1, 2, 3, 4, 5]
    y_data = [2, 4, 5, 4, 6]

    chart_path = ChartGenerator.scatter_plot(
        x_data=x_data,
        y_data=y_data,
        title="Correlación de Datos"
    )

    assert Path(chart_path).exists()
    assert chart_path.endswith(".png")

    Path(chart_path).unlink(missing_ok=True)


def test_pdf_with_multiple_sections():
    """Test PDF with many sections."""
    sections = [
        {"title": f"Sección {i}", "content": f"Contenido {i}"}
        for i in range(5)
    ]

    pdf_bytes = DocumentGenerator.generate_pdf_report(
        title="Reporte Extenso",
        sections=sections
    )

    assert len(pdf_bytes) > 1000
