use std::fmt;
use std::error::Error;

/// Errores empresariales de ELAP Core.
///
/// Cada variante representa una categoría de error específica con:
/// - Código interno para logging y auditoría
/// - Status HTTP automático para API responses
/// - Mensaje para usuario (sin detalles técnicos)
/// - Contexto técnico completo para debugging
#[derive(Debug, Clone)]
pub enum ElapError {
    // === API / HTTP ===
    /// 401 - Autenticación requerida
    Unauthorized(String),

    /// 403 - Permiso denegado
    Forbidden(String),

    /// 404 - Recurso no encontrado
    NotFound(String),

    /// 400 - Datos de entrada inválidos
    ValidationError(String),

    /// 409 - Conflicto (recurso existe, estado inconsistente)
    Conflict(String),

    // === Agentes ===
    /// Agente no encontrado en registry
    AgentNotFound(String),

    /// Ejecución de agente falló
    AgentExecutionFailed(String),

    /// Estado inválido del agente
    InvalidAgentState(String),

    /// Timeout en ejecución de agente
    AgentTimeout(String),

    // === Herramientas ===
    /// Herramienta no registrada
    ToolNotFound(String),

    /// Ejecución de herramienta falló
    ToolExecutionFailed(String),

    /// Timeout en herramienta
    ToolTimeout(String),

    /// Parámetros inválidos para herramienta
    ToolValidationFailed(String),

    // === Base de datos ===
    /// Error de base de datos
    DatabaseError(String),

    /// Pool de conexiones exhausto
    ConnectionPoolExhausted,

    /// Transacción falló
    TransactionFailed(String),

    // === Seguridad ===
    /// Permiso requerido no otorgado (RBAC)
    PermissionDenied(String),

    /// Autenticación falló
    AuthenticationFailed(String),

    /// Auditoría: operación no permitida por política
    PolicyViolation(String),

    // === Configuración ===
    /// Error al cargar configuración
    ConfigError(String),

    /// Validación de configuración falló
    ConfigValidationFailed(String),

    // === I/O ===
    /// Error de I/O (archivo, red, etc.)
    IoError {
        context: String,
        source: String,
    },

    // === Procesos ===
    /// Error al spawnar proceso
    ProcessSpawnFailed(String),

    /// Proceso terminó con error
    ProcessExitFailed(String),

    // === gRPC / IPC ===
    /// Error en llamada gRPC
    GrpcError(String),

    /// Timeout en gRPC
    GrpcTimeout(String),

    /// Conexión no disponible
    ConnectionUnavailable(String),

    /// Servicio no disponible (503)
    ServiceUnavailable(String),

    // === Sistema ===
    /// Error interno no categorizado (debería ser raro)
    InternalError(String),

    /// Funcionalidad no implementada
    NotImplemented(String),
}

impl ElapError {
    /// Código HTTP para esta clase de error
    pub fn status_code(&self) -> u16 {
        match self {
            ElapError::Unauthorized(_) => 401,
            ElapError::Forbidden(_) => 403,
            ElapError::NotFound(_) => 404,
            ElapError::AgentNotFound(_) => 404,
            ElapError::ToolNotFound(_) => 404,
            ElapError::ValidationError(_) => 400,
            ElapError::ToolValidationFailed(_) => 400,
            ElapError::Conflict(_) => 409,
            ElapError::ConnectionPoolExhausted => 503,
            ElapError::ConnectionUnavailable(_) => 503,
            ElapError::ServiceUnavailable(_) => 503,
            ElapError::GrpcTimeout(_) => 504,
            ElapError::AgentTimeout(_) => 504,
            ElapError::ToolTimeout(_) => 504,
            ElapError::NotImplemented(_) => 501,
            _ => 500,
        }
    }

