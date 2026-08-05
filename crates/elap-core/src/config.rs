//! Configuration management for ELAP Core

use serde::{Deserialize, Serialize};

/// Main configuration structure for ELAP
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    /// Application name
    pub app_name: String,
    /// Application version
    pub version: String,
    /// Port for gRPC server
    pub grpc_port: u16,
    /// Python AI Runtime port
    pub ai_runtime_port: u16,
    /// Log level (trace, debug, info, warn, error)
    pub log_level: String,
    /// Database configuration
    pub database: DatabaseConfig,
    /// Security settings
    pub security: SecurityConfig,
}

/// Database configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseConfig {
    /// Database type: sqlite, postgresql
    pub db_type: String,
    /// Connection string
    pub connection_string: String,
    /// Max connections
    pub max_connections: u32,
}

/// Security configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityConfig {
    /// Enable RBAC
    pub rbac_enabled: bool,
    /// Enable encryption at rest
    pub encryption_enabled: bool,
    /// Encryption algorithm (aes256)
    pub encryption_algorithm: String,
    /// Audit logging enabled
    pub audit_logging_enabled: bool,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            app_name: "ELAP".to_string(),
            version: "0.1.0".to_string(),
            grpc_port: 50051,
            ai_runtime_port: 50052,
            log_level: "info".to_string(),
            database: DatabaseConfig::default(),
            security: SecurityConfig::default(),
        }
    }
}

impl Default for DatabaseConfig {
    fn default() -> Self {
        Self {
            db_type: "sqlite".to_string(),
            connection_string: "sqlite:///elap.db".to_string(),
            max_connections: 10,
        }
    }
}

impl Default for SecurityConfig {
    fn default() -> Self {
        Self {
            rbac_enabled: true,
            encryption_enabled: true,
            encryption_algorithm: "aes256".to_string(),
            audit_logging_enabled: true,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_config() {
        let config = Config::default();
        assert_eq!(config.app_name, "ELAP");
        assert_eq!(config.version, "0.1.0");
        assert_eq!(config.grpc_port, 50051);
    }

    #[test]
    fn test_security_defaults() {
        let security = SecurityConfig::default();
        assert!(security.rbac_enabled);
        assert!(security.encryption_enabled);
        assert!(security.audit_logging_enabled);
    }

    #[test]
    fn test_config_serialization() {
        let config = Config::default();
        let json = serde_json::to_string(&config).unwrap();
        let deserialized: Config = serde_json::from_str(&json).unwrap();
        assert_eq!(deserialized.app_name, config.app_name);
    }
}
