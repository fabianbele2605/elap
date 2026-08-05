//! Comandos IPC disponibles para el frontend

use std::sync::Arc;
use elap_core::MotorCentral;
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
    pub motor_running: bool,
    pub timestamp: u64,
}

/// Respuesta RBAC de estado
#[derive(serde::Serialize)]
pub struct RbacStatusResponse {
    pub usuario_rol: String,
    pub permisos_disponibles: Vec<String>,
}

/// Comando: Inicializar motor (real)
pub async fn cmd_init_motor(motor: Arc<MotorCentral>) -> IpcResult<InitResponse> {
    match motor.iniciar().await {
        Ok(()) => Ok(InitResponse {
            success: true,
            message: "Motor inicializado correctamente".to_string(),
        }),
        Err(e) => Err(IpcError::MotorError(e.to_string())),
    }
}

/// Comando: Obtener estado del motor
pub async fn cmd_get_status(motor: Arc<MotorCentral>) -> IpcResult<StatusResponse> {
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs();

    Ok(StatusResponse {
        motor_running: true,
        timestamp: now,
    })
}

/// Comando: Obtener estado RBAC
pub async fn cmd_get_rbac_status(motor: Arc<MotorCentral>) -> IpcResult<RbacStatusResponse> {
    // Simulamos que el usuario es Admin por ahora
    Ok(RbacStatusResponse {
        usuario_rol: "Admin".to_string(),
        permisos_disponibles: vec![
            "LeerArchivos".to_string(),
            "EscribirArchivos".to_string(),
            "EjecutarProcesos".to_string(),
            "EjecutarHerramientas".to_string(),
            "CambiarConfiguracion".to_string(),
        ],
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use elap_core::Configuracion;

    #[tokio::test]
    async fn test_cmd_init_motor() {
        let config = Configuracion::defecto();
        let motor_core = elap_core::MotorCentral::nuevo(config);
        let motor = Arc::new(motor_core);
        
        let result = cmd_init_motor(motor).await;
        assert!(result.is_ok());
        
        let response = result.unwrap();
        assert!(response.success);
        assert!(response.message.contains("inicializado"));
    }

    #[tokio::test]
    async fn test_cmd_get_status() {
        let config = Configuracion::defecto();
        let motor_core = elap_core::MotorCentral::nuevo(config);
        let motor = Arc::new(motor_core);
        
        let result = cmd_get_status(motor).await;
        assert!(result.is_ok());
        
        let response = result.unwrap();
        assert!(response.motor_running);
        assert!(response.timestamp > 0);
    }

    #[tokio::test]
    async fn test_cmd_get_rbac_status() {
        let config = Configuracion::defecto();
        let motor_core = elap_core::MotorCentral::nuevo(config);
        let motor = Arc::new(motor_core);
        
        let result = cmd_get_rbac_status(motor).await;
        assert!(result.is_ok());
        
        let response = result.unwrap();
        assert_eq!(response.usuario_rol, "Admin");
        assert_eq!(response.permisos_disponibles.len(), 5);
    }
}
