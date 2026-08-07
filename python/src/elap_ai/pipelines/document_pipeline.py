"""Pipeline for document upload, chunking, and RAG indexing."""

from typing import Optional, Any
import os
from pathlib import Path

from ..tools.documents.readers import DocumentReader
from ..memory.vector_db import VectorStore


class DocumentPipeline:
    """
    Pipeline to process documents: upload → chunk → embed → index.
    """

    def __init__(self, vector_store: VectorStore, chunk_size: int = 500):
        """
        Initialize pipeline.

        Args:
            vector_store: VectorStore instance for indexing
            chunk_size: Number of characters per chunk
        """
        self.vector_store = vector_store
        self.chunk_size = chunk_size
        self.reader = DocumentReader()

    def process_file(
        self,
        file_path: str,
        collection_name: str,
        metadata: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Process a document file and index it.

        Args:
            file_path: Path to document
            collection_name: Collection to index into
            metadata: Optional metadata to attach

        Returns:
            Processing result {status, chunks_created, document_id}
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return {"status": "error", "message": f"File not found: {file_path}"}

        # Extract text based on file type
        try:
            if file_path.suffix.lower() == ".pdf":
                text, tables = self.reader.read_pdf(str(file_path))
                # TODO: Process tables separately
            elif file_path.suffix.lower() == ".xlsx":
                dfs = self.reader.read_excel(str(file_path))
                text = self._dataframes_to_text(dfs)
            elif file_path.suffix.lower() == ".csv":
                df = self.reader.read_csv(str(file_path))
                text = self._dataframe_to_text(df)
            elif file_path.suffix.lower() == ".docx":
                text = self.reader.read_word(str(file_path))
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported file type: {file_path.suffix}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error reading file: {str(e)}"
            }

        # Chunk text
        chunks = self._chunk_text(text)

        # Create collection if needed
        if collection_name not in self.vector_store.list_collections():
            self.vector_store.create_collection(collection_name)

        # Index chunks
        doc_id = file_path.stem
        chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        chunk_metadata = [
            {
                "source": str(file_path),
                "chunk_index": i,
                "total_chunks": len(chunks),
                **(metadata or {})
            }
            for i in range(len(chunks))
        ]

        # Ensure metadata has at least one key per dict for chromadb
        clean_metadata = []
        for m in chunk_metadata:
            if not m:
                clean_metadata.append({"index": len(clean_metadata)})
            else:
                clean_metadata.append(m)

        self.vector_store.add_documents(
            collection_name=collection_name,
            documents=chunks,
            metadata=clean_metadata,
            ids=chunk_ids,
        )

        return {
            "status": "success",
            "document_id": doc_id,
            "chunks_created": len(chunks),
            "collection": collection_name,
        }

    def search(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5,
    ) -> list[str]:
        """
        Search for relevant document chunks.

        Args:
            collection_name: Collection to search
            query: Search query
            top_k: Number of results

        Returns:
            List of relevant chunks
        """
        # Ensure collection exists with metadata
        if collection_name not in self.vector_store.list_collections():
            self.vector_store.create_collection(collection_name, metadata={"type": "search"})

        results = self.vector_store.search(collection_name, query, top_k)
        return [r["document"] for r in results]

    def _chunk_text(self, text: str) -> list[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Full text to chunk

        Returns:
            List of text chunks
        """
        chunks = []
        overlap = self.chunk_size // 4

        for i in range(0, len(text), self.chunk_size - overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk.strip():
                chunks.append(chunk)

        return chunks

    def _dataframe_to_text(self, df) -> str:
        """Convert DataFrame to text representation."""
        return df.to_string()

    def _dataframes_to_text(self, dfs: dict) -> str:
        """Convert dict of DataFrames to text."""
        parts = []
        for sheet_name, df in dfs.items():
            parts.append(f"=== Sheet: {sheet_name} ===")
            parts.append(df.to_string())
            parts.append("")
        return "\n".join(parts)