    /// Código de error para logging e API responses
    pub fn error_code(&self) -> &'static str {
        match self {
            ElapError::Unauthorized(_) => "UNAUTHORIZED",
            ElapError::Forbidden(_) => "FORBIDDEN",
            ElapError::NotFound(_) => "NOT_FOUND",
            ElapError::ValidationError(_) => "VALIDATION_ERROR",
            ElapError::Conflict(_) => "CONFLICT",
            ElapError::AgentNotFound(_) => "AGENT_NOT_FOUND",
            ElapError::AgentExecutionFailed(_) => "AGENT_EXECUTION_FAILED",
            ElapError::InvalidAgentState(_) => "INVALID_AGENT_STATE",
            ElapError::AgentTimeout(_) => "AGENT_TIMEOUT",
            ElapError::ToolNotFound(_) => "TOOL_NOT_FOUND",
            ElapError::ToolExecutionFailed(_) => "TOOL_EXECUTION_FAILED",
            ElapError::ToolTimeout(_) => "TOOL_TIMEOUT",
            ElapError::ToolValidationFailed(_) => "TOOL_VALIDATION_FAILED",
            ElapError::DatabaseError(_) => "DATABASE_ERROR",
            ElapError::ConnectionPoolExhausted => "CONNECTION_POOL_EXHAUSTED",
            ElapError::ServiceUnavailable(_) => "SERVICE_UNAVAILABLE",
            ElapError::TransactionFailed(_) => "TRANSACTION_FAILED",
            ElapError::PermissionDenied(_) => "PERMISSION_DENIED",
            ElapError::AuthenticationFailed(_) => "AUTHENTICATION_FAILED",
            ElapError::PolicyViolation(_) => "POLICY_VIOLATION",
            ElapError::ConfigError(_) => "CONFIG_ERROR",
            ElapError::ConfigValidationFailed(_) => "CONFIG_VALIDATION_FAILED",
            ElapError::IoError { .. } => "IO_ERROR",
            ElapError::ProcessSpawnFailed(_) => "PROCESS_SPAWN_FAILED",
            ElapError::ProcessExitFailed(_) => "PROCESS_EXIT_FAILED",
            ElapError::GrpcError(_) => "GRPC_ERROR",
            ElapError::GrpcTimeout(_) => "GRPC_TIMEOUT",
            ElapError::ConnectionUnavailable(_) => "CONNECTION_UNAVAILABLE",
            ElapError::InternalError(_) => "INTERNAL_ERROR",
            ElapError::NotImplemented(_) => "NOT_IMPLEMENTED",
        }
    }

    /// Mensaje para usuario (SIN detalles técnicos, SIN paths, SIN comandos)
    /// Siempre es actionable y entendible para usuario final
    pub fn to_user_message(&self) -> String {
        match self {
            ElapError::Unauthorized(_) =>
                "Necesitas iniciar sesión para continuar.".to_string(),
            ElapError::Forbidden(_) =>
                "No tienes permiso para realizar esta acción.".to_string(),
            ElapError::NotFound(_) =>
                "El recurso solicitado no existe.".to_string(),
            ElapError::ValidationError(msg) =>
                format!("Datos inválidos: {}. Revisa el formato.", msg),
            ElapError::Conflict(_) =>
                "La operación conflictúa con el estado actual. Intenta de nuevo.".to_string(),
            ElapError::AgentNotFound(_) =>
                "El agente solicitado no está disponible.".to_string(),
            ElapError::AgentExecutionFailed(_) =>
                "El procesamiento falló. Intenta con una solicitud más simple.".to_string(),
            ElapError::InvalidAgentState(_) =>
                "El agente está en un estado inconsistente. Recarga la página.".to_string(),
            ElapError::AgentTimeout(_) =>
                "El procesamiento tardó demasiado. Intenta de nuevo.".to_string(),
            ElapError::ToolNotFound(_) =>
                "La herramienta solicitada no está disponible. Intenta con otra herramienta.".to_string(),
            ElapError::ToolExecutionFailed(_) =>
                "La herramienta no pudo completarse. Intenta de nuevo.".to_string(),
            ElapError::ToolTimeout(_) =>
                "La herramienta tardó demasiado. Intenta con parámetros más simples.".to_string(),
            ElapError::ToolValidationFailed(_) =>
                "Los parámetros de la herramienta son inválidos.".to_string(),
            ElapError::DatabaseError(_) =>
                "Error temporal en el sistema. Recargando...".to_string(),
            ElapError::ConnectionPoolExhausted =>
                "El sistema está sobrecargado. Intenta en unos segundos.".to_string(),
            ElapError::TransactionFailed(_) =>
                "La operación no se pudo completar. Intenta de nuevo.".to_string(),
            ElapError::PermissionDenied(_) =>
                "No tienes permisos suficientes.".to_string(),
            ElapError::AuthenticationFailed(_) =>
                "La autenticación falló. Intenta de nuevo.".to_string(),
            ElapError::PolicyViolation(_) =>
                "Esta operación no está permitida por política.".to_string(),
            ElapError::ConfigError(_) =>
                "Error de configuración del sistema. Contacta soporte.".to_string(),
            ElapError::ConfigValidationFailed(_) =>
                "Configuración inválida. Contacta soporte.".to_string(),
            ElapError::IoError { .. } =>
                "Error de sistema de archivos. Intenta de nuevo.".to_string(),
            ElapError::ProcessSpawnFailed(_) =>
                "No se pudo iniciar el proceso. Intenta de nuevo.".to_string(),
            ElapError::ProcessExitFailed(_) =>
                "El proceso terminó inesperadamente.".to_string(),
            ElapError::GrpcError(_) =>
                "Error en comunicación del sistema. Intenta de nuevo.".to_string(),
            ElapError::GrpcTimeout(_) =>
                "La comunicación tardó demasiado. Intenta de nuevo.".to_string(),
            ElapError::ConnectionUnavailable(_) =>
                "Servicio no disponible. Intenta en unos segundos.".to_string(),
            ElapError::ServiceUnavailable(_) =>
                "El servicio está temporalmente no disponible. Intenta más tarde.".to_string(),
            ElapError::InternalError(_) =>
                "Error interno. El equipo técnico ha sido notificado.".to_string(),
            ElapError::NotImplemented(_) =>
                "Esta funcionalidad aún no está disponible.".to_string(),
        }
    }

    /// Mensaje para logs (CON detalles técnicos completos)
    /// Para uso interno de desarrolladores y sistemas de monitoreo
    pub fn to_log_message(&self) -> String {
        match self {
            ElapError::Unauthorized(msg) =>
                format!("Unauthorized: {}", msg),
            ElapError::Forbidden(msg) =>
                format!("Forbidden: {}", msg),
            ElapError::NotFound(msg) =>
                format!("NotFound: {}", msg),
            ElapError::ValidationError(msg) =>
                format!("ValidationError: {}", msg),
            ElapError::Conflict(msg) =>
                format!("Conflict: {}", msg),
            ElapError::AgentNotFound(msg) =>
                format!("AgentNotFound: {}", msg),
            ElapError::AgentExecutionFailed(msg) =>
                format!("AgentExecutionFailed: {}", msg),
            ElapError::InvalidAgentState(msg) =>
                format!("InvalidAgentState: {}", msg),
            ElapError::AgentTimeout(msg) =>
                format!("AgentTimeout: {} (exceeded max duration)", msg),
            ElapError::ToolNotFound(msg) =>
                format!("ToolNotFound: {}", msg),
            ElapError::ToolExecutionFailed(msg) =>
                format!("ToolExecutionFailed: {}", msg),
            ElapError::ToolTimeout(msg) =>
                format!("ToolTimeout: {} (exceeded max duration)", msg),
            ElapError::ToolValidationFailed(msg) =>
                format!("ToolValidationFailed: {}", msg),
            ElapError::DatabaseError(msg) =>
                format!("DatabaseError: {}", msg),
            ElapError::ConnectionPoolExhausted =>
                "ConnectionPoolExhausted: No available connections in pool".to_string(),
            ElapError::TransactionFailed(msg) =>
                format!("TransactionFailed: {}", msg),
            ElapError::PermissionDenied(msg) =>
                format!("PermissionDenied (RBAC): {}", msg),
            ElapError::AuthenticationFailed(msg) =>
                format!("AuthenticationFailed: {}", msg),
            ElapError::PolicyViolation(msg) =>
                format!("PolicyViolation (AUDIT): {}", msg),
            ElapError::ConfigError(msg) =>
                format!("ConfigError: {}", msg),
            ElapError::ConfigValidationFailed(msg) =>
                format!("ConfigValidationFailed: {}", msg),
            ElapError::IoError { context, source } =>
                format!("IoError in '{}': {}", context, source),
            ElapError::ProcessSpawnFailed(msg) =>
                format!("ProcessSpawnFailed: {}", msg),
            ElapError::ProcessExitFailed(msg) =>
                format!("ProcessExitFailed: {}", msg),
            ElapError::GrpcError(msg) =>
                format!("GrpcError: {}", msg),
            ElapError::GrpcTimeout(msg) =>
                format!("GrpcTimeout: {} (exceeded max duration)", msg),
            ElapError::ConnectionUnavailable(msg) =>
                format!("ConnectionUnavailable: {}", msg),
            ElapError::ServiceUnavailable(msg) =>
                format!("ServiceUnavailable: {}", msg),
            ElapError::InternalError(msg) =>
                format!("InternalError (unexpected): {}", msg),
            ElapError::NotImplemented(msg) =>
                format!("NotImplemented: {}", msg),
        }
    }
}

