# Fase 5: Error Handling — Plan de Implementación

**Versión**: 1.0  
**Inicio**: 2026-08-08  
**Duración estimada**: 1 semana  
**Entrega**: 2026-08-15  

---

## 📋 Resumen ejecutivo

Implementar un **framework de error handling robusto y consistente** en Rust y Python.

**Objetivo**: Ningún error debe llegar al usuario sin contexto claro. Todos los errores deben:
- ✅ Loguear información técnica completa (interno)
- ✅ Mostrar mensajes claros al usuario (frontend)
- ✅ Trazarse en auditoría (compliance)
- ✅ Permitir recuperación automática donde sea posible

---

## 🎯 Entregables

### 1️⃣ Rust: Custom Error Types (~500 LOC)

**Archivos**:
- `crates/elap-core/src/error.rs` → Mejorar `ElapError`
- `crates/elap-core/src/errors/` (carpeta nueva)
  - `mod.rs`
  - `api_errors.rs` (errores HTTP)
  - `agent_errors.rs` (errores de agents)
  - `tool_errors.rs` (errores de tools)
  - `db_errors.rs` (errores de DB)

**Tipos a definir**:

```rust
#[derive(Debug)]
pub enum ElapError {
    // API
    Unauthorized(String),           // 401
    Forbidden(String),              // 403
    NotFound(String),               // 404
    ValidationError(String),        // 400
    Conflict(String),               // 409
    
    // Agent
    AgentNotFound(String),
    AgentExecutionFailed(String),
    InvalidAgentState(String),
    
    // Tools
    ToolNotFound(String),
    ToolExecutionFailed(String),
    ToolTimeout(String),
    
    // Database
    DatabaseError(String),
    ConnectionPoolExhausted,
    TransactionFailed(String),
    
    // Security
    PermissionDenied(String),
    AuthenticationFailed(String),
    
    // System
    InternalError(String),
    NotImplemented(String),
}

impl ElapError {
    pub fn status_code(&self) -> u16 { /* ... */ }
    pub fn to_user_message(&self) -> String { /* ... */ }  // Sin detalles técnicos
    pub fn to_log_message(&self) -> String { /* ... */ }   // Con detalles técnicos
}
```

**Tests**: 40+ test cases

---

### 2️⃣ Python: Exception Hierarchy (~300 LOC)

**Archivo**: `python/src/elap_ai/errors.py`

```python
class ElapException(Exception):
    """Base exception"""
    code: str = "INTERNAL_ERROR"
    status_code: int = 500
    user_message: str = "Error interno del sistema"
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class ValidationError(ElapException):
    code = "VALIDATION_ERROR"
    status_code = 400

class PermissionDenied(ElapException):
    code = "PERMISSION_DENIED"
    status_code = 403

class NotFound(ElapException):
    code = "NOT_FOUND"
    status_code = 404

class AgentError(ElapException):
    code = "AGENT_ERROR"
    status_code = 500

class ToolError(ElapException):
    code = "TOOL_ERROR"
    status_code = 500

class DocumentGenerationError(ElapException):
    code = "DOCUMENT_GENERATION_ERROR"
    status_code = 500
```

**Tests**: 30+ test cases

---

### 3️⃣ Error Propagation (~400 LOC)

**Rust**:
- `?` operator for Result propagation
- `.map_err()` para convertir errores externos
- Custom context con `.context()` (anyhow-style)

**Python**:
- `raise` con mensajes contextuales
- `try/except/finally` patterns
- Logging antes de re-raise

**Ejemplo Rust**:
```rust
pub fn execute_tool(tool_id: &str, params: &ToolParams) -> Result<Output, ElapError> {
    let tool = self.registry.get(tool_id)
        .ok_or_else(|| ElapError::ToolNotFound(format!("Tool {} not found", tool_id)))?;
    
    tool.validate(params)
        .map_err(|e| ElapError::ValidationError(e.to_string()))?;
    
    tool.execute(params)
        .map_err(|e| ElapError::ToolExecutionFailed(e.to_string()))
}
```

