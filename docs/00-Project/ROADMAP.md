# Roadmap Técnico de ELAP

**Versión**: 1.2  
**Última actualización**: 2026-08-07  
**Duración estimada**: 17 semanas + 4 fases de Document Engine

---

## 📊 Vista general

```
Fase 0: Fundacionales              ██████ ✅
Fase 1: Core Runtime               ██████ ✅
Fase 2: Desktop Runtime            ██████ ✅
Fase 3: Plugin Runtime             ██████ ✅
Fase 4-8: Foundation               ██████ ✅
Fase 9: Python AI Runtime          ██████ ✅
Fase 10: Auth (JWT + RBAC)         ██████ ✅
Fase 11: Persistence (SQLite+PG)   ██████ ✅
Fase 12: Dashboard CLI             ██████ ✅
Fase 13: LangGraph Agent           ██████ ✅
Fase 14: RAG (Embeddings+VectorDB) ██████ ✅
Fase 15: Qdrant Persistence        ██████ ✅
Fase 16: Multi-agent Orchestrator  ██████ ✅
Fase 17: Tauri + React Dashboard   ██████ ✅
Fase 18: Deployment (Docker+K8s)   ██████ ✅
Fase 19: Advanced RAG              ██████ ✅
Fase 20: Integration Testing       ██████ ✅
Fase 21: Role-Model Mapping        ██████ ✅
Fase 22: gRPC Gateway              ██████ ✅
Fase 23: Real LLM Integration      ██████ ✅
Fase 24: Multi-agent Orchestration ██████ ✅
Fase 25: Streaming Responses       ██████ ✅
```

**HITO**: v1.4.0 Production Ready (25/25 fases) 🚀

---

## 🎯 Fase 0: Fundacionales

**Estado**: ✅ Completada  
**Semana**: 1  

### Objetivos

- Inicializar repositorio Git
- Crear estructura de carpetas completa
- Configurar workspace Rust y Python
- Establecer estándares de código
- Generar documentación base

### Deliverables

- [x] Git inicializado
- [x] Carpetas creadas (/docs, /notebook, /crates, /python)
- [x] Cargo.toml (workspace) configurado
- [x] pyproject.toml configurado
- [x] CLAUDE.md completado
- [x] README.md principal
- [x] .gitignore completo
- [x] Estructura de documentación lista
- [ ] CI/CD workflows (GitHub Actions)
- [ ] Primer commit
- [ ] Validación de compilación

### Entregables técnicos

**Código**:
- CoreEngine base (Rust)
- DesktopRuntime base (Rust)
- CLI scaffold (Rust)
- AIRuntime base (Python)

**Documentación**:
- /docs/00-Project/README.md
- /docs/00-Project/ROADMAP.md
- /docs/00-Project/CHANGELOG.md
- /docs/00-Project/TODO.md
- /docs/00-Project/TREE.md
- /docs/01-Architecture/ARCHITECTURE.md
- /docs/01-Architecture/DECISIONS.md
- /docs/02-Development/CONVENTIONS.md

---

## 🔧 Fase 1: Core Runtime

**Estado**: ✅ Completada  
**Semana**: 2  

### Objetivos

Implementar el corazón de la plataforma: task scheduling, process management, configuration, error handling, RBAC.

### Entregables

- ✅ Task scheduler con Tokio (BinaryHeap, 23 tests)
- ✅ Process spawner y manager (15 tests)
- ✅ Config loader YAML (8 tests)
- ✅ Error handling completo (2 tests)
- ✅ RBAC y Auditoría (26 tests)
- ✅ Tests: 75 tests totales, >85% cobertura

### Documentación

- ✅ SCHEDULER.md, PROCESOS.md, CONFIGURACION.md, ERROR_HANDLING.md, SEGURIDAD.md
- ✅ Libro 02 (6 capítulos completados: Intro, Scheduler, Procesos, Config, Errores, RBAC)
- ✅ CHANGELOG.md actualizado

