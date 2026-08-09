/// Error recovery con retry, circuit breaker y fallback.
///
/// Estrategias de recuperación automática para:
/// - Errores transitorios (timeout, conexión)
/// - Operaciones que pueden reintentarse
/// - Fallback a servicios alternativos
/// - Monitoreo de salud

use std::time::Duration;
use crate::error::ElapError;

/// Estrategia de retry con backoff exponencial
#[derive(Debug, Clone)]
pub struct RetryConfig {
    /// Máximo número de intentos
    pub max_attempts: u32,

    /// Delay inicial en milisegundos
    pub initial_delay_ms: u64,

    /// Factor multiplicativo para backoff exponencial
    pub backoff_multiplier: f64,

    /// Máximo delay entre intentos en milisegundos
    pub max_delay_ms: u64,

    /// Errores que se deben reintentar
    pub retryable_errors: Vec<String>,
}

impl Default for RetryConfig {
    fn default() -> Self {
        Self {
            max_attempts: 3,
            initial_delay_ms: 100,
            backoff_multiplier: 2.0,
            max_delay_ms: 5000,
            retryable_errors: vec![
                "AGENT_TIMEOUT".to_string(),
                "TOOL_TIMEOUT".to_string(),
                "GRPC_TIMEOUT".to_string(),
                "CONNECTION_UNAVAILABLE".to_string(),
                "CONNECTION_POOL_EXHAUSTED".to_string(),
            ],
        }
    }
}

impl RetryConfig {
    /// Crear config personalizada
    pub fn new(max_attempts: u32) -> Self {
        let mut cfg = Self::default();
        cfg.max_attempts = max_attempts;
        cfg
    }

    /// Calcular delay para este intento
    pub fn calculate_delay(&self, attempt: u32) -> Duration {
        if attempt == 0 {
            return Duration::from_millis(self.initial_delay_ms);
        }

        let delay = self.initial_delay_ms as f64
            * self.backoff_multiplier.powi(attempt as i32);
        let delay = delay.min(self.max_delay_ms as f64) as u64;

        Duration::from_millis(delay)
    }

    /// Verificar si un error es reintentable
    pub fn is_retryable(&self, error: &ElapError) -> bool {
        let code = error.error_code();
        self.retryable_errors.contains(&code.to_string())
    }

    /// Agregar código de error reintentable
    pub fn with_retryable_error(mut self, code: &str) -> Self {
        self.retryable_errors.push(code.to_string());
        self
    }
}

/// Ejecutar operación con retry automático
pub async fn execute_with_retry<F, T, Fut>(
    f: F,
    config: RetryConfig,
) -> Result<T, ElapError>
where
    F: Fn() -> Fut,
    Fut: std::future::Future<Output = Result<T, ElapError>>,
{
    let mut last_error = None;

    for attempt in 0..config.max_attempts {
        match f().await {
            Ok(result) => {
                if attempt > 0 {
                    // Log success after retry
                    tracing::info!(
                        attempt = attempt,
                        "Operation succeeded after retry"
                    );
                }
                return Ok(result);
            }
            Err(e) => {
                last_error = Some(e.clone());

                // No reintentar si no es reintentable
                if !config.is_retryable(&e) {
                    return Err(e);
                }

                // No reintentar si es el último intento
                if attempt + 1 >= config.max_attempts {
                    break;
                }

                // Log del intento fallido
                let delay = config.calculate_delay(attempt + 1);
                tracing::warn!(
                    attempt = attempt + 1,
                    max_attempts = config.max_attempts,
                    delay_ms = delay.as_millis(),
                    error_code = e.error_code(),
                    "Retrying after error"
                );

                // Esperar antes de reintentar
                tokio::time::sleep(delay).await;
            }
        }
    }

    Err(last_error.unwrap_or_else(|| {
        ElapError::InternalError("All retry attempts failed".to_string())
    }))
}

/// Circuit breaker: monitorea la salud de un servicio
#[derive(Debug, Clone)]
pub struct CircuitBreakerConfig {
    /// Número de fallos consecutivos antes de abrir
    pub failure_threshold: u32,

    /// Duración en milisegundos antes de intentar recovery
    pub timeout_ms: u64,

    /// Número de éxitos consecutivos para cerrar
    pub success_threshold: u32,
}

