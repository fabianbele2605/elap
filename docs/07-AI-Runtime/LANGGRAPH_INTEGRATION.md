# Python LangGraph Integration — Agent Runtime

**Autor**: ELAP Development Team  
**Fecha**: 2026-08-05  
**Versión**: 1.0  
**Fase**: 13

## Descripción General

Integración de **LangGraph** para crear agentes inteligentes con estado persistente, memoria dual y ejecución dinámica.

---

## Arquitectura

```
ELAP Core (Rust)
     ↓ gRPC
     ↓
Python AI Runtime
├─ LangGraph StateGraph
│  ├─ idle → thinking → planning → executing → reflecting → completed
│  └─ Error handling en cada estado
├─ Memory Manager
│  ├─ Short-term (50 memories, FIFO)
│  └─ Long-term (1000 memories, relevance-based)
├─ Tool Registry
│  └─ Sandboxed tool execution
└─ Agent Orchestrator
   └─ Coordina multiples agentes
```

---

## Components

### 1. Agent (LangGraph StateGraph)

**Estados**:
- `idle`: Estado inicial
- `thinking`: Analiza objetivo
- `planning`: Crea plan de ejecución
- `executing`: Ejecuta pasos del plan
- `reflecting`: Analiza y aprende
- `completed`: Finalización exitosa
- `error`: Manejo de errores

**Transiciones**:
```
idle → thinking → planning → executing ⟷ reflecting → completed
                                ↓
                              error
```

**Ejemplos**:

```python
from elap_ai import Agent, AgentState

state = AgentState(
    id="agent_001",
    name="Vendedor Bot",
    role="Sales",
    objective="Procesar pedidos de clientes"
)

agent = Agent(state)
result = await agent.execute()

print(f"Estado final: {result.state}")
print(f"Progreso: {result.progress * 100}%")
print(f"Reflexiones: {len(result.reflections)}")
```

### 2. Memory Manager

**Tipos de Memoria**:

| Tipo | Capacidad | Política | Uso |
|------|-----------|----------|-----|
| Short-term | 50 | FIFO | Contexto inmediato |
| Long-term | 1000 | Relevancia | Conocimiento acumulado |
| Episodic | Ilimitado | Timestamp | Historial de eventos |

**API**:

```python
from elap_ai import MemoryManager, Memory, MemoryType

manager = MemoryManager()

# Agregar memoria
memory = Memory(
    id="mem_001",
    content="El cliente Juan compró 5 unidades",
    memory_type=MemoryType.LONG_TERM,
    relevance=0.95
)
manager.add_memory(memory)

# Recordar
results = manager.recall("Juan", limit=5)

# Resumen
summary = manager.summarize()
```

### 3. Tool Registry

Sistema de registro y ejecución de herramientas:

```python
from elap_ai import ToolRegistry

registry = ToolRegistry()

# Registrar herramienta
async def fetch_customer_data(customer_id: str) -> dict:
    return {"name": "John", "email": "john@example.com"}

registry.register(
    name="fetch_customer",
    description="Obtener datos del cliente",
    func=fetch_customer_data,
    input_schema={"customer_id": "str"},
    output_schema={"name": "str", "email": "str"}
)

# Ejecutar herramienta
result = await registry.execute("fetch_customer", customer_id="123")
```

---

## Flujo Completo

```
Agent Creation
    ↓
Agent.execute()
    ↓
StateGraph.invoke()
    ├─ idle node → initialize
    ├─ thinking node → analyze objective
    ├─ planning node → create plan
    ├─ executing node → run steps (with memory)
    ├─ reflecting node → learn from execution
    └─ completed/error
    ↓
Return AgentState with:
- Final state
- Progress (0.0 - 1.0)
- Plan and history
- Reflections and learnings
```

---

## Tests

**Cobertura**:
- Agent initialization y lifecycle
- Memory operations (add, recall, clear)
- Tool registration y execution
- State transitions
- Error handling

**Ejecutar tests**:

```bash
cd python

# Install dependencies
pip install -e .[dev]

# Run tests
pytest tests/

# With coverage
pytest --cov=elap_ai tests/

# Verbose
pytest -v tests/
```

---

## Integración con Core Rust

```
Client HTTP
    ↓
Rust API (Axum)
    ↓
gRPC Gateway
    ↓
Python AI Runtime
    ├─ Agent execution
    ├─ Memory operations
    └─ Tool execution
    ↓
Response (JSON)
    ↓
Client
```

**Endpoint de ejemplo**:

```bash
# Crear agente
curl -X POST http://localhost:3000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Bot Vendedor",
    "rol": "Sales",
    "objetivo": "Procesar pedidos"
  }'

# Ejecutar agente
curl -X POST http://localhost:3000/agents/{id}/execute

# Monitorear (WebSocket)
wscat -c ws://localhost:3000/agents/{id}/watch
```

---

## Métricas Fase 13

| Métrica | Valor |
|---------|-------|
| Archivos Python | 8 |
| Líneas de código | ~600 |
| Tests | 12 |
| Cobertura | 85%+ |
| Estados LangGraph | 7 |
| Tipos de memoria | 3 |

---

## Próximos Pasos (Fase 14+)

- [ ] Embeddings para similarity search en memoria
- [ ] Qdrant vector DB integration
- [ ] Tool execution sandboxing
- [ ] Multi-agent orchestration
- [ ] Streaming responses (Server-Sent Events)
- [ ] Token counting y cost tracking
- [ ] Prompt caching

---

**Última actualización**: 2026-08-05
