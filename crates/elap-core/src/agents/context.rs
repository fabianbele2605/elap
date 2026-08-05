//! Contexto de ejecución del agente

use serde_json::{json, Value as JsonValue};
use std::collections::HashMap;

/// Contexto disponible para el agente
pub struct ContextoAgente {
    /// Variables disponibles
    pub variables: HashMap<String, JsonValue>,
    /// Objetivo del agente
    pub objetivo: String,
    /// Restricciones
    pub restricciones: Vec<String>,
    /// Timestamp de inicio
    pub timestamp_inicio: String,
}

impl ContextoAgente {
    /// Crear nuevo contexto
    pub fn nuevo(objetivo: String) -> Self {
        Self {
            variables: HashMap::new(),
            objetivo,
            restricciones: Vec::new(),
            timestamp_inicio: chrono::Utc::now().to_rfc3339(),
        }
    }

    /// Establecer variable
    pub fn set_variable(&mut self, clave: String, valor: JsonValue) {
        self.variables.insert(clave, valor);
    }

    /// Obtener variable
    pub fn get_variable(&self, clave: &str) -> Option<JsonValue> {
        self.variables.get(clave).cloned()
    }

    /// Agregar restricción
    pub fn agregar_restriccion(&mut self, restriccion: String) {
        self.restricciones.push(restriccion);
    }

    /// Obtener todas las restricciones
    pub fn obtener_restricciones(&self) -> &[String] {
        &self.restricciones
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_contexto() {
        let contexto = ContextoAgente::nuevo("Analizar datos".to_string());
        assert_eq!(contexto.objetivo, "Analizar datos");
        assert_eq!(contexto.variables.len(), 0);
    }

    #[test]
    fn test_set_get_variable() {
        let mut contexto = ContextoAgente::nuevo("Test".to_string());
        contexto.set_variable("clave1".to_string(), json!("valor1"));

        let obtenida = contexto.get_variable("clave1");
        assert_eq!(obtenida, Some(json!("valor1")));
    }

    #[test]
    fn test_agregar_restriccion() {
        let mut contexto = ContextoAgente::nuevo("Test".to_string());
        contexto.agregar_restriccion("Máximo 5 intentos".to_string());

        assert_eq!(contexto.obtener_restricciones().len(), 1);
    }
}