impl fmt::Display for ElapError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}] {}", self.error_code(), self.to_log_message())
    }
}

impl Error for ElapError {}

impl From<std::io::Error> for ElapError {
    fn from(err: std::io::Error) -> Self {
        ElapError::IoError {
            context: "filesystem".to_string(),
            source: err.to_string(),
        }
    }
}

impl From<sqlx::Error> for ElapError {
    fn from(err: sqlx::Error) -> Self {
        match err {
            sqlx::Error::PoolTimedOut => ElapError::ConnectionPoolExhausted,
            sqlx::Error::PoolClosed => ElapError::ConnectionUnavailable("Pool closed".to_string()),
            _ => ElapError::DatabaseError(err.to_string()),
        }
    }
}

pub type ResultadoElap<T> = Result<T, ElapError>;

#[cfg(test)]
mod tests {
    use super::*;

    // === HTTP Status Codes ===
    #[test]
    fn test_http_status_codes() {
        assert_eq!(ElapError::Unauthorized("test".into()).status_code(), 401);
        assert_eq!(ElapError::Forbidden("test".into()).status_code(), 403);
        assert_eq!(ElapError::NotFound("test".into()).status_code(), 404);
        assert_eq!(ElapError::ValidationError("test".into()).status_code(), 400);
        assert_eq!(ElapError::Conflict("test".into()).status_code(), 409);
        assert_eq!(ElapError::ToolValidationFailed("test".into()).status_code(), 400);
        assert_eq!(ElapError::ConnectionPoolExhausted.status_code(), 503);
        assert_eq!(ElapError::GrpcTimeout("test".into()).status_code(), 504);
        assert_eq!(ElapError::NotImplemented("test".into()).status_code(), 501);
        assert_eq!(ElapError::InternalError("test".into()).status_code(), 500);
    }