---

## 🖥️ Fase 2: Desktop Runtime

**Estado**: ✅ Completada (Pasos 1-5)  
**Semana**: 3  

### Objetivos

Implementar capa de interfaz desktop con IPC bridge y UI components.

### Entregables

- ✅ Estructura Desktop Runtime (Paso 1)
- ✅ IPC Bridge con 3 comandos (Paso 2)
- ✅ UI Components serializables (Paso 3)
- ✅ Integración con MotorCentral real (Paso 4)
- ✅ 4 tests de integración pasando (Paso 5)
- ✅ Documentación técnica (DESKTOP.md)
- ✅ Capítulo 1 del Libro 03

### Próximo: Paso 6
- Implementación de frontend React/TypeScript
- Conexión real de Tauri bridge

---

## 🔌 Fase 3: Plugin Runtime

**Estado**: ✅ Completada (Pasos 1-6)  
**Semana**: 4  

### Objetivos

Sistema extensible para cargar y ejecutar plugins de terceros de forma segura.

### Entregables

- ✅ Plugin trait (6 métodos obligatorios)
- ✅ PluginMetadata con serialización
- ✅ PluginLoader con validación y hash SHA256
- ✅ RegistroPlugins thread-safe con búsquedas
- ✅ PluginSandbox con límites de recursos
- ✅ 35 tests (110 totales en elap-core)
- ✅ Documentación técnica (PLUGIN.md)
- ✅ Capítulo 1 del Libro 04

### Próximo: Paso 7+
- Integración con MotorCentral
- Plugin executor real
- Carga dinámica de símbolos

---

## ⚙️ Fase 4: Configuration Manager

**Estado**: ⏳ Por hacer  
**Semana**: 5  

### Objetivos

Sistema de configuración persistente y versionado.

### Entregables

- Config file format (TOML)
- Config validation
- Config hot-reload
- Environment override support
- Tests

### Documentación

- Configuration Architecture
- Libro 05 para NotebookLM

---

## 📝 Fase 5: Logging

**Estado**: ⏳ Por hacer  
**Semana**: 5  

### Objetivos

Sistema de logging unificado, local-only, sin salida a internet.

### Entregables

- Tracing setup (Rust)
- Structured logging
- Log rotation
- Database persistence
- Audit trail
- Tests

### Documentación

- Logging Architecture
- Libro 05 para NotebookLM

---

## ❌ Fase 5: Error Handling

**Estado**: ⏳ Por hacer  
**Semana**: 6  

### Objetivos

Framework de error handling robusto y consistente.

### Entregables

- Custom error types (Rust + Python)
- Error propagation
- Error recovery
- Error logging
- User-facing error messages
- Tests

### Documentación

- Error Handling Guide
- Libro 06 para NotebookLM

---

## 🔌 Fase 6: Plugin Runtime

**Estado**: ⏳ Por hacer  
**Semana**: 7  

### Objetivos

Framework para cargar y ejecutar plugins de terceros de forma segura.

### Entregables

- Plugin loader (dynamic library loading)
- Plugin manifest format
- Permission model
- Sandbox (basic isolation)
- Plugin registry
- Tests

### Documentación

- Plugin Architecture
- Plugin SDK specification
- Libro 07 para NotebookLM

---

## 🛠️ Fase 7: Tool Engine

**Estado**: ⏳ Por hacer  
**Semana**: 8  

### Objetivos

Motor de herramientas: registro, ejecución segura, permiso validado.

### Entregables

- Tool registry
- Permission validation (RBAC)
- Tool executor (Rust)
- Tool sandbox
- Built-in tools (files, HTTP, SSH, SQL)
- Tests

### Documentación

- Tool Engine Architecture
- Libro 08 para NotebookLM

---

## 🤖 Fase 8: Model Manager

**Estado**: ⏳ Por hacer  
**Semana**: 9  

