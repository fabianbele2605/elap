use serde::{Deserialize, Serialize};
use std::path::Path;
use crate::config::error::{ErrorConfig, ResultadoConfig};

/// Configuración de base de datos.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfigBaseDatos {
    /// Tipo de base de datos (sqlite, postgresql).
    pub tipo: String,
    /// URL de conexión.
    pub url: String,
    /// Pool máximo de conexiones.
    pub pool_size: u32,
    /// Timeout de conexión en segundos.
    pub timeout: u64,
}

/// Configuración de seguridad.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfigSeguridad {
    /// Clave para cifrado AES-256 (en base64 o texto).
    pub clave_cifrado: String,
    /// Habilitar RBAC.
    pub rbac_habilitado: bool,
    /// Ruta del archivo de permisos.
    pub ruta_permisos: String,
    /// Habilitar auditoría.
    pub auditoria_habilitada: bool,
}

/// Configuración del motor de IA.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfigIA {
    /// Endpoint de Ollama (ej. http://localhost:11434).
    pub endpoint_ollama: String,
    /// Modelo por defecto.
    pub modelo_defecto: String,
    /// Timeout de inferencia en segundos.
    pub timeout_inferencia: u64,
    /// Tamaño máximo de contexto.
    pub tamaño_contexto: u32,
}

/// Configuración general de ELAP.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Configuracion {
    /// Nombre de la aplicación.
    pub nombre_app: String,
    /// Versión de la aplicación.
    pub version: String,
    /// Modo de ejecución (development, production).
    pub modo: String,
    /// Puerto del servidor.
    pub puerto: u16,
    /// Nivel de logging (trace, debug, info, warn, error).
    pub nivel_logging: String,
    /// Ruta del archivo de logs.
    pub ruta_logs: String,
    /// Configuración de base de datos.
    pub base_datos: ConfigBaseDatos,
    /// Configuración de seguridad.
    pub seguridad: ConfigSeguridad,
    /// Configuración de IA.
    pub ia: ConfigIA,
}

impl Configuracion {
    /// Crea configuración por defecto para desarrollo.
    pub fn defecto() -> Self {
        Configuracion {
            nombre_app: "ELAP".to_string(),
            version: "0.1.0".to_string(),
            modo: "development".to_string(),
            puerto: 8000,
            nivel_logging: "info".to_string(),
            ruta_logs: "logs/elap.log".to_string(),
            base_datos: ConfigBaseDatos {
                tipo: "sqlite".to_string(),
                url: "sqlite::memory:".to_string(),
                pool_size: 10,
                timeout: 30,
            },
            seguridad: ConfigSeguridad {
                clave_cifrado: "desarrollo-cambiar-en-produccion".to_string(),
                rbac_habilitado: true,
                ruta_permisos: "config/permisos.yaml".to_string(),
                auditoria_habilitada: true,
            },
            ia: ConfigIA {
                endpoint_ollama: "http://localhost:11434".to_string(),
                modelo_defecto: "llama2".to_string(),
                timeout_inferencia: 120,
                tamaño_contexto: 4096,
            },
        }
    }

    /// Carga configuración desde archivo YAML.
    pub fn cargar(ruta: &str) -> ResultadoConfig<Self> {
        let contenido = std::fs::read_to_string(ruta).map_err(|e| {
            ErrorConfig::NoSeLeyoArchivo(format!("{}: {}", ruta, e))
        })?;

        serde_yaml::from_str(&contenido).map_err(|e| {
            ErrorConfig::ErrorYaml(e.to_string())
        })
    }

    /// Guarda configuración a archivo YAML.
    pub fn guardar(&self, ruta: &str) -> ResultadoConfig<()> {
        let contenido = serde_yaml::to_string(self).map_err(|e| {
            ErrorConfig::ErrorYaml(e.to_string())
        })?;

        std::fs::write(ruta, contenido).map_err(|e| {
            ErrorConfig::NoSeEscribioArchivo(format!("{}: {}", ruta, e))
        })?;

        Ok(())
    }

