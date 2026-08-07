"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

# Add source to path
src_path = Path(__file__).parent.parent / "python" / "src"
sys.path.insert(0, str(src_path))

import pytest


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory."""
    test_dir = Path(__file__).parent / "data"
    test_dir.mkdir(exist_ok=True)
    return test_dir


@pytest.fixture
def sample_text():
    """Provide sample text for testing."""
    return """
    Este es un texto de ejemplo para pruebas.
    Contiene múltiples líneas y párrafos.

    Puede ser usado en tests de procesamiento de documentos
    y análisis de texto.
    """


@pytest.fixture
def sample_data():
    """Provide sample data structure."""
    return {
        "empresa": "Andina Foods",
        "empleados": [
            {"nombre": "Juan", "puesto": "Vendedor", "salario": 2000},
            {"nombre": "María", "puesto": "Analista", "salario": 2500},
        ],
        "productos": ["Producto A", "Producto B", "Producto C"],
    }
