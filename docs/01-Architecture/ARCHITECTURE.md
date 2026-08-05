# Arquitectura del Sistema ELAP

**Fase**: 0 (Fundacional)  
**Estado**: 🔄 En progreso  
**Versión**: 1.0-alpha

---

## 1. Descripción general de la arquitectura

ELAP está organizada alrededor de **runtimes independientes**, no de agentes. Cada runtime es un componente especializado que gestiona una responsabilidad específica.

```
┌─────────────────────────────────────────────────────┐
│   Plataforma Enterprise Local de IA (ELAP)          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │   Motor de Escritorio (Tauri + TypeScript)  │   │
│  │   - Gestión de ventanas                     │   │
│  │   - Interfaz de usuario                     │   │
│  │   - Comunicación con Motor Central          │   │
│  └─────────────────────────────────────────────┘   │
│                      ↓↑                             │
│  ┌─────────────────────────────────────────────┐   │
│  │   Motor Central Rust (Tokio)                │   │
│  │   - Planificación de tareas                 │   │
│  │   - Gestión de procesos                     │   │
│  │   - Seguridad (RBAC)                        │   │
│  │   - Motor de plugins                        │   │
│  │   - Puerta de enlace gRPC                   │   │
│  │   - Gestión de configuración                │   │
│  │   - Logging/Auditoría                       │   │
│  └─────────────────────────────────────────────┘   │
│                      ↕ gRPC                        │
│  ┌─────────────────────────────────────────────┐   │
│  │   Motor de IA Python (LangGraph)            │   │
│  │   - Ejecución de agentes                    │   │
│  │   - Inferencia de LLM (Ollama)              │   │
│  │   - Gestión de memoria (RAG)                │   │
│  │   - Ejecución de herramientas               │   │
│  └─────────────────────────────────────────────┘   │
│                      ↓                              │
│  ┌─────────────────────────────────────────────┐   │
│  │   Sistemas externos                         │   │
│  │   - Ollama/llama.cpp (modelos)              │   │
│  │   - Qdrant/ChromaDB (almacén vectorial)     │   │
│  │   - PostgreSQL/SQLite (base de datos)       │   │
│  │   - Sistema de archivos                     │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 2. Principios fundamentales

### 2.1 Rust = Plataforma. Python = IA.

| Responsabilidad | Lenguaje | Por qué |
|---|---|---|
| Ciclo de vida de la aplicación | Rust | Rendimiento, seguridad de memoria, acceso al SO |
| Concurrencia/planificación | Rust | Tokio > asyncio en rendimiento |
| Seguridad/RBAC | Rust | Memoria segura, menor superficie de ataque |
| Gestión de procesos | Rust | Acceso directo al SO |
| Motor de plugins | Rust | Aislamiento y sandboxing seguro |
| **Inferencia de LLM** | **Python** | Ecosistema de Transformers, llama.cpp |
| **RAG/embeddings** | **Python** | LangChain, clientes de base de datos vectorial |
| **Orquestación de agentes** | **Python** | LangGraph, agentes async |
| **Ejecución de herramientas** | **Ambos** | Rust valida, Python ejecuta |

### 2.2 Procesos, no monolito

- **Motor Central** (Rust) se ejecuta como proceso principal
- **Motor de IA** (Python) se ejecuta como proceso separado
- Comunicación vía **gRPC sobre socket de dominio Unix** (TLS-asegurado)
- Beneficios:
  - Si Python falla, el Motor Central sigue funcionando
  - Versionado independiente
  - Puede reiniciar Python sin reiniciar el Motor Central
  - API tipada con contratos (Protocol Buffers)

### 2.3 Local-first, capaz de funcionar offline

- Sin datos que salgan del perímetro empresarial
- Toda la telemetría permanece local
- Los modelos se ejecutan en infraestructura local
- Opcional: características en línea (chequeo de actualizaciones, integraciones en la nube) deshabilitadas por defecto

---

## 3. Arquitectura de componentes

### 3.1 Motor Central Rust (Proceso principal)

**Propósito**: Orquestación, seguridad, gestión del ciclo de vida.

```
elap-core/
├── Motor (ciclo de vida)
├── Planificador de Tareas (basado en Tokio)
├── Gestor de Procesos (spawn/gestionar subprocesos)
├── Motor de Plugins (cargar, aislar, gestionar plugins)
├── Gestor RBAC (validación de permisos)
├── Gestor de Configuración (cargar, recargar en caliente TOML)
├── Logger (estructurado, solo local)
├── Gestor de Actualizaciones (binarios firmados)
├── Gestor de Respaldos (recuperación de configuración + memoria)
├── Puerta de Enlace IPC (servidor gRPC)
└── Gestor de Seguridad (cifrado, secretos)
```

**Responsabilidades clave**:
1. Iniciar/detener ciclo de vida
2. Validar todos los permisos antes de delegar a Python
3. Enrutar solicitudes al agente correcto de IA
4. Gestionar plugins de forma segura
5. Auditar todas las mutaciones (escrituras, llamadas a API)
6. Manejar actualización/recuperación
7. Gestionar recursos de hardware (detectar GPU, asignación de CPU)

### 3.2 Shell de Escritorio (Tauri)

**Propósito**: Interfaz de usuario, gestión de ventanas, integración con el SO.

```
elap-desktop/
├── Gestor de Ventanas (Tauri)
├── Cliente IPC (se comunica con Motor Central)
├── Gestión de Estado (estado de React/Vue)
├── Interfaz de Chat (conversación con agentes)
├── Dashboard (estado, monitoreo)
├── IU de Configuración (gestión de configuración)
└── Monitoreo de Recursos (CPU/GPU/RAM)
```

**Responsabilidades clave**:
1. Mostrar respuestas del agente en tiempo real (streaming)
2. Recopilar entrada del usuario
3. Mostrar salud del sistema
4. Gestionar interfaz de configuración
5. Manejar interfaz de autenticación
6. Mostrar logs de auditoría

### 3.3 CLI (elap-cli)

**Propósito**: Herramientas de línea de comandos para administración y desarrollo.

```
elap-cli/
├── start (lanzar runtimes de core + python)
├── stop (detención elegante)
├── status (chequeo de salud)
├── config (ver/editar configuración)
├── agent (gestionar agentes)
├── model (gestionar modelos)
├── backup (gestionar respaldos)
├── restore (restaurar desde respaldo)
└── logs (ver logs de auditoría)
```

### 3.4 Motor de IA Python (Proceso separado)

**Propósito**: Inferencia de IA, agentes, gestión de memoria.

```
elap_ai/
├── Motor de Agentes (basado en LangGraph)
│   ├── Gestor de Agentes (crear/gestionar agentes)
│   ├── Ejecutor de Agentes (ejecutar lógica del agente)
│   └── Delegación (delegación entre agentes)
├── Motor de Modelos (interfaz Ollama/llama.cpp)
│   ├── Cargador de Modelos (descargar/cargar)
│   ├── Selector de Modelos (elegir por tarea/agente)
│   └── Inferencia (generar tokens)
├── Gestor de Memoria (corta + larga plazo)
│   ├── Memoria Corta Plazo (historial de conversación)
│   ├── Memoria Larga Plazo (base de datos vectorial)
│   └── RAG (generación aumentada por recuperación)
├── Ejecutor de Herramientas (invocación segura de herramientas)
│   ├── Registro de Herramientas (herramientas disponibles)
│   ├── Validador de Herramientas (chequeo de permisos)
│   └── Ejecutor de Herramientas (ejecutar de forma segura)
└── Servidor gRPC (comunicar con Motor Central)
```

**Responsabilidades clave**:
1. Ejecutar agentes (LangGraph)
2. Gestionar memoria de conversación
3. Recuperar contexto relevante (RAG)
4. Generar respuestas (inferencia de LLM)
5. Ejecutar herramientas permitidas
6. Transmitir respuestas de vuelta al Motor Central

---

## 4. Patrones de comunicación

### 4.1 Escritorio ↔ Motor Central (gRPC o REST)

**Escritorio** envía solicitudes del usuario → **Motor Central** valida → enruta a **Python**

```
┌─────────┐
│ Escritorio│
│ (IU)    │
└────┬────┘
     │ gRPC o HTTP
     ↓
