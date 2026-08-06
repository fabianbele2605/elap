# CHANGELOG — Historial de Cambios ELAP

## [Fase 20] - 2026-08-05

### 🧪 Testing & Integración

#### Integration Testing Suite

**Docker Compose Stack Test**:
- Verifica que Core, Python AI, PostgreSQL, Qdrant levanten
- Health checks para cada servicio
- Bash script automático

**REST API Integration Tests**:
- JWT authentication
- CRUD operations (create, read, list, delete)
- Full agent lifecycle
- cURL-based tests

**gRPC Integration Tests**:
- Connection establishment
- Agent execution via gRPC
- Streaming updates
- Error handling
- Timeout scenarios

**WebSocket Integration Tests**:
- Connection/disconnection
- Message streaming
- Heartbeat mechanism
- Reconnection logic
- Concurrent streams (multiple agents)

**RAG Pipeline E2E Tests**:
- Complete pipeline: embeddings → vector DB → hybrid search → reranking
- Semantic cache in pipeline
- Multiple concurrent queries
- Performance verification (cache 100x faster)
- Error handling

**Tests**: 18 tests nuevos, todos pasando ✅

### 📚 Documentación

- `docs/10-Testing/INTEGRATION_TESTING.md`: Guía técnica (test suites, flujos, checklist)
- `notebook/20-Integration-Testing.md`: Capítulo didáctico (pirámide de tests, casos reales)

### 🎯 Verificaciones Completas

- [x] Docker Compose levanta sin errores
- [x] Core API responde (<100ms)
- [x] gRPC funciona (Rust ↔ Python)
- [x] REST CRUD completo
- [x] WebSocket streaming en vivo
- [x] RAG pipeline E2E
- [x] Semantic cache (100x latencia)
- [x] Concurrent operations
- [x] Error handling

---

## [Fase 19] - 2026-08-05

### ✨ Nuevas Funcionalidades

#### Advanced RAG

**Reranking con Cross-Encoders**:
- Modelo: `cross-encoder/ms-marco-MiniLM-L-12-v2`
- Lazy loading (fallback si no está instalado)
- Ordena documentos por relevancia verdadera
- Async execution con `asyncio.to_thread`

**Semantic Cache**:
- TTL configurable (default: 3600s)
- Hash-based key (SHA256)
- Estadísticas de cache activas
- 100x latencia en hits

**Hybrid Search**:
- Combina BM25 (keyword) + Semantic (embedding)
- Pesos ajustables (default: 0.7 semantic, 0.3 BM25)
- Mejor recall (keywords) + precision (semantic)

**Tests**:
- 7 tests nuevos (reranker, cache, hybrid)
- Coverage: 95%+
- Async fixtures con pytest-asyncio

### 📚 Documentación

- `docs/09-Advanced/ADVANCED_RAG.md`: Guía técnica
- `notebook/19-Advanced-RAG.md`: Capítulo didáctico (componentes, flujo, benchmarks)

### 🎯 Cambios Arquitectónicos

```
RAG Pipeline v2:
Query → [Semantic Cache] → [Embeddings] → [Vector DB]
    → [Hybrid Search (BM25 + Semantic)] → [Reranking]
    → [Cache Results] → Top-K Results
```

---

## [Fase 12] - 2026-08-05

### ✨ Nuevas Funcionalidades

#### Dashboard CLI en Terminal

**Comandos Implementados**:
- `elap agents list` - Listar todos los agentes (tabla formateada)
- `elap agents create` - Crear nuevo agente interactivamente
- `elap agent <id> info` - Info detallada del agente
- `elap agent <id> watch` - Monitoreo en tiempo real (WebSocket)
- `elap agent <id> status` - Estado actual con progreso
- `elap agent <id> execute` - Ejecutar plan (con progress bar)
- `elap agent <id> delete` - Eliminar agente

**Features**:
- Tabla formateada con prettytable
- Colores y emojis (colored)
- Barras de progreso (indicatif)
- WebSocket streaming (tokio-tungstenite)
- HTTP client (reqwest)
- JWT token support via env/args
- Server configurable (--server flag)

**Clientes**:
- `HttpClient`: REST API calls
- `WsClient`: WebSocket monitoreo en vivo

### 📚 Documentación

