//! Herramienta para ejecutar queries SQL

use super::tool_trait::Tool;
use serde_json::{json, Value};
use crate::error::{ResultadoElap, ElapError};

/// Herramienta para ejecutar SQL (simulada)
pub struct SqlTool {
    base_datos: String,
}

impl SqlTool {
    /// Crear nueva herramienta SQL
    pub fn nuevo(base_datos: impl Into<String>) -> Self {
        Self {
            base_datos: base_datos.into(),
        }
    }

    /// Validar query SQL
    fn validar_query(&self, query: &str) -> ResultadoElap<()> {
        let query_upper = query.trim().to_uppercase();

        if query_upper.contains("DROP")
            || query_upper.contains("DELETE")
            || query_upper.contains("TRUNCATE")
        {
            return Err(ElapError::Validacion("Operaciones destructivas no permitidas".to_string()));
        }

        if !query_upper.starts_with("SELECT")
            && !query_upper.starts_with("INSERT")
            && !query_upper.starts_with("UPDATE")
        {
            return Err(ElapError::Validacion("Solo SELECT, INSERT y UPDATE permitidos".to_string()));
        }

        Ok(())
    }

    /// Ejecutar SELECT
    fn select(&self, parametros: &Value) -> ResultadoElap<Value> {
        let query = parametros
            .get("query")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'query' requerido".to_string()))?;

        self.validar_query(query)?;

        Ok(json!({
            "tipo": "SELECT",
            "base_datos": self.base_datos,
            "query": query,
            "filas": [
                { "id": 1, "nombre": "Usuario 1" },
                { "id": 2, "nombre": "Usuario 2" }
            ],
            "total_filas": 2,
            "timestamp": chrono::Utc::now().to_rfc3339(),
        }))
    }

    /// Ejecutar INSERT
    fn insert(&self, parametros: &Value) -> ResultadoElap<Value> {
        let query = parametros
            .get("query")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'query' requerido".to_string()))?;

        self.validar_query(query)?;

        Ok(json!({
            "tipo": "INSERT",
            "base_datos": self.base_datos,
            "query": query,
            "filas_insertadas": 1,
            "id_generado": 123,
            "timestamp": chrono::Utc::now().to_rfc3339(),
        }))
    }

    /// Ejecutar UPDATE
    fn update(&self, parametros: &Value) -> ResultadoElap<Value> {
        let query = parametros
            .get("query")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'query' requerido".to_string()))?;

        self.validar_query(query)?;

        Ok(json!({
            "tipo": "UPDATE",
            "base_datos": self.base_datos,
            "query": query,
            "filas_actualizadas": 1,
            "timestamp": chrono::Utc::now().to_rfc3339(),
        }))
    }
}

impl Tool for SqlTool {
    fn nombre(&self) -> &str {
        "sql"
    }

    fn descripcion(&self) -> &str {
        "Ejecutar queries SQL (SELECT, INSERT, UPDATE)"
    }

    fn ejecutar(&self, parametros: &Value) -> ResultadoElap<Value> {
        let operacion = if let Some(op) = parametros.get("operacion").and_then(|v| v.as_str()) {
            op
        } else {
            let query = parametros
                .get("query")
                .and_then(|v| v.as_str())
                .unwrap_or("");
            let upper = query.trim().to_uppercase();
            if upper.starts_with("SELECT") {
                "select"
            } else if upper.starts_with("INSERT") {
                "insert"
            } else {
                "update"
            }
        };

        match operacion {
            "select" => self.select(parametros),
            "insert" => self.insert(parametros),
            "update" => self.update(parametros),
            _ => Err(ElapError::Validacion(format!("Operación SQL desconocida: {}", operacion))),
        }
    }

    fn validar_parametros(&self, parametros: &Value) -> ResultadoElap<()> {
        if !parametros.is_object() {
            return Err(ElapError::Validacion("Los parámetros deben ser un objeto JSON".to_string()));
        }

        if parametros.get("query").is_none() {
            return Err(ElapError::Validacion("Parámetro 'query' requerido".to_string()));
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_herramienta() {
        let tool = SqlTool::nuevo("main_db");
        assert_eq!(tool.nombre(), "sql");
        assert!(!tool.descripcion().is_empty());
    }

    #[test]
    fn test_select_query() {
        let tool = SqlTool::nuevo("main_db");
        let params = json!({
            "operacion": "select",
            "query": "SELECT * FROM usuarios"
        });

        let resultado = tool.ejecutar(&params).unwrap();
        assert_eq!(resultado["tipo"], "SELECT");
        assert_eq!(resultado["total_filas"], 2);
    }

    #[test]
    fn test_insert_query() {
        let tool = SqlTool::nuevo("main_db");
        let params = json!({
            "operacion": "insert",
            "query": "INSERT INTO usuarios (nombre) VALUES ('Juan')"
        });

        let resultado = tool.ejecutar(&params).unwrap();
        assert_eq!(resultado["tipo"], "INSERT");
        assert_eq!(resultado["filas_insertadas"], 1);
    }

    #[test]
    fn test_validar_query_destructiva() {
        let tool = SqlTool::nuevo("main_db");

        let resultado = tool.validar_query("DROP TABLE usuarios");
        assert!(resultado.is_err());

        let resultado = tool.validar_query("DELETE FROM usuarios");
        assert!(resultado.is_err());
    }

    #[test]
    fn test_validar_query_permitida() {
        let tool = SqlTool::nuevo("main_db");

        assert!(tool.validar_query("SELECT * FROM usuarios").is_ok());
        assert!(tool.validar_query("INSERT INTO usuarios VALUES (1)").is_ok());
        assert!(tool.validar_query("UPDATE usuarios SET nombre='Juan'").is_ok());
    }

    #[test]
    fn test_validar_parametros() {
        let tool = SqlTool::nuevo("main_db");

        assert!(tool.validar_parametros(&json!({
            "query": "SELECT * FROM usuarios"
        })).is_ok());

        assert!(tool.validar_parametros(&json!({})).is_err());
    }
}
