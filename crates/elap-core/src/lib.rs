#![warn(missing_docs)]

//! # Motor Central ELAP
//!
//! El núcleo central de la Plataforma Enterprise Local de IA.
//! Gestiona planificación de tareas, seguridad, plugins y comunicación IPC.

pub mod error;
pub mod logging;
pub mod logging_v2;
pub mod config;
pub mod configuration;
pub mod core;
pub mod scheduler;
pub mod procesos;
pub mod security;
pub mod plugin;
pub mod tools;
pub mod models;
pub mod agents;
pub mod api;

pub use core::MotorCentral;
pub use error::ElapError;
pub use config::Configuracion;
pub use configuration::{ConfiguracionAvanzada, CargadorConfiguracion, ValidadorConfiguracion};
pub use scheduler::PlanificadorTareas;
pub use procesos::GestorProcesos;
pub use logging::inicializar_logging;
pub use logging_v2::{LogLevel, LogEntry, LogEvent, LoggerAvanzado};
pub use security::{Rol, Permiso, GestorRbac, RegistroAuditoria, AuditorRbac};
pub use plugin::{Plugin, PluginMetadata, PluginLoader, RegistroPlugins, PluginSandbox, ConfiguracionSandbox, PoliticaEjecucion};
pub use tools::{
    Tool, RegistroHerramientas, ToolMetadata, TipoHerramienta,
    FileTool, HttpTool, SqlTool, SshTool, SystemTool,
    SandboxHerramienta, PoliticaHerramienta, ContextoEjecucion, ValidadorSeguridad,
    EjecutorHerramientas, ResultadoEjecucion,
};
pub use models::{
    ModelMetadata, TipoModelo, OllamaClient, RegistroModelos, CacheEmbeddings,
    ModelManager, MemoriaCorta,
};
pub use agents::{
    Agent, EstadoAgente, ContextoAgente, Plan, Paso,
    EjecutorAgente, AgentError, AgentIntegrado,
    SistemaMemoria, MemoriaCortoTermino, MemoriaLargoTermino,
};
pub use api::{
    AppState, crear_router, AgentEvent,
    Claims, ManagerJWT, RolAPI, Accion, ValidadorRBAC,
};