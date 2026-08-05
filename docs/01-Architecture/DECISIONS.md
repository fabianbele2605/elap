# Architectural Decision Records (ADR)

**Document style**: ADR (Architecture Decision Record)  
**Version**: 1.0-alpha  
**Date created**: 2026-08-04

---

## ADR-001: Use Rust for Core Runtime

**Status**: ✅ **Accepted**

**Decision**: The core orchestration, task scheduling, and process management will be implemented in **Rust**, not Python, Go, or C++.

**Context**:
We need a performant, memory-safe platform that:
- Handles concurrent requests (100+ agents simultaneously)
- Manages processes safely (sandboxing plugins)
- Integrates with OS (file I/O, GPU detection, process signals)
- Runs on minimal hardware (PYMEs with 8GB RAM)

**Considered alternatives**:

| Language | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Rust** | Memory safe, fast, Tokio async, good OS access | Steep learning curve | ✅ **CHOSEN** |
| Python | Easy to write, large AI library | Slow for core, GC, memory overhead | ❌ Not suitable for core |
| Go | Easy concurrency, cross-compile | Less memory safe, less OS access | ❌ Unnecessary 3rd ecosystem |
| C++ | Very fast, fine-grained control | Memory unsafe, complex, slow dev | ❌ Too risky |

**Decision drivers**:
1. **Safety**: Rust prevents entire categories of bugs (memory, race conditions)
2. **Performance**: Minimal overhead, no GC pauses
3. **Ecosystem**: Tokio async runtime is superior to anything in Python/Go
4. **Maintainability**: Strong typing, compiler catches mistakes early

**Consequences**:
- ✅ Reliable core that can run for months without restart
- ✅ Fast task scheduling without GC pauses
- ⚠️ Rust has learning curve (mitigate with mentoring, code reviews)
- ⚠️ Build times slower than Go (acceptable, not critical path)

**Related ADRs**: ADR-002 (Python for AI)

---

## ADR-002: Use Python exclusively for AI Runtime

**Status**: ✅ **Accepted**

**Decision**: All AI/ML workloads (inference, RAG, agents, embeddings) run in **separate Python process**, not in Rust.

**Context**:
- LLM inference: dominated by PyTorch, Transformers, llama.cpp Python bindings
- RAG/embeddings: LangChain, LangGraph, ChromaDB clients
- Agents: LangGraph is Python-first
- Ecosystem maturity: Python is de-facto standard for AI

**Considered alternatives**:

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Python separate process** | Ecosystem fit, can restart independently, typed gRPC API | IPC latency | ✅ **CHOSEN** |
| Rust + llama.cpp bindings | Integrated process, no IPC latency | Limted agent frameworks, reinvent RAG | ❌ Too much work |
| PyO3 (Python bindings in Rust) | Direct integration, low latency | Crashes take down core, tight coupling | ❌ Unsafe |
| Go for AI | ??? | No mainstream AI libraries in Go | ❌ Impractical |

**Decision drivers**:
1. **Ecosystem**: Python ecosystem is unbeatable for AI
2. **Time-to-market**: Leverage existing libraries (LangChain, LangGraph)
3. **Independence**: Python process can crash/restart without losing core
4. **Specialization**: Clear separation of concerns

**Consequences**:
- ✅ Can leverage best-in-class AI libraries
- ✅ Python failures don't crash Rust core
- ✅ Can update Python without recompiling Rust
- ⚠️ gRPC IPC adds ~5-10ms latency (acceptable for inference which takes 500ms+)
- ⚠️ More operational complexity (two processes to manage)

**Mitigation**:
- Use gRPC streaming for efficiency
- Benchmark IPC latency in Phase 1
- Document operational requirements

**Related ADRs**: ADR-001 (Rust core), ADR-003 (gRPC communication)

---

## ADR-003: Use gRPC over Unix socket for Rust ↔ Python communication

**Status**: ✅ **Accepted**

**Decision**: Rust Core and Python AI Runtime communicate via **gRPC over Unix domain socket** (Linux) / named pipe (Windows), with TLS encryption.

