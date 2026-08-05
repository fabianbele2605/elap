# Model Manager — Gestión de modelos de IA locales

**Versión**: 0.1.0  
**Estado**: Fase 7 completada  
**Ubicación**: `crates/elap-core/src/models/`

---

## Visión General

El **Model Manager** integra ELAP con modelos de IA locales a través de **Ollama**. Proporciona:

- **Ollama Integration**: Ejecutar modelos locales (Llama 2, Mistral, etc)
- **Embedding Cache**: Caché automático de vectores
- **Short-term Memory**: Historial de conversación
- **Model Registry**: Registro de modelos disponibles
- **Type Safety**: Modelos tipados (Chat, TextoGenerativo, Embedding)

---

## Arquitectura

### Componentes Principales

```
ModelManager (orquestador)
  ├─ OllamaClient (interfaz con Ollama)
  ├─ RegistroModelos (metadata de modelos)
  ├─ CacheEmbeddings (cache de vectores)
  └─ MemoriaCorta (conversación)
```

### ModelMetadata

```rust
pub struct ModelMetadata {
    pub nombre: String,              // "llama2:7b"
    pub tipo: TipoModelo,            // Chat, TextoGenerativo, Embedding
    pub descripcion: String,
    pub tamaño_mb: u32,
    pub parametros: String,          // "7B", "13B"
    pub version: String,
    pub descargado: bool,
    pub ultima_actualizacion: String,
}
```

### TipoModelo

```rust
pub enum TipoModelo {
    TextoGenerativo,  // LLM para completion
    Embedding,        // Vector embeddings
    Chat,            // Conversacional
}
```

### OllamaClient

```rust
pub struct OllamaClient {
    url_base: String,        // "http://localhost:11434"
    timeout_segundos: u64,
}

impl OllamaClient {
    pub fn generar(&self, modelo: &str, prompt: &str, temp: f32) 
        -> ResultadoElap<String>
    
    pub fn embeddings(&self, modelo: &str, texto: &str) 
        -> ResultadoElap<Vec<f32>>
    
    pub fn chat(&self, modelo: &str, historial: &[(&str, &str)]) 
        -> ResultadoElap<String>
    
    pub fn listar_modelos(&self) -> ResultadoElap<Vec<String>>
    
    pub fn descargar_modelo(&self, nombre: &str) -> ResultadoElap<()>
}
```

### ModelManager (Orquestador)

```rust
pub struct ModelManager {
    cliente: OllamaClient,
    registro: RegistroModelos,
    cache: CacheEmbeddings,
    memoria_corta: VecDeque<MemoriaCorta>,
    modelo_activo: Option<String>,
    max_memoria: usize,
}

impl ModelManager {
    pub fn nuevo(url_ollama: impl Into<String>, max_memoria: usize) -> Self
    
    pub fn registrar_modelo(&self, metadata: ModelMetadata) -> ResultadoElap<()>
    
    pub fn set_modelo_activo(&mut self, nombre: &str) -> ResultadoElap<()>
    
    pub fn generar(&self, prompt: &str, temperatura: f32) 
        -> ResultadoElap<String>
    
    pub fn embeddings(&self, texto: &str) 
        -> ResultadoElap<Vec<f32>>  // Con cache automático
    
    pub fn chat(&mut self, usuario: &str) 
        -> ResultadoElap<String>     // Con memoria
    
    pub fn limpiar_memoria(&mut self) -> ResultadoElap<()>
    
    pub fn obtener_historial(&self) -> Vec<MemoriaCorta>
    
    pub fn tamaño_memoria(&self) -> usize
}
```

### MemoriaCorta

```rust
pub struct MemoriaCorta {
    pub rol: String,        // "usuario" o "asistente"
    pub contenido: String,
    pub timestamp: String,
}
```

### CacheEmbeddings

```rust
pub struct CacheEmbeddings {
    cache: Arc<Mutex<HashMap<String, EntradaCache>>>,
    max_entries: usize,
}

impl CacheEmbeddings {
    pub fn nuevo(max_entries: usize) -> Self
    pub fn obtener(&self, modelo: &str, texto: &str) 
        -> ResultadoElap<Option<Vec<f32>>>
    pub fn guardar(&self, modelo: &str, texto: &str, embedding: Vec<f32>) 
        -> ResultadoElap<()>
    pub fn limpiar(&self) -> ResultadoElap<()>
}
```

### RegistroModelos

```rust
pub struct RegistroModelos {
    modelos: Arc<Mutex<HashMap<String, ModelMetadata>>>,
}

impl RegistroModelos {
    pub fn nuevo() -> Self
    pub fn registrar(&self, metadata: ModelMetadata) -> ResultadoElap<()>
    pub fn obtener(&self, nombre: &str) -> ResultadoElap<ModelMetadata>
    pub fn listar(&self) -> ResultadoElap<Vec<ModelMetadata>>
    pub fn listar_descargados(&self) -> ResultadoElap<Vec<ModelMetadata>>
    pub fn contar(&self) -> ResultadoElap<usize>
}
```

