//! Sandboxing para herramientas con validación de seguridad

use serde_json::Value as JsonValue;
use std::time::Duration;
use crate::error::{ResultadoElap, ElapError};
use crate::security::Permiso;

/// Política de ejecución para una herramienta
#[derive(Debug, Clone)]
pub enum PoliticaHerramienta {
    /// Permitir siempre
    Permitir,
    /// Denegar siempre
    Denegar,
    /// Requerir permiso RBAC específico
    RequerirPermiso(String),
}

/// Configuración de sandbox para una herramienta
#[derive(Debug, Clone)]
pub struct SandboxHerramienta {
    /// Política de ejecución
    pub politica: PoliticaHerramienta,
    /// Timeout máximo de ejecución
    pub timeout: Duration,
    /// Límite máximo de memoria en MB
    pub limite_memoria_mb: u32,
    /// Paths permitidos (si está vacío, todos)
    pub paths_permitidos: Vec<String>,
    /// Comandos bloqueados
    pub comandos_bloqueados: Vec<String>,
}

impl Default for SandboxHerramienta {
    fn default() -> Self {
        Self {
            politica: PoliticaHerramienta::RequerirPermiso("EjecutarHerramientas".to_string()),
            timeout: Duration::from_secs(30),
            limite_memoria_mb: 512,
            paths_permitidos: vec![
                "/data".to_string(),
                "/tmp".to_string(),
                "/reports".to_string(),
            ],
            comandos_bloqueados: vec![
                "rm -rf".to_string(),
                "dd".to_string(),
                "mkfs".to_string(),
                ":(){ :|:& };:".to_string(),
            ],
        }
    }
}

/// Validador de seguridad para herramientas
pub struct ValidadorSeguridad;

impl ValidadorSeguridad {
    /// Validar que el usuario tiene permiso para ejecutar
    pub fn validar_permiso(
        permisos_usuario: &[Permiso],
        permiso_requerido: &str,
    ) -> ResultadoElap<()> {
        let permiso_existe = permisos_usuario.iter().any(|p| {
            format!("{:?}", p).to_lowercase().contains(&permiso_requerido.to_lowercase())
        });

        if permiso_existe {
            Ok(())
        } else {
            Err(ElapError::Validacion(format!(
                "Usuario no tiene permiso: {}",
                permiso_requerido
            )))
        }
    }

    /// Validar ruta dentro de whitelist
    pub fn validar_ruta(
        ruta: &str,
        paths_permitidos: &[String],
    ) -> ResultadoElap<()> {
        if paths_permitidos.is_empty() {
            return Ok(());
        }

        for path_permitido in paths_permitidos {
            if ruta.starts_with(path_permitido) {
                return Ok(());
            }
        }

        Err(ElapError::Validacion(format!(
            "Ruta no permitida: {}",
            ruta
        )))
    }

    /// Validar comando no esté en lista negra
    pub fn validar_comando(
        comando: &str,
        comandos_bloqueados: &[String],
    ) -> ResultadoElap<()> {
        for bloqueado in comandos_bloqueados {
            if comando.contains(bloqueado) {
                return Err(ElapError::Validacion(format!(
                    "Comando bloqueado: {}",
                    bloqueado
                )));
            }
        }

        Ok(())
    }

    /// Validar tamaño de parámetros (proxy para límite memoria)
    pub fn validar_tamaño_parametros(
        parametros: &JsonValue,
        limite_mb: u32,
    ) -> ResultadoElap<()> {
        let json_str = parametros.to_string();
        let bytes = json_str.len();
        let mb = bytes / (1024 * 1024);

        if mb > limite_mb as usize {
            return Err(ElapError::Validacion(format!(
                "Parámetros exceden límite: {} MB > {} MB",
                mb, limite_mb
            )));
        }

        Ok(())
    }

    /// Validar política de ejecución
    pub fn validar_politica(
        politica: &PoliticaHerramienta,
        permisos_usuario: &[Permiso],
    ) -> ResultadoElap<()> {
        match politica {
            PoliticaHerramienta::Permitir => Ok(()),
            PoliticaHerramienta::Denegar => Err(ElapError::Validacion(
                "Herramienta denegada".to_string(),
            )),
            PoliticaHerramienta::RequerirPermiso(permiso) => {
                Self::validar_permiso(permisos_usuario, permiso)
            }
        }
    }
}

