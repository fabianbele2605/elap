//! Plugin Health Monitoring - Monitoreo de salud y métricas de plugins
//!
//! Capacidades:
//! - Tracking de métricas (éxitos, fallos, latencia)
//! - Health scoring automático
//! - Auto-disable de plugins no saludables
//! - Alertas de degradación

use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};
use crate::error::ResultadoElap;

/// Métricas de ejecución
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionMetrics {
    pub total_executions: u64,
    pub successful_executions: u64,
    pub failed_executions: u64,
    pub average_latency_ms: f32,
    pub min_latency_ms: f32,
    pub max_latency_ms: f32,
}

/// Health check results
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum HealthStatus {
    Healthy,    // success_rate > 90%
    Degraded,   // success_rate 70-90%
    Unhealthy,  // success_rate 50-70%
    Critical,   // success_rate < 50%
}

/// Monitor de salud de un plugin
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginHealthMonitor {
    pub plugin_id: String,
    pub last_check: u64,
    pub health_score: f32,  // 0.0 - 1.0
    pub health_status: HealthStatus,
    pub metrics: ExecutionMetrics,
    pub consecutive_failures: u32,
    pub alert_threshold_triggered: bool,
}

impl PluginHealthMonitor {
    /// Crear nuevo monitor de salud
    pub fn new(plugin_id: &str) -> Self {
        Self {
            plugin_id: plugin_id.to_string(),
            last_check: current_timestamp(),
            health_score: 1.0,
            health_status: HealthStatus::Healthy,
            metrics: ExecutionMetrics {
                total_executions: 0,
                successful_executions: 0,
                failed_executions: 0,
                average_latency_ms: 0.0,
                min_latency_ms: 0.0,
                max_latency_ms: 0.0,
            },
            consecutive_failures: 0,
            alert_threshold_triggered: false,
        }
    }

    /// Registrar ejecución exitosa
    pub fn record_success(&mut self, latency_ms: f32) {
        self.metrics.total_executions += 1;
        self.metrics.successful_executions += 1;
        self.consecutive_failures = 0;

        // Actualizar latencias
        if self.metrics.min_latency_ms == 0.0 || latency_ms < self.metrics.min_latency_ms {
            self.metrics.min_latency_ms = latency_ms;
        }
        if latency_ms > self.metrics.max_latency_ms {
            self.metrics.max_latency_ms = latency_ms;
        }

        // Actualizar promedio
        let total_time = (self.metrics.average_latency_ms * (self.metrics.successful_executions - 1) as f32) + latency_ms;
        self.metrics.average_latency_ms = total_time / self.metrics.successful_executions as f32;

        self.recalculate_health();
        self.last_check = current_timestamp();
    }

    /// Registrar ejecución fallida
    pub fn record_failure(&mut self) {
        self.metrics.total_executions += 1;
        self.metrics.failed_executions += 1;
        self.consecutive_failures += 1;

        self.recalculate_health();
        self.last_check = current_timestamp();

        // Revisar si se alcanzó threshold de alerta
        if self.consecutive_failures >= 5 {
            self.alert_threshold_triggered = true;
        }
    }

    /// Recalcular health score
    fn recalculate_health(&mut self) {
        if self.metrics.total_executions == 0 {
            self.health_score = 1.0;
            self.health_status = HealthStatus::Healthy;
            return;
        }

        // Calcular success rate
        let success_rate = self.metrics.successful_executions as f32 / self.metrics.total_executions as f32;

        // Health score: 50% success rate + 30% latency + 20% consistency
        let success_component = success_rate * 0.5;

        let latency_component = if self.metrics.average_latency_ms > 0.0 {
            (1.0 / (1.0 + self.metrics.average_latency_ms / 1000.0)) * 0.3
        } else {
            0.3
        };

        let consistency_component = (1.0 - (self.consecutive_failures as f32 / 10.0).min(1.0)) * 0.2;

        self.health_score = success_component + latency_component + consistency_component;

        // Determinar estado
        self.health_status = match success_rate {
            s if s > 0.9 => HealthStatus::Healthy,
            s if s > 0.7 => HealthStatus::Degraded,
            s if s > 0.5 => HealthStatus::Unhealthy,
            _ => HealthStatus::Critical,
        };
    }