    /// Valida que la configuración sea válida según las reglas de negocio.
    pub fn validar(&self) -> ResultadoConfig<()> {
        if self.puerto == 0 {
            return Err(ErrorConfig::ValorInvalido(
                "Puerto debe ser mayor a 0".to_string(),
            ));
        }

        if self.base_datos.pool_size == 0 {
            return Err(ErrorConfig::CampoFaltante(
                "pool_size debe ser mayor a 0".to_string(),
            ));
        }

        if self.base_datos.url.is_empty() {
            return Err(ErrorConfig::CampoFaltante("url de base de datos".to_string()));
        }

        if self.seguridad.clave_cifrado == "desarrollo-cambiar-en-produccion"
            && self.modo == "production"
        {
            return Err(ErrorConfig::ValorInvalido(
                "En producción, la clave_cifrado debe cambiar".to_string(),
            ));
        }

        if self.ia.timeout_inferencia == 0 {
            return Err(ErrorConfig::ValorInvalido(
                "timeout_inferencia debe ser mayor a 0".to_string(),
            ));
        }

        Ok(())
    }

    /// Retorna true si está en modo producción.
    pub fn es_produccion(&self) -> bool {
        self.modo == "production"
    }

    /// Retorna true si está en modo desarrollo.
    pub fn es_desarrollo(&self) -> bool {
        self.modo == "development"
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_configuracion_defecto() {
        let config = Configuracion::defecto();
        assert_eq!(config.nombre_app, "ELAP");
        assert_eq!(config.puerto, 8000);
        assert!(config.es_desarrollo());
    }

    #[test]
    fn test_validar_puerto_cero() {
        let mut config = Configuracion::defecto();
        config.puerto = 0;
        assert!(config.validar().is_err());
    }

    #[test]
    fn test_validar_pool_size_cero() {
        let mut config = Configuracion::defecto();
        config.base_datos.pool_size = 0;
        assert!(config.validar().is_err());
    }

    #[test]
    fn test_validar_url_vacia() {
        let mut config = Configuracion::defecto();
        config.base_datos.url = String::new();
        assert!(config.validar().is_err());
    }

    #[test]
    fn test_validar_clave_produccion() {
        let mut config = Configuracion::defecto();
        config.modo = "production".to_string();
        assert!(config.validar().is_err());
    }

    #[test]
    fn test_validar_correcto() {
        let mut config = Configuracion::defecto();
        config.modo = "production".to_string();
        config.seguridad.clave_cifrado = "clave-muy-secreta-en-produccion".to_string();
        assert!(config.validar().is_ok());
    }

    #[test]
    fn test_es_produccion() {
        let mut config = Configuracion::defecto();
        assert!(!config.es_produccion());
        config.modo = "production".to_string();
        assert!(config.es_produccion());
    }

    #[test]
    fn test_es_desarrollo() {
        let config = Configuracion::defecto();
        assert!(config.es_desarrollo());
    }

    #[test]
    fn test_guardar_y_cargar() {
        let config = Configuracion::defecto();
        let ruta_temp = "/tmp/test_elap_config.yaml";

        assert!(config.guardar(ruta_temp).is_ok());
        assert!(Path::new(ruta_temp).exists());

        let config_cargada = Configuracion::cargar(ruta_temp);
        assert!(config_cargada.is_ok());

        let config_cargada = config_cargada.unwrap();
        assert_eq!(config_cargada.nombre_app, "ELAP");
        assert_eq!(config_cargada.puerto, 8000);

        let _ = std::fs::remove_file(ruta_temp);
    }

    #[test]
    fn test_cargar_archivo_inexistente() {
        let resultado = Configuracion::cargar("/ruta/inexistente/config.yaml");
        assert!(resultado.is_err());
    }

    #[test]
    fn test_yaml_invalido() {
        let ruta_temp = "/tmp/test_yaml_invalido_elap.yaml";
        std::fs::write(ruta_temp, "esto: no [es valido yaml").ok();

        let resultado = Configuracion::cargar(ruta_temp);
        assert!(resultado.is_err());

        let _ = std::fs::remove_file(ruta_temp);
    }
}
