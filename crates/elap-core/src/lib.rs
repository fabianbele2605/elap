#![warn(missing_docs)]

//! # Motor Central ELAP
//!
//! El núcleo central de la Plataforma Enterprise Local de IA.
//! Gestiona planificación de tareas, seguridad, plugins y comunicación IPC.

pub mod error;
pub mod config;
pub mod core;
pub mod scheduler;
pub mod procesos;

pub use core::MotorCentral;
pub use error::ElapError;
pub use config::Config;
pub use scheduler::PlanificadorTareas;
pub use procesos::GestorProcesos;
