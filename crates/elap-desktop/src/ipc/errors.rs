//! Errores de comunicación IPC

use std::fmt;

/// Errores de IPC
#[derive(Debug)]
pub enum IpcError {
    /// Motor no inicializado
    MotorNotInitialized,
    /// Permiso denegado
    PermissionDenied(String),
    /// Operación inválida
    InvalidOperation(String),
    /// Error del motor central
    MotorError(String),
}

impl fmt::Display for IpcError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::MotorNotInitialized => write!(f, "Motor no inicializado"),
            Self::PermissionDenied(msg) => write!(f, "Permiso denegado: {}", msg),
            Self::InvalidOperation(msg) => write!(f, "Operación inválida: {}", msg),
            Self::MotorError(msg) => write!(f, "Error del motor: {}", msg),
        }
    }
}

impl std::error::Error for IpcError {}
