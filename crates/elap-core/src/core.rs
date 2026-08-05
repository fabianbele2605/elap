//! Motor central y gestión de estado

/// Motor central
#[derive(Debug, Clone)]
pub struct MotorCentral {
    nombre: String,
    version: String,
}

impl MotorCentral {
    /// Crear una nueva instancia del MotorCentral
    pub fn nuevo(nombre: impl Into<String>, version: impl Into<String>) -> Self {
        Self {
            nombre: nombre.into(),
            version: version.into(),
        }
    }

    /// Obtener nombre del motor
    pub fn nombre(&self) -> &str {
        &self.nombre
    }

    /// Obtener versión del motor
    pub fn version(&self) -> &str {
        &self.version
    }

    /// Iniciar el motor
    pub async fn iniciar(&self) -> Result<(), crate::error::ElapError> {
        tracing::info!(
            nombre = self.nombre,
            version = self.version,
            "Iniciando Motor Central ELAP"
        );
        Ok(())
    }

    /// Detener el motor
    pub async fn detener(&self) -> Result<(), crate::error::ElapError> {
        tracing::info!(nombre = self.nombre, "Deteniendo Motor Central ELAP");
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_creacion_motor() {
        let motor = MotorCentral::nuevo("MotorTest", "0.1.0");
        assert_eq!(motor.nombre(), "MotorTest");
        assert_eq!(motor.version(), "0.1.0");
    }

    #[tokio::test]
    async fn test_ciclo_vida_motor() {
        let motor = MotorCentral::nuevo("MotorTest", "0.1.0");
        assert!(motor.iniciar().await.is_ok());
        assert!(motor.detener().await.is_ok());
    }
}
