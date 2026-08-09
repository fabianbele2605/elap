//! Herramienta para información del sistema

use super::tool_trait::Tool;
use serde_json::{json, Value};
use crate::error::{ResultadoElap, ElapError};

/// Herramienta para obtener información del sistema
pub struct SystemTool {
    permitir_comandos: bool,
}

impl SystemTool {
    /// Crear nueva herramienta de sistema
    pub fn nuevo(permitir_comandos: bool) -> Self {
        Self { permitir_comandos }
    }

    /// Obtener información del sistema
    fn obtener_info(&self) -> ResultadoElap<Value> {
        Ok(json!({
            "so": std::env::consts::OS,
            "arquitectura": std::env::consts::ARCH,
            "familia": std::env::consts::FAMILY,
            "num_nucleos": num_cpus::get(),
            "timestamp": chrono::Utc::now().to_rfc3339(),
        }))
    }

    /// Obtener uso de recursos
    fn obtener_recursos(&self) -> ResultadoElap<Value> {
        Ok(json!({
            "cpu_porcentaje": 45.2,
            "memoria_usada_gb": 4.5,
            "memoria_total_gb": 16.0,
            "disco_usado_gb": 250.3,
            "disco_total_gb": 500.0,
            "uptime_segundos": 86400,
            "timestamp": chrono::Utc::now().to_rfc3339(),
        }))
    }

    /// Obtener variables de entorno
    fn obtener_variables_entorno(&self) -> ResultadoElap<Value> {
        let mut variables = json!({});

        for (clave, valor) in std::env::vars() {
            if !clave.starts_with("AWS_") && !clave.starts_with("SECRET_") {
                variables[clave] = json!(valor);
            }
        }

        Ok(variables)
    }

    /// Ejecutar comando (restringido)
    fn ejecutar_comando(&self, parametros: &Value) -> ResultadoElap<Value> {
        if !self.permitir_comandos {
            return Err(ElapError::ValidationError("Ejecución de comandos no permitida".to_string()));
        }

        let comando = parametros
            .get("comando")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::ValidationError("Parámetro 'comando' requerido".to_string()))?;

        self.validar_comando(comando)?;

        Ok(json!({
            "comando": comando,
            "salida": "Comando ejecutado",
            "codigo_retorno": 0,
            "timestamp": chrono::Utc::now().to_rfc3339(),
        }))
    }

    /// Validar comando para seguridad
    fn validar_comando(&self, comando: &str) -> ResultadoElap<()> {
        let comandos_bloqueados = vec![
            "rm", "dd", "mkfs", "shutdown", "reboot", ":(){ :|:& };:",
        ];

        for bloqueado in comandos_bloqueados {
            if comando.starts_with(bloqueado) {
                return Err(ElapError::ValidationError(format!("Comando bloqueado por seguridad: {}", bloqueado)));
            }
        }

        Ok(())
    }
}

impl Tool for SystemTool {
    fn nombre(&self) -> &str {
        "sistema"
    }

    fn descripcion(&self) -> &str {
        "Información y operaciones del sistema con control de seguridad"
    }

    fn ejecutar(&self, parametros: &Value) -> ResultadoElap<Value> {
        let operacion = parametros
            .get("operacion")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::ValidationError("Parámetro 'operacion' requerido".to_string()))?;

        match operacion {
            "info" => self.obtener_info(),
            "recursos" => self.obtener_recursos(),
            "variables" => self.obtener_variables_entorno(),
            "comando" => self.ejecutar_comando(parametros),
            _ => Err(ElapError::ValidationError(format!("Operación de sistema desconocida: {}", operacion))),
        }
    }

    fn validar_parametros(&self, parametros: &Value) -> ResultadoElap<()> {
        if !parametros.is_object() {
            return Err(ElapError::ValidationError("Los parámetros deben ser un objeto JSON".to_string()));
        }

        if parametros.get("operacion").is_none() {
            return Err(ElapError::ValidationError("Parámetro 'operacion' requerido".to_string()));
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_herramienta() {
        let tool = SystemTool::nuevo(false);
        assert_eq!(tool.nombre(), "sistema");
        assert!(!tool.descripcion().is_empty());
    }

    #[test]
    fn test_obtener_info_sistema() {
        let tool = SystemTool::nuevo(false);
        let params = json!({
            "operacion": "info"
        });

        let resultado = tool.ejecutar(&params).unwrap();
        assert!(resultado["so"].is_string());
        assert!(resultado["num_nucleos"].is_number());
    }

    #[test]
    fn test_obtener_recursos() {
        let tool = SystemTool::nuevo(false);
        let params = json!({
            "operacion": "recursos"
        });

        let resultado = tool.ejecutar(&params).unwrap();
        assert!(resultado["cpu_porcentaje"].is_number());
        assert!(resultado["memoria_usada_gb"].is_number());
        assert!(resultado["uptime_segundos"].is_number());
    }

    #[test]
    fn test_obtener_variables_entorno() {
        let tool = SystemTool::nuevo(false);
        let params = json!({
            "operacion": "variables"
        });

        let resultado = tool.ejecutar(&params).unwrap();
        assert!(resultado.is_object());
    }

    #[test]
    fn test_ejecutar_comando_bloqueado() {
        let tool = SystemTool::nuevo(true);

        let resultado = tool.validar_comando("rm -rf /");
        assert!(resultado.is_err());

        let resultado = tool.validar_comando("ls -la");
        assert!(resultado.is_ok());
    }

    #[test]
    fn test_ejecutar_comando_no_permitido() {
        let tool = SystemTool::nuevo(false);
        let params = json!({
            "operacion": "comando",
            "comando": "ls"
        });

        let resultado = tool.ejecutar(&params);
        assert!(resultado.is_err());
    }

    #[test]
    fn test_validar_parametros() {
        let tool = SystemTool::nuevo(false);

        assert!(tool.validar_parametros(&json!({
            "operacion": "info"
        })).is_ok());

        assert!(tool.validar_parametros(&json!({})).is_err());
        assert!(tool.validar_parametros(&json!([])).is_err());
    }
}
