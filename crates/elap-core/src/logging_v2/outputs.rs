//! Outputs de logging (múltiples destinos)

use super::events::LogEvent;
use crate::error::ResultadoElap;

/// Trait para outputs de log
pub trait LogOutput: Send + Sync {
    /// Escribir evento de log
    fn escribir(&self, evento: &LogEvent) -> ResultadoElap<()>;

    /// Flush (vaciar buffer)
    fn flush(&self) -> ResultadoElap<()> {
        Ok(())
    }

    /// Nombre del output
    fn nombre(&self) -> &str;
}

/// Output a consola
pub struct ConsoleOutput {
    nombre: String,
}

impl ConsoleOutput {
    pub fn nuevo() -> Self {
        Self {
            nombre: "console".to_string(),
        }
    }
}

impl LogOutput for ConsoleOutput {
    fn escribir(&self, evento: &LogEvent) -> ResultadoElap<()> {
        let timestamp = evento.entrada.timestamp_legible();
        let nivel = evento.entrada.nivel;
        let modulo = &evento.entrada.modulo;
        let mensaje = &evento.entrada.mensaje;

        println!("[{}] {} | {} | {}", timestamp, nivel, modulo, mensaje);
        Ok(())
    }

    fn nombre(&self) -> &str {
        &self.nombre
    }
}

/// Output a memoria (para testing)
pub struct MemoryOutput {
    nombre: String,
    eventos: std::sync::Arc<std::sync::Mutex<Vec<LogEvent>>>,
}

impl MemoryOutput {
    pub fn nuevo() -> Self {
        Self {
            nombre: "memory".to_string(),
            eventos: std::sync::Arc::new(std::sync::Mutex::new(Vec::new())),
        }
    }

    pub fn obtener_eventos(&self) -> ResultadoElap<Vec<LogEvent>> {
        let eventos = self.eventos.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock de eventos".to_string()
            ))?;
        Ok(eventos.clone())
    }

    pub fn cantidad(&self) -> ResultadoElap<usize> {
        let eventos = self.eventos.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock".to_string()
            ))?;
        Ok(eventos.len())
    }

    pub fn limpiar(&self) -> ResultadoElap<()> {
        let mut eventos = self.eventos.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock".to_string()
            ))?;
        eventos.clear();
        Ok(())
    }
}

impl LogOutput for MemoryOutput {
    fn escribir(&self, evento: &LogEvent) -> ResultadoElap<()> {
        let mut eventos = self.eventos.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock".to_string()
            ))?;
        eventos.push(evento.clone());
        Ok(())
    }

    fn nombre(&self) -> &str {
        &self.nombre
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::logging_v2::events::{LogLevel, LogEntry};

    #[test]
    fn test_console_output() {
        let output = ConsoleOutput::nuevo();
        let entry = LogEntry::nuevo(LogLevel::Info, "test".to_string(), "test".to_string());
        let evento = LogEvent::nuevo(entry);

        assert!(output.escribir(&evento).is_ok());
        assert_eq!(output.nombre(), "console");
    }

    #[test]
    fn test_memory_output() {
        let output = MemoryOutput::nuevo();
        let entry = LogEntry::nuevo(LogLevel::Debug, "debug".to_string(), "test".to_string());
        let evento = LogEvent::nuevo(entry);

        assert!(output.escribir(&evento).is_ok());
        assert_eq!(output.cantidad().unwrap(), 1);
    }

    #[test]
    fn test_memory_output_multiples() {
        let output = MemoryOutput::nuevo();

        for i in 0..5 {
            let entry = LogEntry::nuevo(
                LogLevel::Info,
                format!("mensaje {}", i),
                "test".to_string(),
            );
            let evento = LogEvent::nuevo(entry);
            assert!(output.escribir(&evento).is_ok());
        }

        assert_eq!(output.cantidad().unwrap(), 5);
    }

    #[test]
    fn test_memory_output_limpiar() {
        let output = MemoryOutput::nuevo();
        let entry = LogEntry::nuevo(LogLevel::Info, "test".to_string(), "test".to_string());
        let evento = LogEvent::nuevo(entry);

        assert!(output.escribir(&evento).is_ok());
        assert!(output.limpiar().is_ok());
        assert_eq!(output.cantidad().unwrap(), 0);
    }

    #[test]
    fn test_memory_output_obtener_eventos() {
        let output = MemoryOutput::nuevo();
        let entry = LogEntry::nuevo(LogLevel::Warn, "warning".to_string(), "test".to_string());
        let evento = LogEvent::nuevo(entry);

        assert!(output.escribir(&evento).is_ok());
        let eventos = output.obtener_eventos().unwrap();
        assert_eq!(eventos.len(), 1);
        assert_eq!(eventos[0].entrada.nivel, LogLevel::Warn);
    }
}