---

## Flujo de Operación

### Generación de Texto

```
usuario.generar("Hola, ¿cómo estás?", 0.7)
    ↓
ModelManager valida modelo activo
    ↓
OllamaClient.generar(modelo, prompt, temp)
    ↓
Ollama devuelve texto
    ↓
Retornar a usuario
```

### Embeddings con Cache

```
usuario.embeddings("texto importante")
    ↓
CacheEmbeddings.obtener(modelo, texto)
    ↓
¿Está en cache?
    ├─ SÍ: Retornar vector cached
    └─ NO: 
        └─ OllamaClient.embeddings(modelo, texto)
        └─ CacheEmbeddings.guardar()
        └─ Retornar vector nuevo
```

### Chat con Memoria

```
usuario.chat("Hola")
    ↓
MemoriaCorta.push(usuario)
    ↓
OllamaClient.chat(modelo, historial)
    ↓
MemoriaCorta.push(asistente)
    ↓
¿Memoria > max_memoria?
    └─ SÍ: Eliminar entradas antiguas
    └─ NO: OK
    ↓
Retornar respuesta
```

---

## Ejemplos de Uso

### Ejemplo 1: Generación simple

```rust
use elap_core::{ModelManager, ModelMetadata, TipoModelo};

let mut manager = ModelManager::nuevo("http://localhost:11434", 10);

// Registrar modelo
let metadata = ModelMetadata::nuevo(
    "llama2:7b".to_string(),
    TipoModelo::Chat,
    "Llama 2 7B".to_string(),
    "7B".to_string(),
);
manager.registrar_modelo(metadata)?;
manager.set_modelo_activo("llama2:7b")?;

// Generar texto
let respuesta = manager.generar("Explica qué es la IA", 0.7)?;
println!("{}", respuesta);
```

### Ejemplo 2: Embeddings con cache

```rust
// Primer call: genera y cachea
let vec1 = manager.embeddings("documento importante")?;

// Segundo call: devuelve del cache (instantáneo)
let vec2 = manager.embeddings("documento importante")?;

assert_eq!(vec1, vec2);
```

### Ejemplo 3: Chat con memoria

```rust
manager.chat("Hola, me llamo Juan")?;
manager.chat("¿Recuerdas mi nombre?")?;
manager.chat("¿Cuál es mi nombre?")?;

let historial = manager.obtener_historial();
// historial contiene toda la conversación
```

---

## Performance

### Benchmarks

| Operación | Latencia | Notas |
|-----------|----------|-------|
| generar() | ~500ms | Depende modelo y hardware |
| embeddings() (no cache) | ~50ms | Modelo pequeño |
| embeddings() (cache) | <1ms | Instant |
| chat() | ~500ms | Con historial |

### Optimizaciones

1. **Cache de embeddings**: Evita recalcular vectores
2. **Memoria limitada**: VecDeque con max_memoria
3. **Thread-safe**: Arc<Mutex<>> para compartir
4. **Lazy loading**: Modelos se cargan bajo demanda

---

## Testing

### Cobertura

```
models/
├── model_metadata ....... 3 tests
├── ollama_client ....... 9 tests
├── registry ............ 6 tests
├── cache ............... 5 tests
├── manager ............ 8 tests
└── errors .............. 1 test
                        ─────────
TOTAL:                 32 tests ✅
```

### Ejecutar tests

```bash
cargo test -p elap-core --lib models
```

---

## Requisitos de Sistema

### Ollama

```bash
# Instalar Ollama
curl https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull llama2:7b

# Ejecutar servidor
ollama serve
# Disponible en: http://localhost:11434
```

### Modelos Recomendados

| Modelo | Tamaño | Caso de uso |
|--------|--------|-------------|
| **llama2:7b** | 3.5GB | Chat general |
| **mistral** | 4GB | Chat rápido |
| **neural-chat** | 4GB | Chat optimizado |
| **all-minilm** | 22MB | Embeddings rápido |
| **nomic-embed-text** | 274MB | Embeddings de calidad |

---

## Roadmap Futuro

- **Fase 7.1**: Streaming de respuestas
- **Fase 7.2**: Vector database (Qdrant) para RAG
- **Fase 7.3**: Fine-tuning de modelos
- **Fase 8**: Agent Framework con LangGraph
- **Fase 9**: Multi-model orchestration

---

## Conclusión

El Model Manager proporciona una interfaz simple y segura para ejecutar modelos de IA locales. Con caché automático, memoria conversacional y registro de modelos, es la base para sistemas de IA empresariales sin dependencias externas.

---

**Referencias**:
- [Ollama](https://ollama.ai)
- [TOOL_ENGINE.md](./TOOL_ENGINE.md)
- [SEGURIDAD.md](./SEGURIDAD.md)
