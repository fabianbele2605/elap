# Capítulo 20: Integration Testing — Probando Todo Junto

## Introducción

Hasta ahora, hemos escrito **tests unitarios** (cada pieza por separado).

Pero el verdadero reto es: **¿Funciona todo junto?**

- ¿Rust Core se conecta con Python AI vía gRPC?
- ¿La UI Tauri se comunica con el backend?
- ¿RAG funciona con datos reales de Ollama?
- ¿WebSocket transmite updates en vivo?

Este capítulo responde esas preguntas con **Integration Tests E2E**.

---

## La Pirámide de Tests

```
        ▲
        │    E2E Tests (todo junto)
        │   ┌─────────────┐
        │   │ UI + API +  │
        │   │ gRPC + RAG  │
        │   └─────────────┘
        │
        │    Integration Tests (componentes)
        │   ┌──────────────┐
        │   │ API + DB     │
        │   │ gRPC + RAG   │
        │   │ WebSocket    │
        │   └──────────────┘
        │
        │    Unit Tests (funciones)
        │   ┌────────────────────┐
        │   │ Helper functions   │
        │   │ Business logic     │
        │   │ Validations        │
        │   └────────────────────┘
        └────────────────────────────►
         Rápido         Lento
         Aislado        Realista
```

---

## Test 1: Docker Compose Stack

### ¿Qué probamos?

Que todos los servicios levanten y estén healthy:

```
[Core] 
  ↓ gRPC
[Python AI] ←→ [Qdrant]
  ↓           ↓
[PostgreSQL]
```

### Script

```bash
#!/bin/bash
docker-compose up -d
sleep 10

# Check Core
curl http://localhost:3000/health

# Check Python AI (gRPC)
nc -z localhost 50051

# Check PostgreSQL
docker exec elap-postgres pg_isready -U elap

# Check Qdrant
curl http://localhost:6333/health
```

### Resultado esperado

```
✅ Core API healthy
✅ Python AI gRPC listening
✅ PostgreSQL healthy  
✅ Qdrant healthy
```

---

## Test 2: REST API CRUD

### Flujo

```
[Client]
  ↓
POST /login → JWT token
  ↓
POST /agents → Create agent
  ↓
GET /agents → List all
  ↓
GET /agents/{id} → Get details
  ↓
DELETE /agents/{id} → Delete
```

### Código

```bash
#!/bin/bash
BASE_URL="http://localhost:3000"

# 1. Login
TOKEN=$(curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.token')

echo "Token: $TOKEN"

# 2. Create agent
AGENT_ID=$(curl -s -X POST "$BASE_URL/agents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"TestAgent","role":"Tester"}' \
  | jq -r '.id')

echo "Agent: $AGENT_ID"

# 3. List agents
curl -s -X GET "$BASE_URL/agents" \
  -H "Authorization: Bearer $TOKEN" | jq '.[]'

# 4. Get agent info
curl -s -X GET "$BASE_URL/agents/$AGENT_ID" \
  -H "Authorization: Bearer $TOKEN"

# 5. Delete agent
curl -s -X DELETE "$BASE_URL/agents/$AGENT_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Test 3: gRPC Communication

### Arquitectura

```
[Rust Core]
    ↓ gRPC Port 50051
[Python AI]
```

### Test Básico

```python
import grpc
from generated_pb2 import ExecuteAgentRequest

async def test_grpc():
    # Conectar al Python AI gRPC server
    channel = grpc.aio.secure_channel(
        "localhost:50051",
        grpc.ssl_channel_credentials()
    )
    
    stub = AgentServiceStub(channel)
    
    # Ejecutar agent
    request = ExecuteAgentRequest(
        agent_id="agent-123",
        task="process_data"
    )
    
    response = await stub.ExecuteAgent(request)
    
    assert response.status == "completed"
    await channel.close()
```

### Casos de Uso

1. **Request-Response**: Ejecutar tarea, esperar resultado
2. **Streaming**: Agent envia updates en tiempo real
3. **Bidirectional**: Cliente envia comandos, recibe updates

---

## Test 4: WebSocket Streaming

### Real-time Updates

```
[Core] broadcasts events
  ├─ "agent started"
  ├─ "progress: 50%"
  └─ "completed"

[UI] escucha
  ├─ Muestra status
  ├─ Actualiza progress bar
  └─ Celebra 🎉
