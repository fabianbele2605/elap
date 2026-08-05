# CHANGELOG

Formato basado en [Keep a Changelog](https://keepachangelog.com/).

---

## [0.1.0-alpha] - 2026-08-04

### Fase 0: Fundacionales

#### Added

- Git repository initialized with user configuration
- Complete directory structure created
  - `crates/` for Rust workspace (elap-core, elap-desktop, elap-cli)
  - `python/` for AI Runtime
  - `docs/` with 10 subdirectories for documentation
  - `notebook/` for NotebookLM study materials
  - `tooling/` for CI/CD and scripts
  - `.github/workflows/` for GitHub Actions
- Cargo.toml workspace configuration with shared dependencies
  - Tokio async runtime
  - Tonic gRPC framework
  - Tracing for logging
  - Serde for serialization
  - Ring for crypto
- pyproject.toml for Python package
  - LangChain/LangGraph dependencies
  - Transformers and PyTorch
  - Vector DBs (Qdrant, ChromaDB)
  - Ollama for model inference
- Main documentation files
  - README.md (English, project overview)
  - CLAUDE.md (Engineering standards)
  - .gitignore (Rust + Python + IDE)
- Rust code (elap-core)
  - CoreEngine struct with lifecycle management
  - ElapError type with variants
  - Config struct with DatabaseConfig and SecurityConfig
  - Initial tests (>80% coverage target)
- Rust code (elap-desktop)
  - DesktopRuntime wrapper
  - Basic async lifecycle
- Rust code (elap-cli)
  - CLI with clap
  - Commands: start, version, health, help
  - Logging with tracing
- Python code (elap-ai)
  - AIRuntime base class
  - Async lifecycle (start/stop)
  - health_check method
  - process_query placeholder
- Documentation structure
  - /docs/00-Project/ (README, ROADMAP, CHANGELOG, TODO, TREE)
  - /docs/01-Architecture/ (skeleton)
  - /docs/02-Development/ (skeleton)
  - /docs/03-Modules/ through /10-NotebookLM/ (empty, ready for content)
  - /notebook/Libro-01-Introduccion/ (skeleton)

#### Modified

- None (initial creation)

#### Deprecated

- None

#### Removed

- None

#### Fixed

- None

#### Security

- .gitignore configured to prevent:
  - Rust build artifacts (/target/)
  - Python cache (__pycache__/)
  - Environment files (.env)
  - Private keys and secrets
  - Database files (*.db, *.sqlite)
  - Model files (*.gguf, *.safetensors) — can be added with git-lfs

#### Documentation

- README.md: Project overview, quick start, structure
- CLAUDE.md: Code conventions, architecture principles, security checklist
- ROADMAP.md: 17-phase roadmap with deliverables
- docs/00-Project/README.md: Fase 0 status
- /notebook/ structure created for future study materials

---

## Unreleased

### Next (Fase 1 - Core Runtime)

- [ ] Task scheduler implementation (Tokio)
- [ ] Process manager
- [ ] Plugin framework
- [ ] gRPC gateway Rust ↔ Python
- [ ] RBAC manager
- [ ] Tests (>80% coverage)
- [ ] ARCHITECTURE.md documentation
- [ ] Libro 02 for NotebookLM

---

## Notes

- **Language**: English for code, Spanish for documentation
- **Versioning**: Semantic versioning (MAJOR.MINOR.PATCH)
- **Releases**: One per phase completion
- **Living Documentation**: Every code change comes with documentation

---

**Created**: 2026-08-04  
**Last updated**: 2026-08-04
