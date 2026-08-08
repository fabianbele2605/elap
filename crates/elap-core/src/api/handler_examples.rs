/// Ejemplos de handlers usando el nuevo framework de error handling.
///
/// Estos ejemplos muestran los patrones recomendados para:
/// 1. Validación de entrada
/// 2. Verificación de recursos
/// 3. Control de acceso (RBAC)
/// 4. Conversión de errores externos
/// 5. Propagación de errores con contexto

use axum::{
    extract::{Path, State},
    Json,
};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::error::ElapError;
use super::error_response::{ApiResult, SuccessResponse};

// ============================================================================
// === Estructuras de solicitud/respuesta
// ============================================================================

#[derive(Deserialize)]
pub struct CrearAgentRequest {
    pub nombre: String,
    pub rol: String,
    pub objetivo: String,
}

#[derive(Serialize)]
pub struct AgentResponse {
    pub id: String,
    pub nombre: String,
    pub rol: String,
    pub objetivo: String,
}

#[derive(Deserialize)]
pub struct EjecutarAgentRequest {
    pub entrada: String,
    pub timeout_ms: Option<u64>,
}

#[derive(Serialize)]
pub struct EjecucionResponse {
    pub id: String,
    pub resultado: String,
    pub duracion_ms: u64,
}

// ============================================================================
// === Ejemplo 1: Validación de entrada
// ============================================================================

/// Patrón: Validar datos de entrada
///
/// Antes:
/// ```ignore
/// pub async fn crear_agente(Json(payload): Json<CrearAgentRequest>) -> ... {
///     let agente = crear_agente_internal(&payload.nombre);
/// }
/// ```
///
/// Después:
/// ```ignore
/// pub async fn crear_agente(Json(payload): Json<CrearAgentRequest>) -> ApiResult<Json<SuccessResponse<AgentResponse>>> {
///     // Validar
///     if payload.nombre.is_empty() {
///         return Err(ElapError::ValidationError("Name cannot be empty".to_string()));
///     }
///     if payload.nombre.len() > 256 {
///         return Err(ElapError::ValidationError("Name too long (max 256 chars)".to_string()));
///     }
///     if !["sales", "hr", "finance"].contains(&payload.rol.as_str()) {
///         return Err(ElapError::ValidationError(format!("Invalid role: {}", payload.rol)));
///     }
///
///     // Crear
///     let agente = crear_agente_internal(&payload);
///     Ok(Json(SuccessResponse::created(agente)))
/// }
/// ```

pub async fn ejemplo_validacion(
    Json(payload): Json<CrearAgentRequest>,
) -> ApiResult<Json<SuccessResponse<AgentResponse>>> {
    // ✅ Validar entrada
    payload.nombre.is_empty().then(|| {
        Err(ElapError::ValidationError(
            "Name cannot be empty".to_string(),
        ))
    });

    payload.rol.is_empty().then(|| {
        Err(ElapError::ValidationError(
            "Role cannot be empty".to_string(),
        ))
    });

    // ✅ Crear recurso
    let agente = AgentResponse {
        id: Uuid::new_v4().to_string(),
        nombre: payload.nombre,
        rol: payload.rol,
        objetivo: payload.objetivo,
    };

    Ok(Json(SuccessResponse::created(agente)))
}

// ============================================================================
// === Ejemplo 2: Verificar recurso existe
// ============================================================================

/// Patrón: Verificar que un recurso existe antes de operarlo
///
/// Antes:
/// ```ignore
/// pub async fn get_agent(Path(id): Path<String>) -> ... {
///     match repo.get(&id) {
///         Some(agent) => (StatusCode::OK, Json(agent)),
///         None => (StatusCode::NOT_FOUND, Json(ErrorResponse { ... })),
///     }
/// }
/// ```
///
/// Después:
/// ```ignore
/// pub async fn get_agent(Path(id): Path<String>) -> ApiResult<Json<AgentResponse>> {
///     let agent = REPO.lock()
///         .get(&id)
///         .ok_or_else(|| ElapError::AgentNotFound(
///             format!("Agent {} not found", id)
///         ))?;
///
///     Ok(Json(agent))
/// }
/// ```

pub async fn ejemplo_get_agent(
    Path(id): Path<String>,
) -> ApiResult<Json<AgentResponse>> {
    // Simulado: repo.get(&id)
    let _agent_exists = id == "valid_id";

    if !_agent_exists {
        return Err(ElapError::AgentNotFound(format!(
            "Agent {} not found",
            id
        )));
    }

    // ✅ Retornar recurso
    Ok(Json(AgentResponse {
        id,
        nombre: "Test Agent".to_string(),
        rol: "sales".to_string(),
        objetivo: "test".to_string(),
    }))
}

// ============================================================================
// === Ejemplo 3: Control de acceso (RBAC)
// ============================================================================

/// Patrón: Validar permisos antes de ejecutar acción
///
/// ```ignore
/// pub async fn delete_agent(
///     claims: Claims,  // JWT del usuario
///     Path(id): Path<String>,
/// ) -> ApiResult<Json<Value>> {
///     // ✅ Validar autenticación
///     if claims.user_id.is_empty() {
///         return Err(ElapError::Unauthorized(
///             "User not authenticated".to_string()
///         ));
///     }
///
///     // ✅ Validar permiso (RBAC)
///     let rbac = ValidadorRBAC::new();
///     rbac.validar(claims.role, Accion::Eliminar, "agent")
///         .map_err(|e| ElapError::PermissionDenied(
///             format!("User {} lacks permission: {}", claims.user_id, e)
///         ))?;
///
///     // ✅ Ejecutar
///     REPO.lock().remove(&id)?;
///
///     Ok(Json(json!({"status": "deleted"})))
/// }
/// ```

