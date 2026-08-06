//! Estructura avanzada de configuración

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Configuración avanzada con múltiples opciones
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfiguracionAvanzada {
    /// Versión de la configuración
    pub version: String,

    /// Entorno (desarrollo, producción, testing)
    pub entorno: String,

    /// Opciones genéricas
    pub opciones: HashMap<String, ConfigOption>,

    /// Configuración de logging
    pub logging: ConfigLogging,

    /// Configuración de base de datos
    pub base_datos: ConfigBaseDatos,

    /// Configuración de seguridad
    pub seguridad: ConfigSeguridad,

    /// Configuración de plugins
    pub plugins: ConfigPlugins,
}

/// Opción de configuración genérica
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(untagged)]
pub enum ConfigOption {
    /// Valor booleano
    Booleano(bool),

    /// Valor numérico entero
    Entero(i64),

    /// Valor numérico decimal
    Decimal(f64),

    /// Valor texto
    Texto(String),

    /// Arreglo de valores
    Arreglo(Vec<ConfigOption>),

    /// Objeto anidado
    Objeto(HashMap<String, ConfigOption>),
}

impl ConfigOption {
    /// Obtener como booleano
    pub fn como_bool(&self) -> Option<bool> {
        match self {
            ConfigOption::Booleano(b) => Some(*b),
            _ => None,
        }
    }

    /// Obtener como entero
    pub fn como_entero(&self) -> Option<i64> {
        match self {
            ConfigOption::Entero(n) => Some(*n),
            _ => None,
        }
    }

    /// Obtener como texto
    pub fn como_texto(&self) -> Option<&str> {
        match self {
            ConfigOption::Texto(s) => Some(s),
            _ => None,
        }
    }
}

/// Configuración de logging
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfigLogging {
    /// Nivel de log (debug, info, warn, error)
    pub nivel: String,

    /// Formato de salida
    pub formato: String,

    /// Guardar a archivo
    pub guardar_archivo: bool,

    /// Ruta del archivo de log
    pub ruta_archivo: Option<String>,

    /// Máximo tamaño en MB
    pub tamaño_maximo_mb: u32,
}

impl Default for ConfigLogging {
    fn default() -> Self {
        Self {
            nivel: "info".to_string(),
            formato: "json".to_string(),
            guardar_archivo: true,
            ruta_archivo: Some("./logs/elap.log".to_string()),
            tamaño_maximo_mb: 100,
        }
    }
}

/// Configuración de base de datos
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfigBaseDatos {
    /// Tipo (sqlite, postgresql, mysql)
    pub tipo: String,

    /// URL de conexión
    pub url: Option<String>,

    /// Archivo SQLite
    pub archivo: Option<String>,

    /// Pool de conexiones (máximo)
    pub pool_maximo: u32,

    /// Timeout en segundos
    pub timeout_segundos: u64,
}

impl Default for ConfigBaseDatos {
    fn default() -> Self {
        Self {
            tipo: "sqlite".to_string(),
            url: None,
            archivo: Some("./data/elap.db".to_string()),
            pool_maximo: 10,
            timeout_segundos: 30,
        }
    }
}

/// Configuración de seguridad
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfigSeguridad {
    /// Requiere autenticación
    pub requiere_autenticacion: bool,

    /// RBAC habilitado
    pub rbac_habilitado: bool,

    /// Auditoría habilitada
    pub auditoria_habilitada: bool,

    /// Cifrado de datos sensibles
    pub cifrado_habilitado: bool,

    /// Algoritmo de cifrado
    pub algoritmo_cifrado: String,
}

impl Default for ConfigSeguridad {
    fn default() -> Self {
        Self {
            requiere_autenticacion: true,
            rbac_habilitado: true,
            auditoria_habilitada: true,
            cifrado_habilitado: true,
            algoritmo_cifrado: "AES-256-GCM".to_string(),
        }
    }
}

/// Configuración de plugins
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfigPlugins {
    /// Plugins habilitados
    pub habilitados: bool,

    /// Directorio de plugins
    pub directorio: String,

    /// Cargar automáticamente al inicio
    pub cargar_automaticamente: bool,

    /// Máximo número de plugins
    pub maximo_plugins: u32,
}

impl Default for ConfigPlugins {
    fn default() -> Self {
        Self {
            habilitados: true,
            directorio: "./plugins".to_string(),
            cargar_automaticamente: true,
            maximo_plugins: 50,
        }
    }
}

impl Default for ConfiguracionAvanzada {
    fn default() -> Self {
        Self {
            version: "1.0.0".to_string(),
            entorno: "desarrollo".to_string(),
            opciones: HashMap::new(),
            logging: ConfigLogging::default(),
            base_datos: ConfigBaseDatos::default(),
            seguridad: ConfigSeguridad::default(),
            plugins: ConfigPlugins::default(),
        }
    }
}

impl ConfiguracionAvanzada {
    /// Crear configuración por defecto
    pub fn defecto() -> Self {
        Self::default()
    }

    /// Crear configuración para producción
    pub fn produccion() -> Self {
        let mut config = Self::default();
        config.entorno = "produccion".to_string();
        config.logging.nivel = "warn".to_string();
        config.seguridad.cifrado_habilitado = true;
        config
    }