### Objetivos

Gestor de modelos de IA: descarga, carga, routing, GPU detection.

### Entregables

- Model registry
- Model downloader (from HuggingFace, Ollama)
- GPU detection (NVIDIA CUDA)
- Model loader
- Routing por agente
- Quantization support (GGUF)
- Tests

### Documentación

- Model Architecture
- Libro 09 para NotebookLM

---

## 🧠 Fase 9: Python AI Runtime

**Estado**: ⏳ Por hacer  
**Semana**: 10  

### Objetivos

Runtime de IA en Python: LangGraph, LLM inference, herramientas.

### Entregables

- gRPC server (Python)
- LangGraph integration
- LLM inference (Ollama/llama.cpp/Transformers)
- Tool execution
- Streaming responses
- Tests

### Documentación

- AI Runtime Architecture
- Libro 10 para NotebookLM

---

## 💾 Fase 10: Memory Manager

**Estado**: ⏳ Por hacer  
**Semana**: 11  

### Objetivos

Sistema de memoria: corto plazo, largo plazo, RAG, embeddings.

### Entregables

- Short-term memory (conversation history)
- Long-term memory (vector DB)
- Embedding generation
- RAG (Retrieval-Augmented Generation)
- Vector DB integration (Qdrant/ChromaDB)
- Tests

### Documentación

- Memory Architecture
- RAG Implementation
- Libro 11 para NotebookLM

---

## 🔗 Fase 11: Workflow Engine

**Estado**: ⏳ Por hacer  
**Semana**: 12  

### Objetivos

Orquestación de workflows: encadenamiento de tareas, delegación entre agentes.

### Entregables

- Workflow definition format
- Workflow executor
- State machine
- Agent-to-agent communication
- Error recovery
- Tests

### Documentación

- Workflow Architecture
- Libro 12 para NotebookLM

---

## 👥 Fase 12: Agent Runtime

**Estado**: ⏳ Por hacer  
**Semana**: 13  

### Objetivos

Runtime de agentes: creación, configuración, ejecución especializada por rol.

### Entregables

- Agent registry
- Agent templates (Sales, HR, Accounting, IT, Legal, etc.)
- Agent lifecycle management
- Conversation management
- Handoff entre agentes
- Tests

### Documentación

- Agent Architecture
- Agent Templates
- Libro 13 para NotebookLM

---

## 🎨 Fase 13: Desktop GUI

**Estado**: ⏳ Por hacer  
**Semana**: 14  

### Objetivos

Interfaz gráfica de usuario desktop profesional.

### Entregables

- Dashboard (estado de agentes, hardware)
- Agent chat interface
- Configuration UI
- Permission/RBAC management UI
- Model management UI
- Logs viewer
- Tests

### Documentación

- GUI Architecture
- UI Component Library
- Libro 14 para NotebookLM

---

## 📦 Fase 14: Installer

**Estado**: ⏳ Por hacer  
**Semana**: 15  

### Objetivos

Instalador profesional para windows/Linux.

### Entregables

- Instalador ejecutable (Windows/Linux)
- Post-install setup
- Database initialization
- First-run wizard
- Uninstaller

### Documentación

- Installation Guide
- Admin Manual (partial)
- Libro 15 para NotebookLM

---

## 🔄 Fase 15: Updater

**Estado**: ⏳ Por hacer  
**Semana**: 16  

### Objetivos

Sistema de actualización automática y segura.

### Entregables

- Update checker
- Signed binary verification
- Delta updates
- Rollback capability
- Background update service

### Documentación

- Update Architecture
- Deployment Guide
- Libro 16 para NotebookLM

---

## 🧪 Fase 16: Testing

**Estado**: ⏳ Por hacer  
**Semana**: 17  

### Objetivos

Suite de tests exhaustiva: unit, integration, end-to-end.

### Entregables

