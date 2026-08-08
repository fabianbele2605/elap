# 📂 TREE.md — Estructura del Proyecto ELAP

**Versión**: 1.0  
**Última actualización**: 2026-08-08  
**Propósito**: Mapa completo del repositorio para navegación rápida

---

## Estructura raíz

```
agenteC/
├── Cargo.toml                    # Workspace Rust
├── Cargo.lock
├── CLAUDE.md                     # Estándares y decisiones de desarrollo ✅
├── CHANGELOG.md                  # Historial de cambios
├── TREE.md                       # Este archivo
├── README.md                     # Bienvenida y visión general
├── .gitignore
│
├── docs/                         # 📚 Documentación técnica
│   ├── 00-Project/
│   │   ├── README.md            # Intro al proyecto
│   │   ├── ROADMAP.md           # Fases y timeline ✅
│   │   └── STATUS.md            # Estado actual
│   │
│   ├── 01-Architecture/
│   │   ├── ARCHITECTURE.md      # Diseño del sistema
│   │   ├── DECISIONS.md         # Por qué cada decisión
│   │   ├── API.md               # Endpoints REST
│   │   └── SECURITY.md          # Estrategia de seguridad
│   │
│   ├── 02-Frontend/
│   │   ├── COMPONENTS.md        # Catálogo de componentes React
│   │   ├── STATE.md             # Gestión de estado
│   │   └── STYLING.md           # Tailwind + Responsive
│   │
│   ├── 03-Backend/
│   │   ├── RUST_CORE.md         # Núcleo Rust
│   │   ├── PYTHON_AI.md         # Runtime Python/IA
│   │   ├── GRPC.md              # Protocolo IPC
│   │   └── DATABASE.md          # SQLite/PostgreSQL
│   │
│   └── 04-Document-Engine/
│       ├── TEMPLATES.md         # Plantillas docx
│       ├── KNOWLEDGE_PACK.md    # RAG/Knowledge
│       └── REST_API.md          # Python REST API
│
├── notebook/                     # 📖 Libros para NotebookLM
│   ├── libro-01-fundaciones.md  # Conceptos base
│   ├── libro-02-rust-core.md    # Core Runtime
│   ├── libro-03-python-ai.md    # IA Runtime
│   ├── libro-04-grpc.md         # Comunicación IPC
│   ├── libro-05-database.md     # Persistencia
│   ├── libro-06-document-engine.md  # Document Suite ✅
│   └── ...
│
├── crates/                       # 🦀 Código Rust
│   │
│   ├── elap-core/               # ⭐ Núcleo principal
│   │   ├── Cargo.toml
│   │   ├── build.rs             # Compilación custom
│   │   └── src/
│   │       ├── lib.rs           # Public API
│   │       ├── error.rs         # Tipos de error
│   │       │
│   │       ├── core.rs          # Engine principal
│   │       ├── agents/          # Agent orchestration
│   │       │   ├── mod.rs
│   │       │   ├── agent.rs     # Agent trait
│   │       │   ├── executor.rs  # Ejecución
│   │       │   ├── context.rs   # Contexto
│   │       │   ├── memory.rs    # Memoria
│   │       │   ├── plan.rs      # Planificación
│   │       │   └── errors.rs
│   │       │
│   │       ├── api/             # HTTP REST API
│   │       │   ├── mod.rs
│   │       │   ├── routes.rs    # Definición de rutas
│   │       │   ├── handlers.rs  # Request handlers
│   │       │   ├── middleware.rs
│   │       │   ├── auth.rs      # Autenticación
│   │       │   ├── rbac.rs      # Control de acceso
│   │       │   ├── state.rs     # Application state
│   │       │   └── websocket.rs # WebSocket support
│   │       │
│   │       ├── security/        # Seguridad + RBAC
│   │       │   ├── mod.rs
│   │       │   ├── rbac.rs      # Control de acceso
│   │       │   ├── rol.rs       # Roles
│   │       │   ├── permisos.rs  # Permisos
│   │       │   └── auditor.rs   # Auditoría
│   │       │
│   │       ├── tools/           # Tool execution
│   │       │   ├── mod.rs
│   │       │   ├── registry.rs  # Registro de tools
│   │       │   ├── executor.rs  # Ejecución segura
│   │       │   ├── sandbox.rs   # Aislamiento
│   │       │   ├── file_tool.rs
│   │       │   ├── http_tool.rs
│   │       │   ├── sql_tool.rs
│   │       │   ├── ssh_tool.rs
│   │       │   ├── system_tool.rs
│   │       │   └── web_search.rs
│   │       │
│   │       ├── db/              # Database layer
│   │       │   ├── mod.rs
│   │       │   ├── connection.rs
│   │       │   ├── schema.rs
│   │       │   └── agent_repo.rs
│   │       │
│   │       ├── models/          # Model management
│   │       │   ├── mod.rs
│   │       │   ├── manager.rs
│   │       │   ├── registry.rs
│   │       │   ├── ollama_client.rs
│   │       │   ├── cache.rs
│   │       │   └── model_metadata.rs
│   │       │
│   │       ├── scheduler/       # Task scheduling
│   │       │   ├── mod.rs
│   │       │   ├── task.rs
│   │       │   ├── queue.rs
│   │       │   └── executor.rs
│   │       │
│   │       ├── plugin/          # Plugin system
│   │       │   ├── mod.rs
│   │       │   ├── plugin_trait.rs
│   │       │   ├── loader.rs
│   │       │   ├── registry.rs
│   │       │   ├── metadata.rs
│   │       │   ├── sandbox.rs
│   │       │   └── research_plugin.rs
│   │       │
│   │       ├── configuration/   # Config management
│   │       │   ├── mod.rs
│   │       │   ├── loader.rs
│   │       │   ├── validator.rs
│   │       │   ├── schema.rs
│   │       │   ├── config_struct.rs
│   │       │   └── hotreload.rs
│   │       │
│   │       ├── logging_v2/      # Advanced logging
│   │       │   ├── mod.rs
│   │       │   ├── logger.rs
│   │       │   ├── events.rs
│   │       │   ├── filters.rs
│   │       │   ├── outputs.rs
│   │       │   └── rotation.rs
│   │       │
│   │       ├── procesos/        # Process management
│   │       │   ├── mod.rs
│   │       │   ├── proceso.rs
│   │       │   ├── spawner.rs
│   │       │   ├── ejecutor.rs
│   │       │   └── error.rs
│   │       │
│   │       ├── grpc_client.rs   # gRPC client to Python
│   │       ├── agent_orchestrator.rs
│   │       └── agent_model_mapper.rs
│   │
│   ├── elap-cli/                # 🖥️ CLI tool
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── main.rs
│   │       ├── client/
│   │       │   ├── http_client.rs
│   │       │   ├── ws_client.rs
│   │       │   └── mod.rs
│   │       └── commands/
│   │           ├── agent.rs
│   │           ├── agents.rs
│   │           └── mod.rs
│   │
│   └── elap-desktop/            # 🎨 Tauri Desktop App
│       ├── Cargo.toml
│       ├── build.rs
│       └── src/
│           └── main.rs
│
├── python/                       # 🐍 Código Python
│   ├── pyproject.toml           # Config Python
│   ├── setup.py
│   ├── requirements.txt
│   ├── README.md
│   │
│   └── src/elap_ai/
│       ├── __init__.py
│       ├── main.py              # Entry point
│       ├── config.py            # Configuración
│       ├── errors.py            # Excepciones
│       │
│       ├── agent_runtime/       # LangGraph agents
│       │   ├── __init__.py
│       │   ├── agent.py         # Base agent class
│       │   └── orchestrator.py
│       │
│       ├── agents/              # Agentes específicos
│       │   ├── __init__.py
│       │   ├── example_integration.py
│       │   ├── finance_agent.py
│       │   └── hr_agent.py
│       │
│       ├── memory/              # RAG + Memory
│       │   ├── __init__.py
│       │   ├── short_term.py
│       │   └── long_term.py
│       │
│       ├── tools/               # Tool execution
│       │   ├── __init__.py
│       │   ├── registry.py
│       │   └── executor.py
│       │
│       ├── document_engine/     # Document generation
│       │   ├── __init__.py
│       │   ├── generator.py
│       │   ├── templates.py
│       │   └── rag_engine.py
│       │
│       ├── proto/               # gRPC proto definitions
│       │   ├── __init__.py
│       │   ├── agent_pb2.py
│       │   └── agent_pb2_grpc.py
│       │
│       ├── grpc_server.py       # gRPC server
│       ├── rest_server.py       # Flask/aiohttp REST API ✅
│       │
│       └── tests/
│           ├── __init__.py
│           ├── test_agents.py
│           └── test_tools.py
│
├── web/                          # ⚛️ Frontend React/Tauri
│   ├── index.html               # Entry point
│   ├── package.json             # NPM deps
│   ├── vite.config.ts           # Vite build
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   │
│   ├── src/
│   │   ├── main.tsx             # React root
│   │   ├── App.tsx              # Main component ✅
│   │   ├── types.ts             # TypeScript interfaces
│   │   ├── index.css            # Global styles
│   │   │
│   │   ├── components/
│   │   │   ├── WindowHeader.tsx    # Menu bar ✅
│   │   │   ├── LeftSidebar.tsx     # Agent list ✅
│   │   │   ├── StatusBar.tsx       # Bottom status ✅
│   │   │   ├── ChatArea.tsx
│   │   │   ├── MainChat.tsx
│   │   │   ├── KnowledgePackWizard.tsx
│   │   │   ├── DocumentsGeneratedDashboard.tsx
│   │   │   │
│   │   │   └── tabs/
│   │   │       ├── ChatTab.tsx          # Chat ✅
│   │   │       ├── DashboardTab.tsx     # Real-time metrics ✅
│   │   │       ├── HistoryTab.tsx       # History from API ✅
│   │   │       ├── KnowledgeTab.tsx     # RAG sources ✅
│   │   │       ├── ToolsTab.tsx         # Tools catalog ✅
│   │   │       └── DocumentsTab.tsx     # Documents ✅
│   │   │
│   │   ├── hooks/
│   │   │   └── useChat.ts
│   │   │
│   │   ├── utils/
│   │   │   └── formatting.ts
│   │   │
│   │   └── styles/
│   │       └── tailwind.css
│   │
│   └── dist/                    # Build output
│
└── scripts/                      # 🛠️ Utilidades
    ├── build.sh
    ├── test.sh
    ├── dev.sh
    └── deploy.sh
```

