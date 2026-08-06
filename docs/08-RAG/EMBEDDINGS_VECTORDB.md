# Embeddings + Vector DB — RAG Implementation

**Autor**: ELAP Development Team  
**Fecha**: 2026-08-05  
**Versión**: 1.0  
**Fase**: 14

## Descripción General

Implementación de **RAG (Retrieval-Augmented Generation)** con embeddings de Ollama y vector DB en memoria.

---

## Arquitectura

```
Query
  ↓
Embeddings Client (Ollama)
  ↓
Generate Embedding
  ↓
Vector DB Search
  ↓
Retrieve Similar Documents
  ↓
Augment Context
  ↓
Return to Agent
```

---

## Componentes

### 1. Embeddings Client

Integración con **Ollama** para generar embeddings.

**Modelos soportados**:
- `nomic-embed-text` (768 dims)
- `mxbai-embed-large` (1024 dims)
- `all-minilm` (384 dims - lightweight)

**Ejemplo**:

```python
from elap_ai.embeddings import EmbeddingsClient, NOMIC_EMBED

client = EmbeddingsClient(
    ollama_url="http://localhost:11434",
    model=NOMIC_EMBED
)

# Generar embedding
embedding = await client.embed("Hello world")

# Batch
embeddings = await client.embed_batch([
    "Text 1",
    "Text 2",
    "Text 3"
])

# Health check
is_healthy = await client.health_check()
```

### 2. Vector DB Manager

Almacenamiento y búsqueda de vectores (in-memory).

**Backend**: `InMemoryVectorDB`
- Almacenamiento en memoria
- Búsqueda por similitud coseno
- Escalable para desarrollo/testing

**Ejemplo**:

```python
from elap_ai.vectordb import VectorDBManager, Vector

manager = VectorDBManager()

# Insertar vector
vector = Vector(
    id="doc_1",
    vector=[1.0, 0.2, 0.5],
    text="Document content",
    metadata={"source": "file.txt"}
)
await manager.insert(vector)

# Buscar similares
results = await manager.search(
    query_vector=[1.0, 0.2, 0.5],
    limit=5,
    threshold=0.5
)

for result in results:
    print(f"{result.text} (similitud: {result.similarity:.2%})")
```

### 3. RAG Orchestrator

Coordina embeddings + vector DB.

**API**:

```python
from elap_ai.rag import RAGOrchestrator

rag = RAGOrchestrator()

# Indexar documentos
await rag.index_text("doc_1", "Python tutorial", {"category": "programming"})

await rag.index_batch({
    "doc_1": "Content 1",
    "doc_2": "Content 2",
})

# Recuperar documentos relevantes
results = await rag.retrieve("python", limit=3)

# Generar contexto aumentado
context = await rag.augment_context("How to learn Python?")
# Output: ==== CONTEXTO RECUPERADO ====
#         [1] (similitud: 95%) Content 1
#         [2] (similitud: 89%) Content 2

# Health check
health = await rag.health_check()
# {"embeddings": True, "vectordb": True}
```

---

## Flujo RAG Completo

```
Agent Query
    ↓
RAG.retrieve() → Buscar documentos relevantes
    ↓
Generar contexto aumentado
    ↓
Pasar contexto al agente
    ↓
Agente genera respuesta fundamentada
```

---

## Tests

**Cobertura**:
- Embeddings client (health check, list models)
- Vector DB (insert, search, delete, similarity)
- RAG orchestrator (index, retrieve, augment)

**Ejecutar**:

```bash
cd python
pytest tests/test_embeddings.py -v
pytest tests/test_vectordb.py -v
pytest tests/test_rag.py -v
```

---

## Métricas Fase 14

| Métrica | Valor |
|---------|-------|
| Archivos Python | 6 |
| Líneas de código | ~500 |
| Tests | 16 |
| Cobertura | 90%+ |
| Componentes | 3 (Embeddings, VectorDB, RAG) |

---

## Próximos Pasos (Fase 15+)

- [ ] Integración Qdrant (persistencia)
- [ ] ChromaDB alternativa
- [ ] Semantic caching
- [ ] Reranking con cross-encoders
- [ ] Hybrid search (BM25 + semantic)

---

**Última actualización**: 2026-08-05
