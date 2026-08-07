# 🔧 Fase 2: Guía de Integración

**Fecha:** 2026-08-07  
**Estado:** Estructura creada, lista para desarrollo

---

## 📦 Módulos Creados

### 1. **agents/** — LangGraph Orchestration

```python
from elap_ai.agents import LangGraphAgent, AgentState

agent = LangGraphAgent(
    agent_id="agent_ventas",
    agent_name="Ventas Assistant",
    agent_role="Ventas",
    system_prompt="Eres un asistente de ventas...",
    empresa_contexto={
        "nombre": "Andina Foods",
        "sector": "Alimentos",
        ...
    }
)

response = await agent.execute(
    user_input="¿Cuáles son nuestros productos más vendidos?",
    context_docs=["Producto A: ...", "Producto B: ..."]
)
```

**Archivos:**
- `agent_state.py` — AgentState TypedDict con campos de conversación, contexto, documentos
- `langgraph_agent.py` — Clase principal LangGraphAgent
- `graph_builder.py` — Construcción del grafo con nodos: input → select_tool → execute_tool → generate_response

### 2. **tools/documents/** — Document Processing

```python
from elap_ai.tools.documents import DocumentReader, DocumentGenerator, ChartGenerator

# Lectura
text, tables = DocumentReader.read_pdf("documento.pdf")
df = DocumentReader.read_excel("datos.xlsx")
text = DocumentReader.read_word("informe.docx")

# Generación
pdf_bytes = DocumentGenerator.generate_pdf_report(
    title="Reporte de Ventas",
    sections=[
        {
            "title": "Resumen",
            "content": "Ventas totales: $100K",
            "chart_path": "/tmp/chart.png"
        }
    ]
)

# Gráficos
chart_path = ChartGenerator.bar_chart(
    data={"Enero": 1000, "Febrero": 1500},
    title="Ventas por Mes"
)
```

**Archivos:**
- `readers.py` — DocumentReader (PDF, Excel, Word, CSV, OCR)
- `writers.py` — DocumentGenerator (PDF, Excel, Word)
- `charts.py` — ChartGenerator (bar, line, pie, histogram, scatter)

### 3. **tools/registry.py** — Tool Registration

```python
from elap_ai.tools import ToolRegistry

registry = ToolRegistry()

# Register tools
registry.register(
    name="read_pdf",
    description="Read PDF document",
    parameters={
        "type": "object",
        "properties": {"file_path": {"type": "string"}},
        "required": ["file_path"]
    },
    func=DocumentReader.read_pdf
)

# List tools
tools = registry.list_tools()

# Execute tool
result = registry.execute_tool("read_pdf", file_path="doc.pdf")
```

### 4. **memory/** — RAG & Embeddings

```python
from elap_ai.memory import EmbeddingService, VectorStore

# Embeddings
embeddings = EmbeddingService(model_name="all-MiniLM-L6-v2")
embed = embeddings.embed("Texto a embedificar")
embeds = embeddings.embed_batch(["Texto 1", "Texto 2"])

# Vector DB
vector_store = VectorStore(db_path="./data/chromadb")
vector_store.create_collection("documentos_empresa")

vector_store.add_documents(
    collection_name="documentos_empresa",
    documents=["Documento 1...", "Documento 2..."],
    metadata=[{"source": "pdf1"}, {"source": "pdf2"}]
)

# Search
results = vector_store.search(
    collection_name="documentos_empresa",
    query="¿Cuál es la política de vacaciones?",
    top_k=5
)
```

**Archivos:**
- `embeddings.py` — EmbeddingService (sentence-transformers)
- `vector_db.py` — VectorStore (chromadb wrapper)

### 5. **pipelines/** — Document Processing Pipeline

```python
from elap_ai.pipelines import DocumentPipeline
from elap_ai.memory import VectorStore

vector_store = VectorStore()
pipeline = DocumentPipeline(vector_store, chunk_size=500)

# Upload and index document
result = pipeline.process_file(
    file_path="/path/to/documento.pdf",
    collection_name="documentos_rrhh",
    metadata={"department": "RRHH", "year": 2026}
)

# Search indexed documents
chunks = pipeline.search(
    collection_name="documentos_rrhh",
    query="¿Cuál es el procedimiento de vacaciones?",
    top_k=5
)
```