// ============================================================================
// === Ejemplo 4: Convertir errores externos
// ============================================================================

/// Patrón: Convertir errores de librerías externas
///
/// ```ignore
/// pub async fn query_database() -> ApiResult<Vec<String>> {
///     let results = db.query("SELECT * FROM agents")
///         .await
///         .map_err(|e| ElapError::DatabaseError(
///             format!("Query failed: {}", e)
///         ))?;
///
///     Ok(results)
/// }
/// ```

pub async fn ejemplo_error_conversion() -> ApiResult<Vec<String>> {
    // Simulado: db.query()
    let result: Result<Vec<String>, String> =
        Err("Connection timeout".to_string());

    // ✅ Convertir error externo a ElapError
    let results = result.map_err(|e| {
        ElapError::DatabaseError(format!("Database query failed: {}", e))
    })?;

    Ok(results)
}

// ============================================================================
// === Ejemplo 5: Error con contexto
// ============================================================================

/// Patrón: Agregar contexto (user_id, request_id, etc.) a errores
///
/// ```ignore
/// pub async fn execute_agent(
///     claims: Claims,
///     Path(id): Path<String>,
///     Json(payload): Json<EjecutarAgentRequest>,
/// ) -> ApiResult<Json<EjecucionResponse>> {
///     // ✅ Obtener agente
///     let agent = REPO.lock()
///         .get(&id)
///         .ok_or_else(|| ElapError::AgentNotFound(
///             format!("Agent {} not found", id)
///         ))?;
///
///     // ✅ Ejecutar con timeout
///     let timeout = Duration::from_millis(payload.timeout_ms.unwrap_or(30000));
///     let result = tokio::time::timeout(timeout, agent.execute(&payload.entrada))
///         .await
///         .map_err(|_| {
///             ElapError::AgentTimeout(
///                 format!("Execution timeout after {:?}", timeout)
///             )
///         })?
///         .map_err(|e| {
///             ElapError::AgentExecutionFailed(
///                 format!("Agent execution failed: {}", e)
///             )
///         })?;
///
///     Ok(Json(SuccessResponse::ok(EjecucionResponse {
///         id: Uuid::new_v4().to_string(),
///         resultado: result,
///         duracion_ms: 1500,
///     })))
/// }
/// ```

// ============================================================================
// === Ejemplo 6: Resultado con recuperación automática
// ============================================================================

/// Patrón: Retry automático en errores recuperables
///
/// ```ignore
/// async fn ejecutar_con_retry<F, T>(
///     mut f: F,
///     max_intentos: u32,
/// ) -> ApiResult<T>
/// where
///     F: FnMut() -> BoxFuture<'static, ApiResult<T>>,
/// {
///     for intento in 1..=max_intentos {
///         match f().await {
///             Ok(result) => return Ok(result),
///             Err(e) => {
///                 // Retry solo en errores recuperables
///                 if !e.es_recuperable() {
///                     return Err(e);
///                 }
///                 if intento == max_intentos {
///                     return Err(ElapError::InternalError(
///                         format!("Failed after {} retries", max_intentos)
///                     ));
///                 }
///                 tokio::time::sleep(Duration::from_millis(100 * intento as u64)).await;
///             }
///         }
///     }
///     unreachable!()
/// }
/// ```

// ============================================================================
// === Resumen de patrones
// ============================================================================

/*
TABLA DE PATRONES:

┌─────────────────────────┬──────────────────────────────────┬────────────────┐
│ Situación               │ Patrón                           │ Error a usar   │
├─────────────────────────┼──────────────────────────────────┼────────────────┤
│ Entrada inválida        │ Validar → ValidationError        │ 400            │
│ Recurso no existe       │ Check → NotFound/AgentNotFound   │ 404            │
│ Recurso existe ya       │ Check → Conflict                 │ 409            │
│ Sin autenticación       │ Check → Unauthorized             │ 401            │
│ Sin permiso (RBAC)      │ Validar → PermissionDenied       │ 403            │
│ DB query falla          │ map_err → DatabaseError          │ 500            │
│ gRPC timeout            │ timeout → GrpcTimeout/AgentTimeout│ 504            │
│ Tool no encontrada      │ Check → ToolNotFound             │ 404            │
│ Tool execution falla    │ map_err → ToolExecutionFailed    │ 500            │
│ Pool exhausto           │ Check → ConnectionPoolExhausted  │ 503            │
│ Servicio no disponible  │ Check → ConnectionUnavailable    │ 503            │
│ Error externo           │ map_err → wrap → ElapError       │ 500            │
│ No implementado         │ Check → NotImplemented           │ 501            │
└─────────────────────────┴──────────────────────────────────┴────────────────┘

ESTRUCTURA DE HANDLER:

pub async fn handler(
    // ✅ 1. Extraer datos
    Path(id): Path<String>,
    Json(payload): Json<Request>,
    // ✅ 2. Autenticación (si aplica)
    claims: Claims,
) -> ApiResult<Json<SuccessResponse<Response>>> {
    // ✅ 3. Validar entrada
    if payload.is_invalid() {
        return Err(ElapError::ValidationError("...".to_string()));
    }

    // ✅ 4. Verificar permisos
    validador_rbac.validar(...)?;

    // ✅ 5. Obtener recurso
    let resource = repo.get(&id)
        .ok_or(ElapError::NotFound(...))?;

    // ✅ 6. Ejecutar lógica
    let result = operation()
        .await
        .map_err(|e| ElapError::InternalError(...))?;

    // ✅ 7. Retornar respuesta
    Ok(Json(SuccessResponse::ok(result)))
}
*/
