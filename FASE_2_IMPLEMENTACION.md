# 🔧 FASE 2: Plan Técnico de Implementación

**Objetivo:** Agentes inteligentes que lean, generen y procesen documentos  
**Duración:** 2-3 semanas  
**Enfoque:** LangGraph + Document Tools + RAG Base

---

## 📦 Instalación de Librerías

```bash
# Python - Document Processing
pip install langraph langchain pydantic-ai
pip install pypdf pdfplumber python-docx openpyxl xlsxwriter
pip install reportlab pandas pillow

# Embeddings & RAG
pip install sentence-transformers chromadb
pip install fastembed qdrant-client

# Graficación
pip install matplotlib plotly kaleido seaborn

# OCR
pip install easyocr

# Utils
pip install numpy scipy scikit-learn
```

**Actualizar:** `python/requirements.txt`

---

## 🗂️ Estructura de Módulos Python

```
python/src/elap_ai/
├── agent_runtime.py          # Mantener existente
├── grpc_server.py            # Mantener existente
│
├── agents/                    # ⭐ NUEVO
│   ├── __init__.py
│   ├── langgraph_agent.py    # Orquestación LangGraph
│   ├── agent_state.py        # Estado del agente
│   └── graph_builder.py      # Constructor de grafos
│
├── tools/                     # ⭐ NUEVO - Herramientas
│   ├── __init__.py
│   ├── documents/
│   │   ├── __init__.py
│   │   ├── readers.py        # Lectura: PDF, Excel, Word
│   │   ├── writers.py        # Generación: PDF, Excel
│   │   ├── extractors.py     # OCR, tablas
│   │   └── processors.py     # Procesamiento de datos
│   │
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── reports.py        # Reportes PDF
│   │   ├── charts.py         # Gráficos
│   │   └── excel.py          # Excel avanzado
│   │
│   └── registry.py           # Registro de herramientas
│
├── memory/                    # ⭐ NUEVO - RAG & Memory
│   ├── __init__.py
│   ├── embeddings.py         # sentence-transformers
│   ├── vector_db.py          # chromadb/faiss
│   ├── retriever.py          # Recuperación
│   └── indexer.py            # Indexación de docs
│
├── pipelines/                 # ⭐ NUEVO - Flujos
│   ├── __init__.py
│   ├── document_pipeline.py   # Upload → Index → Search
│   └── report_pipeline.py     # Data → Generate → Export
│
└── config/
    ├── tools_config.yaml     # Configuración de tools
    └── rag_config.yaml       # Configuración RAG
```

---

## 🧠 LangGraph Integration

### Estructura de Agent State

```python
# agents/agent_state.py
from typing import Annotated, Any
from langchain_core.messages import BaseMessage, AnyMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Conversación
    messages: Annotated[list[AnyMessage], add_messages]
    
    # Contexto
    agent_id: str
    agent_name: str
    agent_role: str
    system_prompt: str
    empresa_contexto: dict
    
    # Documentos
    uploaded_documents: list[str]  # paths
    retrieved_context: list[str]   # chunks recuperados
    
    # Estado
    current_tool: str | None
    tool_results: dict[str, Any]
    agent_memory: dict[str, Any]
```

### Graph Builder

```python
# agents/graph_builder.py
def build_agent_graph(agent_config: AgentConfig):
    """
    Construir grafo de agente con:
    - Node: Procesamiento de mensajes
    - Node: Selección de herramientas
    - Node: Ejecución de herramientas
    - Node: Generación de respuesta
    - Edges: Transiciones con condicionales
    """
    
    graph = StateGraph(AgentState)
    
    # Nodos
    graph.add_node("process_input", process_input_node)
    graph.add_node("select_tool", tool_selector_node)
    graph.add_node("execute_tool", tool_executor_node)
    graph.add_node("generate_response", response_generator_node)
    
    # Edges
    graph.add_edge("process_input", "select_tool")
    graph.add_conditional_edges(
        "select_tool",
        route_to_tool,  # Función que decide si usar tool o generar respuesta
        {
            "execute": "execute_tool",
            "respond": "generate_response"
        }
    )
    graph.add_edge("execute_tool", "generate_response")
    graph.add_edge("generate_response", END)
    
    graph.set_entry_point("process_input")
    
    return graph.compile()
```

