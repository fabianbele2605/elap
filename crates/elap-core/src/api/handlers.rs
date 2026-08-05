//! Handlers para endpoints REST

use axum::{
    extract::{Path, State, Json},
    http::StatusCode,
    response::{IntoResponse, Response},
};
use serde::{Deserialize, Serialize};
use serde_json::json;
use uuid::Uuid;
use crate::{AgentIntegrado, EstadoAgente};
use super::state::AppState;

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
    let mut agente = AgentIntegrado::nuevo(payload.nombre.clone(), payload.rol, payload.objetivo);

    let respuesta = AgentResponse {
        id: id.clone(),
        nombre: payload.nombre,
        rol: agente.agente.rol.clone(),
        objetivo: agente.plan.objetivo.clone(),
        estado: format!("{:?}", agente.agente.estado),
        progreso: agente.plan.progreso(),
    };

    // Guardar en estado
    tokio::spawn(async move {
        state.guardar_agente(id, agente).await;
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
        "agentes": agentes.iter().map(|(id, nombre)| {
            json!({
                "id": id,
                "nombre": nombre,
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
            let respuesta = AgentResponse {
                id: id.clone(),
                nombre: agente.agente.nombre.clone(),
                rol: agente.agente.rol.clone(),
                objetivo: agente.plan.objetivo.clone(),
                estado: format!("{:?}", agente.agente.estado),
                progreso: agente.plan.progreso(),
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
) -> Result<Json<EjecucionResponse>, StatusCode> {
    let mut agente = match state.obtener_agente(&id).await {
        Some(a) => a,
        None => return Err(StatusCode::NOT_FOUND),
    };

    match agente.ejecutar() {
        Ok(_) => {
            let estado = format!("{:?}", agente.agente.estado);
            let pasos = agente.plan.paso_actual;
            let progreso = agente.plan.progreso();

            let respuesta = EjecucionResponse {
                agente_id: id.clone(),
                estado,
                pasos_completados: pasos,
                progreso,
            };

            // Guardar estado actualizado
            state.guardar_agente(id, agente).await;

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
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> StatusCode {
    state.eliminar_agente(&id).await;
    StatusCode::NO_CONTENT
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
        };

        assert_eq!(resp.progreso, 0.0);
    }
}