**Context**:
Two independent processes need to communicate:
- Core validates permissions, asks Python to process query
- Python streams back response tokens
- Both run on same machine (local-first principle)

**Considered alternatives**:

| Method | Latency | Typing | Streaming | Complexity | IPC safety |
|--------|---------|--------|-----------|------------|-----------|
| **gRPC/socket** | ~5ms | ✅ Protobuf | ✅ Native | Moderate | ✅ Socket isolation |
| HTTP/REST local | ~10ms | ⚠️ JSON | ❌ Chunked | Low | ⚠️ HTTP overhead |
| ZeroMQ | ~2ms | ❌ Custom | ✅ Yes | High | ⚠️ Custom protocol |
| PyO3 bindings | <1ms | ✅ Typed | ⚠️ Callbacks | High | ❌ Shared memory risk |
| Unix pipes | ~3ms | ❌ Raw bytes | ✅ Yes | Very high | ✅ Safe |

**Decision drivers**:
1. **Typed API**: Protocol Buffers enforce versioning, prevent mismatches
2. **Streaming**: gRPC streaming native (important for token streaming)
3. **Standard**: Industry-standard, proven in production
4. **Process safety**: Separate processes can restart independently
5. **Security**: Can use TLS over socket

**Consequences**:
- ✅ Type-safe API between languages
- ✅ Can version independently
- ✅ Python restart doesn't require Core restart
- ✅ Streaming responses natively supported
- ⚠️ 5-10ms latency per RPC call
- ⚠️ More complex debugging (separate process)

**Mitigation**:
- Use batch requests where possible
- Implement connection pooling
- Log all IPC in audit trail

**Related ADRs**: ADR-001, ADR-002

---

## ADR-004: Use Tauri for Desktop shell (not Electron)

**Status**: ✅ **Accepted**

**Decision**: Desktop application built with **Tauri** (Rust backend, web frontend), not Electron.

**Context**:
Need desktop GUI for:
- Agent chat interface
- Configuration management
- System monitoring
- User authentication

**Considered alternatives**:

| Framework | Binary size | RAM | Backend | Dev speed | Verdict |
|-----------|-------------|-----|---------|-----------|---------|
| **Tauri** | ~10MB | Low (WebKit) | Rust native | Good | ✅ **CHOSEN** |
| Electron | 150MB+ | High (Chromium) | Node.js | Very good | ❌ Too bloated |
| Qt | ~50MB | Medium | C++ | Slow | ❌ C++ complexity |
| wxWidgets | ~30MB | Medium | C++ | Slow | ❌ Old technology |
| Web-only | N/A | N/A | N/A | Very good | ❌ Needs server (breaks offline) |

**Decision drivers**:
1. **Size**: 10MB vs 150MB is critical for PYME distribution
2. **RAM**: Matters on customer hardware (8GB machines)
3. **Native backend**: Direct Rust code, not JavaScript
4. **Offline-capable**: Desktop app, not web browser

**Consequences**:
- ✅ Minimal footprint, fast startup
- ✅ Uses customer OS's WebKit (not bundled Chromium)
- ✅ Can write UI-adjacent code in Rust
- ⚠️ WebKit differences across OS (Windows uses Edge, macOS uses Safari)
- ⚠️ Smaller community than Electron

**Mitigation**:
- Use web standards (HTML/CSS/TS) for UI (maximum compatibility)
- Test across Windows/macOS/Linux
- Contribute to Tauri community

**Related ADRs**: ADR-001 (Rust)

---

## ADR-005: Use Tokio for async task scheduling

**Status**: ✅ **Accepted**

**Decision**: Task scheduling and async operations in Rust use **Tokio**, not async-std or other runtimes.

**Context**:
Core Runtime needs to handle:
- Concurrent agent requests (100+ simultaneously)
- Long-running background jobs (model loading, backups)
- Timers and scheduling
- Process spawning

**Considered alternatives**:

