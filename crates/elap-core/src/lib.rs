#![warn(missing_docs)]

//! # ELAP Core Runtime
//!
//! The central nucleus of the Enterprise Local AI Platform.
//! Manages task scheduling, security, plugins, and IPC communication.

pub mod error;
pub mod config;

/// Core engine and state management
pub mod core {
    /// Main engine struct
    #[derive(Debug, Clone)]
    pub struct CoreEngine {
        name: String,
        version: String,
    }

    impl CoreEngine {
        /// Create a new CoreEngine instance
        pub fn new(name: impl Into<String>, version: impl Into<String>) -> Self {
            Self {
                name: name.into(),
                version: version.into(),
            }
        }

        /// Get engine name
        pub fn name(&self) -> &str {
            &self.name
        }

        /// Get engine version
        pub fn version(&self) -> &str {
            &self.version
        }

        /// Start the engine
        pub async fn start(&self) -> Result<(), crate::error::ElapError> {
            tracing::info!(
                name = self.name,
                version = self.version,
                "Starting ELAP Core Engine"
            );
            Ok(())
        }

        /// Stop the engine
        pub async fn stop(&self) -> Result<(), crate::error::ElapError> {
            tracing::info!(name = self.name, "Stopping ELAP Core Engine");
            Ok(())
        }
    }

    #[cfg(test)]
    mod tests {
        use super::*;

        #[test]
        fn test_engine_creation() {
            let engine = CoreEngine::new("TestEngine", "0.1.0");
            assert_eq!(engine.name(), "TestEngine");
            assert_eq!(engine.version(), "0.1.0");
        }

        #[tokio::test]
        async fn test_engine_lifecycle() {
            let engine = CoreEngine::new("TestEngine", "0.1.0");
            assert!(engine.start().await.is_ok());
            assert!(engine.stop().await.is_ok());
        }
    }
}

pub use core::CoreEngine;
