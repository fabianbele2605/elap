# 🔌 Métodos gRPC — Referencia Completa

**Estado:** ✅ Implementados y testeados  
**Tests:** 54/54 pasando  
**Fecha:** 2026-08-07

---

## 🎯 Métodos Disponibles

### 1. **ExecuteAgent** (Existente)

Ejecutar un agente y obtener respuesta completa.

```protobuf
rpc ExecuteAgent(ExecuteAgentRequest) returns (ExecuteAgentResponse);
```

**Request:**
```python
{
    "agent_id": "agent_ventas",
    "query": "¿Cuáles son nuestros productos principales?"
}
```

**Response:**
```python
{
    "agent_id": "agent_ventas",
    "status": "completed",  # "running", "completed", "error"
    "result": "Los productos principales son...",
    "progress": 1.0,
    "error": ""
}
```

---

### 2. **ExecuteAgentStreaming** (Existente)

Ejecutar agente con streaming de tokens en vivo.

```protobuf
rpc ExecuteAgentStreaming(ExecuteAgentRequest) returns (stream ExecuteAgentChunk);
```

**Cada chunk:**
```python
{
    "agent_id": "agent_ventas",
    "chunk": "Los productos",  # Token o fragmento
    "progress": 0.45,
    "is_final": False,
    "error": ""
}
```

---

### 3. **SearchDocuments** ⭐ NUEVO

Buscar fragmentos de documentos indexados en RAG.

```protobuf
rpc SearchDocuments(SearchDocumentsRequest) returns (SearchDocumentsResponse);
```

**Request:**
```python
{
    "collection": "documentos_rrhh",
    "query": "¿Cuál es la política de vacaciones?",
    "top_k": 5
}
```

**Response:**
```python
{
    "status": "success",
    "chunks": [
        "Las vacaciones se otorgan según... Mínimo 15 días...",
        "Los empleados pueden solicitar vacaciones... Avaladas por su gerente...",
        "Las vacaciones no gozadas pueden trasladarse..."
    ],
    "count": 3,
    "error": ""
}
```

---

### 4. **GenerateReport** ⭐ NUEVO

Generar reporte en PDF o Excel.

```protobuf
rpc GenerateReport(GenerateReportRequest) returns (GenerateReportResponse);
```

**Request:**
```python
{
    "title": "Reporte de Ventas Q3 2026",
    "sections_json": '''[
        {
            "title": "Resumen Ejecutivo",
            "content": "Ventas totales: $500,000"
        },
        {
            "title": "Por Producto",
            "content": "Producto A: $250,000",
            "data": [["Mes", "Cantidad"], ["Enero", "100"]]
        }
    ]''',
    "format": "pdf",
    "company_name": "Andina Foods"
}
```

**Response:**
```python
{
    "status": "success",
    "file_bytes": b"PDF_BINARY_CONTENT...",  # Contenido del PDF/Excel
    "filename": "Reporte de Ventas Q3 2026.pdf",
    "error": ""
}
```

---

### 5. **ExecuteAgentWithRAG** ⭐ NUEVO

Ejecutar agente enriqueciendo su respuesta con contexto de documentos.

```protobuf
rpc ExecuteAgentWithRAG(ExecuteAgentWithRAGRequest) returns (ExecuteAgentWithRAGResponse);
```

**Request:**
```python
{
    "agent_id": "agent_rrhh",
    "query": "¿Cuál es la política de ausencias injustificadas?",
    "rag_collection": "documentos_rrhh"  # Colección para buscar contexto
}
```

**Response:**
```python
{
    "agent_id": "agent_rrhh",
    "status": "completed",
    "result": "Las ausencias injustificadas se consideran como... (respuesta enriquecida con documentos)",
    "context_chunks": [
        "Las ausencias injustificadas serán reportadas...",
        "Se aplicarán descuentos según política..."
    ],
    "context_count": 2,
    "error": ""
}
```

---

### 6. **HealthCheck** (Existente)

Verificar que el servidor está activo.

```protobuf
rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
```

**Request:**
```python
{
    "service": "grpc"
}
```

**Response:**
```python
{
    "status": "ok",
    "message": "AI Runtime is healthy"
}
```

---

## 🚀 Casos de Uso