/// Contexto de ejecución con sandbox
pub struct ContextoEjecucion {
    pub usuario_id: String,
    pub permisos: Vec<Permiso>,
    pub sandbox: SandboxHerramienta,
}

impl ContextoEjecucion {
    /// Crear nuevo contexto
    pub fn nuevo(
        usuario_id: String,
        permisos: Vec<Permiso>,
        sandbox: SandboxHerramienta,
    ) -> Self {
        Self {
            usuario_id,
            permisos,
            sandbox,
        }
    }

    /// Validar ejecución en contexto
    pub fn validar_ejecucion(&self) -> ResultadoElap<()> {
        ValidadorSeguridad::validar_politica(&self.sandbox.politica, &self.permisos)?;
        Ok(())
    }

    /// Validar parámetros en contexto
    pub fn validar_parametros(&self, parametros: &JsonValue) -> ResultadoElap<()> {
        ValidadorSeguridad::validar_tamaño_parametros(
            parametros,
            self.sandbox.limite_memoria_mb,
        )?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sandbox_default() {
        let sandbox = SandboxHerramienta::default();
        assert_eq!(sandbox.timeout.as_secs(), 30);
        assert_eq!(sandbox.limite_memoria_mb, 512);
    }

    #[test]
    fn test_validar_ruta_permitida() {
        let paths = vec!["/data".to_string(), "/tmp".to_string()];
        assert!(ValidadorSeguridad::validar_ruta("/data/archivo.txt", &paths).is_ok());
        assert!(ValidadorSeguridad::validar_ruta("/tmp/test", &paths).is_ok());
    }

    #[test]
    fn test_validar_ruta_no_permitida() {
        let paths = vec!["/data".to_string()];
        let resultado = ValidadorSeguridad::validar_ruta("/etc/passwd", &paths);
        assert!(resultado.is_err());
    }

    #[test]
    fn test_validar_comando_bloqueado() {
        let bloqueados = vec!["rm -rf".to_string()];
        let resultado = ValidadorSeguridad::validar_comando("rm -rf /", &bloqueados);
        assert!(resultado.is_err());
    }

    #[test]
    fn test_validar_comando_permitido() {
        let bloqueados = vec!["rm -rf".to_string()];
        assert!(ValidadorSeguridad::validar_comando("ls -la", &bloqueados).is_ok());
    }

    #[test]
    fn test_politica_permitir() {
        let politica = PoliticaHerramienta::Permitir;
        let permisos = vec![];
        assert!(ValidadorSeguridad::validar_politica(&politica, &permisos).is_ok());
    }

    #[test]
    fn test_politica_denegar() {
        let politica = PoliticaHerramienta::Denegar;
        let permisos = vec![];
        let resultado = ValidadorSeguridad::validar_politica(&politica, &permisos);
        assert!(resultado.is_err());
    }

    #[test]
    fn test_contexto_nuevo() {
        let contexto = ContextoEjecucion::nuevo(
            "usuario_123".to_string(),
            vec![Permiso::EjecutarHerramientas],
            SandboxHerramienta::default(),
        );

        assert_eq!(contexto.usuario_id, "usuario_123");
        assert_eq!(contexto.permisos.len(), 1);
    }

    #[test]
    fn test_contexto_validar_ejecucion() {
        let sandbox = SandboxHerramienta {
            politica: PoliticaHerramienta::Permitir,
            ..Default::default()
        };

        let contexto = ContextoEjecucion::nuevo(
            "usuario_123".to_string(),
            vec![],
            sandbox,
        );

        assert!(contexto.validar_ejecucion().is_ok());
    }

    #[test]
    fn test_validar_tamaño_parametros() {
        let params = serde_json::json!({ "test": "data" });
        assert!(ValidadorSeguridad::validar_tamaño_parametros(&params, 512).is_ok());
    }
}
