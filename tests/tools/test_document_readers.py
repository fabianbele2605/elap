"""Tests for DocumentReader."""

import pytest
import tempfile
from pathlib import Path
from elap_ai.tools.documents import DocumentReader


@pytest.fixture
def sample_csv_file():
    """Create a sample CSV file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("Nombre,Edad,Puesto\n")
        f.write("Juan,30,Vendedor\n")
        f.write("María,28,Analista\n")
        f.write("Carlos,35,Gerente\n")
        return f.name


@pytest.fixture
def cleanup(sample_csv_file):
    """Cleanup temp files."""
    yield
    Path(sample_csv_file).unlink(missing_ok=True)


def test_document_reader_initialization():
    """Test DocumentReader can be instantiated."""
    reader = DocumentReader()
    assert reader is not None


def test_read_csv(sample_csv_file, cleanup):
    """Test reading CSV file."""
    df = DocumentReader.read_csv(sample_csv_file)

    assert len(df) == 3
    assert "Nombre" in df.columns
    assert df.iloc[0]["Nombre"] == "Juan"
    assert df.iloc[2]["Edad"] == 35


def test_csv_data_types(sample_csv_file, cleanup):
    """Test that CSV data types are correct."""
    df = DocumentReader.read_csv(sample_csv_file)

    assert str(df["Nombre"].dtype) in ("object", "string", "str")
    assert "int" in str(df["Edad"].dtype)


def test_read_pdf_missing_file():
    """Test reading non-existent PDF raises error."""
    with pytest.raises(Exception):
        DocumentReader.read_pdf("/nonexistent/file.pdf")


def test_read_excel_missing_file():
    """Test reading non-existent Excel raises error."""
    with pytest.raises(Exception):
        DocumentReader.read_excel("/nonexistent/file.xlsx")


def test_read_word_missing_file():
    """Test reading non-existent Word doc raises error."""
    with pytest.raises(Exception):
        DocumentReader.read_word("/nonexistent/file.docx")


def test_document_reader_methods_exist():
    """Test that all reader methods exist."""
    reader = DocumentReader()

    assert hasattr(reader, 'read_pdf')
    assert hasattr(reader, 'read_excel')
    assert hasattr(reader, 'read_csv')
    assert hasattr(reader, 'read_word')
    assert hasattr(reader, 'ocr_image')


def test_csv_empty_file():
    """Test reading empty CSV."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("Nombre,Edad\n")
        temp_path = f.name

    try:
        df = DocumentReader.read_csv(temp_path)
        assert len(df) == 0
        assert "Nombre" in df.columns
    finally:
        Path(temp_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_read_csv_with_special_chars():
    """Test reading CSV with special characters."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write("Nombre,Descripción\n")
        f.write("Español,Lenguaje de España\n")
        f.write("Francés,Lenguaje de Francia\n")
        temp_path = f.name

    try:
        df = DocumentReader.read_csv(temp_path)
        assert "Español" in df["Nombre"].values
        assert "Lenguaje de España" in df["Descripción"].values
    finally:
        Path(temp_path).unlink(missing_ok=True)
