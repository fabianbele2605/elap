# Libro 01: Introducción — Capítulo 2 — Arquitectura General

**Tema**: Ver el mapa completo antes de entrar en detalles.

---

## 🗺️ Vista de 10,000 pies

```
┌─────────────────────────────────────────────────────────┐
│                  ELAP ARCHITECTURE                      │
│                                                         │
│  ┌─────────────┐           ┌─────────────┐            │
│  │ Desktop UI  │           │  Web API    │            │
│  │  (Tauri)    │           │  (gRPC)     │            │
│  └──────┬──────┘           └──────┬──────┘            │
│         │ REST/IPC               │                    │
│         └───────────┬────────────┘                    │
│                     │                                │
│         ┌───────────▼────────────┐                  │
│         │   Rust Core Runtime    │                  │
│         │  (ELAP Motor Central)  │                  │
│         │                        │                  │
│         │  • Task Scheduler      │                  │
│         │  • Security (RBAC)     │                  │
│         │  • Plugin Engine       │                  │
│         │  • Tool Registry       │                  │
│         │  • Audit Trail         │                  │
│         └───────────┬────────────┘                  │
│                     │ gRPC (bidireccional)         │
│         ┌───────────▼────────────┐                  │
│         │  Python AI Runtime     │                  │
│         │  (AI Agents)           │                  │
│         │                        │                  │
│         │  • LangGraph           │                  │
│         │  • LLM Inference       │                  │
│         │  • Memory + RAG        │                  │
│         │  • Tool Execution      │                  │
│         └────────────────────────┘                  │
│                     │                                │
│         ┌───────────▼────────────┐                  │
│         │  Infrastructure        │                  │
│         │                        │                  │
│         │  • PostgreSQL/SQLite   │                  │
│         │  • Vector DB (Qdrant)  │                  │
│         │  • Ollama (Local LLM)  │                  │
│         │  • File Storage        │                  │
│         └────────────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Capas de ELAP

### Capa 0: Infraestructura
```
Tu servidor (Docker, K8s, bare metal)
├─ CPU/GPU
├─ Memoria RAM
├─ Almacenamiento
└─ Red (solo interna)
```

### Capa 1: Runtime Core (Rust)
```
MotorCentral (Núcleo de ELAP)
├─ Planificador de tareas (Tokio async)
├─ Gestor de procesos (ejecuta herramientas)
├─ Configuración (TOML/YAML)
├─ Seguridad RBAC (quién puede qué)
├─ Auditoría (quién hizo qué)
└─ Plugin Engine (extensibilidad)
```

### Capa 2: Models (LLM Local)
```
Ollama / llama.cpp
├─ Llama 2 (7B, 13B, 70B)
├─ Mistral (rápido)
├─ Falcon (bueno para código)
└─ Quantized (Q4, Q5 para GPU limitadas)
```

### Capa 3: Execution (Python)
```
AI Runtime (Agentes inteligentes)
├─ LangGraph (orquestación de tareas)
├─ Memory (corta + larga plazo)
├─ RAG (recuperación de documentos)
└─ Tool Execution (archivos, HTTP, SQL)
```

### Capa 4: API Gateway
```
gRPC Bidireccional
├─ Rust ←→ Python (comunicación inter-proceso)
└─ Streaming (respuestas en tiempo real)
```

### Capa 5: Interface
```
Desktop/Web UI
├─ Tauri (aplicación desktop)
├─ React (futuro web)
└─ Control + Monitoring
```

---

## 🔄 Flujo de comunicación

### Caso: Usuario pide análisis de documento

```
1. Desktop UI
   Usuario: "Analiza este PDF"
        ↓
2. Rust Core Runtime
   Valida permisos (RBAC)
   Registra acción (auditoría)
        ↓
3. Python AI Runtime
   Carga documento
   Extrae chunks
   Genera embeddings
   Consulta modelo local
        ↓
4. Ollama (Modelo Local)
   Llama 2 7B procesa
   Devuelve respuesta
        ↓
5. Python AI Runtime
   Formatea respuesta
   Almacena en RAG
        ↓
6. Rust Core Runtime
   Comprime respuesta
   Registra resultado
        ↓
7. Desktop UI
   Muestra resultado al usuario
```

**Tiempo total**: <2 segundos (todo local, sin latencia de red)

---

## 📦 Módulos principales

### Rust Core
```
crates/elap-core/
├─ scheduler/       (tareas concurrentes)
├─ procesos/        (ejecución de herramientas)
├─ config/          (configuración)
├─ security/        (RBAC + auditoría)
├─ plugin/          (sistema de plugins)
└─ logging_v2/      (eventos estructurados)
```

### Python AI
```
python/elap_ai/
├─ agent_runtime/   (agentes inteligentes)
├─ memory/          (short-term + long-term)
├─ rag/             (búsqueda de documentos)
├─ tools/           (ejecución de herramientas)
└─ models/          (gestión de LLMs)
```

### Desktop
```
crates/elap-desktop/
├─ ipc/             (puente con core)
├─ ui/              (componentes de UI)
└─ main.rs          (punto de entrada)
```

---

## 🔐 Seguridad en arquitectura

```
Capas de defensa:

┌─ Usuario
│
├─ Capa 1: Autenticación
│  └─ ¿Quién eres?
│
├─ Capa 2: Autorización (RBAC)
│  └─ ¿Tienes permiso para esto?
│
├─ Capa 3: Validación
│  └─ ¿Son válidos estos datos?
│
├─ Capa 4: Plugin Sandbox
│  └─ Si usas plugin → aislado
│
├─ Capa 5: Auditoría
│  └─ Registro de todo lo que hiciste
│
└─ Datos (Encriptados en reposo)
```

---

## ⚡ Performance en arquitectura

### Cuello de botella: gRPC entre Rust y Python

```
Rust (Core)  ←→  gRPC  ←→  Python (AI)
  <1ms              2-5ms              <50ms
              latencia típica
```

**Optimización**: 
- Streaming para respuestas grandes
- Caching de resultados
- Batch processing

---

## 🎯 Decisiones arquitectónicas clave

| Componente | Opción | Razón |
|-----------|--------|-------|
| Core | Rust | Performance + seguridad |
| AI | Python | Ecosistema LLM |
| Comunicación | gRPC | Tipado + streaming |
| Desktop | Tauri | Pequeño binario |
| BD | PostgreSQL + SQLite | Flexible |

---

## 📊 Recursos típicos

### Máquina pequeña (desarrollo)
```
CPU:  4 cores
RAM:  8 GB (4 Rust, 4 Python)
GPU:  Ninguna (CPU mode)
Modelo: Llama 2 7B (lento pero funciona)
```

### Máquina mediana (producción pequeña)
```
CPU:  8 cores
RAM:  16 GB
GPU:  RTX 3060 (12 GB)
Modelo: Llama 2 13B (buena relación)
Usuarios simultáneos: 5-10
```

### Máquina grande (producción)
```
CPU:  16+ cores
RAM:  64 GB+
GPU:  A100 / RTX 4090
Modelo: Llama 2 70B (rápido)
Usuarios simultáneos: 50+
```

---

## 🔜 Siguiente: Capítulo 3

**"Flujo de Datos"**

Cómo se transforman los datos desde entrada hasta resultado:
- Entrada (documento, pregunta)
- Procesamiento (embeddings, ranking)
- Ejecución (modelo local)
- Salida (respuesta)

---

**Capítulo siguiente**: [03-flujo-de-datos.md](03-flujo-de-datos.md)
