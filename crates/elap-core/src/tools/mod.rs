//! Sistema de Herramientas (Tool Engine)
//!
//! Herramientas para acceder a recursos: archivos, HTTP, SQL, etc.
//! Con sandboxing, permisos y validación.

pub mod tool_trait;
pub mod registry;
pub mod metadata;
pub mod errors;
pub mod file_tool;
pub mod http_tool;
pub mod sql_tool;
pub mod ssh_tool;
pub mod system_tool;

pub use tool_trait::Tool;
pub use registry::RegistroHerramientas;
pub use metadata::{ToolMetadata, TipoHerramienta};
pub use errors::ToolError;
pub use file_tool::FileTool;
pub use http_tool::HttpTool;
pub use sql_tool::SqlTool;
pub use ssh_tool::SshTool;
pub use system_tool::SystemTool;