    /// Crear configuración para testing
    pub fn testing() -> Self {
        let mut config = Self::default();
        config.entorno = "testing".to_string();
        config.logging.nivel = "debug".to_string();
        config.logging.guardar_archivo = false;
        config.base_datos.archivo = Some(":memory:".to_string());
        config
    }

    /// Agregar opción personalizada
    pub fn agregar_opcion(&mut self, clave: String, valor: ConfigOption) {
        self.opciones.insert(clave, valor);
    }

    /// Obtener opción personalizada
    pub fn obtener_opcion(&self, clave: &str) -> Option<&ConfigOption> {
        self.opciones.get(clave)
    }

    /// Validar que la configuración es consistente
    pub fn validar(&self) -> Result<(), String> {
        if self.version.is_empty() {
            return Err("Versión no puede estar vacía".to_string());
        }

        if self.entorno.is_empty() {
            return Err("Entorno no puede estar vacío".to_string());
        }

        if self.logging.nivel.is_empty() {
            return Err("Nivel de logging no puede estar vacío".to_string());
        }

        if self.base_datos.pool_maximo == 0 {
            return Err("Pool máximo debe ser > 0".to_string());
        }

        if self.plugins.maximo_plugins == 0 {
            return Err("Máximo de plugins debe ser > 0".to_string());
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_defecto() {
        let config = ConfiguracionAvanzada::defecto();
        assert_eq!(config.version, "1.0.0");
        assert_eq!(config.entorno, "desarrollo");
    }

    #[test]
    fn test_crear_produccion() {
        let config = ConfiguracionAvanzada::produccion();
        assert_eq!(config.entorno, "produccion");
        assert_eq!(config.logging.nivel, "warn");
    }

    #[test]
    fn test_crear_testing() {
        let config = ConfiguracionAvanzada::testing();
        assert_eq!(config.entorno, "testing");
        assert_eq!(config.logging.guardar_archivo, false);
    }

    #[test]
    fn test_agregar_opcion() {
        let mut config = ConfiguracionAvanzada::defecto();
        config.agregar_opcion("puerto".to_string(), ConfigOption::Entero(8080));

        let puerto = config.obtener_opcion("puerto");
        assert!(puerto.is_some());
        assert_eq!(puerto.unwrap().como_entero().unwrap(), 8080);
    }

    #[test]
    fn test_config_option_conversiones() {
        let bool_opt = ConfigOption::Booleano(true);
        assert_eq!(bool_opt.como_bool(), Some(true));

        let int_opt = ConfigOption::Entero(42);
        assert_eq!(int_opt.como_entero(), Some(42));

        let text_opt = ConfigOption::Texto("hola".to_string());
        assert_eq!(text_opt.como_texto(), Some("hola"));
    }

    #[test]
    fn test_validar_configuracion_valida() {
        let config = ConfiguracionAvanzada::defecto();
        assert!(config.validar().is_ok());
    }

    #[test]
    fn test_validar_version_vacia() {
        let mut config = ConfiguracionAvanzada::defecto();
        config.version = "".to_string();
        assert!(config.validar().is_err());
    }

    #[test]
    fn test_validar_pool_zero() {
        let mut config = ConfiguracionAvanzada::defecto();
        config.base_datos.pool_maximo = 0;
        assert!(config.validar().is_err());
    }

    #[test]
    fn test_config_logging_default() {
        let log = ConfigLogging::default();
        assert_eq!(log.nivel, "info");
        assert!(log.guardar_archivo);
    }

    #[test]
    fn test_config_seguridad_default() {
        let seg = ConfigSeguridad::default();
        assert!(seg.rbac_habilitado);
        assert!(seg.auditoria_habilitada);
    }

    #[test]
    fn test_config_plugins_default() {
        let plugins = ConfigPlugins::default();
        assert!(plugins.habilitados);
        assert_eq!(plugins.maximo_plugins, 50);
    }

    #[test]
    fn test_config_base_datos_default() {
        let bd = ConfigBaseDatos::default();
        assert_eq!(bd.tipo, "sqlite");
        assert_eq!(bd.pool_maximo, 10);
    }

    #[test]
    fn test_serializar_deserializar() {
        let config_original = ConfiguracionAvanzada::testing();
        let json = serde_json::to_string(&config_original).unwrap();
        let config_restaurado: ConfiguracionAvanzada = serde_json::from_str(&json).unwrap();
        assert_eq!(config_original.entorno, config_restaurado.entorno);
    }

    #[test]
    fn test_obtener_opcion_inexistente() {
        let config = ConfiguracionAvanzada::defecto();
        assert!(config.obtener_opcion("no_existe").is_none());
    }

    #[test]
    fn test_validar_compatibilidad_entornos() {
        let configs = vec![
            ConfiguracionAvanzada::defecto(),
            ConfiguracionAvanzada::produccion(),
            ConfiguracionAvanzada::testing(),
        ];

        for config in configs {
            assert!(config.validar().is_ok());
        }
    }
}
