# CHANGELOG

Formato basado en [Keep a Changelog](https://keepachangelog.com/).

---

## [0.3.0-alpha] - 2026-08-05

### Fase 1 - Pasos 3-6: Core Runtime (Completo)

#### Agregado

**Paso 3: Gestor de Configuración**
- Módulo `config` completo con `configuracion.rs`
  - Struct Configuracion con modo, versión, puerto, logging
  - Serialización YAML con serde_yaml
  - Validación de parámetros críticos
  - 8 tests de configuración
- Documentación técnica: `docs/03-Modules/CONFIGURACION.md`
- Capítulo 4 del Libro 02

**Paso 4: Manejo de Errores**
- Módulo `error` con tipos personalizados
  - Enum ElapError (Config, Io, Validacion, Proceso, Otro)
  - Alias ResultadoElap<T> para Result<T, ElapError>
  - Implementación Display y Error traits
  - 2 tests de error handling
- Documentación técnica: `docs/03-Modules/ERROR_HANDLING.md`
- Capítulo 5 del Libro 02

**Paso 5: Gestor de Seguridad (RBAC)**
- Módulo `security` completo con:
  - `rol.rs`: Enum Rol (Admin, Usuario, Invitado, Agente)
  - `permisos.rs`: Enum Permiso (5 permisos del sistema)
  - `rbac.rs`: GestorRbac con validación de permisos
  - `auditor.rs`: RegistroAuditoria + AuditorRbac (26 tests)
- Integración en MotorCentral con getters .rbac() y .auditor()
- Documentación técnica: `docs/03-Modules/SEGURIDAD.md`
- Capítulo 6 del Libro 02

**Paso 6: Integración Final**
- Test E2E de flujo completo (RBAC + Auditoría)
- MotorCentral actualizado con 4 tests de integración
- Total: 75 tests pasando en elap-core

#### Modificado

- `crates/elap-core/src/lib.rs`: Agregados módulos config, error, security
- `crates/elap-core/src/core.rs`: Integración de RBAC y Auditoría
- `notebook/Libro-02-Core-Runtime/README.md`: 6/9 capítulos completados

#### Seguridad

- RBAC con tablas de permisos por rol (administrador, usuario, invitado, agente)
- Auditoría con timestamp de cada acción (exitosa o denegada)
- Validación explícita de permisos antes de operaciones sensibles
- Sin panics: todo devuelve Result con error handling
- Thread-safe con Mutex para AuditorRbac

#### Documentación

- 3 módulos documentados técnicamente (CONFIG, ERROR, SECURITY)
- 3 capítulos didácticos para NotebookLM (Caps 4, 5, 6)
- Analogías pedagógicas explicadas paso a paso
- Casos de uso realistas en todos los capítulos

#### Tests

- **Configuración**: 8 tests (tipos, validación, default)
- **Errores**: 2 tests (Display, From<std::io::Error>)
- **RBAC**: 26 tests (roles, permisos, auditoría)
- **Integración**: 4 tests (creación, ciclo vida, getters, E2E)
- **Total Core**: 75 tests pasando ✅

---

## [0.2.0-alpha] - 2026-08-04

### Fase 1 - Paso 2: Gestor de Procesos

#### Agregado

- Módulo `procesos` completo en `crates/elap-core/src/procesos/`
  - `error.rs`: Tipos de error específicos de procesos
  - `proceso.rs`: Definición de Proceso, IdProceso, EstadoProceso
  - `spawner.rs`: Creación y ejecución de procesos del SO
  - `ejecutor.rs`: GestorProcesos API pública (thread-safe)
  - `mod.rs`: Re-exports públicos
- 15 tests nuevos en módulo procesos (todos pasando)
  - 4 tests en proceso.rs
  - 4 tests en spawner.rs
  - 8 tests en ejecutor.rs
- Documentación técnica: `docs/03-Modules/PROCESOS.md`
- Capítulo 3 del Libro 02: `notebook/Libro-02-Core-Runtime/03-gestor-procesos.md`
- Mejorado `.gitignore` con exclusiones para:
  - Tauri (src-tauri/target/, src-tauri/dist/)
  - Node (node_modules/, package-lock.json, yarn.lock)
  - Ollama (.ollama/, ollama_cache/)
  - Backups (*.bak, *.backup)

#### Modificado

- `crates/elap-core/src/lib.rs`: Agregado módulo procesos
- `docs/00-Project/CHANGELOG.md`: Actualizado a español
- `README.md`: Actualizado con email personal y GitHub correcto

#### Seguridad

- GestorProcesos usa Arc<Mutex<>> para thread-safety
- Procesos ejecutados en aislamiento del SO
- Sin panics: todos los métodos devuelven Result/Option
- Validación de IDs antes de ejecutar

#### Documentación

- Documentación técnica profesional (PROCESOS.md)
- Capítulo didáctico para NotebookLM (03-gestor-procesos.md)
- Analogías pedagógicas sin tecnicismos
- 15 tests implementados y documentados

---

## [0.1.0-alpha] - 2026-08-04

### Fase 0: Fundacionales

#### Agregado

- Repositorio Git inicializado con configuración de usuario
- Estructura de carpetas completa
  - `crates/` para workspace Rust (elap-core, elap-desktop, elap-cli)
  - `python/` para Motor de IA
  - `docs/` con 10 subdirectorios para documentación
  - `notebook/` para materiales de estudio NotebookLM
  - `tooling/` para CI/CD y scripts
  - `.github/workflows/` para GitHub Actions
- Configuración Cargo.toml workspace con dependencias compartidas
  - Runtime async Tokio
  - Framework gRPC Tonic
  - Logging con Tracing
  - Serialización con Serde
  - Criptografía con Ring
- pyproject.toml para package Python
  - Dependencias LangChain/LangGraph
  - Transformers y PyTorch
  - Bases de datos vectoriales (Qdrant, ChromaDB)
  - Ollama para inferencia de modelos
- Módulo Planificador de Tareas (Scheduler)
  - IdTarea: identificador único (UUID)
  - EstadoTarea: Pendiente, Ejecutando, Completada, Fallo
  - PrioridadTarea: Alta, Normal, Baja
  - Tarea: metadata completa
  - ColaTareas: BinaryHeap con ordenamiento por prioridad
  - PlanificadorTareas: API pública (thread-safe, Arc<Mutex<>>)
- 23 tests del Planificador (todos pasando)
  - 5 tests en tarea.rs
  - 6 tests en cola.rs
  - 5 tests en ejecutor.rs
  - 2 tests en core.rs
  - 3 tests en config.rs
  - 2 tests en error.rs
- Archivos de documentación principales
  - README.md (en español, visión general del proyecto)
  - CLAUDE.md (estándares de ingeniería)
  - .gitignore (Rust + Python + IDE + secretos)
- Código Rust (elap-core)
  - Struct MotorCentral con gestión de ciclo de vida
  - Type ElapError con variantes
  - Struct Config con ConfigBaseDatos y ConfigSeguridad
  - Tests iniciales (objetivo >80% cobertura)
  - Módulo scheduler completamente implementado
- Código Rust (elap-desktop)
  - Wrapper DesktopRuntime
  - Ciclo de vida async básico
- Código Rust (elap-cli)
  - CLI con clap
  - Comandos: start, version, health, help
  - Logging con tracing
- Código Python (elap-ai)
  - Clase AIRuntime base
  - Ciclo de vida async (iniciar/detener)
  - Método health_check
  - Placeholder process_query
- Estructura de documentación
  - /docs/00-Project/ (README, ROADMAP, CHANGELOG, TODO, TREE)
  - /docs/01-Architecture/ (esqueleto)
  - /docs/02-Development/ (esqueleto)
  - /docs/03-Modules/ hasta /10-NotebookLM/ (listas para contenido)
  - /notebook/Libro-01-Introduccion/ (esqueleto)
- Documentación técnica del Planificador: `docs/03-Modules/SCHEDULER.md`
- Capítulo 1 del Libro 02: `notebook/Libro-02-Core-Runtime/01-introduccion.md`
- Capítulo 2 del Libro 02: `notebook/Libro-02-Core-Runtime/02-planificador-tareas.md`

#### Modificado

- Nada (creación inicial)

#### Deprecado

- Nada

#### Eliminado

- Nada

#### Corregido

- Código y documentación traducidos completamente al español
- Nombres de funciones del Motor Central: CoreEngine → MotorCentral
- Métodos: start/stop → iniciar/detener
- BinaryHeap: corregido ordenamiento para que Alta prioridad salga primero

#### Seguridad

- .gitignore configurado para prevenir:
  - Artefactos de build Rust (/target/)
  - Cache de Python (__pycache__/)
  - Archivos de entorno (.env, .envrc)
  - Claves privadas y secretos
  - Archivos de base de datos (*.db, *.sqlite)
  - Archivos de modelos (*.gguf, *.safetensors) — pueden agregarse con git-lfs
- Planificador: Arc<Mutex<>> para acceso thread-safe
- Sin unwrap() en código de biblioteca

#### Documentación

- README.md: Visión general del proyecto, inicio rápido, estructura
- CLAUDE.md: Convenciones de código, principios de arquitectura, checklist de seguridad
- ROADMAP.md: Roadmap de 17 fases con entregables
- docs/00-Project/README.md: Estado de Fase 0
- docs/01-Architecture/ARCHITECTURE.md: Diseño del sistema (4 libros técnicos)
- /notebook/ estructura creada para materiales de estudio futuros
- Estructura /docs con documentación didáctica

---

## Sin publicar (Próximo)

### Fase 1 - Paso 3: Gestor de Configuración

- [ ] Módulo config con soporte YAML
- [ ] Carga/guardado de configuración
- [ ] Validación de esquema
- [ ] Variables de entorno
- [ ] Tests (>80% cobertura)
- [ ] Documentación técnica
- [ ] Capítulo 4 del Libro 02

### Fase 1 - Paso 4+

- [ ] Motor de Plugins
- [ ] Gateway gRPC (Rust ↔ Python)
- [ ] Gestor de permisos RBAC
- [ ] Tests completos (>80% cobertura)
- [ ] Documentación de arquitectura
- [ ] Libros de estudio para NotebookLM

---

## Notas

- **Lenguaje**: Español para código, documentación y commits
- **Versionamiento**: Semantic versioning (MAYOR.MENOR.PARCHE)
- **Releases**: Una por fase completada
- **Documentación Viva**: Todo cambio de código viene con documentación

---

**Creado**: 2026-08-04  
**Última actualización**: 2026-08-04