---

## 📄 Document Tools Implementation

### Lectura de Documentos

```python
# tools/documents/readers.py

class DocumentReader:
    """Lee múltiples formatos de documentos"""
    
    @staticmethod
    def read_pdf(path: str) -> tuple[str, list[dict]]:
        """
        Lee PDF y extrae:
        - Texto completo
        - Tablas (como dicts)
        - Metadata
        """
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            text = "".join(page.extract_text() for page in pdf.pages)
            tables = []
            for page in pdf.pages:
                for table in page.extract_tables():
                    tables.append({"data": table, "page": page.page_number})
        return text, tables
    
    @staticmethod
    def read_excel(path: str) -> dict[str, Any]:
        """Lee Excel y retorna sheets como DataFrames"""
        import pandas as pd
        return pd.read_excel(path, sheet_name=None)
    
    @staticmethod
    def read_word(path: str) -> str:
        """Lee Word docx"""
        from docx import Document
        doc = Document(path)
        return "\n".join(para.text for para in doc.paragraphs)
```

### Generación de Documentos

```python
# tools/documents/writers.py

class DocumentGenerator:
    """Genera documentos profesionales"""
    
    @staticmethod
    def generate_pdf_report(
        title: str,
        sections: list[dict],  # {title, content, charts}
        company_logo: str | None = None
    ) -> bytes:
        """Genera PDF con reportlab"""
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Image
        
        # Construir elementos
        elements = [Paragraph(title, styles['Heading1'])]
        for section in sections:
            elements.append(Paragraph(section['title'], styles['Heading2']))
            elements.append(Paragraph(section['content'], styles['Normal']))
            if 'chart_path' in section:
                elements.append(Image(section['chart_path'], width=500, height=300))
        
        # Compilar a PDF
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        doc.build(elements)
        return pdf_buffer.getvalue()
    
    @staticmethod
    def generate_excel_report(
        data: dict[str, pd.DataFrame],
        title: str = "Report"
    ) -> bytes:
        """Genera Excel con xlsxwriter"""
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for sheet_name, df in data.items():
                df.to_excel(writer, sheet_name=sheet_name)
        return output.getvalue()
```

### Gráficos

```python
# tools/documents/charts.py

class ChartGenerator:
    """Genera gráficos profesionales"""
    
    @staticmethod
    def bar_chart(data: dict[str, float], title: str) -> str:
        """Genera gráfico de barras → PNG"""
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 6))
        plt.bar(data.keys(), data.values())
        plt.title(title)
        path = f"/tmp/{uuid.uuid4()}.png"
        plt.savefig(path, dpi=150)
        plt.close()
        return path
    
    @staticmethod
    def line_chart(data: list[tuple[str, float]], title: str) -> str:
        """Gráfico de líneas → PNG"""
        import matplotlib.pyplot as plt
        x_vals, y_vals = zip(*data)
        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, marker='o')
        plt.title(title)
        path = f"/tmp/{uuid.uuid4()}.png"
        plt.savefig(path, dpi=150)
        plt.close()
        return path
```

---

## 🧠 RAG Implementation

### Embeddings & Indexing

```python
# memory/embeddings.py

class EmbeddingService:
    """Genera embeddings con sentence-transformers"""
    
    def __init__(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def embed(self, text: str) -> list[float]:
        """Texto → embedding vector"""
        return self.model.encode(text, convert_to_tensor=False).tolist()
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embeddings"""
        return self.model.encode(texts, convert_to_tensor=False).tolist()
```

### Vector Database

