//! Definición de eventos de log

use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};
use std::fmt;

/// Nivel de logging
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "UPPERCASE")]
pub enum LogLevel {
    /// Información de depuración
    Debug = 0,
    /// Información general
    Info = 1,
    /// Advertencias
    Warn = 2,
    /// Errores
    Error = 3,
}

impl fmt::Display for LogLevel {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            LogLevel::Debug => write!(f, "DEBUG"),
            LogLevel::Info => write!(f, "INFO"),
            LogLevel::Warn => write!(f, "WARN"),
            LogLevel::Error => write!(f, "ERROR"),
        }
    }
}

impl LogLevel {
    /// Verificar si debería registrar basado en nivel mínimo
    pub fn deberia_registrar(&self, nivel_minimo: LogLevel) -> bool {
        *self >= nivel_minimo
    }
}

/// Entrada individual de log
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogEntry {
    /// Nivel de severidad
    pub nivel: LogLevel,

    /// Mensaje de log
    pub mensaje: String,

    /// Módulo origen
    pub modulo: String,

    /// Timestamp UTC en segundos
    pub timestamp: u64,
}

impl LogEntry {
    /// Crear nueva entrada
    pub fn nuevo(nivel: LogLevel, mensaje: String, modulo: String) -> Self {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();

        Self {
            nivel,
            mensaje,
            modulo,
            timestamp,
        }
    }

    /// Obtener timestamp legible
    pub fn timestamp_legible(&self) -> String {
        chrono::DateTime::<chrono::Utc>::from(
            UNIX_EPOCH + std::time::Duration::from_secs(self.timestamp)
        )
        .to_rfc3339()
    }
}

/// Evento de log completo
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogEvent {
    /// ID único del evento
    pub id: String,

    /// Entrada de log
    pub entrada: LogEntry,

    /// Contexto adicional
    pub contexto: std::collections::HashMap<String, String>,

    /// Línea de código (opcional)
    pub linea: Option<u32>,

    /// Archivo (opcional)
    pub archivo: Option<String>,
}

impl LogEvent {
    /// Crear nuevo evento
    pub fn nuevo(entrada: LogEntry) -> Self {
        let id = uuid::Uuid::new_v4().to_string();

        Self {
            id,
            entrada,
            contexto: std::collections::HashMap::new(),
            linea: None,
            archivo: None,
        }
    }

    /// Agregar contexto
    pub fn con_contexto(mut self, clave: String, valor: String) -> Self {
        self.contexto.insert(clave, valor);
        self
    }

    /// Establecer ubicación en código
    pub fn con_ubicacion(mut self, archivo: String, linea: u32) -> Self {
        self.archivo = Some(archivo);
        self.linea = Some(linea);
        self
    }

    /// Serializar a JSON
    pub fn a_json(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string(self)
    }

    /// Serializar a JSON pretty
    pub fn a_json_pretty(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string_pretty(self)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_loglevel_display() {
        assert_eq!(LogLevel::Debug.to_string(), "DEBUG");
        assert_eq!(LogLevel::Info.to_string(), "INFO");
        assert_eq!(LogLevel::Warn.to_string(), "WARN");
        assert_eq!(LogLevel::Error.to_string(), "ERROR");
    }

    #[test]
    fn test_loglevel_deberia_registrar() {
        assert!(LogLevel::Error.deberia_registrar(LogLevel::Error));
        assert!(LogLevel::Error.deberia_registrar(LogLevel::Warn));
        assert!(!LogLevel::Debug.deberia_registrar(LogLevel::Info));
    }

    #[test]
    fn test_crear_logentry() {
        let entry = LogEntry::nuevo(
            LogLevel::Info,
            "Mensaje de prueba".to_string(),
            "test_module".to_string(),
        );

        assert_eq!(entry.nivel, LogLevel::Info);
        assert_eq!(entry.mensaje, "Mensaje de prueba");
        assert_eq!(entry.modulo, "test_module");
        assert!(entry.timestamp > 0);
    }

    #[test]
    fn test_timestamp_legible() {
        let entry = LogEntry::nuevo(
            LogLevel::Info,
            "test".to_string(),
            "test".to_string(),
        );
        let legible = entry.timestamp_legible();
        assert!(!legible.is_empty());
        assert!(legible.contains("T"));
    }

    #[test]
    fn test_crear_logevent() {
        let entry = LogEntry::nuevo(
            LogLevel::Info,
            "Evento de prueba".to_string(),
            "test_module".to_string(),
        );
        let evento = LogEvent::nuevo(entry);

        assert!(!evento.id.is_empty());
        assert!(evento.contexto.is_empty());
    }

    #[test]
    fn test_evento_con_contexto() {
        let entry = LogEntry::nuevo(LogLevel::Info, "test".to_string(), "test".to_string());
        let evento = LogEvent::nuevo(entry)
            .con_contexto("user_id".to_string(), "123".to_string())
            .con_contexto("session".to_string(), "abc".to_string());

        assert_eq!(evento.contexto.len(), 2);
        assert_eq!(evento.contexto.get("user_id"), Some(&"123".to_string()));
    }

    #[test]
    fn test_evento_con_ubicacion() {
        let entry = LogEntry::nuevo(LogLevel::Error, "error".to_string(), "test".to_string());
        let evento = LogEvent::nuevo(entry)
            .con_ubicacion("main.rs".to_string(), 42);

        assert_eq!(evento.archivo, Some("main.rs".to_string()));
        assert_eq!(evento.linea, Some(42));
    }

    #[test]
    fn test_evento_a_json() {
        let entry = LogEntry::nuevo(LogLevel::Info, "test".to_string(), "test".to_string());
        let evento = LogEvent::nuevo(entry);

        let json = evento.a_json();
        assert!(json.is_ok());
        assert!(json.unwrap().contains("\"nivel\""));
    }

    #[test]
    fn test_serializar_logevent() {
        let entry = LogEntry::nuevo(LogLevel::Warn, "warning".to_string(), "app".to_string());
        let evento = LogEvent::nuevo(entry);

        let json = serde_json::to_string(&evento).unwrap();
        assert!(json.contains("WARN"));
        assert!(json.contains("warning"));
    }
}