┌─────────────────┐
│ Motor Central   │
│ (Orquestador)   │
└────┬────────────┘
     │ Valida RBAC
     │ Log de auditoría
     ↓
```

### 4.2 Motor Central ↔ Motor de IA Python (gRPC)

**Motor Central** pide a Motor de IA Python procesar consulta → **Python** transmite respuesta

```
┌──────────────┐
│ Motor Central│
└──────┬───────┘
       │ solicitud gRPC
       │ (user_id, agent_id, query)
       ↓
┌──────────────┐
│ Motor de IA  │
│ Python       │ → Buscar memoria (Qdrant)
└──────┬───────┘   → Llamar LLM (Ollama)
       │            → Ejecutar herramientas
       │ respuesta gRPC
       │ (transmisión de tokens)
       ↓
┌──────────────┐
│ Motor Central│
│ (log auditoría)│
└──────────────┘
```

### 4.3 Detalles de IPC (Detalle futuro en Fase 1)

- **Protocolo**: gRPC con Protocol Buffers
- **Transporte**: socket de dominio Unix (Linux) / named pipe (Windows)
- **Seguridad**: TLS 1.3 + autenticación mutua
- **Buffer**: streaming async con contraPresión
- **Objetivo de latencia**: <5ms por solicitud

---

## 5. Persistencia de datos

### 5.1 SQLite (Desarrollo/Instancias pequeñas)

- Archivo único: `elap.db`
- Esquema: usuarios, agentes, permisos, logs de auditoría, conversaciones
- Limitaciones: <10 usuarios concurrentes

### 5.2 PostgreSQL (Empresarial)

- Esquema: idéntico al de SQLite (portátil)
- Soporta: 50+ usuarios concurrentes, replicación
- Requisitos: gestionado por cliente o BBLABS

### 5.3 Base de datos vectorial (Memoria de IA)

**Desarrollo**: ChromaDB (embebido)  
**Producción**: Qdrant (independiente)

- Almacena: incrustaciones de documentos, fragmentos de conversación
- Propósito: RAG (recuperar contexto para prompts)
- Volumen: ~GB a ~TB dependiendo de documentos

---

## 6. Modelo de seguridad (descripción general Fase 0)

### 6.1 RBAC (Control de Acceso Basado en Roles)

```
Usuario → Rol → Permisos
              ├── Acceso al agente (qué agentes pueden usar)
              ├── Acceso a herramientas (qué herramientas pueden llamar)
              └── Acceso a datos (qué archivos/bases de datos)