    // === Error Codes ===
    #[test]
    fn test_error_codes() {
        assert_eq!(ElapError::Unauthorized("test".into()).error_code(), "UNAUTHORIZED");
        assert_eq!(ElapError::Forbidden("test".into()).error_code(), "FORBIDDEN");
        assert_eq!(ElapError::AgentNotFound("test".into()).error_code(), "AGENT_NOT_FOUND");
        assert_eq!(ElapError::ToolNotFound("test".into()).error_code(), "TOOL_NOT_FOUND");
        assert_eq!(ElapError::PermissionDenied("test".into()).error_code(), "PERMISSION_DENIED");
        assert_eq!(ElapError::DatabaseError("test".into()).error_code(), "DATABASE_ERROR");
    }

    // === User Messages (no technical details) ===
    #[test]
    fn test_user_messages_no_technical_details() {
        let msg = ElapError::Unauthorized("user123".into()).to_user_message();
        assert!(!msg.contains("user123"));
        assert!(msg.contains("iniciar sesión"));

        let msg = ElapError::NotFound("resource_xyz".into()).to_user_message();
        assert!(!msg.contains("resource_xyz"));
        assert!(msg.contains("no existe"));

        let msg = ElapError::AgentTimeout("30s".into()).to_user_message();
        assert!(!msg.contains("30s"));
        assert!(msg.contains("Intenta"));
    }

