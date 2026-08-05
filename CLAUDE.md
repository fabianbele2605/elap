# CLAUDE.md — Estándares de ingeniería ELAP

**Versión:** 1.0  
**Propósito:** Guía de referencia rápida para código, arquitectura y decisiones  
**Audiencia:** Todos los desarrolladores de ELAP

---

## 1. Principios fundamentales

### Rust = Plataforma. Python = IA.

```
┌─────────────────────────────────────┐
│   Enterprise Local AI Platform      │
├─────────────────────────────────────┤
│                                     │
│  Rust Core Runtime                  │
│  ├─ Task Scheduling (Tokio)         │
│  ├─ Process Management              │
│  ├─ Security/RBAC                   │
│  ├─ Plugin Engine                   │
│  └─ IPC Gateway (gRPC)              │
│                                     │
├─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤
│                                     │
│  Python AI Runtime (proceso aparte) │
│  ├─ Agent Framework (LangGraph)     │
│  ├─ RAG/Memory (Qdrant/ChromaDB)    │
│  ├─ Model Management (Ollama)       │
│  └─ Tool Execution (sandbox)        │
│                                     │
└─────────────────────────────────────┘
     comunicación: gRPC + TLS
```

**Regla de oro**: Si dudas dónde va algo, pregúntate:
- ¿Es sobre rendimiento, seguridad o sistema operativo? → Rust
- ¿Es sobre IA, modelos o LLMs? → Python

**Excepciones permitidas:**
- APIs simples REST para herramientas específicas (aceptable en Python, no como patrón)
- Scripts de utilidad en Rust si no afectan el core

---

## 2. Convenciones de código

### Rust

```rust
// ✅ Correcto
// Module names: snake_case
mod core_engine;
mod plugin_manager;

// Types/Structs: PascalCase
pub struct CoreEngine;
pub enum RuntimeState;

// Functions/Methods: snake_case
pub fn process_request() {}
pub fn validate_permissions() {}

// Constants: UPPER_SNAKE_CASE
pub const MAX_CONCURRENT_AGENTS: usize = 256;
pub const BUFFER_SIZE_KB: usize = 64;

// Private helpers: with _ prefix when internal
fn _validate_signature() {}
```

**Imports**:
```rust
// Grouped: std, external crates, internal modules
use std::path::PathBuf;
use tokio::sync::mpsc;
use crate::core::{Engine, State};
```

**Error handling**:
```rust
// Use Result<T, E> always
pub fn risky_operation() -> Result<Output, ElapError> {
    // ...
}

// Never .unwrap() or .panic!() in library code
// Use ? operator for propagation
let value = some_operation()?;
```

### Python

```python
# ✅ Correcto
# Module names: snake_case
from elap_ai.agent_runtime import AgentRuntime

# Classes: PascalCase
class AgentRuntime:
    pass

class LLMModel:
    pass

# Functions/Methods: snake_case
def process_request(self, query: str) -> str:
    pass

def validate_permissions(self) -> bool:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_CONCURRENT_AGENTS = 256
BUFFER_SIZE_KB = 64

# Type hints: mandatory (PEP 484)
def create_agent(name: str, role: str) -> Agent:
    pass
```

**Imports**:
```python
# Grouped: stdlib, third-party, local
import asyncio
from typing import Optional

import pydantic
from langchain import LLMChain

from elap_ai.core import Agent
```

---

## 3. Arquitectura

### Living Documentation obligatoria

**REGLA**: Ninguna línea de código puede existir sin documentación.

Al terminar cada módulo/fase:

```
✅ Código compilable y ejecutable
✅ Tests pasando (>80% cobertura en Rust)
✅ Documentación técnica (/docs)
✅ Capítulo para NotebookLM (/notebook)
✅ CHANGELOG.md actualizado
✅ ROADMAP.md actualizado
✅ TREE.md (árbol del proyecto) actualizado
✅ Commit generado con Conventional Commits
```

### Estructura de módulos Rust

```
crates/elap-core/
├── src/
│   ├── lib.rs           # Public API del crate
│   ├── mod.rs           # Re-exports públicos
│   ├── error.rs         # Tipos de error
│   ├── config.rs        # Configuración
│   │
│   ├── core/
│   │   ├── mod.rs
│   │   ├── engine.rs
│   │   └── state.rs
│   │
│   ├── security/
│   │   ├── mod.rs
│   │   ├── rbac.rs
│   │   └── crypto.rs
│   │
│   └── ipc/
│       ├── mod.rs
│       ├── grpc_gateway.rs
│       └── protocol.rs
│
├── Cargo.toml
└── tests/
    └── integration_tests.rs
```

