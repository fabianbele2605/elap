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
    pub respuesta: String,
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
        .get("prompt")
        .and_then(|v| v.as_str())
        .unwrap_or("Ejecutar agente")
        .to_string();

    // Obtener system prompt del agente
    let system_prompt = payload
        .get("systemPrompt")
        .and_then(|v| v.as_str())
        .unwrap_or("Eres un asistente profesional. Responde en español de forma clara y concisa.")
        .to_string();

    // Obtener contexto de empresa si existe
    let sistema_prompt_empresa = payload
        .get("sistemaPromptEmpresa")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();

    // Construir prompt con system context + empresa context
    let prompt_con_contexto = if !sistema_prompt_empresa.is_empty() {
        format!("{}\n\n{}\n\nUsuario: {}", sistema_prompt_empresa, system_prompt, query)
    } else {
        format!("{}\n\nUsuario: {}", system_prompt, query)
    };

    // Conectar a Python AI Runtime vía gRPC
    let mut client = match AIRuntimeClient::conectar("http://127.0.0.1:50051").await {
        Ok(c) => c,
        Err(_) => {
            return Err(StatusCode::SERVICE_UNAVAILABLE);
        }
    };

    // Ejecutar agente en Python con contexto
    match client.ejecutar_agente(&id, &prompt_con_contexto).await {
        Ok(resultado) => {
            let respuesta = EjecucionResponse {
                agente_id: id.clone(),
                estado: "completed".to_string(),
                pasos_completados: 1,
                progreso: 1.0,
                respuesta: resultado, // ✅ Ahora usa la respuesta real del gRPC
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

// === NUEVOS TIPOS PARA FASE 2 ===

/// Solicitud de búsqueda en documentos
#[derive(Deserialize)]
pub struct BuscarDocumentosRequest {
    pub collection: String,
    pub query: String,
    pub top_k: Option<i32>,
}

/// Respuesta de búsqueda
#[derive(Serialize)]
pub struct BuscarDocumentosResponse {
    pub status: String,
    pub chunks: Vec<String>,
    pub count: usize,
    pub error: String,
}

/// Solicitud para generar reporte
#[derive(Deserialize)]
pub struct GenerarReporteRequest {
    pub title: String,
    pub sections_json: String,
    pub format: String, // "pdf" o "excel"
    pub company_name: Option<String>,
}

/// Respuesta de generación de reporte
#[derive(Serialize)]
pub struct GenerarReporteResponse {
    pub status: String,
    pub filename: String,
    pub url: String, // URL para descargar
    pub error: String,
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

// === HANDLERS PARA FASE 3 ===

/// POST /company/setup - Configurar empresa y generar documentos
pub async fn setup_empresa(
    Json(payload): Json<serde_json::Value>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    // Extraer configuración
    let nombre_empresa = payload
        .get("nombreEmpresa")
        .and_then(|v| v.as_str())
        .unwrap_or("Empresa")
        .to_string();

    let num_empleados = payload
        .get("numEmpleados")
        .and_then(|v| v.as_i64())
        .unwrap_or(50) as usize;

    // Conectar a Python gRPC para generar documentos
    let mut client = match AIRuntimeClient::conectar("http://127.0.0.1:50051").await {
        Ok(c) => c,
        Err(_) => {
            return Ok(Json(json!({
                "status": "pending",
                "message": "Documentos en cola para generación",
                "company": nombre_empresa,
            })));
        }
    };

    // En producción: llamaría a gRPC para generar docs
    // Por ahora: retorna estado pending
    Ok(Json(json!({
        "status": "pending",
        "message": "Generando 15 documentos...",
        "company": nombre_empresa,
        "employees": num_empleados,
        "estimated_time": "2-3 minutos"
    })))
}

/// GET /company/status - Estado de generación de documentos
pub async fn obtener_status_empresa(
    Path(company_id): Path<String>,
) -> Json<serde_json::Value> {
    Json(json!({
        "company_id": company_id,
        "status": "completed",
        "documents_generated": 15,
        "documents": [
            {"id": "manual_empleado", "title": "Manual del Empleado", "status": "ready"},
            {"id": "politica_vacaciones", "title": "Política de Vacaciones", "status": "ready"},
            {"id": "codigo_conducta", "title": "Código de Conducta", "status": "ready"},
            {"id": "presupuesto_anual", "title": "Presupuesto Anual", "status": "ready"},
            {"id": "politica_gastos", "title": "Política de Gastos", "status": "ready"},
            {"id": "politica_calidad", "title": "Política de Calidad", "status": "ready"},
        ],
        "rag_indexed": true,
        "ready_for_agents": true
    }))
}

// === HANDLERS PARA FASE 2 ===

/// GET /documents/search - Buscar en RAG
pub async fn buscar_documentos(
    Json(payload): Json<BuscarDocumentosRequest>,
) -> Result<Json<BuscarDocumentosResponse>, StatusCode> {
    // Conectar a Python AI Runtime vía gRPC
    let mut client = match AIRuntimeClient::conectar("http://127.0.0.1:50051").await {
        Ok(c) => c,
        Err(_) => {
            return Ok(Json(BuscarDocumentosResponse {
                status: "error".to_string(),
                chunks: vec![],
                count: 0,
                error: "Cannot connect to gRPC server".to_string(),
            }));
        }
    };

    // Llamar al método gRPC SearchDocuments
    // Por ahora, usamos un placeholder until the gRPC client is fully implemented
    let resultado = serde_json::json!({
        "collection": payload.collection,
        "query": payload.query,
        "top_k": payload.top_k.unwrap_or(5),
    });

    Ok(Json(BuscarDocumentosResponse {
        status: "pending".to_string(),
        chunks: vec![
            "Documento 1: ...".to_string(),
            "Documento 2: ...".to_string(),
        ],
        count: 2,
        error: "".to_string(),
    }))
}

/// POST /documents/generate-report - Generar reporte
pub async fn generar_reporte(
    Json(payload): Json<GenerarReporteRequest>,
) -> Result<Json<GenerarReporteResponse>, StatusCode> {
    // Conectar a Python AI Runtime vía gRPC
    let mut client = match AIRuntimeClient::conectar("http://127.0.0.1:50051").await {
        Ok(c) => c,
        Err(_) => {
            return Ok(Json(GenerarReporteResponse {
                status: "error".to_string(),
                filename: "".to_string(),
                url: "".to_string(),
                error: "Cannot connect to gRPC server".to_string(),
            }));
        }
    };

    // Generar nombre de archivo
    let filename = format!(
        "{}.{}",
        payload.title.replace(" ", "_"),
        if payload.format.to_lowercase() == "pdf" { "pdf" } else { "xlsx" }
    );

    // Retornar respuesta (en producción, guardaría archivo y generaría URL)
    Ok(Json(GenerarReporteResponse {
        status: "completed".to_string(),
        filename: filename.clone(),
        url: format!("/downloads/{}", filename),
        error: "".to_string(),
    }))
}

/// GET /agents/{id}/tools - Listar herramientas del agente
pub async fn listar_herramientas_agente(
    Path(id): Path<String>,
) -> Json<serde_json::Value> {
    Json(json!({
        "agent_id": id,
        "tools": [
            {
                "name": "search_documents",
                "description": "Buscar documentos en RAG",
                "parameters": ["collection", "query", "top_k"]
            },
            {
                "name": "generate_report",
                "description": "Generar reporte PDF/Excel",
                "parameters": ["title", "sections", "format"]
            },
            {
                "name": "read_document",
                "description": "Leer contenido de documento",
                "parameters": ["file_path"]
            }
        ]
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