```python
# memory/vector_db.py

class VectorStore:
    """Chromadb wrapper para buscar documentos"""
    
    def __init__(self):
        import chromadb
        self.client = chromadb.Client()
        self.collection = None
    
    def create_collection(self, name: str):
        self.collection = self.client.get_or_create_collection(name=name)
    
    def add_documents(self, docs: list[str], metadata: list[dict] = None):
        """Indexar documentos"""
        embeddings = EmbeddingService().embed_batch(docs)
        self.collection.add(
            ids=[f"doc_{i}" for i in range(len(docs))],
            documents=docs,
            embeddings=embeddings,
            metadatas=metadata or [{}] * len(docs)
        )
    
    def search(self, query: str, top_k: int = 5) -> list[str]:
        """Buscar documentos similares"""
        query_embedding = EmbeddingService().embed(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results['documents'][0]
```

---

## 🔌 Rust Backend Endpoints (Nuevos)

```rust
// crates/elap-core/src/api/handlers.rs

// POST /documents/upload
pub async fn upload_document(
    multipart: Multipart,
    state: AppState,
) -> Result<Json<DocumentResponse>, StatusCode> {
    // Guardar archivo
    // Indexar en RAG
    // Retornar metadata
}

// GET /documents/{id}/search
pub async fn search_documents(
    Path(agent_id): Path<String>,
    Query(SearchQuery { q, top_k }): Query<SearchQuery>,
) -> Result<Json<SearchResult>, StatusCode> {
    // Llamar a Python para búsqueda RAG
    // Retornar chunks recuperados
}

// POST /documents/{id}/generate-report
pub async fn generate_report(
    Path(agent_id): Path<String>,
    Json(ReportRequest { data, format }): Json<ReportRequest>,
) -> Result<Bytes, StatusCode> {
    // Llamar a Python para generar PDF/Excel
    // Retornar archivo binario
}

// GET /agents/{id}/tools
pub async fn list_agent_tools(
    Path(agent_id): Path<String>,
) -> Result<Json<Vec<Tool>>, StatusCode> {
    // Listar herramientas disponibles para agente
}
```

---

## 🧪 Testing Strategy

### Semana 1: LangGraph
```bash
pytest tests/agents/test_langgraph_agent.py -v
pytest tests/agents/test_graph_builder.py -v
```

### Semana 2: Document Tools
```bash
pytest tests/tools/documents/test_readers.py -v
pytest tests/tools/documents/test_writers.py -v
pytest tests/tools/documents/test_charts.py -v
```

### Semana 3: RAG
```bash
pytest tests/memory/test_embeddings.py -v
pytest tests/memory/test_vector_db.py -v
pytest tests/pipelines/test_document_pipeline.py -v
```

---

## 📊 Hitos de Entrega

### Hito 1: LangGraph (Fin Semana 1)
```
✅ Agentes con estado persistente
✅ Selección automática de herramientas
✅ Ejecución de tools
✅ Integración con gRPC
```

### Hito 2: Document Tools (Fin Semana 2)
```
✅ Lectura: PDF, Excel, Word
✅ Generación: PDF, Excel
✅ Gráficos: Matplotlib/Plotly
✅ OCR: easyocr integrado
```

### Hito 3: RAG Base (Fin Semana 3)
```
✅ Embeddings locales
✅ Indexación en chromadb
✅ Búsqueda vectorial
✅ Integración con agentes
```

---

## 🎯 Criterios de Aceptación

- [ ] LangGraph agent responde con contexto persistente
- [ ] Documento PDF se indexa automáticamente
- [ ] Agente busca y recupera contexto de documentos
- [ ] Reporte se genera en PDF/Excel automáticamente
- [ ] Performance: <5s para búsqueda RAG
- [ ] Tests: >80% cobertura
- [ ] Documentación: API Reference actualizada

---

**Inicio:** 2026-08-07  
**Fin planeado:** 2026-08-28  
**Siguiente:** Fase 3 — Knowledge Pack Generator