| Runtime | Throughput | Ecosystem | Maturity | Verdict |
|---------|-----------|-----------|----------|---------|
| **Tokio** | Very high (millions/sec) | Excellent (gRPC, Hyper) | Production-ready | ✅ **CHOSEN** |
| async-std | Good | Small ecosystem | Less mature | ❌ Smaller community |
| embassy | Embedded-focused | Specialized | Less general | ❌ Not suitable |

**Decision drivers**:
1. **Industry standard**: Used by Rust companies (Discord, Cloudflare, etc.)
2. **Ecosystem support**: gRPC (tonic) built on Tokio
3. **Performance**: Exceptional throughput
4. **Maturity**: Production-proven

**Consequences**:
- ✅ Excellent performance for concurrent operations
- ✅ Rich ecosystem of libraries
- ✅ Well-documented, large community
- ⚠️ Learning curve for async Rust
- ⚠️ Some debugging complexity (async stacktraces)

**Related ADRs**: ADR-001 (Rust)

---

## ADR-006: SQLite for dev, PostgreSQL for enterprise

**Status**: ✅ **Accepted**

**Decision**: Application supports both **SQLite** (development/single-user) and **PostgreSQL** (enterprise multi-user), with same schema.

**Context**:
Different deployment scenarios:
- **PYME**: Single machine, single database, <10GB data
- **Enterprise**: Multiple servers, concurrent users, HA requirements

**Considered alternatives**:

| Database | Dev | Enterprise | Schema migration | Verdict |
|----------|-----|-----------|-----------------|---------|
| **SQLite + PostgreSQL** | ✅ | ✅ | Same schema | ✅ **CHOSEN** |
| SQLite only | ✅ | ❌ Limited | N/A | ❌ Doesn't scale |
| PostgreSQL only | ⚠️ Extra setup | ✅ | Single schema | ⚠️ Dev friction |
| MongoDB | ⚠️ | ⚠️ | Flexible but messy | ❌ Overkill |

**Decision drivers**:
1. **Developer experience**: SQLite requires zero setup, perfect for local dev
2. **Production**: PostgreSQL proven for enterprise workloads
3. **Portability**: Same queries work against both
4. **Licensing**: Both open-source, no cost

**Consequences**:
- ✅ Zero setup for developers
- ✅ Enterprise customers get proven database
- ✅ No vendor lock-in
- ⚠️ Must test migrations against both
- ⚠️ Some SQL dialects differ

**Mitigation**:
- Standardize on ANSI SQL
- Use sqlx for type-safe queries
- Automated testing against both databases

**Related ADRs**: ADR-010 (Vector DB choice)

---

## ADR-007: Local-first architecture (no cloud by default)

**Status**: ✅ **Accepted**

**Decision**: ELAP is **offline-capable by default**. No required cloud services. Telemetry and updates stay local.

**Context**:
Enterprise customers (especially regulated industries) require:
- Data never leaves premises
- Compliance with GDPR, HIPAA, SOC2
- Operation during internet outages
- No dependence on vendor infrastructure

**Considered alternatives**:

| Model | Offline | Privacy | Deployment | Verdict |
|-------|---------|---------|------------|---------|
| **Local-first (cloud optional)** | ✅ | ✅ | Customer hardware | ✅ **CHOSEN** |
| Cloud-first (self-hosted option) | ⚠️ | ⚠️ | Cloud + fallback | ❌ Not suitable |
| Cloud-only | ❌ | ❌ | Vendor servers | ❌ Fails SRS |

**Decision drivers**:
1. **Market requirement**: Regulated industries need this
2. **Differentiation**: ChatGPT/Claude are cloud-only
3. **Compliance**: GDPR means data stays in EU, HIPAA means secured
4. **Resilience**: No internet? Still works

**Consequences**:
- ✅ Appealing to regulated industries
- ✅ No recurring cloud costs for customers
- ✅ Meets compliance requirements
- ⚠️ No centralized logging/monitoring (must be on-premises)
- ⚠️ Updates require manual deployment or VPN

**Mitigation**:
- Provide easy update mechanism (signed binaries)
- Offer optional cloud sync (for customers who want it)
- Document air-gapped deployment

**Related ADRs**: None (architectural principle)

---

## ADR-008: RBAC (Role-Based Access Control) from day one

