/// Error handling para API REST.
///
/// Integra `ElapError` con Axum para conversiones automáticas
/// de errores a respuestas HTTP JSON.

use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde::Serialize;
use crate::error::ElapError;

/// Respuesta de error JSON para API
#[derive(Serialize, Debug)]
pub struct ErrorResponse {
    /// Código de error interno (UNAUTHORIZED, AGENT_NOT_FOUND, etc.)
    pub code: String,

    /// Status HTTP (400, 401, 403, 404, 500, etc.)
    pub status: u16,

    /// Mensaje seguro para usuario (sin detalles técnicos)
    pub message: String,

    /// Contexto técnico (opcional, solo en desarrollo)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub detail: Option<String>,
}

impl ErrorResponse {
    /// Crear respuesta de error desde `ElapError`
    pub fn from_elap_error(error: ElapError) -> Self {
        let status = error.status_code();
        let code = error.error_code().to_string();
        let message = error.to_user_message();

        // En desarrollo, incluir detalles técnicos
        let detail = if cfg!(debug_assertions) {
            Some(error.to_log_message())
        } else {
            None
        };

        Self {
            code,
            status,
            message,
            detail,
        }
    }
}

impl IntoResponse for ErrorResponse {
    fn into_response(self) -> Response {
        let status = StatusCode::from_u16(self.status)
            .unwrap_or(StatusCode::INTERNAL_SERVER_ERROR);

        (status, Json(self)).into_response()
    }
}

impl From<ElapError> for ErrorResponse {
    fn from(error: ElapError) -> Self {
        Self::from_elap_error(error)
    }
}

impl IntoResponse for ElapError {
    fn into_response(self) -> Response {
        ErrorResponse::from_elap_error(self).into_response()
    }
}

/// Tipo de resultado para handlers
pub type ApiResult<T> = Result<T, ElapError>;

// ============================================================================
// === Respuesta exitosa estándar
// ============================================================================

/// Respuesta exitosa genérica para API
#[derive(Serialize, Debug)]
pub struct SuccessResponse<T: Serialize> {
    /// Código de operación
    pub code: String,

    /// Status HTTP (200, 201, etc.)
    pub status: u16,

    /// Datos de respuesta
    pub data: T,
}

impl<T: Serialize> SuccessResponse<T> {
    /// Crear respuesta exitosa (200 OK)
    pub fn ok(data: T) -> Self {
        Self {
            code: "SUCCESS".to_string(),
            status: 200,
            data,
        }
    }

    /// Crear respuesta creada (201 Created)
    pub fn created(data: T) -> Self {
        Self {
            code: "CREATED".to_string(),
            status: 201,
            data,
        }
    }

    /// Crear respuesta aceptada (202 Accepted)
    pub fn accepted(data: T) -> Self {
        Self {
            code: "ACCEPTED".to_string(),
            status: 202,
            data,
        }
    }
}

impl<T: Serialize> IntoResponse for SuccessResponse<T> {
    fn into_response(self) -> Response {
        let status = StatusCode::from_u16(self.status)
            .unwrap_or(StatusCode::OK);

        (status, Json(self)).into_response()
    }
}

// ============================================================================
// === Patrones comunes de error
// ============================================================================

/// Patrón: Verificar que un recurso existe
/// ```ignore
/// pub async fn get_agent(
///     Path(id): Path<String>,
/// ) -> ApiResult<Json<AgentResponse>> {
///     let agent = repo.get(&id)
///         .ok_or(ElapError::AgentNotFound(format!("Agent {} not found", id)))?;
///
///     Ok(Json(agent))
/// }
/// ```

/// Patrón: Validar entrada
/// ```ignore
/// pub async fn create_agent(
///     Json(payload): Json<CrearAgentRequest>,
/// ) -> ApiResult<Json<AgentResponse>> {
///     if payload.nombre.is_empty() {
///         return Err(ElapError::ValidationError("Name cannot be empty".to_string()));
///     }
///
///     Ok(Json(agent))
/// }
/// ```

/// Patrón: Convertir errores externos
/// ```ignore
/// pub async fn query_db() -> ApiResult<Vec<String>> {
///     let results = db.query()
///         .await
///         .map_err(|e| ElapError::DatabaseError(e.to_string()))?;
///
///     Ok(results)
/// }
/// ```

/// Patrón: Contexto de error con usuario
/// ```ignore
/// pub async fn execute_agent(
///     claims: Claims,
///     Json(payload): Json<ExecuteRequest>,
/// ) -> ApiResult<Json<ExecutionResponse>> {
///     let context = vec![
///         ("user_id".to_string(), claims.user_id),
///         ("agent_id".to_string(), payload.agent_id.clone()),
///     ];
///
///     agent.execute(payload.input)
///         .await
///         .map_err(|e| ElapError::AgentExecutionFailed(e))?
/// }
/// ```

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_response_from_elap_error() {
        let error = ElapError::AgentNotFound("agent_123".into());
        let response = ErrorResponse::from_elap_error(error);

        assert_eq!(response.code, "AGENT_NOT_FOUND");
        assert_eq!(response.status, 404);
        assert!(!response.message.contains("agent_123"));
    }

    #[test]
    fn test_success_response_ok() {
        #[derive(Serialize)]
        struct Data {
            value: i32,
        }

        let response = SuccessResponse::ok(Data { value: 42 });
        assert_eq!(response.status, 200);
        assert_eq!(response.code, "SUCCESS");
    }

    #[test]
    fn test_success_response_created() {
        #[derive(Serialize)]
        struct Data {
            id: String,
        }

        let response = SuccessResponse::created(Data {
            id: "123".to_string(),
        });
        assert_eq!(response.status, 201);
        assert_eq!(response.code, "CREATED");
    }

    #[test]
    fn test_error_response_status_codes() {
        let errors = vec![
            (
                ElapError::Unauthorized("test".into()),
                401,
                "UNAUTHORIZED",
            ),
            (ElapError::Forbidden("test".into()), 403, "FORBIDDEN"),
            (ElapError::NotFound("test".into()), 404, "NOT_FOUND"),
            (
                ElapError::ValidationError("test".into()),
                400,
                "VALIDATION_ERROR",
            ),
            (ElapError::InternalError("test".into()), 500, "INTERNAL_ERROR"),
        ];

        for (error, expected_status, expected_code) in errors {
            let response = ErrorResponse::from_elap_error(error);
            assert_eq!(response.status, expected_status);
            assert_eq!(response.code, expected_code);
        }
    }

    #[test]
    fn test_error_response_user_message_safe() {
        let error = ElapError::ToolExecutionFailed(
            "timeout in grpc call to localhost:50051".into(),
        );
        let response = ErrorResponse::from_elap_error(error);

        // User message debe ser seguro
        assert!(!response.message.contains("localhost"));
        assert!(!response.message.contains("50051"));
        assert!(!response.message.contains("grpc"));
    }
}
