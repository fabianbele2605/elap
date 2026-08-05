//! Web API REST para agentes

pub mod handlers;
pub mod routes;
pub mod middleware;
pub mod state;

pub use routes::crear_router;
pub use state::AppState;
