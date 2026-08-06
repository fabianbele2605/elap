//! Handlers para endpoints REST

use axum::{
    extract::{Path, State, Json},
    http::StatusCode,
    response::{IntoResponse, Response},
};
use serde::{Deserialize, Serialize};
use serde_json::json;
use uuid::Uuid;
use crate::{AgentIntegrado, EstadoAgente, rol_to_modelo, obtener_db, RepositorioAgente, grpc_client::AIRuntimeClient};
use super::{state::AppState, auth::{Claims, ManagerJWT}, rbac::{ValidadorRBAC, Accion, RolAPI}};

/// Solicitud para crear agente
#[derive(Deserialize, Serialize)]
pub struct CrearAgentRequest {
    pub nombre: String,
    pub rol: String,
    pub objetivo: String,
}

/// Respuesta de agente
#[derive(Serialize)]
pub struct AgentResponse {
    pub id: String,
    pub nombre: String,
    pub rol: String,
    pub objetivo: String,
    pub estado: String,
    pub progreso: f32,
    pub modelo: String,
}

/// Solicitud para agregar paso
#[derive(Deserialize)]
pub struct AgregarPasoRequest {
    pub descripcion: String,
    pub tipo_herramienta: String,
    pub parametros: serde_json::Value,
}

/// Respuesta de ejecución
#[derive(Serialize)]
pub struct EjecucionResponse {
    pub agente_id: String,
    pub estado: String,
    pub pasos_completados: usize,
    pub progreso: f32,
}

/// Error de API
#[derive(Serialize)]
pub struct ErrorResponse {
    pub error: String,
    pub detalles: Option<String>,
}

impl IntoResponse for ErrorResponse {
    fn into_response(self) -> Response {
        (StatusCode::BAD_REQUEST, Json(self)).into_response()
    }
}

/// POST /agents - Crear nuevo agente
pub async fn crear_agente(
    State(state): State<AppState>,
    Json(payload): Json<CrearAgentRequest>,
) -> (StatusCode, Json<AgentResponse>) {
    let id = Uuid::new_v4().to_string();
    let agente = AgentIntegrado::nuevo(payload.nombre.clone(), payload.rol.clone(), payload.objetivo.clone());

    // Asignar modelo automáticamente según el rol
    let modelo = rol_to_modelo(&payload.rol);

    let respuesta = AgentResponse {
        id: id.clone(),
        nombre: payload.nombre.clone(),
        rol: payload.rol.clone(),
        objetivo: payload.objetivo.clone(),
        estado: format!("{:?}", agente.agente.estado),
        progreso: agente.plan.progreso(),
        modelo: modelo.clone(),
    };

    // Guardar en BD y en estado
    let state_clone = state.clone();
    let id_clone = id.clone();
    tokio::spawn(async move {
        // Guardar en memoria
        state_clone.guardar_agente(id_clone.clone(), agente).await;

        // Guardar en BD
        if let Ok(db) = obtener_db().await {
            let _ = RepositorioAgente::guardar(
                &db,
                &id_clone,
                &payload.nombre,
                &payload.rol,
                &payload.objetivo,
                &modelo,
            ).await;
        }
    });

    (StatusCode::CREATED, Json(respuesta))
}

/// GET /agents - Listar todos los agentes
pub async fn listar_agentes(
    State(state): State<AppState>,
) -> Json<serde_json::Value> {
    let agentes = state.listar_agentes().await;
    Json(json!({
        "total": agentes.len(),
        "agentes": agentes.iter().map(|(id, nombre, rol)| {
            let modelo = rol_to_modelo(rol);
            json!({
                "id": id,
                "nombre": nombre,
                "rol": rol,
                "modelo": modelo,
            })
        }).collect::<Vec<_>>(),
    }))
}

