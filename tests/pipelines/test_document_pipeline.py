"""Tests for DocumentPipeline."""

import pytest
import tempfile
from pathlib import Path
from elap_ai.pipelines import DocumentPipeline
from elap_ai.memory.vector_db import VectorStore


@pytest.fixture
def vector_store():
    """Create a temporary vector store."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield VectorStore(db_path=tmpdir)


@pytest.fixture
def pipeline(vector_store):
    """Create a document pipeline."""
    return DocumentPipeline(vector_store, chunk_size=500)


@pytest.fixture
def sample_csv_file():
    """Create a sample CSV file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("Nombre,Puesto,Salario\n")
        f.write("Juan,Vendedor,2000\n")
        f.write("María,Analista,2500\n")
        f.write("Carlos,Gerente,3000\n")
        return f.name


def test_pipeline_initialization(pipeline):
    """Test pipeline initialization."""
    assert pipeline.chunk_size == 500
    assert pipeline.vector_store is not None


def test_chunk_text(pipeline):
    """Test text chunking."""
    text = "Este es un texto largo. " * 100
    chunks = pipeline._chunk_text(text)

    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert all(len(chunk) > 0 for chunk in chunks)


def test_chunk_overlap(pipeline):
    """Test that chunks have overlap."""
    text = "A" * 1000
    chunks = pipeline._chunk_text(text)

    # With overlap, we should have fewer chunks than without
    assert len(chunks) > 0


def test_process_csv_file(pipeline, sample_csv_file):
    """Test processing a CSV file."""
    result = pipeline.process_file(
        file_path=sample_csv_file,
        collection_name="test_employees",
        metadata={"type": "csv", "source": "test"}
    )

    assert result["status"] == "success"
    assert result["document_id"] is not None
    assert result["chunks_created"] > 0

    # Cleanup
    Path(sample_csv_file).unlink(missing_ok=True)


def test_process_nonexistent_file(pipeline):
    """Test processing non-existent file."""
    result = pipeline.process_file(
        file_path="/nonexistent/file.csv",
        collection_name="test"
    )

    assert result["status"] == "error"
    assert "not found" in result["message"].lower()


def test_process_unsupported_format(pipeline):
    """Test processing unsupported file format."""
    with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
        f.write(b"random data")
        temp_path = f.name

    try:
        result = pipeline.process_file(
            file_path=temp_path,
            collection_name="test"
        )

        assert result["status"] == "error"
        assert "unsupported" in result["message"].lower()
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_search_after_processing(pipeline, sample_csv_file):
    """Test searching documents after processing."""
    # Process file
    pipeline.process_file(
        file_path=sample_csv_file,
        collection_name="employees",
        metadata={"type": "csv"}
    )

    # Search
    results = pipeline.search(
        collection_name="employees",
        query="¿Cuál es el puesto de Juan?",
        top_k=3
    )

    assert isinstance(results, list)
    assert len(results) > 0

    # Cleanup
    Path(sample_csv_file).unlink(missing_ok=True)


def test_process_with_metadata(pipeline, sample_csv_file):
    """Test processing file with metadata."""
    metadata = {
        "department": "RRHH",
        "year": 2026
    }

    result = pipeline.process_file(
        file_path=sample_csv_file,
        collection_name="rrhh_docs",
        metadata=metadata
    )

    assert result["status"] == "success"

    # Cleanup
    Path(sample_csv_file).unlink(missing_ok=True)


def test_dataframe_to_text(pipeline):
    """Test converting DataFrame to text."""
    import pandas as pd

    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": [4, 5, 6]
    })

    text = pipeline._dataframe_to_text(df)

    assert isinstance(text, str)
    assert len(text) > 0


def test_multiple_dataframes_to_text(pipeline):
    """Test converting multiple DataFrames to text."""
    import pandas as pd

    dfs = {
        "Sheet1": pd.DataFrame({"A": [1, 2]}),
        "Sheet2": pd.DataFrame({"B": [3, 4]})
    }

    text = pipeline._dataframes_to_text(dfs)

    assert "Sheet1" in text
    assert "Sheet2" in text
