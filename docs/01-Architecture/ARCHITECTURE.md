# ELAP System Architecture

**Fase**: 0 (Fundacional)  
**Estado**: 🔄 In Progress  
**Version**: 1.0-alpha

---

## 1. Architecture Overview

ELAP (Enterprise Local AI Platform) is organized around **independent runtimes**, not agents. Each runtime is a specialized component managing a specific concern.

```
┌─────────────────────────────────────────────────────┐
│   Enterprise Local AI Platform (ELAP)               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │   Desktop Runtime (Tauri + TypeScript)      │   │
│  │   - Window management                       │   │
│  │   - User interface                          │   │
│  │   - Communication with Core                 │   │
│  └─────────────────────────────────────────────┘   │
│                      ↓↑                             │
│  ┌─────────────────────────────────────────────┐   │
│  │   Rust Core Runtime (Tokio)                 │   │
│  │   - Task scheduling                         │   │
│  │   - Process management                      │   │
│  │   - Security (RBAC)                         │   │
│  │   - Plugin engine                           │   │
│  │   - gRPC gateway                            │   │
│  │   - Configuration management                │   │
│  │   - Logging/Audit                           │   │
│  └─────────────────────────────────────────────┘   │
│                      ↕ gRPC                        │
│  ┌─────────────────────────────────────────────┐   │
│  │   Python AI Runtime (LangGraph)             │   │
│  │   - Agent execution                         │   │
│  │   - LLM inference (Ollama)                  │   │
│  │   - Memory management (RAG)                 │   │
│  │   - Tool execution                          │   │
│  └─────────────────────────────────────────────┘   │
│                      ↓                              │
│  ┌─────────────────────────────────────────────┐   │
│  │   External Systems                          │   │
│  │   - Ollama/llama.cpp (models)               │   │
│  │   - Qdrant/ChromaDB (vector store)          │   │
│  │   - PostgreSQL/SQLite (database)            │   │
│  │   - File system                             │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 2. Core Principles

### 2.1 Rust = Platform. Python = AI.

| Responsibility | Language | Why |
|---|---|---|
| Application lifecycle | Rust | Performance, memory safety, system access |
| Concurrency/scheduling | Rust | Tokio > asyncio for throughput |
| Security/RBAC | Rust | Memory-safe, lower attack surface |
| Process management | Rust | Direct OS access |
| Plugin engine | Rust | Safe sandboxing |
| **LLM inference** | **Python** | Transformers, llama.cpp ecosystem |
| **RAG/embeddings** | **Python** | LangChain, vector DB clients |
| **Agent orchestration** | **Python** | LangGraph, async agents |
| **Tool execution** | **Both** | Rust validates, Python executes |

### 2.2 Processes, not monolith

- **Core Runtime** (Rust) runs as main process
- **AI Runtime** (Python) runs as separate process
- Communication via **gRPC over Unix domain socket** (TLS-secured)
- Benefits:
  - If Python crashes, Core keeps running
  - Independent versioning and updates
  - Can restart Python without restarting Core
  - Typed API contracts (Protocol Buffers)

### 2.3 Local-first, offline-capable

- No data leaves the enterprise perimeter
- All telemetry stays local
- Models run on local infrastructure
- Optional: online features (updates check, cloud integrations) disabled by default

---

## 3. Component Architecture

### 3.1 Rust Core (Main Process)

**Purpose**: Orchestration, security, lifecycle management.

```
elap-core/
├── Engine (lifecycle)
├── TaskScheduler (Tokio-based)
├── ProcessManager (spawn/manage subprocesses)
├── PluginEngine (load, sandbox, manage plugins)
├── RbacManager (permissions validation)
├── ConfigManager (load, hot-reload TOML)
├── Logger (structured, local-only)
├── UpdateManager (signed binary updates)
├── BackupManager (config + memory recovery)
├── IpcGateway (gRPC server)
└── SecurityManager (encryption, secrets)
```

**Key responsibilities**:
1. Start/stop lifecycle
2. Validate all permissions before delegating to Python
3. Route requests to correct AI agent
4. Manage plugins securely
5. Audit all mutations (writes, API calls)
6. Handle update/recovery
7. Manage hardware resources (detect GPU, CPU allocation)

### 3.2 Desktop Shell (Tauri)

**Purpose**: User interface, window management, native OS integration.

```
elap-desktop/
├── WindowManager (Tauri)
├── IpcClient (communicates with Core)
├── StateManagement (React/Vue state)
├── ChatInterface (agent conversation)
├── Dashboard (status, monitoring)
├── ConfigUI (settings management)
└── ResourceMonitor (CPU/GPU/RAM)
```

**Key responsibilities**:
1. Display agent responses in real-time (streaming)
2. Collect user input
3. Show system health
4. Manage configuration UI
5. Handle authentication UI
6. Show audit logs

### 3.3 CLI (elap-cli)

**Purpose**: Command-line tools for administration and development.

```
elap-cli/
├── start (launch core + python runtimes)
├── stop (graceful shutdown)
├── status (health check)
├── config (view/edit configuration)
├── agent (manage agents)
├── model (manage models)
├── backup (manage backups)
├── restore (restore from backup)
└── logs (view audit logs)
```

### 3.4 Python AI Runtime (Separate Process)

**Purpose**: AI inference, agents, memory management.

```
elap_ai/
├── AgentRuntime (LangGraph-based)
│   ├── AgentManager (create/manage agents)
│   ├── AgentExecutor (run agent logic)
│   └── Handoff (delegation between agents)
├── ModelRuntime (Ollama/llama.cpp interface)
│   ├── ModelLoader (download/load)
│   ├── ModelSelector (choose by task/agent)
│   └── Inference (generate tokens)
├── MemoryManager (short + long-term)
│   ├── ShortTermMemory (conversation history)
│   ├── LongTermMemory (vector DB)
│   └── RAG (retrieval-augmented generation)
├── ToolExecutor (secure tool invocation)
│   ├── ToolRegistry (available tools)
│   ├── ToolValidator (check permissions)
│   └── ToolRunner (execute safely)
└── GrpcServer (communicate with Core)
```

**Key responsibilities**:
1. Execute agents (LangGraph)
2. Manage conversation memory
3. Retrieve relevant context (RAG)
4. Generate responses (LLM inference)
5. Execute allowed tools
6. Stream responses back to Core

---

## 4. Communication Patterns

### 4.1 Desktop ↔ Core (gRPC or REST)

**Desktop** sends user requests → **Core** validates → routes to **Python**

```
┌─────────┐
│ Desktop │
│ (UI)    │
└────┬────┘
     │ gRPC or HTTP
     ↓
