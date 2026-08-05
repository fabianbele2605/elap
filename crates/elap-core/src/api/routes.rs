//! Rutas de la API REST

use axum::{
    routing::{get, post, delete},
    Router,
};
use super::{handlers, websocket, state::AppState, middleware};

/// Crear router con todas las rutas
pub fn crear_router(state: AppState) -> Router {
    Router::new()
        // Agentes
        .route("/agents", post(handlers::crear_agente))
        .route("/agents", get(handlers::listar_agentes))
        .route("/agents/:id", get(handlers::obtener_agente))
        .route("/agents/:id/pasos", post(handlers::agregar_paso))
        .route("/agents/:id/execute", post(handlers::ejecutar_agente))
        .route("/agents/:id/status", get(handlers::obtener_estado))
        .route("/agents/:id", delete(handlers::eliminar_agente))
        // WebSocket
        .route("/agents/:id/watch", get(websocket::monitorear_agente))
        .with_state(state)
        .layer(middleware::cors_layer())
        .layer(middleware::logging_layer())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_router_creation() {
        let state = AppState::nuevo();
        let _router = crear_router(state);
        // Si compila, es un éxito
    }
}