    #[test]
    fn test_user_messages_are_actionable() {
        let messages = vec![
            ElapError::AgentTimeout("test".into()).to_user_message(),
            ElapError::DatabaseError("test".into()).to_user_message(),
            ElapError::ToolNotFound("test".into()).to_user_message(),
        ];

        for msg in messages {
            // Deben contener acciones (Intenta, Contacta, Recarga, etc)
            assert!(
                msg.contains("Intenta") || msg.contains("Contacta") || msg.contains("Recarga"),
                "Message not actionable: {}",
                msg
            );
        }
    }

    // === Log Messages (with technical details) ===
    #[test]
    fn test_log_messages_include_context() {
        let msg = ElapError::AgentExecutionFailed("timeout in eval".into()).to_log_message();
        assert!(msg.contains("timeout in eval"));
        assert!(msg.contains("AgentExecutionFailed"));

        let msg = ElapError::ToolValidationFailed("invalid param: foo".into()).to_log_message();
        assert!(msg.contains("invalid param: foo"));
    }

    // === From Conversions ===
    #[test]
    fn test_from_io_error() {
        let io_error = std::io::Error::new(std::io::ErrorKind::NotFound, "File not found");
        let elap_error = ElapError::from(io_error);
        assert!(matches!(elap_error, ElapError::IoError { .. }));
        assert_eq!(elap_error.error_code(), "IO_ERROR");
    }

    #[test]
    fn test_io_error_preserves_context() {
        let io_error = std::io::Error::new(std::io::ErrorKind::PermissionDenied, "Access denied");
        let elap_error = ElapError::from(io_error);
        let log_msg = elap_error.to_log_message();
        assert!(log_msg.contains("Access denied"));
    }

    // === Display Implementation ===
    #[test]
    fn test_display_format() {
        let error = ElapError::ToolNotFound("web_search".into());
        let display_str = error.to_string();
        assert!(display_str.contains("TOOL_NOT_FOUND"));
        assert!(display_str.contains("web_search"));
    }

    // === Agent Errors ===
    #[test]
    fn test_agent_error_types() {
        assert_eq!(
            ElapError::AgentNotFound("agent123".into()).error_code(),
            "AGENT_NOT_FOUND"
        );
        assert_eq!(
            ElapError::AgentExecutionFailed("eval failed".into()).error_code(),
            "AGENT_EXECUTION_FAILED"
        );
        assert_eq!(
            ElapError::InvalidAgentState("zombie".into()).error_code(),
            "INVALID_AGENT_STATE"
        );
        assert_eq!(
            ElapError::AgentTimeout("30s".into()).error_code(),
            "AGENT_TIMEOUT"
        );
    }

    // === Tool Errors ===
    #[test]
    fn test_tool_error_types() {
        assert_eq!(
            ElapError::ToolNotFound("grep".into()).error_code(),
            "TOOL_NOT_FOUND"
        );
        assert_eq!(
            ElapError::ToolExecutionFailed("exit code 1".into()).error_code(),
            "TOOL_EXECUTION_FAILED"
        );
        assert_eq!(
            ElapError::ToolTimeout("60s".into()).error_code(),
            "TOOL_TIMEOUT"
        );
        assert_eq!(
            ElapError::ToolValidationFailed("missing param".into()).error_code(),
            "TOOL_VALIDATION_FAILED"
        );
    }

