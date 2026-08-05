# TODO - Pendientes del Proyecto

**Última actualización**: 2026-08-04  
**Estado actual**: Fase 0 en progreso

---

## 🔴 Blockers - URGENTE

- [ ] Validar que `cargo build` compila sin errores
- [ ] Validar que `cargo test` pasa todos los tests
- [ ] Validar que `python -m pytest` funciona
- [ ] Primer commit Git con todos los archivos

---

## 🟡 Fase 0 - Pendientes

### Documentación

- [ ] /docs/01-Architecture/ARCHITECTURE.md (documentar decisiones fundacionales)
- [ ] /docs/01-Architecture/DECISIONS.md (por qué Rust+Python, gRPC, etc.)
- [ ] /docs/02-Development/CONVENTIONS.md (mejorar y expandir)
- [ ] /docs/02-Development/SETUP.md (guía de desarrollo local)
- [ ] /docs/02-Development/TESTING.md (estrategia de testing)
- [ ] /notebook/Libro-01-Introduccion/ (capítulos 1-5)
  - [ ] 01-Vision.md
  - [ ] 02-Arquitectura.md
  - [ ] 03-Roadmap.md
  - [ ] 04-Tecnologias.md
  - [ ] 05-BuenasPracticas.md

### CI/CD

- [ ] GitHub Actions workflow para Rust build/test/linting
- [ ] GitHub Actions workflow para Python build/test
- [ ] Coverage reports (codecov.io)
- [ ] Pre-commit hooks (black, ruff, clippy, rustfmt)

### Tests

- [ ] Tests for elap-core/error.rs (✓ 100%)
- [ ] Tests for elap-core/config.rs (✓ 100%)
- [ ] Tests for elap-core/core.rs (✓ 80%)
- [ ] Tests for elap-desktop (✓ 70%)
- [ ] Tests for elap-cli (50%)
- [ ] Tests for Python AIRuntime (50%)

### Code Quality

- [ ] Ejecutar `cargo clippy` y corregir warnings
- [ ] Ejecutar `cargo fmt --check` y formatear
- [ ] Ejecutar `ruff check` en Python y corregir
- [ ] Ejecutar `black` en Python
- [ ] Verificar `cargo audit` para vulnerabilidades
- [ ] Verificar `safety check` en Python

---

## 🟢 Fase 1 - Próxima

Cuando Fase 0 esté 100% completada:

- [ ] Core Runtime implementation
- [ ] Task scheduler with Tokio
- [ ] Process manager
- [ ] Plugin registry and loader
- [ ] Config hot-reload
- [ ] Full RBAC implementation
- [ ] gRPC protocol definition (.proto files)
- [ ] ARCHITECTURE.md (Core Runtime)
- [ ] Libro 02 para NotebookLM
- [ ] Tests (>80% coverage)

---

## 📋 Checklist final Fase 0

Antes de marcar Fase 0 como "Done", validar:

- [ ] **Código**
  - [ ] Compila: `cargo build --release`
  - [ ] Tests pasan: `cargo test`
  - [ ] Python tests pasan: `python -m pytest`
  - [ ] Sin warnings: `cargo clippy`
  - [ ] Formateado: `cargo fmt`
  - [ ] Sin vulnerabilidades: `cargo audit`

- [ ] **Documentación**
  - [ ] README.md completo
  - [ ] CLAUDE.md completo
  - [ ] ROADMAP.md completo
  - [ ] CHANGELOG.md completo
  - [ ] TODO.md actualizado (este archivo)
  - [ ] TREE.md completo
  - [ ] ARCHITECTURE.md básico
  - [ ] DECISIONS.md básico
  - [ ] /docs/02-Development/CONVENTIONS.md

- [ ] **Git**
  - [ ] Primer commit realizado
  - [ ] .gitignore funciona
  - [ ] Ningún archivo sensible fue commiteado

- [ ] **NotebookLM**
  - [ ] /notebook/Libro-01-Introduccion/ creado
  - [ ] Estructura básica lista

- [ ] **Validaciones externas**
  - [ ] Verificar compilación en GitHub Actions (pendiente setup)

---

## 📝 Prioridad

| Prioridad | Tarea | Blocker | Estimado |
|-----------|-------|---------|----------|
| 🔴 P0 | Validar compilación | Sí | 15 min |
| 🔴 P0 | Validar tests | Sí | 15 min |
| 🔴 P0 | Primer commit | Sí | 10 min |
| 🟡 P1 | Documentación técnica | No | 2 horas |
| 🟡 P1 | Libro 01 para NotebookLM | No | 3 horas |
| 🟡 P1 | CI/CD setup | No | 1 hora |
| 🟢 P2 | Code quality checks | No | 1 hora |

---

**Total estimado para Fase 0**: 8-10 horas de trabajo

**Última actualización**: 2026-08-04