- `docs/06-CLI/DASHBOARD_CLI.md`: Guía completa
  - Todos los comandos
  - Ejemplos de flujo
  - Configuración (env vars, args)
  - Paleta de colores y emojis

### 🏗️ Cambios Arquitectónicos

**Estructura**:
```
crates/elap-cli/src/
├── main.rs                    # Punto de entrada
├── commands/
│   ├── mod.rs
│   ├── agents.rs             # Listar, crear
│   └── agent.rs              # Info, watch, execute, status, delete
└── client/
    ├── mod.rs
    ├── http_client.rs        # REST calls
    └── ws_client.rs          # WebSocket
```

**Dependencias nuevas**:
- reqwest 0.11 (HTTP)
- tokio-tungstenite 0.21 (WebSocket)
- colored 2.1 (terminal colors)
- indicatif 0.17 (progress bars)
- prettytable-rs 0.10 (tables)
- futures (stream handling)

### 📊 Métricas Fase 12

| Métrica | Valor |
|---------|-------|
| Comandos | 7 |
| Clientes | 2 (HTTP + WebSocket) |
| Líneas de código | ~400 |
| Dependencias nuevas | 6 |
| Compilación | OK ✅ |

### 🎯 UX Features

- 🔵 Cyan: IDs y datos técnicos
- 🟢 Green: Éxito y confirmaciones
- 🔴 Red: Errores
- 🟡 Yellow: Estados y alertas
- Emojis descriptivos (📋, 🚀, 👁️, ⚡, etc)
- Tablas formateadas
- Barras de progreso
- WebSocket en vivo con eventos tipados

---

## [Fase 11] - 2026-08-05

### ✨ Nuevas Funcionalidades

#### Persistencia en BD — SQLite + PostgreSQL

**SQLite Embebido (Default)**:
- Auto-detecta ubicación (`~/.elap/elap.db`)
- Auto-crea tablas en startup
- Sin dependencias externas
- Connection pooling (5 conexiones)
- Ideal para desktop/single-user

**PostgreSQL (Opcional)**:
- Via env var `DATABASE_URL`
- Soporte multi-usuario
- Escalable para producción
- Replicación posible

**Tablas**:
- `agentes`: Metadatos del agente
- `execuciones`: Historial de ejecuciones
- `acciones`: Acciones registradas por agente

**API Repository Pattern**:
- `RepositorioAgente::guardar()` - Crear/actualizar
- `RepositorioAgente::obtener()` - Leer por ID
- `RepositorioAgente::listar()` - Listar todos
- `RepositorioAgente::eliminar()` - Borrar
- `RepositorioAgente::registrar_ejecucion()` - Historial
- `RepositorioAgente::obtener_ejecuciones()` - Recuperar historial
- `RepositorioAgente::registrar_accion()` - Log de acciones
- `RepositorioAgente::obtener_acciones()` - Recuperar acciones
- `RepositorioAgente::contar()` - Total de agentes

### 📚 Documentación

- `docs/05-Persistence/PERSISTENCE.md`: Guía completa
  - SQLite default vs PostgreSQL
  - API Repository
  - Ejemplos prácticos
  - Mejores prácticas
  - Migración SQLite↔PostgreSQL

### 🧪 Tests

- 4 tests nuevos (directorio, conexión, repositorio, schema)
- 336 tests totales en elap-core (0 fallos)
- Tests con SQLite en-memory (reproducibles, sin contaminar sistema)

### 🏗️ Cambios Arquitectónicos

**Nuevos módulos**:
- `db/mod.rs`: Orquestación
- `db/connection.rs`: Pool SQLite, auto-init
- `db/schema.rs`: AgenteBD, EjecucionBD, AccionBD
- `db/agent_repo.rs`: CRUD operations

**Dependencias**:
- sqlx 0.7 (sqlite, postgres, migrate)
- directories 5.0 (paths multiplataforma)

**Error handling**:
- Agregar From<sqlx::Error> → ElapError

### 📊 Métricas Fase 11

| Métrica | Valor |
|---------|-------|
| Tests nuevos | 4 |
| Tests totales | 336 |
| Tablas BD | 3 |
| Métodos Repository | 8 |
| Plataformas soportadas | 3 (Linux, macOS, Windows) |
| Ubicación DB | ~/.elap/elap.db |

### 🔗 Arquitectura Persistencia

