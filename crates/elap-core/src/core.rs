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
            .map_err(|e| ElapError::ConfigError(e.to_string()))?;

        info!("Motor Central iniciando...");
        info!("Modo: {}", self.config.modo);
        info!("Versión: {}", self.config.version);
        info!("Nombre: {}", self.config.nombre_app);

        // Validar configuración
        self.config.validar()
            .map_err(|e| ElapError::ValidationError(e.to_string()))?;

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

    #[test]
    fn test_flujo_completo_rbac_y_auditoria() {
        // Test E2E: Usuario intenta ejecutar herramienta
        // 1. Crear motor con configuración
        let config = Configuracion::defecto();
        let motor = MotorCentral::nuevo(config);

        // 2. Simular: usuario ADMIN intenta ejecutar herramienta
        let usuario_rol = Rol::Admin;
        let herramienta = "procesar_datos";

        // 3. Validar permiso (RBAC)
        let permiso_ok = motor.rbac()
            .validar_permiso(usuario_rol, Permiso::EjecutarHerramientas);
        assert!(permiso_ok.is_ok(), "Admin debería tener permiso");

        // 4. Registrar acceso exitoso (Auditoría)
        motor.auditor().registrar_acceso("admin_001", "ejecutar_herramienta", herramienta);

        // 5. Validar usuario normal (sin permiso para cambiar config)
        let usuario_rol_normal = Rol::Usuario;
        let permiso_fail = motor.rbac()
            .validar_permiso(usuario_rol_normal, Permiso::CambiarConfiguracion);
        assert!(permiso_fail.is_err(), "Usuario normal no debería tener permiso");

        // 6. Registrar intento fallido (Auditoría)
        motor.auditor().registrar_intento_fallido(
            "usuario_001",
            "cambiar_config",
            "config.yaml"
        );

        // 7. Verificar registros auditados
        let registros = motor.auditor().obtener_registros();
        assert_eq!(registros.len(), 2, "Debe haber 2 registros auditados");
        assert_eq!(registros[0].resultado, "exitoso");
        assert_eq!(registros[1].resultado, "denegado");
    }
}
