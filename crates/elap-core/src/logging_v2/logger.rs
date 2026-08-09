//! Logger avanzado con múltiples outputs

use super::events::{LogLevel, LogEntry, LogEvent};
use super::outputs::LogOutput;
use crate::error::ResultadoElap;
use std::sync::{Arc, Mutex};

/// Logger avanzado
pub struct LoggerAvanzado {
    outputs: Arc<Mutex<Vec<Arc<dyn LogOutput>>>>,
    nivel_minimo: LogLevel,
}

impl LoggerAvanzado {
    /// Crear nuevo logger
    pub fn nuevo(nivel_minimo: LogLevel) -> Self {
        Self {
            outputs: Arc::new(Mutex::new(Vec::new())),
            nivel_minimo,
        }
    }

    /// Agregar output
    pub fn agregar_output(&self, output: Arc<dyn LogOutput>) -> ResultadoElap<()> {
        let mut outputs = self.outputs.lock()
            .map_err(|_| crate::error::ElapError::InternalError(
                "No se pudo adquirir lock de outputs".to_string()
            ))?;
        outputs.push(output);
        Ok(())
    }

    /// Registrar log
    pub fn log(&self, evento: LogEvent) -> ResultadoElap<()> {
        if !evento.entrada.nivel.deberia_registrar(self.nivel_minimo) {
            return Ok(());
        }

        let outputs = self.outputs.lock()
            .map_err(|_| crate::error::ElapError::InternalError(
                "No se pudo adquirir lock".to_string()
            ))?;

        for output in outputs.iter() {
            output.escribir(&evento)?;
        }

        Ok(())
    }

    /// Debug
    pub fn debug(&self, modulo: &str, mensaje: &str) -> ResultadoElap<()> {
        let entry = LogEntry::nuevo(
            LogLevel::Debug,
            mensaje.to_string(),
            modulo.to_string(),
        );
        let evento = LogEvent::nuevo(entry);
        self.log(evento)
    }

    /// Info
    pub fn info(&self, modulo: &str, mensaje: &str) -> ResultadoElap<()> {
        let entry = LogEntry::nuevo(
            LogLevel::Info,
            mensaje.to_string(),
            modulo.to_string(),
        );
        let evento = LogEvent::nuevo(entry);
        self.log(evento)
    }

    /// Warn
    pub fn warn(&self, modulo: &str, mensaje: &str) -> ResultadoElap<()> {
        let entry = LogEntry::nuevo(
            LogLevel::Warn,
            mensaje.to_string(),
            modulo.to_string(),
        );
        let evento = LogEvent::nuevo(entry);
        self.log(evento)
    }

    /// Error
    pub fn error(&self, modulo: &str, mensaje: &str) -> ResultadoElap<()> {
        let entry = LogEntry::nuevo(
            LogLevel::Error,
            mensaje.to_string(),
            modulo.to_string(),
        );
        let evento = LogEvent::nuevo(entry);
        self.log(evento)
    }

    /// Cantidad de outputs
    pub fn cantidad_outputs(&self) -> ResultadoElap<usize> {
        let outputs = self.outputs.lock()
            .map_err(|_| crate::error::ElapError::InternalError(
                "No se pudo adquirir lock".to_string()
            ))?;
        Ok(outputs.len())
    }

    /// Flush todos los outputs
    pub fn flush(&self) -> ResultadoElap<()> {
        let outputs = self.outputs.lock()
            .map_err(|_| crate::error::ElapError::InternalError(
                "No se pudo adquirir lock".to_string()
            ))?;

        for output in outputs.iter() {
            output.flush()?;
        }

        Ok(())
    }
}

impl Clone for LoggerAvanzado {
    fn clone(&self) -> Self {
        Self {
            outputs: self.outputs.clone(),
            nivel_minimo: self.nivel_minimo,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::outputs::MemoryOutput;

    #[test]
    fn test_crear_logger() {
        let logger = LoggerAvanzado::nuevo(LogLevel::Info);
        assert_eq!(logger.cantidad_outputs().unwrap(), 0);
    }

    #[test]
    fn test_agregar_output() {
        let logger = LoggerAvanzado::nuevo(LogLevel::Info);
        let output = Arc::new(MemoryOutput::nuevo());

        assert!(logger.agregar_output(output).is_ok());
        assert_eq!(logger.cantidad_outputs().unwrap(), 1);
    }

    #[test]
    fn test_log_debug() {
        let logger = LoggerAvanzado::nuevo(LogLevel::Debug);
        let output = Arc::new(MemoryOutput::nuevo());
        let output_clone = output.clone();

        assert!(logger.agregar_output(output).is_ok());
        assert!(logger.debug("test", "mensaje debug").is_ok());

        assert_eq!(output_clone.cantidad().unwrap(), 1);
    }

    #[test]
    fn test_log_info() {
        let logger = LoggerAvanzado::nuevo(LogLevel::Info);
        let output = Arc::new(MemoryOutput::nuevo());
        let output_clone = output.clone();

        assert!(logger.agregar_output(output).is_ok());
        assert!(logger.info("test", "mensaje info").is_ok());

        assert_eq!(output_clone.cantidad().unwrap(), 1);
    }

    #[test]
    fn test_log_warn() {
        let logger = LoggerAvanzado::nuevo(LogLevel::Warn);
        let output = Arc::new(MemoryOutput::nuevo());
        let output_clone = output.clone();

        assert!(logger.agregar_output(output).is_ok());
        assert!(logger.warn("test", "mensaje warn").is_ok());

        assert_eq!(output_clone.cantidad().unwrap(), 1);
    }

    #[test]
    fn test_log_error() {
        let logger = LoggerAvanzado::nuevo(LogLevel::Error);
        let output = Arc::new(MemoryOutput::nuevo());
        let output_clone = output.clone();

        assert!(logger.agregar_output(output).is_ok());
        assert!(logger.error("test", "mensaje error").is_ok());

        assert_eq!(output_clone.cantidad().unwrap(), 1);
    }

    #[test]
    fn test_filtrar_por_nivel() {
        let logger = LoggerAvanzado::nuevo(LogLevel::Warn);
        let output = Arc::new(MemoryOutput::nuevo());
        let output_clone = output.clone();

        assert!(logger.agregar_output(output).is_ok());

        // Debug e Info no se registran
        assert!(logger.debug("test", "debug").is_ok());
        assert!(logger.info("test", "info").is_ok());
        assert_eq!(output_clone.cantidad().unwrap(), 0);

        // Warn y Error sí se registran
        assert!(logger.warn("test", "warn").is_ok());
        assert!(logger.error("test", "error").is_ok());
        assert_eq!(output_clone.cantidad().unwrap(), 2);
    }

    #[test]
    fn test_clonar_logger() {
        let logger1 = LoggerAvanzado::nuevo(LogLevel::Info);
        let output = Arc::new(MemoryOutput::nuevo());
        assert!(logger1.agregar_output(output).is_ok());

        let logger2 = logger1.clone();
        assert_eq!(logger2.cantidad_outputs().unwrap(), 1);
    }

    #[test]
    fn test_flush() {
        let logger = LoggerAvanzado::nuevo(LogLevel::Info);
        let output = Arc::new(MemoryOutput::nuevo());
        assert!(logger.agregar_output(output).is_ok());
        assert!(logger.flush().is_ok());
    }
}