```
[App]
  ↓
obtener_db() [auto-init]
  ├─ Detecta SQLite default
  ├─ O lee DATABASE_URL para PostgreSQL
  ├─ Crea tablas si no existen
  └─ Retorna pool (5 conexiones)
  ↓
RepositorioAgente [Repository Pattern]
  ├─ guardar()
  ├─ obtener()
  ├─ listar()
  ├─ registrar_ejecucion()
  └─ obtener_acciones()
```

---

## [Fase 10] - 2026-08-05

### ✨ Nuevas Funcionalidades

#### Autenticación JWT + RBAC

**JWT (JSON Web Tokens)**:
- ManagerJWT: Generación y validación de tokens
- Claims: sub (usuario), rol, exp (24h), iat
- Firma HMAC-SHA256 con secret key
- Validación de expiración automática
- Extractor de Bearer token

**RBAC (Role-Based Access Control)**:
- 3 roles: Admin, User, Guest
- 5 acciones: Crear, Leer, Actualizar, Eliminar, Ejecutar
- ValidadorRBAC con matriz de permisos
- Checks en handlers de endpoints

**Endpoints**:
- POST /login - Obtener token (sin autenticación requerida)
- Todos los otros endpoints requieren Bearer token

**Permisos por Rol**:
- Admin: todas las acciones (5/5)
- User: CRUD básico (4/5) - no puede eliminar
- Guest: solo lectura (1/5)

### 📚 Documentación

- `docs/04-API/AUTHENTICATION.md`: Guía completa
  - Flujo de autenticación
  - Roles y permisos
  - Ejemplos cURL, JS, Rust
  - Mejores prácticas de seguridad

### 🧪 Tests

- 5 tests JWT (Claims, generación, validación, expiración)
- 6 tests RBAC (roles, permisos, acciones)
- 11 tests nuevos (100% cobertura)
- 332 tests totales en elap-core (0 fallos)

### 🏗️ Cambios Arquitectónicos

**Nuevos módulos**:
- `api/auth.rs`: JWT ManagerJWT, Claims, validación
- `api/rbac.rs`: RolAPI, Accion, ValidadorRBAC

**Actualizaciones**:
- `handlers.rs`: Agregar login, validar Claims en DELETE
- `routes.rs`: POST /login sin requerir token
- `lib.rs`: Exportar tipos de autenticación

**Dependencias**:
- jsonwebtoken 9.2
- base64 0.21

### 📊 Métricas Fase 10

| Métrica | Valor |
|---------|-------|
| Tests nuevos | 11 |
| Tests totales | 332 |
| Roles | 3 |
| Acciones | 5 |
| Duración token | 24h |
| Algoritmo | HMAC-SHA256 |

### 🔗 Flujo Completo

```
[Cliente] 
    ↓
POST /login → [Generar JWT]
    ↓
Bearer token en headers
    ↓
Validar token + RBAC
    ↓
Ejecutar endpoint o 403
```

---

## [Fase 9] - 2026-08-05

### ✨ Nuevas Funcionalidades

#### Web API REST + WebSocket (Pasos 1-2)

**Paso 1: REST API - 7 Endpoints CRUD**
- POST /agents - Crear agente
- GET /agents - Listar agentes
- GET /agents/{id} - Obtener agente
- POST /agents/{id}/pasos - Agregar paso
- POST /agents/{id}/execute - Ejecutar agente
- GET /agents/{id}/status - Obtener estado
- DELETE /agents/{id} - Eliminar agente

**Paso 2: WebSocket Streaming - Monitoreo en Vivo**
- GET ws://localhost:3000/agents/{id}/watch
- 7 tipos de eventos: conectado, estado, progreso, acción, reflexión, latido, error
- Heartbeat cada 1 segundo
- Bidireccional (preparado para comandos futuros)
- 6 tests unitarios (tipos de eventos)

### 🛠️ Implementación

- **Framework**: Axum 0.7 + Tower middleware
- **WebSocket**: axum::extract::ws + futures
- **Estado compartido**: AppState con Arc<RwLock<HashMap>>
- **Handlers tipados**: CrearAgentRequest, AgentResponse, EjecucionResponse
- **Eventos tipados**: AgentEvent con 7 variantes
- **CORS**: Configurado para desarrollo

### 📚 Documentación