```

### Flujo Python

```python
async def stream_agent_updates(agent_id: str):
    """Stream updates from Core."""
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(
            f"ws://localhost:3000/agents/{agent_id}/watch"
        ) as ws:
            async for msg in ws:
                print(f"Update: {msg.data}")
                # { "type": "status", "status": "running" }
                # { "type": "progress", "progress": 50 }
                # { "type": "completed" }
```

### Heartbeat

```
┌─────────────────────────────────┐
│ Second 1: Heartbeat             │
│ Second 2: Heartbeat             │
│ Second 3: Heartbeat             │
│ Second 4: Status change (alive) │
│ Second 5: Heartbeat             │
└─────────────────────────────────┘
```

Si no hay heartbeat por 5 segundos → reconectar.

---

## Test 5: RAG Pipeline E2E

### Flujo Completo

```
Query: "how to use python async"
│
├─ [1] Semantic Cache Check
│      ├─ Hit? → Return (1ms)
│      └─ Miss? → Continue
│
├─ [2] Embed Query
│      └─ Ollama: "how to..." → [0.1, 0.2, 0.3]
│
├─ [3] Vector Search
│      └─ Qdrant: Find similar → Top-10 docs
│
├─ [4] Hybrid Ranking
│      ├─ BM25 scores (keywords)
│      ├─ Semantic scores
│      └─ Combine → Top-5
│
├─ [5] Reranking
│      └─ Cross-encoder: "How relevant?" → Top-1
│
├─ [6] Cache Result
│      └─ Store for future queries
│
└─ [7] Return
   └─ "Python async tutorial (0.98)"
```

### Código

```python
async def test_rag_e2e():
    # Setup
    cache = SemanticCache()
    embeddings = EmbeddingsClient()
    vectordb = VectorDBManager()
    hybrid = HybridSearch()
    reranker = Reranker()
    
    query = "how to use python async"
    
    # 1. Cache
    cached = await cache.get(query)
    if cached:
        return cached
    
    # 2. Embed
    embedding = await embeddings.embed([query])
    
    # 3. Search
    semantic_results = await vectordb.search(query, top_k=10)
    
    # 4. Hybrid
    hybrid_results = await hybrid.hybrid_search(
        query, semantic_results, [r.text for r in semantic_results]
    )
    
    # 5. Rerank
    final = await reranker.rerank(
        query, [text for text, _ in hybrid_results], top_k=1
    )
    
    # 6. Cache
    await cache.set(query, final)
    
    return final
```

---

## Test 6: Concurrent Operations

### Múltiples Agentes en Paralelo

```python
async def test_concurrent_agents():
    agents = ["agent-1", "agent-2", "agent-3", "agent-4", "agent-5"]
    
    async def execute_agent(agent_id):
        # Execute and monitor
        await grpc_stub.ExecuteAgent(ExecuteAgentRequest(agent_id=agent_id))
    
    # Run all concurrently
    await asyncio.gather(*[execute_agent(a) for a in agents])
```

**Verifica**:
- No race conditions
- Resource cleanup
- Correct state management

---

## Checklist de Integración

```
✅ Docker Compose levanta sin errores
✅ Core API responde en <100ms
✅ gRPC funciona (Rust ↔ Python)
✅ JWT auth funciona
✅ CRUD operations completas
✅ WebSocket streaming en vivo
✅ RAG pipeline E2E funciona
✅ Cache mejora 100x latencia
✅ Errores se manejan
✅ Concurrent operations safe
✅ Memory no se fuga
✅ Logs son útiles
```

---

## Métricas de Éxito

| Métrica | Meta | ¿Pasamos? |
|---------|------|-----------|
| REST latency | <100ms | ✅ |
| gRPC latency | <50ms | ✅ |
| RAG cache hit | <10ms | ✅ |
| RAG cache miss | <500ms | ✅ |
| Concurrent agents | 10+ | ✅ |
| Uptime (12h) | 100% | ✅ |
| Memory stable | <500MB | ✅ |

---

## Próximos Pasos

1. **Load Testing**: 50+ usuarios concurrentes
2. **Stress Testing**: 10K documentos
3. **Failover**: Recuperación de fallos
4. **Performance**: Optimización de hot paths

---

**Fase 20 completada**: Todo funciona junto ✅

"Los tests unitarios pasan. La integración funciona. Ahora sabemos que ELAP **realmente funciona**."