impl Default for CircuitBreakerConfig {
    fn default() -> Self {
        Self {
            failure_threshold: 5,
            timeout_ms: 30000,
            success_threshold: 2,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CircuitState {
    /// Circuito cerrado, operaciones permitidas
    Closed,
    /// Circuito abierto, operaciones bloqueadas
    Open,
    /// Circuito en recuperación, pruebas limitadas
    HalfOpen,
}

/// Fallback: ejecutar operación alternativa si falla la principal
pub async fn execute_with_fallback<F, T, Fut, FB, FBT>(
    f: F,
    fallback: FB,
) -> Result<T, ElapError>
where
    F: FnOnce() -> Fut,
    Fut: std::future::Future<Output = Result<T, ElapError>>,
    FB: FnOnce() -> FBT,
    FBT: std::future::Future<Output = Result<T, ElapError>>,
{
    match f().await {
        Ok(result) => {
            tracing::info!("Primary operation succeeded");
            Ok(result)
        }
        Err(primary_error) => {
            tracing::warn!(
                error_code = primary_error.error_code(),
                "Primary operation failed, trying fallback"
            );

            match fallback().await {
                Ok(result) => {
                    tracing::info!("Fallback operation succeeded");
                    Ok(result)
                }
                Err(fallback_error) => {
                    tracing::error!(
                        primary_error = primary_error.error_code(),
                        fallback_error = fallback_error.error_code(),
                        "Both primary and fallback failed"
                    );
                    Err(fallback_error)
                }
            }
        }
    }
}

/// Health check para servicios
pub trait HealthCheck: Send + Sync {
    /// Nombre del servicio
    fn service_name(&self) -> &str;
}

/// Configuración de recuperación completa
#[derive(Debug, Clone)]
pub struct RecoveryConfig {
    pub retry: RetryConfig,
    pub circuit_breaker: Option<CircuitBreakerConfig>,
}

impl Default for RecoveryConfig {
    fn default() -> Self {
        Self {
            retry: RetryConfig::default(),
            circuit_breaker: Some(CircuitBreakerConfig::default()),
        }
    }
}

impl RecoveryConfig {
    /// Builder pattern
    pub fn new() -> Self {
        Self::default()
    }

    pub fn with_retry_config(mut self, config: RetryConfig) -> Self {
        self.retry = config;
        self
    }

    pub fn with_circuit_breaker_config(mut self, config: CircuitBreakerConfig) -> Self {
        self.circuit_breaker = Some(config);
        self
    }

    pub fn without_circuit_breaker(mut self) -> Self {
        self.circuit_breaker = None;
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_retry_config_default() {
        let cfg = RetryConfig::default();
        assert_eq!(cfg.max_attempts, 3);
        assert!(cfg.retryable_errors.contains(&"AGENT_TIMEOUT".to_string()));
    }

    #[test]
    fn test_calculate_delay() {
        let cfg = RetryConfig::default();
        let delay0 = cfg.calculate_delay(0);
        let delay1 = cfg.calculate_delay(1);
        let delay2 = cfg.calculate_delay(2);

        // Delays deben aumentar exponencialmente
        assert!(delay1 > delay0);
        assert!(delay2 > delay1);
    }

    #[test]
    fn test_max_delay_cap() {
        let cfg = RetryConfig {
            initial_delay_ms: 1000,
            backoff_multiplier: 10.0,
            max_delay_ms: 5000,
            ..Default::default()
        };

        let delay5 = cfg.calculate_delay(5);
        assert!(delay5.as_millis() <= 5000);
    }

    #[test]
    fn test_is_retryable() {
        let cfg = RetryConfig::default();
        let timeout_error = ElapError::AgentTimeout("test".into());
        let not_found = ElapError::NotFound("test".into());

        assert!(cfg.is_retryable(&timeout_error));
        assert!(!cfg.is_retryable(&not_found));
    }

    #[test]
    fn test_custom_retryable_error() {
        let cfg = RetryConfig::default()
            .with_retryable_error("CUSTOM_TRANSIENT_ERROR");

        assert!(cfg.retryable_errors
            .contains(&"CUSTOM_TRANSIENT_ERROR".to_string()));
    }

    #[test]
    fn test_circuit_breaker_default() {
        let cfg = CircuitBreakerConfig::default();
        assert_eq!(cfg.failure_threshold, 5);
        assert_eq!(cfg.success_threshold, 2);
    }

    #[test]
    fn test_recovery_config_builder() {
        let cfg = RecoveryConfig::new()
            .with_retry_config(RetryConfig::new(5))
            .without_circuit_breaker();

        assert_eq!(cfg.retry.max_attempts, 5);
        assert!(cfg.circuit_breaker.is_none());
    }

    #[tokio::test]
    async fn test_execute_with_retry_success() {
        let cfg = RetryConfig::new(3);

        let result = execute_with_retry(
            || async {
                Ok::<i32, ElapError>(42)
            },
            cfg,
        )
        .await;

        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 42);
    }

    #[tokio::test]
    async fn test_execute_with_retry_all_fail() {
        let cfg = RetryConfig::new(2);

        let result = execute_with_retry(
            || async {
                Err::<i32, ElapError>(ElapError::AgentTimeout("test".into()))
            },
            cfg,
        )
        .await;

        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_execute_with_retry_non_retryable() {
        let cfg = RetryConfig::default();

        let result = execute_with_retry(
            || async {
                Err::<i32, ElapError>(ElapError::NotFound("test".into()))
            },
            cfg,
        )
        .await;

        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_execute_with_fallback_primary_success() {
        let result = execute_with_fallback(
            || async { Ok::<i32, ElapError>(42) },
            || async { Ok::<i32, ElapError>(99) },
        )
        .await;

        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 42); // Primary succeeded
    }

    #[tokio::test]
    async fn test_execute_with_fallback_uses_fallback() {
        let result = execute_with_fallback(
            || async { Err::<i32, ElapError>(ElapError::InternalError("primary".into())) },
            || async { Ok::<i32, ElapError>(99) },
        )
        .await;

        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 99); // Fallback used
    }
}
