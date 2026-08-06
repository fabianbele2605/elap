# Advanced RAG — Reranking + Semantic Cache + Hybrid Search

**Fase 19 — Advanced RAG Features**

---

## Componentes

### 1. Reranker (Cross-Encoder)

Mejora la relevancia reordenando resultados con un modelo cross-encoder.

```python
from elap_ai.rag.reranker import Reranker

reranker = Reranker()

# Reranquear resultados
results = await reranker.rerank(
    query="python programming",
    documents=[...],
    top_k=5
)
```

**Modelos soportados:**
- `cross-encoder/ms-marco-MiniLM-L-12-v2` (default, rápido)
- `cross-encoder/mmarco-mMiniLMv2-L12-H384-V1` (multilingual)

---

### 2. Semantic Cache

Cache inteligente que reutiliza resultados de queries similares.

```python
from elap_ai.rag.cache import SemanticCache

cache = SemanticCache(ttl_seconds=3600)

# Guardar resultado
await cache.set("python tutorial", results)

# Obtener del cache
cached = await cache.get("python tutorial", embedding)

# Estadísticas
stats = cache.get_stats()
```

**Ventajas:**
- Reduce latencia en queries frecuentes
- Ahorra cálculos de embedding
- Configurable TTL

---

### 3. Hybrid Search

Combina búsqueda léxica (BM25) + semántica (embedding).

```python
from elap_ai.rag.hybrid_search import HybridSearch

hybrid = HybridSearch(
    semantic_weight=0.7,  # 70% semántica
    bm25_weight=0.3       # 30% keyword
)

results = await hybrid.hybrid_search(
    query="python code",
    semantic_results=[...],
    documents=[...],
    limit=5
)
```

**Ventajas:**
- Mejor recall (encuentra docs relevantes por keyword)
- Mejor precision (ordena por semantics)
- Balanceable por caso de uso

---

## Flujo RAG Completo

```
Query
  ↓
[1] Check Semantic Cache
  ├─ Hit → return cached
  └─ Miss → continue
  ↓
[2] Semantic Search (embeddings)
  ↓
[3] Hybrid Ranking (BM25 + semantic)
  ↓
[4] Reranking (cross-encoder)
  ↓
[5] Cache Results
  ↓
Return Top-K
```

---

## Tests

```bash
pytest tests/test_advanced_rag.py -v
```

**Cobertura:**
- Reranking (4 tests)
- Semantic Cache (3 tests)
- Hybrid Search (2 tests)

---

## Performance

| Componente | Latencia | Mejora |
|-----------|----------|--------|
| Cache hit | <1ms | 100x |
| Reranking | ~50ms | +relevance |
| Hybrid (vs semantic alone) | +5ms | +recall |

---

## Próximas Mejoras

- [ ] GPU-accelerated reranking
- [ ] Distributed cache (Redis)
- [ ] Query expansion
- [ ] Fusion ranking (RRF)

---

**Última actualización**: 2026-08-05
