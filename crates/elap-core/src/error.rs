//! Error types for ELAP Core

use std::fmt;

/// Main error type for ELAP Core
#[derive(Debug)]
pub enum ElapError {
    /// Permission denied for operation
    PermissionDenied(String),
    /// Module or component not found
    ModuleNotFound(String),
    /// gRPC communication error
    GrpcError(String),
    /// Configuration error
    ConfigError(String),
    /// Authentication failure
    AuthenticationError(String),
    /// Plugin error
    PluginError(String),
    /// Generic internal error
    Internal(String),
}

impl fmt::Display for ElapError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ElapError::PermissionDenied(msg) => write!(f, "Permission denied: {}", msg),
            ElapError::ModuleNotFound(msg) => write!(f, "Module not found: {}", msg),
            ElapError::GrpcError(msg) => write!(f, "gRPC error: {}", msg),
            ElapError::ConfigError(msg) => write!(f, "Configuration error: {}", msg),
            ElapError::AuthenticationError(msg) => write!(f, "Authentication error: {}", msg),
            ElapError::PluginError(msg) => write!(f, "Plugin error: {}", msg),
            ElapError::Internal(msg) => write!(f, "Internal error: {}", msg),
        }
    }
}

impl std::error::Error for ElapError {}

impl From<String> for ElapError {
    fn from(msg: String) -> Self {
        ElapError::Internal(msg)
    }
}

impl From<&str> for ElapError {
    fn from(msg: &str) -> Self {
        ElapError::Internal(msg.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_display() {
        let err = ElapError::PermissionDenied("User lacks write access".to_string());
        assert_eq!(
            err.to_string(),
            "Permission denied: User lacks write access"
        );
    }

    #[test]
    fn test_error_from_string() {
        let err: ElapError = "test error".into();
        assert!(matches!(err, ElapError::Internal(_)));
    }
}
