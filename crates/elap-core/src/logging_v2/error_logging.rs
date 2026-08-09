/// Logging estructurado para errores con contexto completo.
///
/// Integra ElapError con tracing para capturar:
/// - Código de error (UNAUTHORIZED, AGENT_NOT_FOUND, etc.)
/// - Status HTTP (401, 404, 500, etc.)
/// - Contexto (user_id, request_id, agent_id, etc.)
/// - Stacktrace si aplica
/// - Severidad (ERROR, WARN, INFO)

use tracing::{error, warn, info, debug, Span};
use std::collections::HashMap;
use crate::error::ElapError;

/// Contexto de error para logging
#[derive(Debug, Clone)]
pub struct ErrorContext {
    /// ID único de la solicitud (para tracking)
    pub request_id: Option<String>,

    /// ID del usuario
    pub user_id: Option<String>,

    /// ID del agente (si aplica)
    pub agent_id: Option<String>,

    /// ID de la herramienta (si aplica)
    pub tool_id: Option<String>,

    /// Información adicional
    pub extra: HashMap<String, String>,
}

impl ErrorContext {
    /// Crear contexto vacío
    pub fn new() -> Self {
        Self {
            request_id: None,
            user_id: None,
            agent_id: None,
            tool_id: None,
            extra: HashMap::new(),
        }
    }

    /// Agregar request ID
    pub fn with_request_id(mut self, id: impl Into<String>) -> Self {
        self.request_id = Some(id.into());
        self
    }

    /// Agregar user ID
    pub fn with_user_id(mut self, id: impl Into<String>) -> Self {
        self.user_id = Some(id.into());
        self
    }

    /// Agregar agent ID
    pub fn with_agent_id(mut self, id: impl Into<String>) -> Self {
        self.agent_id = Some(id.into());
        self
    }

    /// Agregar tool ID
    pub fn with_tool_id(mut self, id: impl Into<String>) -> Self {
        self.tool_id = Some(id.into());
        self
    }

    /// Agregar campo personalizado
    pub fn with_extra(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.extra.insert(key.into(), value.into());
        self
    }

    /// Convertir a campos para tracing
    fn to_trace_fields(&self) -> String {
        let mut fields = vec![];

        if let Some(req_id) = &self.request_id {
            fields.push(format!("request_id={}", req_id));
        }
        if let Some(user_id) = &self.user_id {
            fields.push(format!("user_id={}", user_id));
        }
        if let Some(agent_id) = &self.agent_id {
            fields.push(format!("agent_id={}", agent_id));
        }
        if let Some(tool_id) = &self.tool_id {
            fields.push(format!("tool_id={}", tool_id));
        }

        for (key, value) in &self.extra {
            fields.push(format!("{}={}", key, value));
        }

        fields.join(" | ")
    }
}

impl Default for ErrorContext {
    fn default() -> Self {
        Self::new()
    }
}

/// Loguear error con contexto
pub fn log_error(error: &ElapError, context: Option<&ErrorContext>) {
    let code = error.error_code();
    let status = error.status_code();
    let message = error.to_log_message();

    let context_str = context
        .map(|ctx| ctx.to_trace_fields())
        .unwrap_or_default();

    match status {
        // 4xx: Errores del cliente (WARN)
        400..=499 => {
            if !context_str.is_empty() {
                warn!(
                    code = code,
                    status = status,
                    context = context_str,
                    "{}", message
                );
            } else {
                warn!(code = code, status = status, "{}", message);
            }
        }
        // 5xx: Errores del servidor (ERROR)
        500..=599 => {
            if !context_str.is_empty() {
                error!(
                    code = code,
                    status = status,
                    context = context_str,
                    "{}", message
                );
            } else {
                error!(code = code, status = status, "{}", message);
            }
        }
        // Otros
        _ => {
            if !context_str.is_empty() {
                info!(code = code, status = status, context = context_str, "{}", message);
            } else {
                info!(code = code, status = status, "{}", message);
            }
        }
    }
}

