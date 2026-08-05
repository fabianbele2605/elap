#![warn(missing_docs)]

//! # ELAP Desktop Runtime
//!
//! Capa de interfaz gráfica para ELAP usando Tauri.
//! Proporciona GUI y gestión de ventanas para la plataforma.

use elap_core::{MotorCentral, Configuracion};

/// Gestor de aplicación desktop
#[derive(Debug)]
pub struct DesktopRuntime {
    core: MotorCentral,
}

impl DesktopRuntime {
    /// Crear una nueva instancia de DesktopRuntime
    pub fn new(core: MotorCentral) -> Self {
        Self { core }
    }

    /// Inicializar el entorno desktop
    pub async fn initialize(&self) -> Result<(), Box<dyn std::error::Error>> {
        tracing::info!("Inicializando Desktop Runtime");
        self.core.iniciar().await?;
        Ok(())
    }

    /// Detener el entorno desktop
    pub async fn shutdown(&self) -> Result<(), Box<dyn std::error::Error>> {
        tracing::info!("Deteniendo Desktop Runtime");
        self.core.detener().await?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_desktop_runtime_creation() {
        let config = Configuracion::defecto();
        let core = MotorCentral::nuevo(config);
        let desktop = DesktopRuntime::new(core);
        assert!(desktop.initialize().await.is_ok());
        assert!(desktop.shutdown().await.is_ok());
    }
}
