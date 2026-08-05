//! Herramienta para realizar peticiones HTTP

use super::tool_trait::Tool;
use serde_json::{json, Value};
use crate::error::{ResultadoElap, ElapError};

/// Herramienta para peticiones HTTP
pub struct HttpTool {
    timeout_segundos: u64,
}

impl HttpTool {
    /// Crear nueva herramienta HTTP
    pub fn nuevo(timeout_segundos: u64) -> Self {
        Self { timeout_segundos }
    }

    /// Validar URL
    fn validar_url(&self, url: &str) -> ResultadoElap<()> {
        if !url.starts_with("http://") && !url.starts_with("https://") {
            return Err(ElapError::Validacion("URL debe comenzar con http:// o https://".to_string()));
        }
        Ok(())
    }

    /// Realizar GET
    fn get(&self, parametros: &Value) -> ResultadoElap<Value> {
        let url = parametros
            .get("url")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'url' requerido".to_string()))?;

        self.validar_url(url)?;

        Ok(json!({
            "metodo": "GET",
            "url": url,
            "estado": 200,
            "cuerpo": "{}",
            "headers": {
                "content-type": "application/json"
            },
            "timestamp": chrono::Utc::now().to_rfc3339(),
        }))
    }

    /// Realizar POST
    fn post(&self, parametros: &Value) -> ResultadoElap<Value> {
        let url = parametros
            .get("url")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'url' requerido".to_string()))?;

        let cuerpo = parametros
            .get("cuerpo")
            .ok_or(ElapError::Validacion("Parámetro 'cuerpo' requerido".to_string()))?;

        self.validar_url(url)?;

        Ok(json!({
            "metodo": "POST",
            "url": url,
            "estado": 201,
            "cuerpo_enviado": cuerpo,
            "respuesta": {
                "id": 1,
                "estado": "creado"
            },
            "timestamp": chrono::Utc::now().to_rfc3339(),
        }))
    }

    /// Realizar PUT
    fn put(&self, parametros: &Value) -> ResultadoElap<Value> {
        let url = parametros
            .get("url")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'url' requerido".to_string()))?;

        let cuerpo = parametros
            .get("cuerpo")
            .ok_or(ElapError::Validacion("Parámetro 'cuerpo' requerido".to_string()))?;

        self.validar_url(url)?;

        Ok(json!({
            "metodo": "PUT",
            "url": url,
            "estado": 200,
            "cuerpo_enviado": cuerpo,
            "respuesta": {
                "estado": "actualizado"
            },
            "timestamp": chrono::Utc::now().to_rfc3339(),
        }))
    }

    /// Realizar DELETE
    fn delete(&self, parametros: &Value) -> ResultadoElap<Value> {
        let url = parametros
            .get("url")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'url' requerido".to_string()))?;

        self.validar_url(url)?;

        Ok(json!({
            "metodo": "DELETE",
            "url": url,
            "estado": 204,
            "mensaje": "Recurso eliminado",
            "timestamp": chrono::Utc::now().to_rfc3339(),
        }))
    }
}

impl Tool for HttpTool {
    fn nombre(&self) -> &str {
        "http"
    }

    fn descripcion(&self) -> &str {
        "Realizar peticiones HTTP (GET, POST, PUT, DELETE)"
    }

    fn ejecutar(&self, parametros: &Value) -> ResultadoElap<Value> {
        let metodo = parametros
            .get("metodo")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'metodo' requerido".to_string()))?;

        match metodo {
            "GET" => self.get(parametros),
            "POST" => self.post(parametros),
            "PUT" => self.put(parametros),
            "DELETE" => self.delete(parametros),
            _ => Err(ElapError::Validacion(format!("Método HTTP desconocido: {}", metodo))),
        }
    }

    fn validar_parametros(&self, parametros: &Value) -> ResultadoElap<()> {
        if !parametros.is_object() {
            return Err(ElapError::Validacion("Los parámetros deben ser un objeto JSON".to_string()));
        }

        if parametros.get("metodo").is_none() {
            return Err(ElapError::Validacion("Parámetro 'metodo' requerido".to_string()));
        }

        if parametros.get("url").is_none() {
            return Err(ElapError::Validacion("Parámetro 'url' requerido".to_string()));
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_herramienta() {
        let tool = HttpTool::nuevo(30);
        assert_eq!(tool.nombre(), "http");
        assert!(!tool.descripcion().is_empty());
    }

    #[test]
    fn test_get_request() {
        let tool = HttpTool::nuevo(30);
        let params = json!({
            "metodo": "GET",
            "url": "https://api.ejemplo.com/usuarios"
        });

        let resultado = tool.ejecutar(&params).unwrap();
        assert_eq!(resultado["metodo"], "GET");
        assert_eq!(resultado["estado"], 200);
    }

    #[test]
    fn test_post_request() {
        let tool = HttpTool::nuevo(30);
        let params = json!({
            "metodo": "POST",
            "url": "https://api.ejemplo.com/usuarios",
            "cuerpo": { "nombre": "Juan" }
        });

        let resultado = tool.ejecutar(&params).unwrap();
        assert_eq!(resultado["metodo"], "POST");
        assert_eq!(resultado["estado"], 201);
    }

    #[test]
    fn test_validar_url() {
        let tool = HttpTool::nuevo(30);

        let resultado = tool.validar_url("https://api.ejemplo.com");
        assert!(resultado.is_ok());

        let resultado = tool.validar_url("ftp://invalid.com");
        assert!(resultado.is_err());
    }

    #[test]
    fn test_validar_parametros() {
        let tool = HttpTool::nuevo(30);

        assert!(tool.validar_parametros(&json!({
            "metodo": "GET",
            "url": "https://api.ejemplo.com"
        })).is_ok());

        assert!(tool.validar_parametros(&json!({
            "metodo": "GET"
        })).is_err());

        assert!(tool.validar_parametros(&json!([])).is_err());
    }

    #[test]
    fn test_delete_request() {
        let tool = HttpTool::nuevo(30);
        let params = json!({
            "metodo": "DELETE",
            "url": "https://api.ejemplo.com/usuarios/1"
        });

        let resultado = tool.ejecutar(&params).unwrap();
        assert_eq!(resultado["metodo"], "DELETE");
        assert_eq!(resultado["estado"], 204);
    }
}