**Ejemplo Python**:
```python
async def generate_document(self, template_id: str, data: dict) -> str:
    try:
        template = self.get_template(template_id)
        if not template:
            raise NotFound(f"Template {template_id} not found")
        
        result = await template.render(data)
        logger.info(f"✅ Document generated: {template_id}")
        return result
    except DocumentGenerationError:
        raise  # Re-raise conocidos
    except Exception as e:
        logger.error(f"Unexpected error in document generation: {e}")
        raise ElapException(f"Failed to generate document: {e}")
```

---

### 4️⃣ Error Logging (~300 LOC)

**Niveles**:
- `ERROR`: Errores que requieren atención inmediata
- `WARN`: Errores recuperables (retry automático, fallback, etc.)
- `INFO`: Operaciones normales completadas
- `DEBUG`: Info para debugging (requestID, stacktrace, etc.)

**Información a loguear**:
```
❌ [ERROR] Tool execution failed
   ├── Context: user=user123, tool_id=web_search, request_id=abc-123
   ├── Error code: TOOL_EXECUTION_FAILED
   ├── Message: Timeout after 30 seconds
   ├── Stacktrace: (python/rust stacktrace)
   ├── Timestamp: 2026-08-08T10:30:45.123Z
   └── Action: Automatic retry in 5 seconds | Manual action required
```

**Archivos**:
- [crates/elap-core/src/logging_v2/](crates/elap-core/src/logging_v2/) (Rust — ya existe)
- `python/src/elap_ai/logging_config.py` (nuevo)

---

### 5️⃣ User-Facing Error Messages (~200 LOC)

**Principios**:
- ❌ NO: "Failed to query database connection pool (connection timeout)"
- ✅ SÍ: "El sistema está saturado. Intenta en unos segundos."

- ❌ NO: "Agent task timeout after 300000ms waiting for gRPC response"
- ✅ SÍ: "El procesamiento tardó demasiado. Intenta con una solicitud más simple."

**Archivo**: `python/src/elap_ai/error_messages.py`

```python
ERROR_MESSAGES = {
    "AGENT_TIMEOUT": "El procesamiento tardó demasiado. Intenta con una solicitud más simple.",
    "TOOL_NOT_FOUND": "La herramienta solicitada no está disponible.",
    "PERMISSION_DENIED": "No tienes permiso para realizar esta acción.",
    "DATABASE_ERROR": "Error temporal en el sistema. Recargando...",
    "INVALID_INPUT": "La solicitud contiene datos inválidos. Revisa el formato.",
    "INTERNAL_ERROR": "Error interno. El equipo técnico ha sido notificado.",
}

def get_user_message(error_code: str) -> str:
    return ERROR_MESSAGES.get(error_code, "Algo salió mal. Intenta de nuevo.")
```

**Flujo Frontend**:
```tsx
// ChatTab.tsx
catch (error) {
    const userMessage = error.userMessage || "Algo salió mal.";
    setMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ ${userMessage}`,
        isError: true
    }]);
    
    // Log internamente
    console.error('[DEBUG]', error.details);
}
```

---

### 6️⃣ Error Recovery (~300 LOC)

**Estrategias**:

| Escenario | Estrategia |
|-----------|-----------|
| Tool timeout | Retry automático (3x, con backoff exponencial) |
| Database connection lost | Reconnect automático |
| gRPC unavailable | Fallback a modo local (si aplica) |
| Autenticación expirada | Refresh token automático |
| Rate limiting | Queue + retry después de cooldown |

**Ejemplo**:
```rust
pub async fn execute_with_retry<F, T>(
    f: F,
    max_retries: u32,
) -> Result<T, ElapError>
where
    F: Fn() -> BoxFuture<'static, Result<T, ElapError>>,
{
    let mut attempt = 0;
    loop {
        match f().await {
            Ok(result) => return Ok(result),
            Err(e) if attempt < max_retries => {
                attempt += 1;
                let backoff = Duration::from_millis(100 * 2u64.pow(attempt));
                warn!("Retry attempt {} after {:?}", attempt, backoff);
                sleep(backoff).await;
            }
            Err(e) => return Err(e),
        }
    }
}
```

---

### 7️⃣ Tests (~200+ casos)

**Rust**:
```rust
#[test]
fn test_error_serialization() { /* ... */ }

