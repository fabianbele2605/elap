#![warn(missing_docs)]

//! # ELAP Desktop Runtime
//!
//! Desktop application shell for ELAP using Tauri.
//! Provides GUI and window management for the platform.

use elap_core::CoreEngine;

/// Desktop application manager
#[derive(Debug)]
pub struct DesktopRuntime {
    core: CoreEngine,
}

impl DesktopRuntime {
    /// Create a new DesktopRuntime
    pub fn new(core: CoreEngine) -> Self {
        Self { core }
    }

    /// Initialize the desktop environment
    pub async fn initialize(&self) -> Result<(), Box<dyn std::error::Error>> {
        tracing::info!("Initializing Desktop Runtime");
        self.core.start().await?;
        Ok(())
    }

    /// Shutdown the desktop environment
    pub async fn shutdown(&self) -> Result<(), Box<dyn std::error::Error>> {
        tracing::info!("Shutting down Desktop Runtime");
        self.core.stop().await?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_desktop_runtime_creation() {
        let core = CoreEngine::new("TestCore", "0.1.0");
        let desktop = DesktopRuntime::new(core);
        assert!(desktop.initialize().await.is_ok());
        assert!(desktop.shutdown().await.is_ok());
    }
}