    // === Security Errors ===
    #[test]
    fn test_security_error_types() {
        assert_eq!(
            ElapError::PermissionDenied("read_sensitive_data".into()).error_code(),
            "PERMISSION_DENIED"
        );
        assert_eq!(
            ElapError::AuthenticationFailed("invalid token".into()).error_code(),
            "AUTHENTICATION_FAILED"
        );
        assert_eq!(
            ElapError::PolicyViolation("late night execution".into()).error_code(),
            "POLICY_VIOLATION"
        );
    }

    // === Database Errors ===
    #[test]
    fn test_database_error_types() {
        assert_eq!(
            ElapError::DatabaseError("connection refused".into()).error_code(),
            "DATABASE_ERROR"
        );
        assert_eq!(
            ElapError::ConnectionPoolExhausted.error_code(),
            "CONNECTION_POOL_EXHAUSTED"
        );
        assert_eq!(
            ElapError::TransactionFailed("rollback".into()).error_code(),
            "TRANSACTION_FAILED"
        );
    }

    // === Configuration Errors ===
    #[test]
    fn test_config_error_types() {
        assert_eq!(
            ElapError::ConfigError("file not found".into()).error_code(),
            "CONFIG_ERROR"
        );
        assert_eq!(
            ElapError::ConfigValidationFailed("invalid schema".into()).error_code(),
            "CONFIG_VALIDATION_FAILED"
        );
    }

    // === Communication Errors ===
    #[test]
    fn test_communication_error_types() {
        assert_eq!(
            ElapError::GrpcError("connection refused".into()).error_code(),
            "GRPC_ERROR"
        );
        assert_eq!(
            ElapError::GrpcTimeout("30s".into()).error_code(),
            "GRPC_TIMEOUT"
        );
        assert_eq!(
            ElapError::ConnectionUnavailable("server down".into()).error_code(),
            "CONNECTION_UNAVAILABLE"
        );
    }

    // === HTTP Error Categories ===
    #[test]
    fn test_client_error_codes_4xx() {
        let errors = vec![
            ElapError::Unauthorized("test".into()),
            ElapError::Forbidden("test".into()),
            ElapError::NotFound("test".into()),
            ElapError::ValidationError("test".into()),
            ElapError::Conflict("test".into()),
        ];

        for error in errors {
            let code = error.status_code();
            assert!(code >= 400 && code < 500, "Expected 4xx status, got {}", code);
        }
    }

    #[test]
    fn test_server_error_codes_5xx() {
        let errors = vec![
            ElapError::InternalError("test".into()),
            ElapError::DatabaseError("test".into()),
            ElapError::AgentExecutionFailed("test".into()),
        ];

        for error in errors {
            let code = error.status_code();
            assert!(code >= 500 && code < 600, "Expected 5xx status, got {}", code);
        }
    }

    // === Error Recovery Information ===
    #[test]
    fn test_recoverable_errors() {
        // Estos errores deberían tener retry automático
        let recoverable = vec![
            ElapError::AgentTimeout("test".into()),
            ElapError::ToolTimeout("test".into()),
            ElapError::GrpcTimeout("test".into()),
            ElapError::ConnectionUnavailable("test".into()),
        ];

        for error in recoverable {
            let user_msg = error.to_user_message();
            // Mensajes de retry automático o reintentos
            assert!(
                user_msg.contains("Intenta") || user_msg.contains("unos segundos"),
                "Non-recoverable message for {}: {}",
                error.error_code(),
                user_msg
            );
        }
    }

    // === New Error Type (ResultadoElap) ===
    #[test]
    fn test_resultado_elap_type() {
        let result: ResultadoElap<i32> = Ok(42);
        assert!(result.is_ok());

        let error: ResultadoElap<i32> = Err(ElapError::NotFound("test".into()));
        assert!(error.is_err());
    }
}