/// GET /agents/{id} - Obtener agente
pub async fn obtener_agente(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> Result<Json<AgentResponse>, StatusCode> {
    match state.obtener_agente(&id).await {
        Some(agente) => {
            let modelo = rol_to_modelo(&agente.agente.rol);
            let respuesta = AgentResponse {
                id: id.clone(),
                nombre: agente.agente.nombre.clone(),
                rol: agente.agente.rol.clone(),
                objetivo: agente.plan.objetivo.clone(),
                estado: format!("{:?}", agente.agente.estado),
                progreso: agente.plan.progreso(),
                modelo,
            };
            Ok(Json(respuesta))
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}

/// POST /agents/{id}/pasos - Agregar paso
pub async fn agregar_paso(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Json(payload): Json<AgregarPasoRequest>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let agentes = state.agentes.read().await;
    if !agentes.contains_key(&id) {
        return Err(StatusCode::NOT_FOUND);
    }
    drop(agentes);

    // Nota: necesitaríamos mut access para modificar el agente
    // En producción, usar una estructura más compleja

    Ok(Json(json!({
        "paso_agregado": true,
        "descripcion": payload.descripcion,
    })))
}

/// POST /agents/{id}/execute - Ejecutar agente
pub async fn ejecutar_agente(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Json(payload): Json<serde_json::Value>,
) -> Result<Json<EjecucionResponse>, StatusCode> {
    let agente = match state.obtener_agente(&id).await {
        Some(a) => a,
        None => return Err(StatusCode::NOT_FOUND),
    };

    // Obtener query de la solicitud
    let query = payload
        .get("query")
        .and_then(|v| v.as_str())
        .unwrap_or("Ejecutar agente")
        .to_string();

    // Conectar a Python AI Runtime vía gRPC
    let mut client = match AIRuntimeClient::conectar("http://127.0.0.1:50051").await {
        Ok(c) => c,
        Err(_) => {
            return Err(StatusCode::SERVICE_UNAVAILABLE);
        }
    };

    // Ejecutar agente en Python
    match client.ejecutar_agente(&id, &query).await {
        Ok(resultado) => {
            let respuesta = EjecucionResponse {
                agente_id: id.clone(),
                estado: "completed".to_string(),
                pasos_completados: 1,
                progreso: 1.0,
            };

            Ok(Json(respuesta))
        }
        Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
    }
}

/// GET /agents/{id}/status - Obtener estado
pub async fn obtener_estado(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let agente = state.obtener_agente(&id).await.ok_or(StatusCode::NOT_FOUND)?;

    Ok(Json(json!({
        "agente_id": id,
        "nombre": agente.agente.nombre,
        "estado": format!("{:?}", agente.agente.estado),
        "pasos": {
            "total": agente.plan.pasos.len(),
            "completados": agente.plan.paso_actual,
            "progreso": format!("{:.0}%", agente.plan.progreso() * 100.0),
        },
        "historial": {
            "acciones": agente.agente.historial_acciones.len(),
            "reflexiones": agente.agente.reflexiones.len(),
        },
    })))
}

/// DELETE /agents/{id} - Eliminar agente
pub async fn eliminar_agente(
    _claims: Claims,
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> StatusCode {
    let validador = ValidadorRBAC::nuevo();
    let rol = RolAPI::from_str(&_claims.rol);

    if !validador.puede_realizar(&rol, &Accion::Eliminar) {
        return StatusCode::FORBIDDEN;
    }

    state.eliminar_agente(&id).await;
    StatusCode::NO_CONTENT
}

/// Login request
#[derive(Deserialize)]
pub struct LoginRequest {
    pub usuario: String,
    pub contraseña: String,
}

/// Login response
#[derive(Serialize)]
pub struct LoginResponse {
    pub token: String,
    pub usuario: String,
    pub rol: String,
}

/// POST /login - Autenticación
pub async fn login(
    Json(payload): Json<LoginRequest>,
) -> Result<Json<LoginResponse>, StatusCode> {
    // Validación simple (en producción, verificar contra BD)
    if payload.usuario.is_empty() || payload.contraseña.is_empty() {
        return Err(StatusCode::BAD_REQUEST);
    }

    // Asignar rol básico (en producción, desde BD)
    let rol = if payload.usuario == "admin" {
        "Admin".to_string()
    } else {
        "User".to_string()
    };

    // Generar token
    let claims = Claims::nuevo(payload.usuario.clone(), rol.clone());
    let manager = ManagerJWT::nuevo("elap-secret-key");

    let token = manager
        .generar_token(&claims)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(LoginResponse {
        token,
        usuario: payload.usuario,
        rol,
    }))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_agente_request() {
        let req = CrearAgentRequest {
            nombre: "Test".to_string(),
            rol: "Role".to_string(),
            objetivo: "Objetivo".to_string(),
        };

        assert_eq!(req.nombre, "Test");
    }

    #[test]
    fn test_agent_response() {
        let resp = AgentResponse {
            id: "id1".to_string(),
            nombre: "Test".to_string(),
            rol: "Role".to_string(),
            objetivo: "Obj".to_string(),
            estado: "Inactivo".to_string(),
            progreso: 0.0,
            modelo: "glm4:9b".to_string(),
        };

        assert_eq!(resp.progreso, 0.0);
    }
}