**Regla**: Cada carpeta necesita `mod.rs` con:
```rust
// lib.rs o mod.rs
pub mod core;
pub mod security;
pub mod ipc;

// Re-exports públicos
pub use core::Engine;
pub use security::RbacManager;
```

### Estructura de módulos Python

```
python/
├── src/elap_ai/
│   ├── __init__.py           # Public API
│   ├── main.py               # Entry point
│   ├── config.py             # Configuración
│   ├── errors.py             # Excepciones
│   │
│   ├── agent_runtime/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── orchestrator.py
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── short_term.py
│   │   └── long_term.py
│   │
│   └── tools/
│       ├── __init__.py
│       ├── registry.py
│       └── executor.py
│
├── tests/
│   ├── __init__.py
│   ├── test_agent_runtime.py
│   └── test_memory.py
│
└── pyproject.toml
```

---

## 4. Testing

### Rust

**Cobertura mínima**: 80% en el core.

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_permission_validation_success() {
        // Arrange
        let rbac = RbacManager::new();
        
        // Act
        let result = rbac.validate_permission("user_123", "read_data");
        
        // Assert
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_async_operation() {
        // ...
    }
}
```

**Ejecutar tests**:
```bash
cargo test
cargo test -- --nocapture              # Ver output
cargo tarpaulin --out Html             # Coverage report
```

### Python

**Cobertura mínima**: 70%.

```python
import pytest

def test_agent_creation():
    # Arrange
    agent = Agent(name="TestAgent", role="Sales")
    
    # Act
    result = agent.initialize()
    
    # Assert
    assert result is True

@pytest.mark.asyncio
async def test_async_process():
    # ...
    pass
```

**Ejecutar tests**:
```bash
python -m pytest
python -m pytest --cov=elap_ai       # Coverage
pytest -v                             # Verbose
```

---

## 5. Git y Commits

### Conventional Commits en ESPAÑOL

**IMPORTANTE**: Todos los commits deben estar en **ESPAÑOL**, aunque el código esté en inglés.

```
<tipo>(<scope>): <mensaje>

<cuerpo>

<pie>
```

**Tipos**:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `refactor`: Cambio de código sin alterar funcionalidad
- `test`: Tests o cobertura de tests
- `ci`: Cambios en CI/CD
- `chore`: Cambios en build, deps, etc.

**Ejemplos correctos**:

```
feat(core): Agregar task scheduler con Tokio

Implementa task scheduling para ejecutar trabajos concurrentes.
Soporta 256 tareas simultáneas.

Fixes #123
```

```
fix(security): Validar permisos antes de ejecutar herramientas

Agrega RBAC check obligatorio. Sin esto, usuarios podían usar
herramientas no autorizadas.

Breaking change: Requiere migración de permisos existentes.
```

```
docs(readme): Actualizar instrucciones de instalación

Agregan pasos de configuración para PostgreSQL y Qdrant.
Aclara requisitos de hardware mínimo.
```

```
test(core): Aumentar cobertura de error handling a 95%

Agrega tests para casos edge en validación de permisos.
```

### Branch naming

```
main              # Producción
develop           # Desarrollo principal

feature/core-engine           # Nueva funcionalidad
fix/security-rbac             # Bug fix
docs/api-documentation        # Solo documentación
```

---

## 6. Errores y logging

### Rust — Error handling

```rust
// Define custom error type
#[derive(Debug)]
pub enum ElapError {
    PermissionDenied(String),
    ModuleNotFound(String),
    GrpcError(String),
}

// Use in functions
pub fn execute_tool(tool_id: &str) -> Result<Output, ElapError> {
    if !has_permission(tool_id) {
        return Err(ElapError::PermissionDenied(
            format!("User lacks permission for tool: {}", tool_id)
        ));
    }
    Ok(Output::default())
}
```

### Python — Exception handling

```python
class ElapException(Exception):
    """Base exception for ELAP"""
    pass

class PermissionDenied(ElapException):
    """User lacks required permissions"""
    pass

class ModuleNotFound(ElapException):
    """Required module not found"""
    pass

# Use in functions
def execute_tool(tool_id: str) -> dict:
    if not has_permission(tool_id):
        raise PermissionDenied(f"User lacks permission for: {tool_id}")
    return {}
```

### Logging

```rust
// Rust
use tracing::{info, warn, error};

info!("Core engine started");
warn!("Slow operation detected: {}ms", duration);
error!("Authentication failed for user: {}", user_id);
```

```python
# Python
import logging

logger = logging.getLogger(__name__)

