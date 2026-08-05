//! Herramienta para ejecutar comandos remotos vía SSH

use super::tool_trait::Tool;
use serde_json::{json, Value};
use crate::error::{ResultadoElap, ElapError};

/// Herramienta para SSH (simulada)
pub struct SshTool {
    hosts_permitidos: Vec<String>,
}

impl SshTool {
    /// Crear nueva herramienta SSH con hosts permitidos
    pub fn nuevo(hosts_permitidos: Vec<String>) -> Self {
        Self { hosts_permitidos }
    }

    /// Validar host
    fn validar_host(&self, host: &str) -> ResultadoElap<()> {
        if !self.hosts_permitidos.contains(&host.to_string()) {
            return Err(ElapError::Validacion(format!("Host '{}' no está en whitelist", host)));
        }
        Ok(())
    }

    /// Validar comando
    fn validar_comando(&self, comando: &str) -> ResultadoElap<()> {
        let comandos_bloqueados = vec!["rm -rf", "dd", ":(){ :|:& };:"];

        for bloqueado in comandos_bloqueados {
            if comando.contains(bloqueado) {
                return Err(ElapError::Validacion(format!("Comando bloqueado: {}", bloqueado)));
            }
        }

        Ok(())
    }

    /// Ejecutar comando remoto
    fn ejecutar_remoto(&self, parametros: &Value) -> ResultadoElap<Value> {
        let host = parametros
            .get("host")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'host' requerido".to_string()))?;

        let comando = parametros
            .get("comando")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'comando' requerido".to_string()))?;

        self.validar_host(host)?;
        self.validar_comando(comando)?;

        Ok(json!({
            "host": host,
            "comando": comando,
            "estado": 0,
            "salida": "Comando ejecutado exitosamente",
            "timestamp": chrono::Utc::now().to_rfc3339(),
        }))
    }

    /// Copiar archivo remoto
    fn copiar_archivo(&self, parametros: &Value) -> ResultadoElap<Value> {
        let host = parametros
            .get("host")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'host' requerido".to_string()))?;

        let origen = parametros
            .get("origen")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'origen' requerido".to_string()))?;

        let destino = parametros
            .get("destino")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'destino' requerido".to_string()))?;

        self.validar_host(host)?;

        Ok(json!({
            "host": host,
            "origen": origen,
            "destino": destino,
            "bytes_copiados": 4096,
            "timestamp": chrono::Utc::now().to_rfc3339(),
        }))
    }
}

impl Tool for SshTool {
    fn nombre(&self) -> &str {
        "ssh"
    }

    fn descripcion(&self) -> &str {
        "Ejecutar comandos remotos y copiar archivos vía SSH"
    }

    fn ejecutar(&self, parametros: &Value) -> ResultadoElap<Value> {
        let operacion = parametros
            .get("operacion")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'operacion' requerido".to_string()))?;

        match operacion {
            "ejecutar" => self.ejecutar_remoto(parametros),
            "copiar" => self.copiar_archivo(parametros),
            _ => Err(ElapError::Validacion(format!("Operación SSH desconocida: {}", operacion))),
        }
    }

    fn validar_parametros(&self, parametros: &Value) -> ResultadoElap<()> {
        if !parametros.is_object() {
            return Err(ElapError::Validacion("Los parámetros deben ser un objeto JSON".to_string()));
        }

        if parametros.get("operacion").is_none() {
            return Err(ElapError::Validacion("Parámetro 'operacion' requerido".to_string()));
        }

        if parametros.get("host").is_none() {
            return Err(ElapError::Validacion("Parámetro 'host' requerido".to_string()));
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn crear_herramienta() -> SshTool {
        SshTool::nuevo(vec![
            "servidor1.com".to_string(),
            "servidor2.com".to_string(),
        ])
    }

    #[test]
    fn test_crear_herramienta() {
        let tool = crear_herramienta();
        assert_eq!(tool.nombre(), "ssh");
        assert!(!tool.descripcion().is_empty());
    }

    #[test]
    fn test_ejecutar_comando_remoto() {
        let tool = crear_herramienta();
        let params = json!({
            "operacion": "ejecutar",
            "host": "servidor1.com",
            "comando": "ls -la /home"
        });

        let resultado = tool.ejecutar(&params).unwrap();
        assert_eq!(resultado["host"], "servidor1.com");
        assert_eq!(resultado["estado"], 0);
    }

    #[test]
    fn test_validar_host_no_permitido() {
        let tool = crear_herramienta();

        let resultado = tool.validar_host("host-no-permitido.com");
        assert!(resultado.is_err());
    }

    #[test]
    fn test_validar_comando_bloqueado() {
        let tool = crear_herramienta();

        let resultado = tool.validar_comando("rm -rf /");
        assert!(resultado.is_err());

        let resultado = tool.validar_comando("ls -la");
        assert!(resultado.is_ok());
    }

    #[test]
    fn test_copiar_archivo() {
        let tool = crear_herramienta();
        let params = json!({
            "operacion": "copiar",
            "host": "servidor1.com",
            "origen": "/home/archivo.txt",
            "destino": "/backup/archivo.txt"
        });

        let resultado = tool.ejecutar(&params).unwrap();
        assert_eq!(resultado["host"], "servidor1.com");
        assert!(resultado["bytes_copiados"].is_number());
    }

    #[test]
    fn test_validar_parametros() {
        let tool = crear_herramienta();

        assert!(tool.validar_parametros(&json!({
            "operacion": "ejecutar",
            "host": "servidor1.com"
        })).is_ok());

        assert!(tool.validar_parametros(&json!({
            "operacion": "ejecutar"
        })).is_err());
    }
}