#[test]
fn test_error_propagation() { /* ... */ }

#[tokio::test]
async fn test_retry_logic() { /* ... */ }

#[test]
fn test_user_message_no_technical_details() { /* ... */ }
```

**Python**:
```python
def test_exception_hierarchy():
    assert issubclass(PermissionDenied, ElapException)
    assert PermissionDenied("test").status_code == 403

async def test_error_recovery_with_retry():
    # Simulate 2 failures, then success
    ...
```

**Cobertura**: >85% en error paths

---

## 📚 Documentación

### 1. Error Handling Guide (`docs/05-Error-Handling/GUIDE.md`)
- Cómo crear errores nuevos
- Cómo loguear correctamente
- Cómo mostrar mensajes al usuario
- Patrones de recuperación

### 2. Libro 07 para NotebookLM (`notebook/libro-07-error-handling.md`)
- Capítulo 1: Errores en sistemas distribuidos
- Capítulo 2: Error handling en Rust
- Capítulo 3: Error handling en Python
- Capítulo 4: Logging y auditoría
- Capítulo 5: Testing de error cases

---

## 🔄 Actualizaciones necesarias

### CHANGELOG.md
```markdown
## [1.6.0] - 2026-08-15

### Added
- Custom error types (Rust + Python)
- Error propagation framework
- User-facing error messages
- Automatic error recovery (retry, fallback)
- Advanced error logging with context
- Error handling tests (200+ cases)
```

### ROADMAP.md
```markdown
### 5 - Error Handling ✅ (2026-08-15)
- Custom error types (Rust + Python)
- Error propagation
- Error recovery
- Error logging
- User-facing error messages
- Tests (>85% coverage)
- Error Handling Guide
- Libro 07 para NotebookLM
```

---

## 🎬 Orden de implementación

1. **Día 1** (2026-08-08):
   - ✅ Definir custom error types (Rust)
   - ✅ Definir exception hierarchy (Python)

2. **Día 2** (2026-08-09):
   - ✅ Implementar error propagation en Rust
   - ✅ Implementar error propagation en Python

3. **Día 3-4** (2026-08-10 a 2026-08-11):
   - ✅ Mejorar logging con contexto
   - ✅ Implementar user messages
   - ✅ Comenzar tests

4. **Día 5** (2026-08-12):
   - ✅ Error recovery (retry, fallback)
   - ✅ Completar tests (>85%)

5. **Día 6** (2026-08-13):
   - ✅ Documentación (Error Handling Guide)
   - ✅ Libro 07 para NotebookLM

6. **Día 7** (2026-08-15):
   - ✅ Review final
   - ✅ Actualizar CHANGELOG + ROADMAP
   - ✅ Commit final

---

## ✅ Checklist de finalización

- [ ] Custom error types definidos en Rust
- [ ] Exception hierarchy definida en Python
- [ ] Error propagation funcional en ambos lenguajes
- [ ] Logging de errores con contexto completo
- [ ] User messages claros y sin detalles técnicos
- [ ] Recovery automática (retry, fallback)
- [ ] Tests >85% cobertura
- [ ] Error Handling Guide escrito
- [ ] Libro 07 para NotebookLM completado
- [ ] CHANGELOG.md actualizado
- [ ] ROADMAP.md actualizado
- [ ] TREE.md actualizado
- [ ] Commit Conventional Commits (español)

---

**Próximo**: Fase 6 - Plugin Runtime (después del 2026-08-15)