- Unit tests completos (>90% Rust, >80% Python)
- Integration tests
- End-to-end tests
- Performance benchmarks
- Load testing

### Documentación

- Testing Strategy
- Test Report
- Libro 17 para NotebookLM

---

## 📦 Fase 17: Packaging

**Estado**: ⏳ Por hacer  
**Semana**: 18  

### Objetivos

Empaquetamiento final: binarios, documentación, distribución.

### Entregables

- Binary releases (Windows/Linux)
- Docker image (optional)
- Documentation package
- License and legal files
- Release notes
- Enterprise Guide

### Documentación

- Deployment Guide (final)
- Admin Manual (final)
- User Manual
- Libro 18 para NotebookLM (Enterprise Guide)

---

## 📚 Libros para NotebookLM

Al final del proyecto, tendremos **18 libros** completos para estudio:

1. ✅ Libro 01 - Introducción (pendiente Cap 4, 5)
2. ✅ Libro 02 - Core Runtime (Fase 1)
3. ✅ Libro 03 - Desktop Runtime (Fase 2)
4. ✅ Libro 04 - Plugin Runtime (Fase 3)
5. ⏳ Libro 05 - Configuration Manager (Fase 4)
6. ⏳ Libro 06 - Logging (Fase 5)
7. ⏳ Libro 07 - Error Handling (Fase 6)
8. ⏳ Libro 08 - Tool Engine (Fase 7)
9. ⏳ Libro 09 - Model Manager (Fase 8)
10. ⏳ Libro 10 - Python AI Runtime (Fase 9)
11. ⏳ Libro 11 - Memory Manager (Fase 10)
12. ⏳ Libro 12 - Workflow Engine (Fase 11)
13. ⏳ Libro 13 - Agent Runtime (Fase 12)
14. ⏳ Libro 14 - Desktop GUI (Fase 13)
15. ⏳ Libro 15 - Installer (Fase 14)
16. ⏳ Libro 16 - Updater (Fase 15)
17. ⏳ Libro 17 - Testing (Fase 16)
18. ⏳ Libro 18 - Packaging (Fase 17)

---

## 📋 Tracking

| Fase | Estado | Documento | Libro |
|------|--------|-----------|-------|
| 0 | ✅ Completada | README.md | - |
| 1 | ✅ Completada | ARCHITECTURE.md | Libro 02 |
| 2 | ✅ Completada | DESKTOP.md | Libro 03 |
| 3 | ✅ Completada | PLUGIN.md | Libro 04 |
| 4a | ✅ Completada | DOCUMENT_ENGINE.md | - |
| 4b | ✅ Completada | KNOWLEDGE_PACK.md | - |
| 4c | ✅ Completada | FASE_4C_COMPLETADA.md | - |
| 4d | ⏳ Próxima | DOCUMENTS_TAB.md | - |
| 5+ | ⏳ Por hacer | - | Libro 06+ |

---

## 📌 Fase 4: Document Engine Suite

**Objetivo General:** Automatizar generación de documentos profesionales con IA

### 4a - Document Engine Core ✅
- DocumentEngine base
- Generators (Word, PDF, Excel, PowerPoint, HTML)
- Andina Foods theme + professional theme
- Templates (contract, invoice, report)

### 4b - Knowledge Pack Generator ✅
- Company setup wizard
- Auto-generate 15 template documents
- RAG indexing
- Ready for agents

### 4c - Document Engine Agent Integration ✅ (2026-08-08)
- HRAgent para contratos laborales
- FinanceAgent para facturas/reportes
- REST API (Python ↔ Rust)
- Descarga desde chat (botones azules)
- **Status:** Producción-ready

### 4d - Documents Tab (Próxima)
- Listar documentos generados
- Filtrar por tipo/empleado
- Metadatos (fecha, tamaño)
- Regenerar/eliminar/descargar
- **Estimado:** 2-3 horas

---

**Próximo**: Fase 4d - Documents Tab Management