### Caso 1: Agente RRHH responde pregunta sobre políticas

```python
# 1. Buscar contexto relevante
response = stub.SearchDocuments(
    SearchDocumentsRequest(
        collection="documentos_rrhh",
        query="vacaciones",
        top_k=5
    )
)

# 2. Ejecutar agente con contexto
response = stub.ExecuteAgentWithRAG(
    ExecuteAgentWithRAGRequest(
        agent_id="agent_rrhh",
        query="¿Cuántos días de vacaciones me corresponden?",
        rag_collection="documentos_rrhh"
    )
)

# → Respuesta: "Según nuestras políticas, te corresponden 15 días..."
```

---

### Caso 2: Generar reporte de ventas

```python
# 1. Obtener datos (desde base de datos, API, etc.)
sales_data = get_sales_data()

# 2. Generar reporte
report_response = stub.GenerateReport(
    GenerateReportRequest(
        title="Reporte de Ventas Mensual",
        sections_json=json.dumps([
            {
                "title": "Resumen",
                "content": f"Total: ${sales_data['total']}"
            },
            {
                "title": "Por Región",
                "data": sales_data['by_region']
            }
        ]),
        format="pdf",
        company_name="Andina Foods"
    )
)

# → Retorna PDF binario listo para descargar
pdf_bytes = report_response.file_bytes
with open("reporte.pdf", "wb") as f:
    f.write(pdf_bytes)
```

---

### Caso 3: Pipeline de indexación y búsqueda

```python
# 1. Indexar documentos (desde aplicación Rust/web)
# POST /documents/upload → Rust llama a Python gRPC

# 2. Buscar documentos relevantes
context = stub.SearchDocuments(
    SearchDocumentsRequest(
        collection="documentos_empresa",
        query="proceso de contratación",
        top_k=3
    )
)

# 3. Usar contexto en respuesta
response = stub.ExecuteAgentWithRAG(
    ExecuteAgentWithRAGRequest(
        agent_id="agent_rrhh",
        query="¿Cuál es el proceso para contratar?",
        rag_collection="documentos_empresa"
    )
)
```

---

## 📝 Implementación en Rust

Desde el backend Rust, hacer llamadas gRPC es simple:

```rust
// Conectar al servidor gRPC
let mut client = AgentServiceClient::connect("http://127.0.0.1:50051").await?;

// Búsqueda
let request = tonic::Request::new(SearchDocumentsRequest {
    collection: "documentos_rrhh".to_string(),
    query: "vacaciones".to_string(),
    top_k: 5,
});

let response = client.search_documents(request).await?;
let chunks = response.into_inner().chunks;

// Generación de reporte
let report_request = GenerateReportRequest {
    title: "Mi Reporte".to_string(),
    sections_json: sections_json_str,
    format: "pdf".to_string(),
    company_name: "Empresa".to_string(),
};

let pdf_bytes = client.generate_report(report_request).await?.into_inner().file_bytes;
```

---

## 🔧 Configuración

**Servidor Python gRPC:**
```bash
source venv/bin/activate
python -m elap_ai.grpc_server
# Escucha en 127.0.0.1:50051
```

**Cliente desde Rust:**
```rust
// En Cargo.toml
[dependencies]
tonic = "0.10"
prost = "0.12"
tokio = { version = "1", features = ["full"] }
```

---

## 📊 Rendimiento

| Operación | Latencia Esperada |
|-----------|------------------|
| **ExecuteAgent** | 30-50s (CPU) / 2-5s (GPU) |
| **SearchDocuments** | <2s (chromadb local) |
| **GenerateReport** | <5s (PDF) / <3s (Excel) |
| **ExecuteAgentWithRAG** | 35-55s (incluye búsqueda) |

---

## ✅ Tests de Integración

```bash
source venv/bin/activate
python -m pytest tests/test_grpc_integration.py -v

# Resultado: 7/7 tests pasando
```

---

## 🚀 Próximos Pasos

1. **Endpoints REST en Rust** — Wrappear gRPC calls
2. **Frontend Upload** — React component para documentos
3. **Autenticación** — TLS y tokens JWT
4. **Monitoreo** — Métricas de gRPC

---

**Generado:** 2026-08-07  
**Última actualización:** Post-Implementación gRPC
