//! Web API REST para agentes

pub mod handlers;
pub mod routes;
pub mod middleware;
pub mod state;
pub mod websocket;
pub mod auth;
pub mod rbac;

pub use routes::crear_router;
pub use state::AppState;
pub use websocket::AgentEvent;
pub use auth::{Claims, ManagerJWT};
pub use rbac::{RolAPI, Accion, ValidadorRBAC};
