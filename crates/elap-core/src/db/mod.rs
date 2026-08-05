//! Persistencia en base de datos

pub mod connection;
pub mod schema;
pub mod agent_repo;

pub use connection::{Database, obtener_db};
pub use schema::Schema;
pub use agent_repo::RepositorioAgente;
