//! Web API REST para agentes

pub mod handlers;
pub mod routes;
pub mod middleware;
pub mod state;
pub mod websocket;

pub use routes::crear_router;
pub use state::AppState;
pub use websocket::AgentEvent;