---

## 🔌 Integración con gRPC (Python Backend)

En `grpc_server.py`, agregar nuevo endpoint para herramientas:

```python
class ElAPServicer(agent_pb2_grpc.ElAPServicer):
    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.vector_store = VectorStore()
        
    async def ejecutar_herramienta(self, request, context):
        """Execute a tool and return result"""
        try:
            result = self.tool_registry.execute_tool(
                name=request.tool_name,
                **json.loads(request.parameters)
            )
            return agent_pb2.ToolResponse(
                success=True,
                result=json.dumps(result)
            )
        except Exception as e:
            return agent_pb2.ToolResponse(
                success=False,
                error=str(e)
            )
```

---

## 🔌 Integración con Rust Backend

Nuevos endpoints en `crates/elap-core/src/api/handlers.rs`:

```rust
// POST /documents/upload
pub async fn upload_document(
    multipart: Multipart,
) -> Result<Json<DocumentResponse>, StatusCode> {
    // Guardar archivo
    // Llamar a Python para procesamiento
    // Retornar metadata
}

// GET /documents/search
pub async fn search_documents(
    Query(params): Query<SearchQuery>,
) -> Result<Json<SearchResult>, StatusCode> {
    // Llamar a Python para búsqueda RAG
    // Retornar chunks recuperados
}

// POST /documents/generate-report
pub async fn generate_report(
    Json(request): Json<ReportRequest>,
) -> Result<Bytes, StatusCode> {
    // Llamar a Python para generar PDF/Excel
    // Retornar archivo binario
}
```

---

## 🧪 Testing Strategy

### Unit Tests (Python)

```bash
# Test embeddings
pytest tests/memory/test_embeddings.py -v

# Test document readers
pytest tests/tools/test_readers.py -v

# Test vector DB
pytest tests/memory/test_vector_db.py -v

# Test pipeline
pytest tests/pipelines/test_document_pipeline.py -v
```

**Archivo de ejemplo:** `tests/memory/test_vector_db.py`

```python
import pytest
from elap_ai.memory import VectorStore, EmbeddingService

def test_vector_store_creation():
    store = VectorStore(db_path=":memory:")
    store.create_collection("test")
    assert "test" in store.list_collections()

@pytest.mark.asyncio
async def test_add_and_search():
    store = VectorStore(db_path=":memory:")
    store.create_collection("test")
    
    store.add_documents(
        "test",
        documents=["Python es un lenguaje", "JavaScript es versátil"],
        metadata=[{"lang": "es"}, {"lang": "es"}]
    )
    
    results = store.search("test", "lenguaje de programación", top_k=1)
    assert len(results) == 1
    assert "Python" in results[0]["document"]
```

---

## 📊 Cronograma Semana 1

**LangGraph Integration:**

| Tarea | Status | Fecha |
|-------|--------|-------|
| [ ] Instalar langgraph | ⏳ | 2026-08-07 |
| [ ] Validar AgentState | ⏳ | 2026-08-07 |
| [ ] Tests de graph_builder | ⏳ | 2026-08-08 |
| [ ] Integrar con grpc_server.py | ⏳ | 2026-08-08 |
| [ ] End-to-end test | ⏳ | 2026-08-09 |

---

## 🚀 Próximos Pasos

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Crear tests directory:**
   ```bash
   mkdir -p tests/memory tests/tools tests/agents tests/pipelines
   ```

3. **Ejecutar tests básicos:**
   ```bash
   pytest tests/ -v
   ```

4. **Integrar con gRPC:** Actualizar `grpc_server.py` para usar LangGraphAgent

5. **Frontend:** Crear endpoints en Rust para `/documents` API

---

## 📚 Documentación

- **[FASE_2_PLAN.md](FASE_2_PLAN.md)** — Plan técnico completo
- **[FASE_2_IMPLEMENTACION.md](FASE_2_IMPLEMENTACION.md)** — Detalles de implementación
- API Reference: Será generado en Semana 3

---

**Generado:** 2026-08-07  
**Próxima actualización:** Post-Semana 1
