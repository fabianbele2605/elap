//! Módulo de Configuración Avanzada
//!
//! Sistema de configuración persistente, versionado y validado.
//! Soporta múltiples formatos: TOML, YAML, JSON.
//! Incluye validación por esquema y hot-reload.

pub mod config_struct;
pub mod loader;
pub mod validator;
pub mod schema;
pub mod hotreload;

pub use config_struct::ConfiguracionAvanzada;
pub use loader::CargadorConfiguracion;
pub use validator::{ValidadorConfiguracion, ResultadoValidacion};
pub use schema::EsquemaConfiguracion;
pub use hotreload::{MonitorHotReload, ArchivoMonitoreado};