logger.info("AI Runtime started")
logger.warning("Slow inference: %.2f seconds", duration)
logger.error("Authentication failed for user: %s", user_id)
```

---

## 7. Documentación obligatoria

### Por archivo

```rust
/// Manages security policies and RBAC rules.
///
/// This is the central authority for permission validation.
/// Every operation must be validated through this manager.
///
/// # Example
/// ```ignore
/// let rbac = RbacManager::new();
/// rbac.validate_permission("user_123", "read_data")?;
/// ```
pub struct RbacManager {
    // ...
}
```

### Por función

```python
def validate_permission(user_id: str, resource: str) -> bool:
    """
    Validate if a user has permission to access a resource.
    
    Args:
        user_id: The user's unique identifier
        resource: The resource being accessed (e.g., "read_data")
    
    Returns:
        True if permission is granted, False otherwise
    
    Raises:
        ElapException: If validation fails
    
    Example:
        >>> validate_permission("user_123", "read_sensitive_data")
        True
    """
    pass
```

---

## 8. Decisiones arquitectónicas clave

| Decisión | Justificación | Alternativa descartada |
|----------|--------------|----------------------|
| **Rust + Python** | Rust para núcleo (performance, seguridad), Python para IA (ecosistema) | Go como tercera lengua: demasiada complejidad |
| **gRPC sobre socket local** | Tipado, streaming, aislamiento de procesos | PyO3 bindings: acoplamiento fuerte |
| **Tauri para desktop** | Binario pequeño (~10MB), bajo consumo RAM | Electron: 150MB+, mucho RAM |
| **Tokio para async** | Mejor throughput que asyncio | asyncio: insuficiente para concurrencia del core |
| **PostgreSQL + SQLite** | SQLite para desarrollo/pequeño, PostgreSQL para empresa | Solo SQLite: sin concurrencia; solo PostgreSQL: overhead en desarrollo |

---

## 9. Performance y escalabilidad

### Benchmarks de referencia (objetivos)

| Métrica | Objetivo | Herramienta |
|---------|----------|-------------|
| Latencia primer token | <3s (CPU 8-core, 16GB RAM, modelo 7B Q4) | Criterion (Rust), pytest-benchmark (Python) |
| Throughput concurrente | 50 usuarios simultáneos | Load testing |
| Uso de memoria (core) | <100MB base | Valgrind, /usr/bin/time |
| Tamaño binario | <30MB (con UI) | `ls -lh` |

### Profiling

```bash
# Rust
cargo flamegraph
cargo bench

# Python
python -m cProfile -o output.prof main.py
python -m pstats output.prof
```

---

## 10. Security checklist

- [ ] Ningún dato sensible en logs
- [ ] RBAC validado antes de cada operación sensible
- [ ] Contraseñas/tokens cifrados en reposo (AES-256)
- [ ] Comunicación IPC con TLS
- [ ] No confío en entrada del usuario (validar siempre)
- [ ] Auditoría completa de operaciones de escritura
- [ ] Errores no exponen información interna
- [ ] Dependencias auditadas (cargo audit, safety check)

---

## 11. Checklist para Pull Requests

- [ ] Código compila sin warnings: `cargo build --release`
- [ ] Tests pasan: `cargo test` + `pytest`
- [ ] Cobertura aceptable (>80% Rust, >70% Python)
- [ ] Documentación técnica en `/docs`
- [ ] Capítulo para NotebookLM en `/notebook` (si aplica)
- [ ] CHANGELOG.md actualizado
- [ ] Commit sigue Conventional Commits
- [ ] No hay `unwrap()`, `panic!()` en library code (Rust)
- [ ] Sin `print()` debug; usar logger (Python)
- [ ] Sin credenciales, keys, tokens expuestos

---

## 12. Recursos

### Documentación generada
- **[ROADMAP.md](docs/00-Project/ROADMAP.md)** — Fases y timeline
- **[ARCHITECTURE.md](docs/01-Architecture/ARCHITECTURE.md)** — Diseño del sistema
- **[DECISIONS.md](docs/01-Architecture/DECISIONS.md)** — Por qué cada decisión
- **[Libros en /notebook](notebook/)** — Material de estudio

### Referencias externas
- **Rust**: https://doc.rust-lang.org/book/, https://tokio.rs/
- **Python**: https://peps.python.org/pep-0008/, https://python-docs.readthedocs.io/
- **gRPC**: https://grpc.io/docs/what-is-grpc/
- **Clean Architecture**: https://blog.cleancoder.com/
- **Conventional Commits**: https://www.conventionalcommits.org/

---

## ¿Dudas?

Consulta primero:
1. Este archivo (CLAUDE.md)
2. [DECISIONS.md](docs/01-Architecture/DECISIONS.md)
3. Los documentos en [/docs](docs/)
4. Los libros didácticos en [/notebook](notebook/)

**Última actualización**: 2026-08-04