/// Loguear error con recuperación automática
pub fn log_recoverable_error(error: &ElapError, retry_attempt: u32, max_retries: u32, context: Option<&ErrorContext>) {
    let code = error.error_code();
    let message = error.to_log_message();

    let context_str = context
        .map(|ctx| ctx.to_trace_fields())
        .unwrap_or_default();

    let retry_info = format!("attempt {}/{}", retry_attempt, max_retries);

    if !context_str.is_empty() {
        warn!(
            code = code,
            retry_attempt = retry_attempt,
            max_retries = max_retries,
            context = context_str,
            "{} - {}", message, retry_info
        );
    } else {
        warn!(
            code = code,
            retry_attempt = retry_attempt,
            max_retries = max_retries,
            "{} - {}", message, retry_info
        );
    }
}

/// Loguear operación exitosa después de retry
pub fn log_success_after_retry(attempt: u32, duration_ms: u64, context: Option<&ErrorContext>) {
    let context_str = context
        .map(|ctx| ctx.to_trace_fields())
        .unwrap_or_default();

    if !context_str.is_empty() {
        info!(
            attempt = attempt,
            duration_ms = duration_ms,
            context = context_str,
            "Operation succeeded after retry"
        );
    } else {
        info!(
            attempt = attempt,
            duration_ms = duration_ms,
            "Operation succeeded after retry"
        );
    }
}

/// Loguear handler request/response
pub fn log_handler(method: &str, path: &str, status: u16, duration_ms: u64, context: Option<&ErrorContext>) {
    let context_str = context
        .map(|ctx| ctx.to_trace_fields())
        .unwrap_or_default();

    let level = match status {
        200..=299 => "info",
        400..=499 => "warn",
        500..=599 => "error",
        _ => "info",
    };

    match level {
        "info" => {
            if !context_str.is_empty() {
                info!(
                    method = method,
                    path = path,
                    status = status,
                    duration_ms = duration_ms,
                    context = context_str,
                    "{} {} -> {}", method, path, status
                );
            } else {
                info!(
                    method = method,
                    path = path,
                    status = status,
                    duration_ms = duration_ms,
                    "{} {} -> {}", method, path, status
                );
            }
        }
        "warn" => {
            if !context_str.is_empty() {
                warn!(
                    method = method,
                    path = path,
                    status = status,
                    duration_ms = duration_ms,
                    context = context_str,
                    "{} {} -> {}", method, path, status
                );
            } else {
                warn!(
                    method = method,
                    path = path,
                    status = status,
                    duration_ms = duration_ms,
                    "{} {} -> {}", method, path, status
                );
            }
        }
        "error" => {
            if !context_str.is_empty() {
                error!(
                    method = method,
                    path = path,
                    status = status,
                    duration_ms = duration_ms,
                    context = context_str,
                    "{} {} -> {}", method, path, status
                );
            } else {
                error!(
                    method = method,
                    path = path,
                    status = status,
                    duration_ms = duration_ms,
                    "{} {} -> {}", method, path, status
                );
            }
        }
        _ => {}
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_context_with_request_id() {
        let ctx = ErrorContext::new().with_request_id("req-123");
        assert_eq!(ctx.request_id, Some("req-123".to_string()));
    }

    #[test]
    fn test_error_context_with_user_id() {
        let ctx = ErrorContext::new().with_user_id("user-456");
        assert_eq!(ctx.user_id, Some("user-456".to_string()));
    }

    #[test]
    fn test_error_context_chaining() {
        let ctx = ErrorContext::new()
            .with_request_id("req-123")
            .with_user_id("user-456")
            .with_agent_id("agent-789");

        assert_eq!(ctx.request_id, Some("req-123".to_string()));
        assert_eq!(ctx.user_id, Some("user-456".to_string()));
        assert_eq!(ctx.agent_id, Some("agent-789".to_string()));
    }

    #[test]
    fn test_error_context_to_trace_fields() {
        let ctx = ErrorContext::new()
            .with_request_id("req-123")
            .with_user_id("user-456");

        let fields = ctx.to_trace_fields();
        assert!(fields.contains("request_id=req-123"));
        assert!(fields.contains("user_id=user-456"));
    }

    #[test]
    fn test_error_context_extra_fields() {
        let ctx = ErrorContext::new()
            .with_extra("operation", "create_agent")
            .with_extra("duration_ms", "1500");

        let fields = ctx.to_trace_fields();
        assert!(fields.contains("operation=create_agent"));
        assert!(fields.contains("duration_ms=1500"));
    }
}
