//! WebSocket para monitoreo en vivo de agentes

use axum::{
    extract::{ws::{WebSocket, WebSocketUpgrade}, Path, State},
    response::IntoResponse,
};
use futures::{sink::SinkExt, stream::StreamExt};
use serde::{Deserialize, Serialize};
use serde_json::json;
use crate::EstadoAgente;
use super::state::AppState;

/// Evento de agente para streaming
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct AgentEvent {
    /// Tipo de evento
    pub tipo: String,
    /// Contenido del evento
    pub datos: serde_json::Value,
    /// Timestamp
    pub timestamp: String,
}

impl AgentEvent {
    /// Crear evento de estado
    pub fn estado(estado: &str) -> Self {
        Self {
            tipo: "estado".to_string(),
            datos: json!({"estado": estado}),
            timestamp: chrono::Utc::now().to_rfc3339(),
        }
    }

    /// Crear evento de progreso
    pub fn progreso(pasos_completados: usize, total: usize) -> Self {
        let porcentaje = if total > 0 {
            (pasos_completados as f32 / total as f32) * 100.0
        } else {
            0.0
        };

        Self {
            tipo: "progreso".to_string(),
            datos: json!({
                "pasos_completados": pasos_completados,
                "total": total,
                "porcentaje": porcentaje,
            }),
            timestamp: chrono::Utc::now().to_rfc3339(),
        }
    }

    /// Crear evento de acción
    pub fn accion(descripcion: String) -> Self {
        Self {
            tipo: "accion".to_string(),
            datos: json!({"descripcion": descripcion}),
            timestamp: chrono::Utc::now().to_rfc3339(),
        }
    }

    /// Crear evento de reflexión
    pub fn reflexion(contenido: String) -> Self {
        Self {
            tipo: "reflexion".to_string(),
            datos: json!({"contenido": contenido}),
            timestamp: chrono::Utc::now().to_rfc3339(),
        }
    }

    /// Crear evento de error
    pub fn error(mensaje: String) -> Self {
        Self {
            tipo: "error".to_string(),
            datos: json!({"mensaje": mensaje}),
            timestamp: chrono::Utc::now().to_rfc3339(),
        }
    }

    /// Serializar a JSON string
    pub fn to_json_string(&self) -> String {
        serde_json::to_string(self).unwrap_or_default()
    }
}

/// WebSocket handler para monitorear agente
pub async fn monitorear_agente(
    ws: WebSocketUpgrade,
    Path(id): Path<String>,
    State(state): State<AppState>,
) -> impl IntoResponse {
    ws.on_upgrade(|socket| handle_socket(socket, id, state))
}

/// Manejar conexión WebSocket
async fn handle_socket(socket: WebSocket, agente_id: String, state: AppState) {
    // Verificar que el agente existe primero
    if state.obtener_agente(&agente_id).await.is_none() {
        let (mut sender, _) = socket.split();
        let evento = AgentEvent::error(format!("Agente {} no encontrado", agente_id));
        let _ = sender.send(axum::extract::ws::Message::Text(evento.to_json_string())).await;
        return;
    }

    let (mut sender, _receiver) = socket.split();

    // Obtener agente inicial
    if let Some(agente) = state.obtener_agente(&agente_id).await {
        // Enviar estado inicial
        let evento = AgentEvent::estado(&format!("{:?}", agente.agente.estado));
        let _ = sender.send(axum::extract::ws::Message::Text(evento.to_json_string())).await;

        // Enviar progreso inicial
        let evento = AgentEvent::progreso(
            agente.plan.paso_actual,
            agente.plan.pasos.len(),
        );
        let _ = sender.send(axum::extract::ws::Message::Text(evento.to_json_string())).await;

        // Enviar historial de acciones
        for accion in &agente.agente.historial_acciones {
            let evento = AgentEvent::accion(accion.clone());
            let _ = sender.send(axum::extract::ws::Message::Text(evento.to_json_string())).await;
        }

        // Enviar reflexiones
        for reflexion in &agente.agente.reflexiones {
            let evento = AgentEvent::reflexion(reflexion.clone());
            let _ = sender.send(axum::extract::ws::Message::Text(evento.to_json_string())).await;
        }

        // Enviar mensaje de conexión exitosa
        let evento_conexion = AgentEvent {
            tipo: "conectado".to_string(),
            datos: json!({
                "agente_id": agente_id.clone(),
                "mensaje": "Monitoreo en vivo iniciado"
            }),
            timestamp: chrono::Utc::now().to_rfc3339(),
        };
        let _ = sender.send(axum::extract::ws::Message::Text(evento_conexion.to_json_string())).await;
    }

    // Mantener conexión abierta con latidos
    let mut interval = tokio::time::interval(std::time::Duration::from_secs(1));
    loop {
        interval.tick().await;

        match state.obtener_agente(&agente_id).await {
            Some(agente_actualizado) => {
                let evento = AgentEvent {
                    tipo: "latido".to_string(),
                    datos: json!({
                        "estado": format!("{:?}", agente_actualizado.agente.estado),
                        "progreso": agente_actualizado.plan.progreso(),
                        "pasos": agente_actualizado.plan.paso_actual,
                        "total": agente_actualizado.plan.pasos.len(),
                    }),
                    timestamp: chrono::Utc::now().to_rfc3339(),
                };
                if sender.send(axum::extract::ws::Message::Text(evento.to_json_string())).await.is_err() {
                    break;
                }
            }
            None => {
                let evento = AgentEvent::error("Agente no encontrado".to_string());
                let _ = sender.send(axum::extract::ws::Message::Text(evento.to_json_string())).await;
                break;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_agent_event_estado() {
        let evento = AgentEvent::estado("Ejecutando");
        assert_eq!(evento.tipo, "estado");
        assert!(evento.datos["estado"].is_string());
    }

    #[test]
    fn test_agent_event_progreso() {
        let evento = AgentEvent::progreso(2, 4);
        assert_eq!(evento.tipo, "progreso");
        assert_eq!(evento.datos["pasos_completados"], 2);
        assert_eq!(evento.datos["porcentaje"], 50.0);
    }

    #[test]
    fn test_agent_event_accion() {
        let evento = AgentEvent::accion("Leer archivo".to_string());
        assert_eq!(evento.tipo, "accion");
        assert!(evento.datos["descripcion"].is_string());
    }

    #[test]
    fn test_agent_event_reflexion() {
        let evento = AgentEvent::reflexion("Aprendí algo".to_string());
        assert_eq!(evento.tipo, "reflexion");
    }

    #[test]
    fn test_agent_event_error() {
        let evento = AgentEvent::error("Falló".to_string());
        assert_eq!(evento.tipo, "error");
    }

    #[test]
    fn test_agent_event_to_json_string() {
        let evento = AgentEvent::estado("Test");
        let json_str = evento.to_json_string();
        assert!(json_str.contains("\"tipo\":\"estado\""));
    }
}
