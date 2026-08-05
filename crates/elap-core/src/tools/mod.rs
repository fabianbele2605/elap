//! Sistema de Herramientas (Tool Engine)
//!
//! Herramientas para acceder a recursos: archivos, HTTP, SQL, etc.
//! Con sandboxing, permisos y validación.

pub mod tool_trait;
pub mod registry;
pub mod metadata;
pub mod errors;

pub use tool_trait::Tool;
pub use registry::RegistroHerramientas;
pub use metadata::{ToolMetadata, TipoHerramienta};
pub use errors::ToolError;
