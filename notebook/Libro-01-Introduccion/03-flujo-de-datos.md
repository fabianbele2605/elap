# Libro 01: Introducción — Capítulo 3 — Flujo de datos

**Tema**: Cómo viaja un dato desde que entra hasta que sale.

---

## 🔄 Flujo completo: Usuario pregunta, sistema responde

```
┌─ USUARIO PREGUNTA ─────────────────────────────────────────┐
│ "¿Cuál es la capital de Francia?"                           │
└───────────────────────────────────────────────────────────┘
              ↓
┌─ DESKTOP UI ──────────────────────────────────────────────┐
│ • Usuario escribe en el chat                              │
│ • Presiona "Enviar"                                       │
│ • UI envía mensaje por IPC                                │
└───────────────────────────────────────────────────────────┘
              ↓
┌─ RUST CORE (MotorCentral) ────────────────────────────────┐
│ 1. Recibe petición por IPC                                │
│ 2. Valida RBAC: ¿Usuario puede ejecutar herramientas?     │
│ 3. Registra en auditoría: "usuario_123 solicitó análisis" │
│ 4. Crea tarea en scheduler con prioridad ALTA             │
│ 5. Pasa a Python AI runtime via gRPC                      │
└───────────────────────────────────────────────────────────┘
              ↓
┌─ PYTHON AI (LangGraph) ───────────────────────────────────┐
│ 1. Recibe pregunta: "¿Capital de Francia?"                │
│ 2. Extrae embedding (vector de significado)               │
│ 3. Consulta memoria (¿lo preguntó antes?)                 │
│ 4. Si no está en memoria → consulta modelo local          │
│ 5. Llama a Ollama con Llama 2 7B                          │
└───────────────────────────────────────────────────────────┘
              ↓
┌─ OLLAMA (LLM Local) ──────────────────────────────────────┐
│ Modelo: Llama 2 7B quantizado                             │
│ Tiempo: ~0.5 segundos (todo local, sin red)               │
│ Respuesta: "La capital de Francia es París"               │
└───────────────────────────────────────────────────────────┘
              ↓
┌─ PYTHON AI (Guardando resultado) ─────────────────────────┐
│ 1. Recibe respuesta del modelo                            │
│ 2. Almacena en RAG (vector database)                      │
│ 3. Actualiza memoria a corto plazo                        │
│ 4. Serializa como JSON                                    │
│ 5. Envía de vuelta a Rust core                            │
└───────────────────────────────────────────────────────────┘
              ↓
┌─ RUST CORE (Finalizando) ─────────────────────────────────┐
│ 1. Recibe respuesta de Python                             │
│ 2. Verifica integridad                                    │
│ 3. Registra en auditoría: "respuesta exitosa"             │
│ 4. Comprime respuesta (si es grande)                      │
│ 5. Envía a UI por IPC                                     │
└───────────────────────────────────────────────────────────┘
              ↓
┌─ DESKTOP UI (Mostrando resultado) ────────────────────────┐
│ 1. Recibe respuesta                                       │
│ 2. Actualiza chat                                         │
│ 3. Muestra: "La capital de Francia es París"              │
└───────────────────────────────────────────────────────────┘
              ↓
┌─ USUARIO VE RESPUESTA ────────────────────────────────────┐
│ "La capital de Francia es París"                          │
│ (Tiempo total: <2 segundos, sin internet)                 │
└───────────────────────────────────────────────────────────┘
```

---

## 📊 En números

```
Usuarios simultáneos: 5
Preguntas/segundo: 2-3
Latencia promedio: 800ms
Ancho de banda: 0 (local)
Privacidad: 100% (datos nunca salen)
Costo: Solo electricidad
```

---

## 🔐 Puntos de seguridad en el flujo

```
1. Entrada (UI)
   └─ Validación básica

2. IPC (Rust ← UI)
   └─ Encriptación TLS

3. RBAC (Rust)
   └─ ¿Usuario tiene permiso?

4. Auditoría (Rust)
   └─ Registro: quién, qué, cuándo

5. Herramienta (Python)
   └─ Sandbox: límites de acceso

6. Salida (Python → Rust)
   └─ Validación de formato

7. IPC (Rust → UI)
   └─ Encriptación TLS
```

---

## 💾 Dónde se guardan los datos

```
Pasos 1-2 (UI → Rust):
  └─ Memoria RAM (mientras se procesa)

Pasos 3-4 (Rust):
  └─ Logs: /var/log/elap/
  └─ Auditoría: PostgreSQL

Paso 5 (Pregunta a modelo):
  └─ Contexto: RAM
  └─ Cache: Redis (opcional)

Paso 6 (Respuesta):
  └─ RAG/Vector DB: Qdrant
  └─ Memoria: ChromaDB

Paso 7 (Respuesta final):
  └─ Historial: PostgreSQL (opcional)
```

---

## 🎯 Optimizaciones

| Problema | Solución |
|----------|----------|
| Preguntas repetidas | Caching en memoria + RAG |
| Modelos lentos | Quantization (Q4, Q5) |
| Mucha concurrencia | Task scheduling + queue |
| Grandes respuestas | Compresión gzip |
| Queries lentas | Índices en vector DB |

---

## 🔜 Siguiente: Capítulo 4

**"Conceptos Clave"**

Aprenderás:
- Agentes vs tareas
- Permisos y roles
- Plugins y herramientas
- Sandboxing

---

**Capítulo siguiente**: [04-conceptos-clave.md](04-conceptos-clave.md)
