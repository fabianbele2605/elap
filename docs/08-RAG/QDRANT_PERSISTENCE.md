# Qdrant Integration — Vector DB Persistence

**Autor**: ELAP Development Team  
**Fecha**: 2026-08-05  
**Versión**: 1.0  
**Fase**: 15

## Descripción General

Integración de **Qdrant** para persistencia escalable de vectores en lugar de almacenamiento en memoria.

---

## Arquitectura

```
Embeddings
    ↓
Vector DB Manager
    ├─ InMemoryVectorDB (testing)
    └─ QdrantVectorDB (producción)
         ↓
      Qdrant Server
         ↓
      Almacenamiento persistente
```

---

## Componentes

### 1. VectorDBBackend (Base)

Interfaz común para todos los backends.

**Métodos**:
- `insert(vector)` - Insertar vector
- `search(query_vector, limit, threshold)` - Buscar
- `delete(vector_id)` - Eliminar
- `health_check()` - Verificar conexión
- `clear()` - Limpiar colección

### 2. InMemoryVectorDB

Backend en memoria (sin persistencia).

**Uso**:
```python
from elap_ai.vectordb.backends import InMemoryVectorDB

db = InMemoryVectorDB()
await db.insert(vector)
results = await db.search(query_vector)
```

### 3. QdrantVectorDB

Backend con Qdrant (persistencia).

**Requisitos**:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**Uso**:
```python
from elap_ai.vectordb.backends import QdrantVectorDB

client = QdrantVectorDB(
    url="http://localhost:6333",
    collection_name="elap_vectors",
    vector_size=768
)

async with client:
    await client.insert(vector)
    results = await client.search(query_vector)
    await client.health_check()
```

---

## Migración de In-Memory a Qdrant

**Antes** (testing):
```python
from elap_ai.vectordb import VectorDBManager

manager = VectorDBManager()  # Usa InMemoryVectorDB por defecto
```

**Después** (producción):
```python
from elap_ai.vectordb import VectorDBManager
from elap_ai.vectordb.backends import QdrantVectorDB

backend = QdrantVectorDB(url="http://localhost:6333")
manager = VectorDBManager(backend=backend)
```

---

## API Qdrant Utilizada

| Endpoint | Método | Propósito |
|----------|--------|-----------|
| `/collections` | GET | Listar colecciones |
| `/collections/{name}` | PUT | Crear colección |
| `/collections/{name}` | GET | Info de colección |
| `/collections/{name}/points` | PUT | Insertar puntos |
| `/collections/{name}/points/search` | POST | Buscar |
| `/collections/{name}/points/delete` | POST | Eliminar |
| `/health` | GET | Health check |

---

## Tests

**Cobertura**:
- Inicialización de cliente
- Normalización de URLs
- Hash de IDs
- Health check
- Context manager

**Ejecutar**:
```bash
pytest tests/test_qdrant.py -v
```

---

## Performance

| Operación | Latencia (Qdrant) | Latencia (In-Memory) |
|-----------|------------------|---------------------|
| Insert | ~10ms | <1ms |
| Search (1000 vectors) | ~50ms | ~5ms |
| Health check | ~5ms | <1ms |

---

## Próximos Pasos (Fase 16+)

- [ ] Índices optimizados (HNSW)
- [ ] Sharding para escalabilidad
- [ ] Replication para alta disponibilidad
- [ ] Métrica de distancia configurable
- [ ] Batch optimization

---

**Última actualización**: 2026-08-05