```

Cada operación se valida contra el rol del usuario antes de la ejecución.

### 6.2 Cifrado

- **En reposo**: AES-256 para configuraciones/secretos sensibles
- **En tránsito**: TLS 1.3 para IPC
- **Sin cifrado de nube por defecto** (local-first significa clave local)

### 6.3 Logging de auditoría

Cada operación registrada:
- ID de usuario
- Marca de tiempo
- Acción (lectura/escritura/ejecución)
- Recurso
- Resultado (éxito/fallo)

Almacenado en SQLite/PostgreSQL, inmutable.

---

## 7. Puntos de extensibilidad

### 7.1 Plugins (Fase 6)

Código Rust personalizado compilado a .so/.dll, cargado en tiempo de ejecución.  
Aislado usando modelo de capacidad.

Ejemplo: procesador PDF personalizado, conector de CRM empresarial.

### 7.2 Herramientas (Fase 7)

Funciones Python registradas en ToolRegistry.  
Invocadas por agentes después de validación RBAC.

Ejemplo: Enviar correo, consultar SQL, leer/escribir archivos.

### 7.3 Agentes (Fase 12)

Agentes basados en LangGraph ejecutándose en Motor de IA Python.  
Composición: modelo + herramientas + memoria + prompt.

Ejemplo: Agente de Ventas, agente de RRHH, agente de Finanzas.

### 7.4 Modelos (Fase 8)

Intercambiar LLM sin cambiar arquitectura.  
Soporte: Ollama, llama.cpp, Transformers, HuggingFace.

Ejemplo: Cambiar de Llama-7B a Mistral-8x7B.

---

## 8. Modelo de despliegue

### 8.1 Máquina única (PYME)

```
┌─────────────────────────────────────┐
│ Laptop/Servidor del cliente         │
├─────────────────────────────────────┤
│                                     │
│ ┌──────────────────────────────┐   │
│ │ ELAP (Rust + Python + Tauri) │   │
│ │ + SQLite                      │   │
│ │ + ChromaDB                    │   │
│ │ + Ollama                      │   │
│ └──────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