┌─────────────────┐
│ Rust Core       │
│ (Orchestrator)  │
└────┬────────────┘
     │ Validates RBAC
     │ Audit log
     ↓
```

### 4.2 Core ↔ Python AI Runtime (gRPC)

**Core** asks Python runtime to process query → **Python** streams response

```
┌──────────────┐
│ Rust Core    │
└──────┬───────┘
       │ gRPC request
       │ (user_id, agent_id, query)
       ↓
┌──────────────┐
│ Python AI    │
│ Runtime      │ → Search memory (Qdrant)
└──────┬───────┘   → Call LLM (Ollama)
       │            → Execute tools
       │ gRPC response
       │ (streaming tokens)
       ↓
┌──────────────┐
│ Rust Core    │
│ (logs audit) │
└──────────────┘
```

### 4.3 IPC Details (Future detail in Phase 1)

- **Protocol**: gRPC with Protocol Buffers
- **Transport**: Unix domain socket (Linux) / named pipe (Windows)
- **Security**: TLS 1.3 + mutual authentication
- **Buffer**: Async streaming with backpressure
- **Latency target**: <5ms per request

---

## 5. Data Persistence

### 5.1 SQLite (Development/Small instances)

- Single file: `elap.db`
- Schema: users, agents, permissions, audit logs, conversations
- Limitations: <10 concurrent users

### 5.2 PostgreSQL (Enterprise)

- Schema: same as SQLite (portable)
- Supports: 50+ concurrent users, replication
- Requirements: managed by customer or BBLABS

### 5.3 Vector Database (AI Memory)

**Development**: ChromaDB (embedded)  
**Production**: Qdrant (standalone)

- Stores: document embeddings, conversation snippets
- Purpose: RAG (retrieve context for prompts)
- Volume: ~GB to ~TB depending on documents

---

## 6. Security Model (Phase 0 overview)

### 6.1 RBAC (Role-Based Access Control)

```
User → Role → Permissions
              ├── Agent access (which agents can use)
              ├── Tool access (which tools can call)
              └── Data access (which files/databases)
