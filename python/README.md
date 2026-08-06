# ELAP AI Runtime — Python LangGraph Integration

**Enterprise Local AI Platform** — Python runtime con agentes inteligentes basados en LangGraph.

---

## Instalación

### Prerequisites

- Python 3.10+
- pip/uv

### Setup

```bash
# Navega a la carpeta python
cd python

# Instala dependencias de desarrollo
pip install -e .[dev]

# O con uv (más rápido)
uv pip install -e .[dev]
```

---

## Estructura

```
python/
├── src/elap_ai/
│   ├── __init__.py                 # Public API
│   ├── agent_runtime/
│   │   ├── __init__.py
│   │   └── agent.py               # Agent con LangGraph StateGraph
│   ├── memory/
│   │   ├── __init__.py
│   │   └── memory.py              # Memory Manager (short/long-term)
│   └── tools/
│       ├── __init__.py
│       └── registry.py            # Tool Registry y execution
├── tests/
│   ├── __init__.py
│   ├── test_agent.py              # Agent tests
│   ├── test_memory.py             # Memory tests
│   └── test_tools.py              # Tool Registry tests
└── pyproject.toml
```

---

## Uso Rápido

### Crear y ejecutar agente

```python
import asyncio
from elap_ai import Agent, AgentState

async def main():
    # Crear agente
    state = AgentState(
        id="agent_001",
        name="Asistente de Ventas",
        role="Sales",
        objective="Procesar pedidos de clientes"
    )
    
    agent = Agent(state)
    
    # Ejecutar
    result = await agent.execute()
    
    # Ver resultado
    print(f"Estado: {result.state}")
    print(f"Progreso: {result.progress * 100:.0f}%")
    print(f"Pasos completados: {result.current_step}/{result.total_steps}")
    print(f"Reflexiones: {len(result.reflections)}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Usar Memory Manager

```python
from elap_ai import MemoryManager, Memory, MemoryType

# Crear manager
manager = MemoryManager(max_short_term=50, max_long_term=1000)

# Agregar memoria
memory = Memory(
    id="mem_001",
    content="El cliente prefiere pagos mensuales",
    memory_type=MemoryType.LONG_TERM,
    relevance=0.95
)
manager.add_memory(memory)

# Recordar
results = manager.recall("cliente", limit=5)
for mem in results:
    print(f"[{mem.relevance:.0%}] {mem.content}")

# Resumen
print(manager.summarize())
```

### Registrar y usar herramientas

```python
from elap_ai import ToolRegistry

registry = ToolRegistry()

# Registrar herramienta
async def get_weather(city: str) -> dict:
    return {"city": city, "temperature": 25, "condition": "sunny"}

registry.register(
    name="get_weather",
    description="Obtener clima de una ciudad",
    func=get_weather,
    input_schema={"city": "str"},
    output_schema={"temperature": "int", "condition": "str"}
)

# Ejecutar
result = await registry.execute("get_weather", city="Madrid")
print(result)
```

---

## Tests

```bash
# Ejecutar todos los tests
pytest

# Tests específicos
pytest tests/test_agent.py -v

# Con coverage
pytest --cov=elap_ai --cov-report=html

# Watch mode (requiere pytest-watch)
ptw
```

---

## Dependencias Principales

| Package | Versión | Propósito |
|---------|---------|-----------|
| langgraph | 0.0.1+ | StateGraph y workflows |
| langchain | 0.1.0+ | LLM chains y utilities |
| pydantic | 2.0+ | Data validation |
| aiohttp | 3.8+ | HTTP async client |

---

## Documentación

- **[LANGGRAPH_INTEGRATION.md](../docs/07-AI-Runtime/LANGGRAPH_INTEGRATION.md)** — Arquitectura y componentes
- **[CLAUDE.md](../CLAUDE.md)** — Estándares de código

---

## Estado Actual

**Fase 13 - Python LangGraph Integration**:
- ✅ Agent con LangGraph StateGraph (7 estados)
- ✅ Memory Manager (short-term y long-term)
- ✅ Tool Registry para ejecución de herramientas
- ✅ 12 tests (85%+ coverage)
- ✅ Documentación técnica

**Próximos (Fase 14+)**:
- [ ] Embeddings con Ollama
- [ ] Vector DB (Qdrant/ChromaDB)
- [ ] Streaming responses
- [ ] Multi-agent orchestration
- [ ] Prompt optimization

---

**Última actualización**: 2026-08-05
