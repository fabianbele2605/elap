//! Filtros y rate-limiting para logs

use super::events::{LogEvent, LogLevel};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};

/// Filtro de log
pub trait FilterLog: Send + Sync {
    /// Determinar si el evento pasa el filtro
    fn aplicar(&self, evento: &LogEvent) -> bool;
}

/// Filtro por nivel mínimo
pub struct FiltroNivel {
    nivel_minimo: LogLevel,
}

impl FiltroNivel {
    pub fn nuevo(nivel_minimo: LogLevel) -> Self {
        Self { nivel_minimo }
    }
}

impl FilterLog for FiltroNivel {
    fn aplicar(&self, evento: &LogEvent) -> bool {
        evento.entrada.nivel >= self.nivel_minimo
    }
}

/// Filtro por módulo
pub struct FiltroModulo {
    modulos: Vec<String>,
    invertir: bool,
}

impl FiltroModulo {
    pub fn nuevo(modulos: Vec<String>, invertir: bool) -> Self {
        Self { modulos, invertir }
    }
}

impl FilterLog for FiltroModulo {
    fn aplicar(&self, evento: &LogEvent) -> bool {
        let contiene = self.modulos.contains(&evento.entrada.modulo);
        if self.invertir {
            !contiene
        } else {
            contiene
        }
    }
}

/// Rate limiter para logs
pub struct RateLimiter {
    limites: Arc<Mutex<HashMap<String, Vec<u64>>>>,
    eventos_por_segundo: u32,
}

impl RateLimiter {
    pub fn nuevo(eventos_por_segundo: u32) -> Self {
        Self {
            limites: Arc::new(Mutex::new(HashMap::new())),
            eventos_por_segundo,
        }
    }

    /// Verificar si el evento puede ser registrado
    pub fn permitir(&self, clave: &str) -> bool {
        let ahora = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();

        let mut limites = match self.limites.lock() {
            Ok(l) => l,
            Err(_) => return true,
        };

        let timestamps = limites.entry(clave.to_string()).or_insert_with(Vec::new);

        // Limpiar timestamps antiguos (más de 1 segundo)
        timestamps.retain(|&ts| ahora - ts < 1);

        // Verificar si está dentro del límite
        if (timestamps.len() as u32) < self.eventos_por_segundo {
            timestamps.push(ahora);
            true
        } else {
            false
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::logging_v2::events::LogEntry;

    #[test]
    fn test_filtro_nivel() {
        let filtro = FiltroNivel::nuevo(LogLevel::Warn);
        let entry_error = LogEntry::nuevo(LogLevel::Error, "error".to_string(), "test".to_string());
        let evento_error = LogEvent::nuevo(entry_error);

        let entry_info = LogEntry::nuevo(LogLevel::Info, "info".to_string(), "test".to_string());
        let evento_info = LogEvent::nuevo(entry_info);

        assert!(filtro.aplicar(&evento_error));
        assert!(!filtro.aplicar(&evento_info));
    }

    #[test]
    fn test_filtro_modulo() {
        let filtro = FiltroModulo::nuevo(vec!["database".to_string()], false);

        let entry_db = LogEntry::nuevo(LogLevel::Info, "query".to_string(), "database".to_string());
        let evento_db = LogEvent::nuevo(entry_db);

        let entry_http = LogEntry::nuevo(LogLevel::Info, "request".to_string(), "http".to_string());
        let evento_http = LogEvent::nuevo(entry_http);

        assert!(filtro.aplicar(&evento_db));
        assert!(!filtro.aplicar(&evento_http));
    }

    #[test]
    fn test_filtro_modulo_invertido() {
        let filtro = FiltroModulo::nuevo(vec!["database".to_string()], true);

        let entry_db = LogEntry::nuevo(LogLevel::Info, "query".to_string(), "database".to_string());
        let evento_db = LogEvent::nuevo(entry_db);

        let entry_http = LogEntry::nuevo(LogLevel::Info, "request".to_string(), "http".to_string());
        let evento_http = LogEvent::nuevo(entry_http);

        assert!(!filtro.aplicar(&evento_db));
        assert!(filtro.aplicar(&evento_http));
    }

    #[test]
    fn test_rate_limiter() {
        let limiter = RateLimiter::nuevo(5);

        // Primeros 5 eventos deberían pasar
        for _ in 0..5 {
            assert!(limiter.permitir("clave"));
        }

        // El 6to debería bloquearse
        assert!(!limiter.permitir("clave"));
    }

    #[test]
    fn test_rate_limiter_claves_diferentes() {
        let limiter = RateLimiter::nuevo(2);

        assert!(limiter.permitir("user_1"));
        assert!(limiter.permitir("user_1"));
        assert!(!limiter.permitir("user_1"));

        // Clave diferente tiene su propio límite
        assert!(limiter.permitir("user_2"));
        assert!(limiter.permitir("user_2"));
        assert!(!limiter.permitir("user_2"));
    }
}