---

## 📊 Estadísticas

| Componente | Estado | LOC | Tests | Docs |
|-----------|--------|-----|-------|------|
| **Rust Core** | ✅ 80% | ~8,500 | 200+ | 🟢 Alta |
| **Python AI** | ✅ 70% | ~2,800 | 100+ | 🟢 Alta |
| **Frontend** | ✅ 95% | ~4,200 | 50+ | 🟢 Media |
| **gRPC** | ✅ 90% | ~1,200 | 30+ | 🟡 Media |
| **Database** | ✅ 85% | ~800 | 40+ | 🟢 Alta |
| **Security** | ✅ 80% | ~1,500 | 60+ | 🟢 Alta |
| **Document Engine** | ✅ 100% | ~600 | 80+ | 🟢 Alta |
| **Total** | **85%** | **~19,600** | **560+** | **🟢 Alta** |

---

## 🎯 Navegación rápida

### Por funcionalidad

| Necesito... | Archivo |
|------------|---------|
| Crear un nuevo agente | [agents/agent.rs](crates/elap-core/src/agents/agent.rs) |
| Agregar un endpoint REST | [handlers.rs](crates/elap-core/src/api/handlers.rs) |
| Implementar una herramienta | [tools/](crates/elap-core/src/tools/) |
| Cambiar seguridad/RBAC | [security/rbac.rs](crates/elap-core/src/security/rbac.rs) |
| Agregar componente React | [components/tabs/](web/src/components/tabs/) |
| Agregar plantilla documento | [document_engine/](python/src/elap_ai/document_engine/) |
| Configurar base datos | [db/schema.rs](crates/elap-core/src/db/schema.rs) |
| Logging y debug | [logging_v2/](crates/elap-core/src/logging_v2/) |

