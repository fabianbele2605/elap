#![warn(missing_docs)]

//! # ELAP Desktop Runtime
//!
//! Desktop application shell for ELAP using Tauri.
//! Provides GUI and window management for the platform.

use elap_core::MotorCentral;

/// Desktop application manager
#[derive(Debug)]
pub struct DesktopRuntime {
    core: MotorCentral,
}

impl DesktopRuntime {
    /// Create a new DesktopRuntime
    pub fn new(core: MotorCentral) -> Self {
        Self { core }
    }

    /// Initialize the desktop environment
    pub async fn initialize(&self) -> Result<(), Box<dyn std::error::Error>> {
        tracing::info!("Initializing Desktop Runtime");
        self.core.iniciar().await?;
        Ok(())
    }

    /// Shutdown the desktop environment
    pub async fn shutdown(&self) -> Result<(), Box<dyn std::error::Error>> {
        tracing::info!("Shutting down Desktop Runtime");
        self.core.detener().await?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_desktop_runtime_creation() {
        let core = MotorCentral::nuevo("MotorTest", "0.1.0");
        let desktop = DesktopRuntime::new(core);
        assert!(desktop.initialize().await.is_ok());
        assert!(desktop.shutdown().await.is_ok());
    }
}
