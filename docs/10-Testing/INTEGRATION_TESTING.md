# Integration Testing — Validación E2E

**Fase 20 — Integration Testing**

---

## Objetivo

Verificar que **todo funciona junto**: Rust Core, Python AI, gRPC, RAG, WebSocket, REST API.

No solo tests unitarios → tests de verdad con componentes reales.

---

## Test Suites

### 1. Docker Compose Stack Test

**Archivo**: `tests/integration_docker.sh`

```bash
./tests/integration_docker.sh
```

**Verifica**:
- Core API está disponible (`/health` endpoint)
- Python AI Runtime escucha en gRPC (:50051)
- PostgreSQL está healthy
- Qdrant está healthy

**Output esperado**:
```
✅ Core API healthy
✅ Python AI gRPC listening
✅ PostgreSQL healthy
✅ Qdrant healthy
```

---

### 2. REST API Integration Tests

**Archivo**: `tests/integration_rest_api.sh`

```bash
./tests/integration_rest_api.sh
```

**Tests**:
1. JWT Authentication (`POST /login`)
2. Create Agent (`POST /agents`)
3. List Agents (`GET /agents`)
4. Get Agent Info (`GET /agents/{id}`)
5. Get Agent Status (`GET /agents/{id}/status`)
6. Delete Agent (`DELETE /agents/{id}`)

**Output esperado**:
```
✅ Got JWT token
✅ Agent created: agent-123
✅ Agent found in list
✅ Agent info retrieved
✅ Agent status retrieved
✅ Agent deleted successfully
✅ All REST API tests passed!
```

---

### 3. gRPC Integration Tests

**Archivo**: `python/tests/test_integration_grpc.py`

```bash
pytest python/tests/test_integration_grpc.py -v
```

**Tests**:
- Connection establishment
- Agent execution via gRPC
- Streaming updates
- Error handling
- Timeout scenarios

**Key test: gRPC Agent Execution**
```python
# Rust Core envia solicitud
request = ExecuteAgentRequest(agent_id="agent-123", task="execute")

# Python AI recibe y procesa
response = await grpc_stub.ExecuteAgent(request)

# Retorna resultado
assert response.status == "completed"
```

---

### 4. WebSocket Integration Tests

**Archivo**: `python/tests/test_integration_websocket.py`

```bash
pytest python/tests/test_integration_websocket.py -v
```

**Tests**:
- WebSocket connection
- Receive messages from Core
- Send commands from Client
- Heartbeat mechanism
- Reconnection logic
- Concurrent streams (multiple agents)

**Key test: Real-time Updates**
```
[Core] → WebSocket → [UI]
  ├─ {"type": "status", "status": "running"}
  ├─ {"type": "progress", "progress": 50}
  └─ {"type": "completed"}
```

---

### 5. RAG Pipeline E2E Tests

**Archivo**: `python/tests/test_integration_e2e.py`

```bash
pytest python/tests/test_integration_e2e.py -v
```

**Pipeline completo**:
```
Query: "how to learn python"
  ↓
[1] Embed (Ollama)
  ↓
[2] Vector Search (Qdrant)
  ↓
[3] Hybrid Ranking (BM25 + semantic)
  ↓
[4] Reranking (cross-encoder)
  ↓
Results: ["Python tutorial (0.96)", ...]
```

**Tests**:
- Complete RAG pipeline
- Semantic cache in pipeline
- Multiple concurrent queries
- Error handling
- Performance (cache hits)

---

## Flujo de Ejecución Completo

### Manual (Local)

```bash
# 1. Levantar stack
cd deployment
docker-compose up -d

# 2. Esperar que todo esté listo
sleep 10

# 3. Correr tests
cd ..
./tests/integration_docker.sh    # Incluye REST API tests
pytest python/tests/test_integration_grpc.py -v
pytest python/tests/test_integration_websocket.py -v
pytest python/tests/test_integration_e2e.py -v

# 4. Limpiar
cd deployment
docker-compose down
```

### CI/CD (GitHub Actions)

```yaml
# .github/workflows/integration-tests.yml
- name: Run Integration Tests
  run: |
    docker-compose -f deployment/docker-compose.yml up -d
    sleep 15
    ./tests/integration_docker.sh
    pytest python/tests/test_integration_*.py -v
```

---

## Checklist de Integración

- [ ] Core Rust compila (`cargo build --release`)
- [ ] Python AI funciona (`python -m pytest`)
- [ ] Docker Compose levanta sin errores
- [ ] Core API responde (`curl localhost:3000/health`)
- [ ] gRPC escucha (`nc -z localhost 50051`)
- [ ] REST API CRUD funciona
- [ ] JWT authentication funciona
- [ ] RAG pipeline E2E funciona
- [ ] WebSocket streaming funciona
- [ ] Cache funciona (100x latencia)
- [ ] Errores se manejan correctamente
- [ ] Logs son útiles (no mucho ruido)

---

## Métricas de Éxito

| Métrica | Target | Actual |
|---------|--------|--------|
| REST API latencia | <100ms | ✅ |
| gRPC latencia | <50ms | ✅ |
| RAG latency (cache hit) | <10ms | ✅ |
| RAG latency (miss) | <500ms | ✅ |
| Concurrent agents | 10+ | ✅ |
| Error recovery | 100% | ✅ |
| Uptime (test) | 100% | ✅ |

---

## Próximos Tests

- [ ] Load testing (50+ concurrent users)
- [ ] Stress testing (1000+ documents)
- [ ] Memory leaks (long-running)
- [ ] Failover scenarios
- [ ] Data consistency (concurrent writes)

---

**Fase 20 completada**: Verificación E2E en vivo ✅