### Por equipo

| Rol | Archivos principales |
|-----|----------------------|
| **Backend/Rust** | `crates/elap-core/src/` |
| **IA/Python** | `python/src/elap_ai/` |
| **Frontend/React** | `web/src/components/` |
| **DevOps/Config** | `docs/`, `Cargo.toml`, `pyproject.toml` |
| **Security** | `crates/elap-core/src/security/`, `crates/elap-core/src/tools/sandbox.rs` |

---

## 🔄 Flujo de código

```
┌─────────────────────────────────────────────────────────────┐
│                   User (Tauri Desktop)                       │
│                      web/src/App.tsx                          │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐      ┌──────────────────┐
│  React Frontend  │      │   Python REST    │
│  (Components)    │◄────►│   (Port 5000)    │
│                  │      │  (aiohttp)       │
└────────┬─────────┘      └──────────────────┘
         │                         │
         │                         ▼
         │                ┌──────────────────┐
         │                │  Python gRPC     │
         │                │  (Port 50051)    │
         │                └────────┬─────────┘
         │                         │
         └────────────┬────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   Rust Core Engine     │
         │   (Port 3000)          │
         │   - Orchestration      │
         │   - Security/RBAC      │
         │   - Scheduling         │
         │   - Tools Execution    │
         └────────────────────────┘
```

---

## 📦 Dependencias clave

### Rust
- **tokio**: Async runtime
- **actix-web**: HTTP server
- **serde**: Serialización
- **sqlx**: Database
- **tracing**: Logging
- **tonic**: gRPC

### Python
- **langgraph**: Agent framework
- **ollama**: Local LLM
- **aiohttp**: Async HTTP
- **docxtpl**: Document generation
- **qdrant-client**: Vector DB

### Frontend
- **React**: UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Lucide Icons**: Icons
- **Vite**: Build tool

---

## 🚀 Cómo navegar

1. **Inicio rápido**: Lee [CLAUDE.md](CLAUDE.md) y [README.md](README.md)
2. **Arquitectura**: [docs/01-Architecture/ARCHITECTURE.md](docs/01-Architecture/ARCHITECTURE.md)
3. **Cambios recientes**: [CHANGELOG.md](CHANGELOG.md)
4. **Próximas fases**: [docs/00-Project/ROADMAP.md](docs/00-Project/ROADMAP.md)
5. **Aprender en profundidad**: `/notebook` (libros de NotebookLM)

---

**Última sincronización**: 2026-08-08  
**Mantenedor**: Fabian Robles  
**Versión del proyecto**: 1.5.0-stable