Datos basados en archivo, <30GB disco requerido, 16GB RAM mínimo.

### 8.2 Multi-máquina (Empresarial)

```
┌─────────────────────────────────────┐
│ Servidor 1: Motor Central ELAP + Escritorio│
├─────────────────────────────────────┤
│ Servidor 2: Motor de IA Python      │
├─────────────────────────────────────┤
│ Servidor 3: Base de datos PostgreSQL│
├─────────────────────────────────────┤
│ Servidor 4: Base de datos vectorial Qdrant│
├─────────────────────────────────────┤
│ Servidor 5: Caché de modelo Ollama  │
└─────────────────────────────────────┘
  (todos detrás de red privada, sin internet)
```

Escalable, resiliente, gestión de múltiples nodos.

---

## 9. Comparación con alternativas

### Solo Python

❌ Problemas:
- Rendimiento pobre en operaciones principales
- Sobrecarga de memoria (GC, runtime)
- Difícil gestionar procesos de forma segura
- Difícil aislar plugins

### Go + Python

❌ Problemas:
- Tres ecosistemas (cargo + go mod + pip)
- Go agrega complejidad sin resolver problemas ya buenos en Rust
- Mayor carga de mantenimiento

### Node.js (Electron)

❌ Problemas:
- Binario 150MB+ vs Tauri ~10MB
- Alto consumo de RAM
- Menos control sobre el SO nativo

### C++ + Python

❌ Problemas:
- Problemas de seguridad de memoria en C++
- Proceso de compilación complejo
- Más lento de desarrollar comparado con Rust

**Elegido: Rust + Python** ✅
- Rendimiento + seguridad + ajuste del ecosistema
- Límite claro del lenguaje (plataforma vs IA)
- Lo mejor de ambos mundos

---

## 10. Evolución por fases

| Fase | Agrega | Cambios |
|------|--------|---------|
| 0 | Fundacionales | Estructura, módulos base |
| 1 | Motor Central | Planificación de tareas, procesos, plugins |
| 2 | Escritorio | Ventana Tauri, comunicación |
| 3-5 | Plomería | Config, logging, errores |
| 6-7 | Extensibilidad | Plugins, herramientas |
| 8-10 | Motor de IA | Modelos, agentes, memoria |
| 11-12 | Orquestación | Flujos, delegación |
| 13-14 | UX/Despliegue | GUI, instalador |
| 15-17 | Pulido | Actualizaciones, testing, empaquetado |

---

## 11. Objetivos de rendimiento

| Operación | Objetivo | Hardware de referencia |
|-----------|----------|-------------------|
| Latencia de primer token | <3s | CPU 8-núcleos, 16GB RAM, modelo 7B Q4 |
| Usuarios concurrentes | 50 | 16-núcleos, 64GB RAM, 1 GPU |
| Rendimiento de inferencia | 20 tokens/seg | Igual al anterior |
| Inicio del Motor | <2s | SSD, sin espera GPU |

---

## 12. Siguientes pasos

Ver:
- [DECISIONS.md](DECISIONS.md) — Por qué estas opciones
- [/docs/02-Development/SETUP.md](../02-Development/SETUP.md) — Cómo construir localmente
- [/docs/02-Development/CONVENTIONS.md](../02-Development/CONVENTIONS.md) — Estándares de código

---

**Última actualización**: 2026-08-04  
**Próxima revisión**: Después de completar Fase 1
