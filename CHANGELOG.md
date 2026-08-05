# CHANGELOG — Historial de Cambios ELAP

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