    /// ¿Debería estar deshabilitado?
    pub fn should_be_disabled(&self) -> bool {
        self.health_status == HealthStatus::Critical || self.consecutive_failures >= 10
    }

    /// Obtener resumen de salud
    pub fn get_summary(&self) -> String {
        format!(
            "Plugin: {} | Status: {:?} | Score: {:.2} | Success: {}/{} | Failures: {}",
            self.plugin_id,
            self.health_status,
            self.health_score,
            self.metrics.successful_executions,
            self.metrics.total_executions,
            self.consecutive_failures
        )
    }

    /// Reset del monitor
    pub fn reset(&mut self) {
        self.metrics = ExecutionMetrics {
            total_executions: 0,
            successful_executions: 0,
            failed_executions: 0,
            average_latency_ms: 0.0,
            min_latency_ms: 0.0,
            max_latency_ms: 0.0,
        };
        self.consecutive_failures = 0;
        self.alert_threshold_triggered = false;
        self.health_score = 1.0;
        self.health_status = HealthStatus::Healthy;
        self.last_check = current_timestamp();
    }
}

/// Obtener timestamp actual
fn current_timestamp() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_health_monitor_new() {
        let monitor = PluginHealthMonitor::new("test_plugin");
        assert_eq!(monitor.plugin_id, "test_plugin");
        assert_eq!(monitor.health_score, 1.0);
        assert_eq!(monitor.health_status, HealthStatus::Healthy);
    }

    #[test]
    fn test_record_success() {
        let mut monitor = PluginHealthMonitor::new("test");
        monitor.record_success(100.0);

        assert_eq!(monitor.metrics.total_executions, 1);
        assert_eq!(monitor.metrics.successful_executions, 1);
        assert_eq!(monitor.metrics.average_latency_ms, 100.0);
    }

    #[test]
    fn test_record_failure() {
        let mut monitor = PluginHealthMonitor::new("test");
        monitor.record_failure();

        assert_eq!(monitor.metrics.total_executions, 1);
        assert_eq!(monitor.metrics.failed_executions, 1);
        assert_eq!(monitor.consecutive_failures, 1);
    }

    #[test]
    fn test_health_degradation() {
        let mut monitor = PluginHealthMonitor::new("test");

        // 7 éxitos, 3 fallos = 70% = Degraded
        for _ in 0..7 {
            monitor.record_success(50.0);
        }
        for _ in 0..3 {
            monitor.record_failure();
        }

        assert_eq!(monitor.health_status, HealthStatus::Degraded);
    }

    #[test]
    fn test_should_be_disabled() {
        let mut monitor = PluginHealthMonitor::new("test");

        // 10 fallos consecutivos
        for _ in 0..10 {
            monitor.record_failure();
        }

        assert!(monitor.should_be_disabled());
    }

    #[test]
    fn test_alert_threshold() {
        let mut monitor = PluginHealthMonitor::new("test");

        for _ in 0..5 {
            monitor.record_failure();
        }

        assert!(monitor.alert_threshold_triggered);
    }

    #[test]
    fn test_reset() {
        let mut monitor = PluginHealthMonitor::new("test");

        for _ in 0..5 {
            monitor.record_success(50.0);
        }

        monitor.reset();

        assert_eq!(monitor.metrics.total_executions, 0);
        assert_eq!(monitor.consecutive_failures, 0);
        assert_eq!(monitor.health_score, 1.0);
    }

    #[test]
    fn test_latency_tracking() {
        let mut monitor = PluginHealthMonitor::new("test");

        monitor.record_success(10.0);
        monitor.record_success(20.0);
        monitor.record_success(30.0);

        assert_eq!(monitor.metrics.min_latency_ms, 10.0);
        assert_eq!(monitor.metrics.max_latency_ms, 30.0);
        assert_eq!(monitor.metrics.average_latency_ms, 20.0);
    }
}
