//! Componentes visuales de la interfaz

use serde::{Deserialize, Serialize};

/// Componente: Ventana principal
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WindowComponent {
    pub title: String,
    pub width: u32,
    pub height: u32,
    pub resizable: bool,
}

impl Default for WindowComponent {
    fn default() -> Self {
        Self {
            title: "ELAP - Enterprise Local AI Platform".to_string(),
            width: 1200,
            height: 800,
            resizable: true,
        }
    }
}

/// Componente: Botón
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ButtonComponent {
    pub id: String,
    pub label: String,
    pub enabled: bool,
    pub action: String,
}

/// Componente: Panel de logs
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogPanelComponent {
    pub logs: Vec<LogEntry>,
    pub max_lines: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogEntry {
    pub timestamp: u64,
    pub level: String, // "trace", "debug", "info", "warn", "error"
    pub message: String,
}

impl LogPanelComponent {
    pub fn new(max_lines: usize) -> Self {
        Self {
            logs: Vec::new(),
            max_lines,
        }
    }

    /// Agregar entrada de log
    pub fn add_log(&mut self, level: &str, message: &str) {
        use std::time::{SystemTime, UNIX_EPOCH};
        
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        self.logs.push(LogEntry {
            timestamp,
            level: level.to_string(),
            message: message.to_string(),
        });

        // Mantener máximo de líneas
        if self.logs.len() > self.max_lines {
            self.logs.remove(0);
        }
    }
}
