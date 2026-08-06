//! Sistema de Logging Avanzado (v2)
//!
//! Logging estructurado con múltiples outputs, rotación, filtrado y rate-limiting.

pub mod events;
pub mod outputs;
pub mod logger;
pub mod rotation;
pub mod filters;

pub use events::{LogLevel, LogEntry, LogEvent};
pub use outputs::LogOutput;
pub use logger::LoggerAvanzado;
pub use rotation::{EstrategiaRotacion, GestorRotacion};
pub use filters::{FilterLog, FiltroNivel, FiltroModulo, RateLimiter};
