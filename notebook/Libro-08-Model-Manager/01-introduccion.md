# Libro 08: Model Manager — Capítulo 1 — Introducción

**Tema**: El cerebro de ELAP: modelos de IA locales.

---

## 🧠 ¿Qué es un modelo?

Un **modelo** es una red neuronal entrenada que puede:
- Generar texto
- Entender significado (embeddings)
- Conversar

**Analogía**: Una persona muy culta que memorizó millones de libros

```
┌─ MODELO ─────────────────────────────┐
│ Entrada: "Hola, ¿cómo estás?"        │
│ Cerebro: Red neuronal (7B parámetros)│
│ Salida: "Hola, estoy bien, ¿y tú?"  │
└───────────────────────────────────────┘
```

---

## 🏠 Ollama: Modelos en tu máquina

**Ollama** es un programa que ejecuta modelos de IA **sin internet**.

```
Internet          Local (MEJOR)
  ↓                 ↓
CloudGPT API      Ollama
  ↓                 ↓
Mensajes → red     Mensajes → GPU/CPU
  ↓                 ↓
Respuesta (lenta)  Respuesta (rápida)
Costo: $$          Costo: Electricidad
```

**Ventajas locales**:
- ✅ Privacidad total (sin enviar datos)
- ✅ Sin latencia de red
- ✅ Sin costos por API
- ✅ Funciona offline

---

## 📚 Los 3 tipos de modelos en ELAP

### 1. TextoGenerativo

Completa un prompt.

```
Entrada: "En el año 2050..."
Modelo:  "En el año 2050, la IA habrá..."
```

### 2. Embedding

Convierte texto en vector (número).

```
"Gato" → [0.1, 0.5, -0.3, ..., 0.8]
         384 dimensiones
         ↑
    Representa el SIGNIFICADO
```

### 3. Chat

Conversa como un asistente.

```
Usuario: "¿Qué es una función?"
Modelo: "Una función es un bloque de código..."
Usuario: "¿Puedo retornar dos valores?"
Modelo: "Sí, usando una tupla: return (a, b)"
         ↑
      Recuerda la conversación anterior
```

---

## 🧮 Modelos recomendados

| Modelo | Tamaño | Velocidad | Calidad | Mejor para |
|--------|--------|-----------|---------|-----------|
| **llama2:7b** | 3.5GB | Rápido | Media | Chat general |
| **mistral** | 4GB | Muy rápido | Media | Respuestas cortas |
| **all-minilm** | 22MB | Instantáneo | Buena | Embeddings |

---

## 💾 Model Manager: Orquestador

```
┌─ Model Manager ───────────────────┐
│                                   │
│ 1. Registrar modelos              │
│    └─ Guardar metadata            │
│                                   │
│ 2. Cachear embeddings             │
│    └─ Si pido lo mismo, gratis    │
│                                   │
│ 3. Mantener memoria               │
│    └─ Recuerda conversación       │
│                                   │
│ 4. Conectar con Ollama            │
│    └─ Ejecutar modelo             │
│                                   │
└───────────────────────────────────┘
```

---

## 🎯 Flujos comunes

### Flujo 1: Preguntar algo

```
Usuario: "¿Cuál es la capital de Francia?"
         ↓
ModelManager.generar(prompt, temp=0.7)
         ↓
OllamaClient.generar("llama2:7b", prompt)
         ↓
Ollama ejecuta el modelo
         ↓
"París"
```

### Flujo 2: Buscar documentos similares

```
Usuario busca: "cómo cocinar"
         ↓
ModelManager.embeddings("cómo cocinar")
         ↓
¿Está en cache? NO
         ↓
OllamaClient.embeddings(modelo, texto)
         ↓
Vector: [0.2, -0.5, 0.8, ...]
         ↓
Buscar documentos cercanos
         ↓
Retornar recetas similares
```

### Flujo 3: Conversación inteligente

```
1. "Me llamo Juan"
   ↓ ModelManager.chat("Me llamo Juan")
   ↓ Memoria: [usuario, asistente]

2. "¿Cuál es mi nombre?"
   ↓ ModelManager.chat("¿Cuál es mi nombre?")
   ↓ Usa historial completo
   ↓ "Tu nombre es Juan"
   ↓ Memoria: [usuario, asistente, usuario, asistente]
```

---

## ⚡ Optimizaciones automáticas

### Cache de Embeddings

```
Primer call:  embeddings("importante")
  └─ Genera vector (50ms)
  └─ Guarda en cache

Segundo call: embeddings("importante")
  └─ Lee del cache (<1ms)
  └─ 50x más rápido!
```

### Memoria Limitada

```
Conversación muy larga:
  ↓ Mantiene últimas 10 entradas
  ↓ Descarta antiguas automáticamente
  ↓ Evita memoria infinita
```

---

## 🔢 Parámetros: ¿Qué significan?

```
"llama2:7b"
       ↑
       7 billion parámetros = 3.5GB descargado

Más grande = más inteligente pero más lento
  7B:  Rápido, medio inteligente
  13B: Medio, más inteligente
  70B: Muy lento, muy inteligente
```

---

## 🌡️ Temperatura

```
temperature = 0.1  (Frío, predecible)
  └─ Respuestas iguales siempre
  └─ Ideal para búsqueda

temperature = 0.7  (Normal)
  └─ Variedad + coherencia
  └─ Ideal para chat

temperature = 1.0  (Caliente, creativo)
  └─ Respuestas impredecibles
  └─ Ideal para escritura creativa
```

---

## 📊 Arquitectura de Model Manager

```
Usuario
  ↓
ModelManager (orquestador)
  ├─ OllamaClient (ejecuta modelo)
  ├─ RegistroModelos (qué modelos hay)
  ├─ CacheEmbeddings (memory rápida)
  └─ MemoriaCorta (conversación)
  ↓
Ollama (servidor local)
  ↓
Tu GPU/CPU
```

---

## 🚀 Primeros pasos

### 1. Instalar Ollama

```bash
curl https://ollama.ai/install.sh | sh
```

### 2. Descargar modelo

```bash
ollama pull llama2:7b
# Descarga ~3.5GB
```

### 3. Crear Model Manager

```rust
let mut manager = ModelManager::nuevo(
    "http://localhost:11434",
    10  // max 10 entradas en memoria
)?;
```

### 4. Registrar modelo

```rust
let metadata = ModelMetadata::nuevo(
    "llama2:7b".to_string(),
    TipoModelo::Chat,
    "Llama 2 7B".to_string(),
    "7B".to_string(),
);
manager.registrar_modelo(metadata)?;
manager.set_modelo_activo("llama2:7b")?;
```

### 5. Usar

```rust
let respuesta = manager.generar("Hola", 0.7)?;
println!("{}", respuesta);
```

---

## ✨ Próximo: Capítulo 2

**"Tu primer modelo"**

Aprenderás:
- Descargar e instalar Ollama
- Crear tu primer Model Manager
- Generar texto, embeddings, chat
- Experimentar con temperaturas
- Medir performance

---

**Siguiente capítulo**: [02-tu-primer-modelo.md](02-tu-primer-modelo.md)