```

Every operation validated against user's role before execution.

### 6.2 Encryption

- **At rest**: AES-256 for sensitive configs/secrets
- **In transit**: TLS 1.3 for IPC
- **No default cloud encryption** (local-first means local key)

### 6.3 Audit Logging

Every operation recorded:
- User ID
- Timestamp
- Action (read/write/execute)
- Resource
- Result (success/failure)

Stored in SQLite/PostgreSQL, immutable.

---

## 7. Extensibility Points

### 7.1 Plugins (Phase 6)

Custom Rust code compiled to .so/.dll, loaded at runtime.  
Sandboxed using capability model.

Example: Custom PDF processor, enterprise CRM connector.

### 7.2 Tools (Phase 7)

Python functions registered in ToolRegistry.  
Invoked by agents after RBAC validation.

Example: Send email, query SQL, read/write files.

### 7.3 Agents (Phase 12)

LangGraph-based agents running in Python AI Runtime.  
Composition: model + tools + memory + prompt.

Example: Sales agent, HR agent, Finance agent.

### 7.4 Models (Phase 8)

Swap LLM without changing architecture.  
Support: Ollama, llama.cpp, Transformers, HuggingFace.

Example: Switch from Llama-7B to Mistral-8x7B.

---

## 8. Deployment Model

### 8.1 Single-machine (PYME)

```
┌─────────────────────────────────────┐
│ Customer Laptop/Server              │
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

File-based data, <30GB disk required, 16GB RAM minimum.

### 8.2 Multi-machine (Enterprise)

```
┌─────────────────────────────────────┐
│ Server 1: ELAP Core + Desktop       │
├─────────────────────────────────────┤
│ Server 2: Python AI Runtime         │
├─────────────────────────────────────┤
│ Server 3: PostgreSQL database       │
├─────────────────────────────────────┤
│ Server 4: Qdrant vector DB          │
├─────────────────────────────────────┤
│ Server 5: Ollama model cache        │
└─────────────────────────────────────┘
  (all behind private network, no internet)
```

Scalable, resilient, multi-node management.

---

## 9. Comparison with alternatives

### Single-language (Python only)

❌ Problems:
- Poor performance on core operations
- Memory overhead (GC, runtime)
- Hard to manage processes safely
- Difficult to sandbox plugins

### Go + Python

❌ Problems:
- Three ecosystems (cargo + go mod + pip)
- Go adds complexity without solving Rust's already-good problems
- Higher maintenance burden

### Node.js (Electron)

❌ Problems:
- 150MB+ binary vs Tauri ~10MB
- High RAM consumption
- Less control over native OS

### C++ + Python

❌ Problems:
- Memory safety issues in C++
- Complex build process
- Slow to develop compared to Rust

**Chosen: Rust + Python** ✅
- Performance + safety + ecosystem fit
- Clear language boundary (platform vs AI)
- Best of both worlds

---

## 10. Phase-wise evolution

| Phase | Adds | Changes |
|-------|------|---------|
| 0 | Foundations | Structure, base modules |
| 1 | Core Engine | Task scheduling, processes, plugins |
| 2 | Desktop | Tauri window, communication |
| 3-5 | Plumbing | Config, logging, errors |
| 6-7 | Extensibility | Plugins, tools |
| 8-10 | AI Core | Models, agents, memory |
| 11-12 | Orchestration | Workflows, delegation |
| 13-14 | UX/Deployment | GUI, installer |
| 15-17 | Polish | Updates, testing, packaging |

---

## 11. Performance targets

| Operation | Target | Hardware reference |
|-----------|--------|-------------------|
| First token latency | <3s | CPU 8-core, 16GB RAM, 7B Q4 model |
| Concurrent users | 50 | 16-core, 64GB RAM, 1 GPU |
| Inference throughput | 20 tokens/sec | Same as above |
| Core startup | <2s | SSD, no GPU wait |

---

## 12. Next steps

See:
- [DECISIONS.md](DECISIONS.md) — Why these choices
- [/docs/02-Development/SETUP.md](../02-Development/SETUP.md) — How to build locally
- [/docs/02-Development/CONVENTIONS.md](../02-Development/CONVENTIONS.md) — Code standards

---

**Last updated**: 2026-08-04  
**Next review**: After Phase 1 completion