**Status**: ✅ **Accepted**

**Decision**: Security model is **RBAC** (Role-Based Access Control), enforced at Rust core level, not application level.

**Context**:
Enterprise deployment requires:
- Granular permissions (who can use which agents/tools)
- Audit trail of all operations
- Prevention of privilege escalation
- Compliance with least-privilege principle

**Considered alternatives**:

| Model | Enforcement | Flexibility | Implementation |
|-------|------------|-------------|-----------------|
| **RBAC (core)** | Mandatory | Roles + rules | Rust, can't bypass | ✅ **CHOSEN** |
| ACL (Access Control Lists) | Granular | User-by-user | Harder to manage at scale | ❌ Not scalable |
| Trust boundary (app-level) | Weak | High | Easy to bypass | ❌ Not secure |

**Decision drivers**:
1. **Compliance**: Required by enterprise customers
2. **Safety**: Can't accidentally expose data
3. **Auditability**: Logs show who did what
4. **Scalability**: Roles easier to manage than per-user ACLs

**Consequences**:
- ✅ Enterprise-grade security
- ✅ Audit trails for compliance
- ✅ Prevents accidental data leaks
- ⚠️ More setup complexity (define roles)
- ⚠️ Performance cost (permission checks on every operation)

**Mitigation**:
- Cache permission checks
- Document role templates (Sales, HR, IT, etc.)
- Provide UI for permission management

**Related ADRs**: ADR-009 (Encryption)

---

## ADR-009: AES-256 encryption for data at rest

**Status**: ✅ **Accepted**

**Decision**: Sensitive data (configs, secrets, conversation history) encrypted with **AES-256** at rest.

**Context**:
Customer data must be protected if:
- Hardware stolen
- Disk removed
- Unauthorized access to filesystem

**Considered alternatives**:

| Cipher | Key size | Speed | Standard | Verdict |
|--------|----------|-------|----------|---------|
| **AES-256** | 256-bit | Fast (hardware acceleration) | FIPS approved | ✅ **CHOSEN** |
| AES-128 | 128-bit | Slightly faster | FIPS but weaker | ⚠️ Less secure |
| ChaCha20 | 256-bit | Good | IETF standard | ⚠️ Less universal |
| Twofish | 256-bit | Slower | Academic | ❌ Older |

**Decision drivers**:
1. **Strength**: 256-bit key resists quantum attacks longer than 128-bit
2. **Performance**: Hardware acceleration available (AES-NI)
3. **Standard**: FIPS 140-2 approved
4. **Library**: Ring crate has battle-tested implementation

**Consequences**:
- ✅ Industry standard (DoD, NIST approved)
- ✅ Protects against theft scenarios
- ⚠️ Key management required (where to store master key?)
- ⚠️ Performance cost (mitigated by hardware acceleration)

**Mitigation**:
- Key stored in memory only (not on disk)
- Key derivation from master secret
- Regular key rotation optional

**Related ADRs**: ADR-007 (Local-first), ADR-008 (RBAC)

---

## ADR-010: Qdrant for production, ChromaDB for dev

**Status**: ✅ **Accepted**

**Decision**: Vector database is **Qdrant** for enterprise, **ChromaDB** for development.

**Context**:
RAG (Retrieval-Augmented Generation) requires vector database:
- Store embeddings of documents
- Semantic similarity search
- Scalable to millions of vectors

**Considered alternatives**:

| Database | Dev | Enterprise | Written in | Verdict |
|----------|-----|-----------|-----------|---------|
| **Qdrant** | ⚠️ Extra setup | ✅ | Rust | ✅ **Enterprise** |
| **ChromaDB** | ✅ Easy | ⚠️ Limited | Python | ✅ **Dev** |
| Weaviate | ⚠️ | ✅ | Go | ❌ Overkill |
| Pinecone | ⚠️ Cloud-only | ✅ | Managed | ❌ Fails offline requirement |
| Elasticsearch | ⚠️ Complex | ✅ | Java | ❌ Too heavyweight |

