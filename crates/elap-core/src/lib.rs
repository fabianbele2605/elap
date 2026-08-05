#![warn(missing_docs)]

//! # Motor Central ELAP
//!
//! El núcleo central de la Plataforma Enterprise Local de IA.
//! Gestiona planificación de tareas, seguridad, plugins y comunicación IPC.

pub mod error;
pub mod logging;
pub mod config;
pub mod core;
pub mod scheduler;
pub mod procesos;
pub mod security;
pub mod plugin;

pub use core::MotorCentral;
pub use error::ElapError;
pub use config::Configuracion;
pub use scheduler::PlanificadorTareas;
pub use procesos::GestorProcesos;
pub use logging::inicializar_logging;
pub use security::{Rol, Permiso, GestorRbac, RegistroAuditoria, AuditorRbac};
pub use plugin::{Plugin, PluginMetadata, PluginLoader, RegistroPlugins, PluginSandbox, ConfiguracionSandbox, PoliticaEjecucion};