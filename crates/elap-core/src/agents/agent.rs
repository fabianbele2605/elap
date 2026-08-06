//! Definición base de Agente

use serde_json::{json, Value as JsonValue};
use crate::error::{ResultadoElap, ElapError};

/// Estados posibles de un agente
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum EstadoAgente {
    /// Esperando instrucción
    Inactivo,
    /// Planificando qué hacer
    Planificando,
    /// Ejecutando acciones
    Ejecutando,
    /// Pensando/reflexionando
    Reflexionando,
    /// Completado exitosamente
    Completado,
    /// Error durante ejecución
    Error,
}

impl std::fmt::Display for EstadoAgente {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            EstadoAgente::Inactivo => write!(f, "inactivo"),
            EstadoAgente::Planificando => write!(f, "planificando"),
            EstadoAgente::Ejecutando => write!(f, "ejecutando"),
            EstadoAgente::Reflexionando => write!(f, "reflexionando"),
            EstadoAgente::Completado => write!(f, "completado"),
            EstadoAgente::Error => write!(f, "error"),
        }
    }
}

/// Agente inteligente
#[derive(Clone)]
pub struct Agent {
    /// Identificador único
    pub id: String,
    /// Nombre del agente
    pub nombre: String,
    /// Descripción de rol
    pub rol: String,
    /// Estado actual
    pub estado: EstadoAgente,
    /// Historial de acciones
    pub historial_acciones: Vec<String>,
    /// Reflections/pensamientos
    pub reflexiones: Vec<String>,
}

impl Agent {
    /// Crear nuevo agente
    pub fn nuevo(nombre: String, rol: String) -> Self {
        Self {
            id: uuid::Uuid::new_v4().to_string(),
            nombre,
            rol,
            estado: EstadoAgente::Inactivo,
            historial_acciones: Vec::new(),
            reflexiones: Vec::new(),
        }
    }

    /// Cambiar estado
    pub fn cambiar_estado(&mut self, nuevo_estado: EstadoAgente) {
        self.estado = nuevo_estado;
    }

    /// Registrar acción
    pub fn registrar_accion(&mut self, accion: String) {
        self.historial_acciones.push(format!(
            "[{}] {}",
            chrono::Utc::now().to_rfc3339(),
            accion
        ));
    }

    /// Registrar reflexión
    pub fn registrar_reflexion(&mut self, reflexion: String) {
        self.reflexiones.push(format!(
            "[{}] {}",
            chrono::Utc::now().to_rfc3339(),
            reflexion
        ));
    }

    /// Obtener resumen del agente
    pub fn resumen(&self) -> JsonValue {
        json!({
            "id": self.id,
            "nombre": self.nombre,
            "rol": self.rol,
            "estado": self.estado.to_string(),
            "acciones_totales": self.historial_acciones.len(),
            "reflexiones": self.reflexiones.len(),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_agente() {
        let agent = Agent::nuevo(
            "Analizador".to_string(),
            "Analista de datos".to_string(),
        );

        assert_eq!(agent.nombre, "Analizador");
        assert_eq!(agent.estado, EstadoAgente::Inactivo);
    }

    #[test]
    fn test_cambiar_estado() {
        let mut agent = Agent::nuevo("Test".to_string(), "Test".to_string());
        agent.cambiar_estado(EstadoAgente::Ejecutando);
        assert_eq!(agent.estado, EstadoAgente::Ejecutando);
    }

    #[test]
    fn test_registrar_accion() {
        let mut agent = Agent::nuevo("Test".to_string(), "Test".to_string());
        agent.registrar_accion("Acción 1".to_string());
        assert_eq!(agent.historial_acciones.len(), 1);
    }

    #[test]
    fn test_registrar_reflexion() {
        let mut agent = Agent::nuevo("Test".to_string(), "Test".to_string());
        agent.registrar_reflexion("Reflexión 1".to_string());
        assert_eq!(agent.reflexiones.len(), 1);
    }

    #[test]
    fn test_estado_display() {
        assert_eq!(EstadoAgente::Inactivo.to_string(), "inactivo");
        assert_eq!(EstadoAgente::Ejecutando.to_string(), "ejecutando");
    }

    #[test]
    fn test_resumen() {
        let agent = Agent::nuevo("Test".to_string(), "Role".to_string());
        let resumen = agent.resumen();
        assert_eq!(resumen["nombre"], "Test");
    }
}
