//! Módulo de Sistema de Plugins
//!
//! Framework para cargar y ejecutar plugins de terceros
//! de forma segura con aislamiento y control de permisos.

pub mod plugin_trait;
pub mod metadata;
pub mod loader;
pub mod registry;
pub mod sandbox;

pub use plugin_trait::Plugin;
pub use metadata::PluginMetadata;
pub use loader::PluginLoader;
pub use registry::RegistroPlugins;
pub use sandbox::{PluginSandbox, ConfiguracionSandbox, PoliticaEjecucion};
