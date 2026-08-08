# Fase 5: Error Handling — Enterprise-Grade Error Framework

**Estado**: 🚀 En progreso (iniciada 2026-08-08)  
**Duración**: 7 días (entrega 2026-08-15)  
**Equipo**: Backend (Rust) + IA (Python) + Frontend (React)

---

## 🎯 Visión

En una plataforma empresarial, los errores no son excepciones — son el camino a la resiliencia.

ELAP implementará un **framework de error handling** que:

```
Errores internos (técnicos, detallados)
                 ↓
           [Framework]
                 ↓
Mensajes al usuario (claros, sin tecnicismos)
```

**Ejemplo**:

**Interno**:
```
❌ [ERROR] gRPC call to Python runtime failed
   • RequestID: abc-123-def-456
   • Endpoint: localhost:50051/GenerateDocument
   • Timeout: 30000ms
   • Stacktrace: [...]
   • Action: Retry in 5s
```

**Usuario**:
```
❌ El procesamiento tardó demasiado. Intenta con una solicitud más simple.
```

---

## 📋 Contenido de esta carpeta

```
docs/05-Error-Handling/
├── README.md           # Este archivo
├── PLAN.md            # Plan de implementación detallado
├── GUIDE.md           # Guía de uso (durante/después de implementación)
└── CHECKLIST.md       # Checklist de finalización
```

---

## 🔧 Estructura a implementar

### Rust (`crates/elap-core/src/errors/`)

```rust
pub enum ElapError {
    // HTTP/API
    Unauthorized(String),        // 401
    Forbidden(String),           // 403
    NotFound(String),            // 404
    ValidationError(String),     // 400
    
    // Agent
    AgentNotFound(String),
    AgentExecutionFailed(String),
    
    // Tools
    ToolNotFound(String),
    ToolExecutionFailed(String),
    
    // Database
    DatabaseError(String),
    
    // Security
    PermissionDenied(String),
    
    // System
    InternalError(String),
}

impl ElapError {
    pub fn status_code(&self) -> u16
    pub fn to_user_message(&self) -> String     // SIN detalles técnicos
    pub fn to_log_message(&self) -> String      // CON detalles técnicos
}
```

### Python (`python/src/elap_ai/errors.py`)

```python
class ElapException(Exception):
    code: str = "INTERNAL_ERROR"
    status_code: int = 500
    user_message: str = "Error interno"

class PermissionDenied(ElapException):
    code = "PERMISSION_DENIED"
    status_code = 403

class ValidationError(ElapException):
    code = "VALIDATION_ERROR"
    status_code = 400

# ...
```

---

## 🎬 Fases de la implementación

### ✅ Semana 1 (2026-08-08 a 2026-08-15)

| Día | Tarea | Archivos |
|-----|-------|----------|
| 1 (08) | Error types definition | `crates/elap-core/src/errors/` + `python/src/elap_ai/errors.py` |
| 2 (09) | Error propagation | Updated handlers + agents |
| 3-4 (10-11) | Logging + user messages | `logging_v2/` + `error_messages.py` |
| 5 (12) | Error recovery | Retry + fallback logic |
| 6 (13) | Tests + docs | Tests + GUIDE.md |
| 7 (15) | Final review | CHANGELOG + commit |

---

## 🔍 Ejemplos de implementación

### Antes (sin framework)

```rust
// ❌ Vago, no recoverable
fn execute_tool(&self, id: &str) -> Result<String> {
    let tool = self.tools.get(id)?;
    tool.run()?;
    Ok("Done".to_string())
}

// Usuario ve: "Error"
```

### Después (con framework)

```rust
// ✅ Claro, context-rich, recoverable
pub fn execute_tool(&self, id: &str) -> Result<Output, ElapError> {
    let tool = self.registry.get(id)
        .ok_or_else(|| ElapError::ToolNotFound(
            format!("Tool '{}' not registered in {}", id, self.registry_id)
        ))?;
    
    execute_with_retry(
        || Box::pin(tool.run()),
        max_retries: 3,
    ).await
        .map_err(|e| ElapError::ToolExecutionFailed(format!(
            "After 3 retries: {}",
            e
        )))
}

// Usuario ve: "La herramienta no está disponible" (si no existe)
// o "Retry automático en 5 segundos" (si timeout)
```

---

## 📊 Objetivos de calidad

| Métrica | Objetivo |
|---------|----------|
| **Test coverage** | >85% en error paths |
| **User message clarity** | 0 technical jargon |
| **Logging completeness** | RequestID + context en todos los logs |
| **Recovery rate** | 80%+ de errores recoverable automáticamente |
| **Documentation** | Cada error type documentado con ejemplo |

---

## 📚 Documentación relacionada

- **[PLAN.md](PLAN.md)** — Plan detallado (tiempos, archivos, entregables)
- **[GUIDE.md](GUIDE.md)** — Cómo usar el framework (se completa durante fase)
- **[CHECKLIST.md](CHECKLIST.md)** — Checklist de finalización

---

## 🚀 Cómo empezar

### Para el equipo Rust
1. Lee [PLAN.md](PLAN.md) sección "Rust: Custom Error Types"
2. Abre `crates/elap-core/src/error.rs`
3. Ejecuta: `cargo test error::`

### Para el equipo Python
1. Lee [PLAN.md](PLAN.md) sección "Python: Exception Hierarchy"
2. Abre `python/src/elap_ai/errors.py`
3. Ejecuta: `python -m pytest tests/test_errors.py`

### Para el equipo Frontend
1. Lee [PLAN.md](PLAN.md) sección "User-Facing Error Messages"
2. Prepara `web/src/error-handler.ts`
3. Intégra con `web/src/components/tabs/ChatTab.tsx`

---

## 💾 Repositorio de decisiones

### ¿Por qué custom error types?
**Razón**: Errores genéricos (`.unwrap()`, `panic!()`) no dan contexto. Custom types permiten:
- ✅ Serializar para enviar a frontend
- ✅ Loguear con contexto (RequestID, usuario, etc.)
- ✅ Traducir a mensajes claros para usuario
- ✅ Implementar recovery automático

### ¿Por qué separar user messages de technical messages?
**Razón**: Seguridad + UX
- ❌ No revelar detalles internos (prevenir information disclosure)
- ✅ Usuario ve algo claro y accionable

### ¿Por qué retry automático?
**Razón**: Resiliencia
- Network timeout → retry en 5s
- Database lock → retry en 500ms
- Rate limiting → retry después de cooldown

---

## 🔗 Integración con otras fases

| Fase | Integración |
|------|-------------|
| Fase 4 (Document Engine) | Error recovery para document generation |
| Fase 6 (Plugin Runtime) | Error handling para plugins dinámicos |
| Fase 7+ (Testing) | Testy errors, edge cases |

---

## 🎓 Lectura recomendada (antes de empezar)

- [Rust Book — Result Type](https://doc.rust-lang.org/book/ch09-00-error-handling.html)
- [Python PEP 3134 — Exception Chaining](https://peps.python.org/pep-3134/)
- [OWASP — Error Handling Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html)
- [Google Cloud — Error Reporting Best Practices](https://cloud.google.com/logging/docs/reference/error-reporting)

---

**¿Preguntas?** Consulta [PLAN.md](PLAN.md) o abre un issue.

---

**Última actualización**: 2026-08-08  
**Próxima revisión**: 2026-08-15 (cuando fase se complete)
