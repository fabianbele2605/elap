//! Trait base para herramientas

use serde_json::Value as JsonValue;
use crate::error::ResultadoElap;

/// Trait que todas las herramientas implementan
pub trait Tool: Send + Sync {
    /// Nombre de la herramienta
    fn nombre(&self) -> &str;

    /// Descripción
    fn descripcion(&self) -> &str;

    /// Ejecutar la herramienta
    fn ejecutar(&self, parametros: &JsonValue) -> ResultadoElap<JsonValue>;

    /// Validar parámetros antes de ejecutar
    fn validar_parametros(&self, parametros: &JsonValue) -> ResultadoElap<()>;
}

/// Resultado de ejecución
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct ResultadoHerramienta {
    pub exitoso: bool,
    pub datos: JsonValue,
    pub error: Option<String>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_resultado_herramienta() {
        let resultado = ResultadoHerramienta {
            exitoso: true,
            datos: serde_json::json!({"key": "value"}),
            error: None,
        };

        assert!(resultado.exitoso);
    }
}
