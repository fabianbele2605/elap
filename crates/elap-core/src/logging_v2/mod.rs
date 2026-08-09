//! Sistema de Logging Avanzado (v2)
//!
//! Logging estructurado con múltiples outputs, rotación, filtrado y rate-limiting.
//! Integra error handling con tracing para contexto completo.

pub mod events;
pub mod outputs;
pub mod logger;
pub mod rotation;
pub mod filters;
pub mod error_logging;

pub use events::{LogLevel, LogEntry, LogEvent};
pub use outputs::LogOutput;
pub use logger::LoggerAvanzado;
pub use rotation::{EstrategiaRotacion, GestorRotacion};
pub use filters::{FilterLog, FiltroNivel, FiltroModulo, RateLimiter};
pub use error_logging::{ErrorContext, log_error, log_recoverable_error, log_success_after_retry, log_handler};
