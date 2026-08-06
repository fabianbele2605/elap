//! Estados de interfaz de usuario

use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};

/// Estado general de la aplicación
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppState {
    pub motor_running: bool,
    pub timestamp: u64,
    pub mode: String, // "desarrollo" o "producción"
}

impl AppState {
    /// Crear nuevo estado con timestamp actual
    pub fn new(motor_running: bool, mode: &str) -> Self {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        Self {
            motor_running,
            timestamp,
            mode: mode.to_string(),
        }
    }
}

/// Estado de barra de herramientas
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolbarState {
    pub can_start: bool,
    pub can_stop: bool,
    pub can_execute_tools: bool,
}

impl Default for ToolbarState {
    fn default() -> Self {
        Self {
            can_start: true,
            can_stop: false,
            can_execute_tools: false,
        }
    }
}

/// Estado de barra de estado (status bar)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StatusBarState {
    pub message: String,
    pub level: String, // "info", "warning", "error"
    pub timestamp: u64,
}

impl StatusBarState {
    pub fn info(message: &str) -> Self {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        
        Self {
            message: message.to_string(),
            level: "info".to_string(),
            timestamp,
        }
    }
}
