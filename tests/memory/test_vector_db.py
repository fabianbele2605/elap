"""Tests for VectorStore."""

import pytest
import tempfile
from pathlib import Path
from elap_ai.memory.vector_db import VectorStore


@pytest.fixture
def temp_db_path():
    """Create temporary database directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_vector_store_initialization(temp_db_path):
    """Test VectorStore initialization."""
    store = VectorStore(db_path=temp_db_path)
    assert store.db_path == temp_db_path


def test_create_collection(temp_db_path):
    """Test creating a collection."""
    store = VectorStore(db_path=temp_db_path)
    store.create_collection("test_collection", metadata={"type": "test"})

    collections = store.list_collections()
    assert "test_collection" in collections


def test_add_documents(temp_db_path):
    """Test adding documents to collection."""
    store = VectorStore(db_path=temp_db_path)
    store.create_collection("docs", metadata={"type": "documents"})

    documents = [
        "Python es un lenguaje de programación",
        "JavaScript se usa en navegadores",
        "Rust es un lenguaje seguro"
    ]

    store.add_documents(
        collection_name="docs",
        documents=documents,
        metadata=[
            {"lang": "es", "type": "python"},
            {"lang": "es", "type": "javascript"},
            {"lang": "es", "type": "rust"}
        ]
    )

    stats = store.get_collection_stats("docs")
    assert stats["count"] == 3


def test_search_documents(temp_db_path):
    """Test searching for similar documents."""
    store = VectorStore(db_path=temp_db_path)
    store.create_collection("docs", metadata={"type": "documents"})

    documents = [
        "Las vacaciones son un derecho de los empleados",
        "El salario mínimo debe cumplirse",
        "Los impuestos se pagan anualmente",
        "La educación es importante"
    ]

    store.add_documents("docs", documents)

    # Search for documents about employment
    results = store.search("docs", "derechos de empleados", top_k=2)

    assert len(results) <= 2
    assert len(results) > 0
    assert "document" in results[0]


def test_search_returns_metadata(temp_db_path):
    """Test that search results include metadata."""
    store = VectorStore(db_path=temp_db_path)
    store.create_collection("docs", metadata={"type": "documents"})

    documents = ["Documento de prueba"]
    metadata = [{"source": "test.pdf", "page": 1}]

    store.add_documents(
        "docs",
        documents,
        metadata=metadata,
        ids=["doc_1"]
    )

    results = store.search("docs", "prueba", top_k=1)

    assert len(results) > 0
    assert results[0]["metadata"]["source"] == "test.pdf"


def test_delete_collection(temp_db_path):
    """Test deleting a collection."""
    store = VectorStore(db_path=temp_db_path)
    store.create_collection("temp")

    assert "temp" in store.list_collections()

    store.delete_collection("temp")

    assert "temp" not in store.list_collections()


def test_multiple_collections(temp_db_path):
    """Test managing multiple collections."""
    store = VectorStore(db_path=temp_db_path)

    store.create_collection("collection_a")
    store.create_collection("collection_b")

    store.add_documents("collection_a", ["Doc A"])
    store.add_documents("collection_b", ["Doc B"])

    results_a = store.search("collection_a", "A")
    results_b = store.search("collection_b", "B")

    assert len(results_a) > 0
    assert len(results_b) > 0


def test_custom_ids(temp_db_path):
    """Test adding documents with custom IDs."""
    store = VectorStore(db_path=temp_db_path)
    store.create_collection("docs", metadata={"type": "documents"})

    documents = ["Document 1", "Document 2"]
    ids = ["custom_id_1", "custom_id_2"]

    store.add_documents("docs", documents, ids=ids)

    results = store.search("docs", "Document", top_k=2)

    doc_ids = [r["id"] for r in results]
    assert "custom_id_1" in doc_ids or "custom_id_2" in doc_ids