**Decision drivers**:
1. **Dev speed**: ChromaDB embeds in process, zero setup
2. **Production**: Qdrant proven, written in Rust (fits our stack)
3. **Offline**: Both run locally (no cloud dependency)
4. **Scale**: Qdrant handles millions of vectors

**Consequences**:
- ✅ Smooth dev → prod transition
- ✅ Both support offline operation
- ⚠️ Different configuration paths (embed vs standalone)
- ⚠️ Migration needed when moving from dev to prod

**Mitigation**:
- Abstract vector DB behind interface
- Provide migration tools
- Document both configurations

**Related ADRs**: ADR-006 (SQL databases)

---

## ADR-011: No fork of code, plugin system instead

**Status**: ✅ **Accepted**

**Decision**: Customization via **plugin system**, not code forks.

**Context**:
Customers will need customization (new agents, tools, integrations). Forks are unsustainable:
- Merging upstream difficult
- Each customer is snowflake
- Version fragmentation

**Considered alternatives**:

| Model | Flexibility | Maintainability | Upgrade path | Verdict |
|-------|-------------|-----------------|--------------|---------|
| **Plugins** | High | Easy | Clean | ✅ **CHOSEN** |
| Forks | Very high | Nightmare | Painful | ❌ Unsustainable |
| Configuration only | Limited | Easy | Simple | ⚠️ Not flexible enough |

**Decision drivers**:
1. **Scalability**: Can't maintain N forks
2. **Upgrades**: Plugins are version-agnostic
3. **Ecosystem**: Encourage community contributions
4. **Business**: Marketplace opportunity (Phase 6)

**Consequences**:
- ✅ Sustainable customization model
- ✅ Marketplace opportunity
- ✅ Clear upgrade path for customers
- ⚠️ Must design stable plugin API
- ⚠️ Security burden (vet plugins)

**Mitigation**:
- Define plugin manifest with permissions
- Sandbox plugins (capabilities model)
- Provide SDK and examples
- Code review process for official plugins

**Related ADRs**: None (business/architectural)

---

## ADR-012: Conventional Commits for git history

**Status**: ✅ **Accepted**

**Decision**: All commits follow **Conventional Commits** specification.

**Context**:
Clean git history aids:
- Changelog generation
- Semantic versioning (auto-compute)
- Code review
- Revert safety

**Considered alternatives**:

| Format | Readability | Automation | Verdict |
|--------|-------------|-----------|---------|
| **Conventional** | ✅ Clear | ✅ Can parse | ✅ **CHOSEN** |
| Descriptive freeform | ✅ Good | ❌ Can't parse | ❌ No automation |
| Imperative mood | ✅ Good | ❌ Ambiguous | ⚠️ Less structure |

**Decision drivers**:
1. **Automation**: Can generate CHANGELOG
2. **Standard**: Used by Angular, Vue, Kubernetes
3. **Clarity**: Type + scope + message is precise

**Consequences**:
- ✅ Automated CHANGELOG generation
- ✅ Clear commit history
- ✅ SemVer automation possible
- ⚠️ Requires discipline (can add linting)

**Mitigation**:
- Add git hooks to enforce format
- Document in CLAUDE.md
- Examples in PR templates

**Related ADRs**: None (process/tooling)

---

## Summary table

| ADR | Decision | Status |
|-----|----------|--------|
| 001 | Rust for core | ✅ Accepted |
| 002 | Python for AI | ✅ Accepted |
| 003 | gRPC over socket | ✅ Accepted |
| 004 | Tauri desktop | ✅ Accepted |
| 005 | Tokio async | ✅ Accepted |
| 006 | SQLite+PostgreSQL | ✅ Accepted |
| 007 | Local-first | ✅ Accepted |
| 008 | RBAC security | ✅ Accepted |
| 009 | AES-256 encryption | ✅ Accepted |
| 010 | Qdrant+ChromaDB vectors | ✅ Accepted |
| 011 | Plugins > forks | ✅ Accepted |
| 012 | Conventional Commits | ✅ Accepted |

---

**Document version**: 1.0-alpha  
**Last updated**: 2026-08-04  
**Next review**: After Phase 1, update with Phase 1 ADRs