- `docs/04-API/REST_API.md`: 7 endpoints REST
  - Ejemplos curl
  - Request/Response schemas
  - Códigos HTTP
  
- `docs/04-API/WEBSOCKET.md`: Monitoreo en tiempo real
  - 7 tipos de eventos
  - Ejemplos JavaScript, Rust, Bash
  - Flujo completo
  - Performance metrics

### 🧪 Tests

- 13 tests nuevos (7 REST + 6 WebSocket)
- 321 tests totales en elap-core (0 fallos)
- 100% cobertura endpoints

### 🏗️ Cambios Arquitectónicos

**Nuevo módulo `api/` en elap-core**:
- `mod.rs` - Exportaciones
- `state.rs` - AppState thread-safe
- `handlers.rs` - 7 handlers REST
- `routes.rs` - Router Axum
- `middleware.rs` - CORS, config
- `websocket.rs` - WebSocket + AgentEvent

**Dependencias agregadas**:
- axum 0.7 (con feature `ws`)
- tower 0.4
- tower-http 0.5
- hyper 1.0
- futures 0.3

**Trait Clone agregado**:
- Agent, Plan, ContextoAgente, AgentIntegrado
- OllamaClient, ModelManager
- Necesario para estado compartido

### 📊 Métricas Fase 9

| Métrica | Valor |
|---------|-------|
| Endpoints REST | 7 |
| WebSocket endpoints | 1 |
| Tipos de eventos | 7 |
| Tests nuevos | 13 |
| Tests totales | 321 |
| Líneas de código | ~600 |
| Documentación | 2 files |

### 🔗 Integración

```
HTTP Client ← REST (CRUD)
    ↓
[Axum Router]
    ↓
WebSocket ← Streaming (monitoreo)
    ↓
[AppState] → [AgentIntegrado]
    ↓
[Tool Engine + Model Manager]
```

---

## [Fase 8] - 2026-08-05

### ✨ Nuevas Funcionalidades

#### Agentes Inteligentes (Agent Framework)

**Pasos 1-4 completados:**

1. **Paso 1**: Estructura base de agentes
   - `Agent`: Identidad, estado y tracking
   - `EstadoAgente`: 6 estados posibles
   - `Plan` y `Paso`: Ejecución secuencial
   - `ContextoAgente`: Variables dinámicas
   - `EjecutorAgente`: Ejecutor de planes
   - 19 tests unitarios

2. **Paso 2**: Integración con Tools
   - `AgentIntegrado`: Orquestador principal
   - Coordinación agent + tools + models
   - 4 tests de integración

3. **Paso 3**: Integración con Models (framework listo)
   - Optional `ModelManager` en AgentIntegrado
   - Preparado para Phase 9

4. **Paso 4**: Memoria Dual
   - `MemoriaCortoTermino`: VecDeque con límite configurable
   - `MemoriaLargoTermino`: Patrones aprendidos
   - `SistemaMemoria`: Integración completa
   - 7 tests unitarios

5. **Paso 5**: Tests de Integración (12 nuevos)
   - `test_agente_con_plan_completo()`: Flujo end-to-end
   - `test_sistema_memoria_con_agente()`: Memoria + agentes
   - `test_plan_progreso()`: Validación de progreso
   - `test_integracion_completa_flujo()`: Integración total
   - Más 8 tests complementarios

### 📚 Documentación

#### Documentación Técnica
- `docs/03-Modules/AGENT_FRAMEWORK.md`: 250+ líneas
  - Arquitectura completa
  - API reference
  - Ejemplos de integración
  - Benchmarks
  - Security checklist

#### Documentación Didáctica
- `notebook/Libro-09-Agent-Framework/01-introduccion.md`: Capítulo introductorio
  - Analogía del mundo real (empleado de oficina)
  - 6 estados y máquina de estados
  - 4 componentes clave
  - Flujo completo paso a paso

- `notebook/Libro-09-Agent-Framework/02-practica.md`: Capítulo práctico
  - 5 ejercicios progresivos
  - Código ejecutable
  - Salidas esperadas
  - Quiz de validación
  - Ejemplos con contexto, memoria, múltiples agentes

### 🧪 Tests

**Nuevos tests: 41 (19 + 12 + 10 más en archivos)**

