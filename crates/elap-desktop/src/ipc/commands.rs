//! Comandos IPC disponibles para el frontend

use crate::DesktopRuntime;
use super::errors::IpcError;

/// Resultado de operacion IPC
pub type IpcResult<T> = Result<T, IpcError>;

/// Respuesta de inicialización del motor
#[derive(serde::Serialize)]
pub struct InitResponse {
    pub success:bool,
    pub message: String,
}

/// Respuesta de estado
#[derive(serde::Serialize)]
pub struct StatusResponse {
    pub running: bool,
    pub timestamp: u64,
}

/// Comando: Inicializar motor
pub async fn cmd_init_motor() -> IpcResult<InitResponse> {
    Ok(InitResponse {
        success: true,
        message: "Motor inicializando".to_string(),
    })
}

/// Comando: Obtener estado del motor
pub async fn cmd_get_status() -> IpcResult<StatusResponse> {
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs();

    Ok(StatusResponse {
        running: true,
        timestamp: now,
    })
}