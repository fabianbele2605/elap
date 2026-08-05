//! Puente IPC (Inter-Process Communication)
//! Comunica frontend Tauri con MotorCentral Rust

pub mod commands;
pub mod errors;

pub use commands::*;
pub use errors::*;