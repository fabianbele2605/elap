//! Motor central y gestión de estado

use crate::logging::inicializar_logging;
use crate::error::{ElapError, ResultadoElap};
use tracing::info;
use crate::Configuracion;
use crate::security::{GestorRbac, AuditorRbac};

/// Motor central de ELAP.
#[derive(Debug)]
pub struct MotorCentral {
    config: Configuracion,
    gestor_rbac: GestorRbac,
    auditor: AuditorRbac,
}

impl MotorCentral {
    /// Crea una nueva instancia del MotorCentral.
    pub fn nuevo(config: Configuracion) -> Self {
        Self {
            config,
            gestor_rbac: GestorRbac::nuevo(),
            auditor: AuditorRbac::nuevo(),
        }
    }

    /// Obtener configuración del motor.
    pub fn config(&self) -> &Configuracion {
        &self.config
    }

    /// Obtener gestor de control de acceso (RBAC).
    pub fn rbac(&self) -> &GestorRbac {
        &self.gestor_rbac
    }

    /// Obtener auditor de acceso.
    pub fn auditor(&self) -> &AuditorRbac {
        &self.auditor
    }

    /// Iniciar el motor central.
    pub async fn iniciar(&self) -> ResultadoElap<()> {
        // Inicializar logging
        inicializar_logging(&self.config.ruta_logs, &self.config.nivel_logging)
            .map_err(|e| ElapError::Config(e.to_string()))?;

        info!("Motor Central iniciando...");
        info!("Modo: {}", self.config.modo);
        info!("Versión: {}", self.config.version);
        info!("Nombre: {}", self.config.nombre_app);

        // Validar configuración
        self.config.validar()
            .map_err(|e| ElapError::Validacion(e.to_string()))?;

        Ok(())
    }

    /// Detener el motor central.
    pub async fn detener(&self) -> ResultadoElap<()> {
        info!("Motor Central deteniendo...");
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{Rol, Permiso};

    #[test]
    fn test_creacion_motor() {
        let config = Configuracion::defecto();
        let motor = MotorCentral::nuevo(config);
        assert_eq!(motor.config().nombre_app, "ELAP");
    }

    #[tokio::test]
    async fn test_ciclo_vida_motor() {
        let config = Configuracion::defecto();
        let motor = MotorCentral::nuevo(config);
        assert!(motor.iniciar().await.is_ok());
        assert!(motor.detener().await.is_ok());
    }

    #[test]
    fn test_motor_tiene_rbac() {
        let config = Configuracion::defecto();
        let motor = MotorCentral::nuevo(config);
        let rbac = motor.rbac();
        // Verificar que RBAC fue inicializado
        assert!(rbac.validar_permiso(Rol::Admin, Permiso::LeerArchivos).is_ok());
    }

    #[test]
    fn test_motor_tiene_auditor() {
        let config = Configuracion::defecto();
        let motor = MotorCentral::nuevo(config);
        let auditor = motor.auditor();
        // Registrar una acción y verificar
        auditor.registrar_acceso("admin", "test", "recurso");
        assert_eq!(auditor.obtener_registros().len(), 1);
    }
}