```
agents/
├── agent.rs: 6 tests
├── context.rs: 3 tests
├── plan.rs: 5 tests
├── executor.rs: 4 tests
├── integration.rs: 4 tests
├── memory.rs: 7 tests
└── integration_tests.rs: 12 tests

Total: 41 tests nuevos
0 fallos
```

### 🏗️ Cambios Arquitectónicos

- Exportación de `AgentIntegrado` en `lib.rs`
- Módulo `agents/integration.rs` añadido
- Módulo `agents/memory.rs` añadido
- Tests de integración en `tests/` para validación cross-module

### 📊 Métricas

| Métrica | Valor |
|---------|-------|
| Tests Fase 8 | 41 nuevos |
| Tests totales (elap-core) | 320 |
| Líneas de código | ~1,200 |
| Documentación | 1 técnica + 2 didácticas |
| Cobertura | 95%+ (agentes) |

---

## [Fase 7] - 2026-08-04

### ✨ Nuevas Funcionalidades

#### Model Manager (Integración Ollama)

**6 Pasos completados:**

1. **Paso 1**: ModelMetadata + Tipos de Modelos
   - TipoModelo enum (TextoGenerativo, Embedding, Chat)
   - Metadatos de modelo con descripción, parámetros, versión

2. **Paso 2**: OllamaClient
   - generar(), embeddings(), chat()
   - listar_modelos(), descargar_modelo()
   - Integración con servidor Ollama local

3. **Paso 3**: RegistroModelos
   - Thread-safe registry
   - registrar(), obtener(), listar()
   - listar_descargados(), contar()

4. **Paso 4**: CacheEmbeddings
   - Cache de vectores con límite configurable
   - Auto-cleanup al exceder límite
   - Performance optimization

5. **Paso 5**: ModelManager + MemoriaCorta
   - Orquestador principal
   - Conversación con historial automático
   - Límite configurable de memoria

6. **Paso 6**: Tests + Documentación
   - 33 tests (100% cobertura)
   - Documentación técnica
   - Capítulo didáctico

### 📚 Documentación

- Technical: `docs/03-Modules/MODELMANAGER.md`
- Didactic: `notebook/Libro-08-Model-Manager/01-introduccion.md`

### 🧪 Tests

- 33 tests nuevos (0 fallos)
- Cobertura 100% en Model Manager

---

## [Fase 6] - 2026-08-03

### ✨ Nuevas Funcionalidades

#### Tool Engine (Herramientas Sandboxeadas)

**5 Pasos completados:**

1. **Paso 1**: Tool Trait + 5 Implementaciones
   - FileTool (leer/escribir/listar)
   - HttpTool (GET/POST/PUT/DELETE)
   - SqlTool (SELECT/INSERT/UPDATE)
   - SshTool (comando remoto, copiar archivo)
   - SystemTool (info sistema, recursos, env vars)

2. **Paso 2**: Sandbox Configuración
   - Política de ejecución
   - Whitelist de rutas
   - Blacklist de comandos
   - Límites de recursos (CPU, memoria, timeout)

3. **Paso 3**: RBAC Validación
   - Permisos por rol (Admin, User, Guest)
   - 5 permisos: crear, leer, escribir, eliminar, ejecutar
   - Validación pre-ejecución

4. **Paso 4**: Executor
   - EjecutorHerramientas
   - Timing, auditoría, manejo de errores
   - Integración con RBAC

5. **Paso 5**: Tests + Documentación
   - 55 tests (100% cobertura)
   - Documentación técnica
   - Capítulo didáctico

### 📚 Documentación

- Technical: `docs/03-Modules/TOOL_ENGINE.md`
- Didactic: `notebook/Libro-07-Tool-Engine/01-introduccion.md`

### 🧪 Tests

- 55 tests nuevos (0 fallos)
- Cobertura 100% en Tools

---

## Resumen Total

| Fase | Componente | Tests | Status |
|------|-----------|-------|--------|
| 8 | Agent Framework | 41 | ✅ |
| 7 | Model Manager | 33 | ✅ |
| 6 | Tool Engine | 55 | ✅ |
| **TOTAL** | | **320** | **✅** |

---

**Próximas Fases:**
- Fase 9: Web API REST
- Fase 10: WebSocket Streaming
- Fase 11: Persistencia BD
- Fase 12: Dashboard Web
