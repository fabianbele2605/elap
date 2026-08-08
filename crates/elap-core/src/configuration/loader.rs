//! Cargador de configuración desde archivos

use std::path::PathBuf;
use std::fs;
use crate::error::ResultadoElap;
use super::config_struct::ConfiguracionAvanzada;

/// Cargador de configuración
pub struct CargadorConfiguracion {
    ruta_base: PathBuf,
}

impl CargadorConfiguracion {
    /// Crear nuevo cargador
    pub fn nuevo(ruta_base: PathBuf) -> Self {
        Self { ruta_base }
    }

    /// Cargar configuración desde archivo TOML
    pub fn cargar_toml(&self, archivo: &str) -> ResultadoElap<ConfiguracionAvanzada> {
        let ruta = self.ruta_base.join(archivo);

        if !ruta.exists() {
            return Err(crate::error::ElapError::ConfigError(
                format!("Archivo de configuración no encontrado: {:?}", ruta)
            ));
        }

        let contenido = fs::read_to_string(&ruta)
            ?;

        let config: ConfiguracionAvanzada = toml::from_str(&contenido)
            .map_err(|e| crate::error::ElapError::ConfigError(
                format!("Error parsando TOML: {}", e)
            ))?;

        config.validar()
            .map_err(|e| crate::error::ElapError::ValidationError(e))?;

        Ok(config)
    }

    /// Cargar configuración desde archivo YAML
    pub fn cargar_yaml(&self, archivo: &str) -> ResultadoElap<ConfiguracionAvanzada> {
        let ruta = self.ruta_base.join(archivo);

        if !ruta.exists() {
            return Err(crate::error::ElapError::ConfigError(
                format!("Archivo de configuración no encontrado: {:?}", ruta)
            ));
        }

        let contenido = fs::read_to_string(&ruta)
            ?;

        let config: ConfiguracionAvanzada = serde_yaml::from_str(&contenido)
            .map_err(|e| crate::error::ElapError::ConfigError(
                format!("Error parsando YAML: {}", e)
            ))?;

        config.validar()
            .map_err(|e| crate::error::ElapError::ValidationError(e))?;

        Ok(config)
    }

    /// Cargar configuración desde archivo JSON
    pub fn cargar_json(&self, archivo: &str) -> ResultadoElap<ConfiguracionAvanzada> {
        let ruta = self.ruta_base.join(archivo);

        if !ruta.exists() {
            return Err(crate::error::ElapError::ConfigError(
                format!("Archivo de configuración no encontrado: {:?}", ruta)
            ));
        }

        let contenido = fs::read_to_string(&ruta)
            ?;

        let config: ConfiguracionAvanzada = serde_json::from_str(&contenido)
            .map_err(|e| crate::error::ElapError::ConfigError(
                format!("Error parsando JSON: {}", e)
            ))?;

        config.validar()
            .map_err(|e| crate::error::ElapError::ValidationError(e))?;

        Ok(config)
    }

    /// Cargar con fallback a defecto
    pub fn cargar_o_defecto(&self, archivo: &str) -> ConfiguracionAvanzada {
        match self.cargar_toml(archivo) {
            Ok(config) => config,
            Err(_) => ConfiguracionAvanzada::defecto(),
        }
    }

    /// Guardar configuración a archivo TOML
    pub fn guardar_toml(&self, archivo: &str, config: &ConfiguracionAvanzada) -> ResultadoElap<()> {
        let ruta = self.ruta_base.join(archivo);

        let contenido = toml::to_string_pretty(config)
            .map_err(|e| crate::error::ElapError::ConfigError(
                format!("Error serializando TOML: {}", e)
            ))?;

        fs::write(&ruta, contenido)
            ?;

        Ok(())
    }

    /// Directorio base
    pub fn ruta_base(&self) -> &PathBuf {
        &self.ruta_base
    }

    /// Descubrir archivos de configuración en el directorio
    pub fn descubrir(&self) -> ResultadoElap<Vec<PathBuf>> {
        if !self.ruta_base.exists() {
            return Ok(Vec::new());
        }

        let mut archivos = Vec::new();

        match fs::read_dir(&self.ruta_base) {
            Ok(entries) => {
                for entry in entries.flatten() {
                    let path = entry.path();
                    if let Some(ext) = path.extension() {
                        let ext_str = ext.to_string_lossy();
                        if ext_str == "toml" || ext_str == "yaml" || ext_str == "yml" || ext_str == "json" {
                            archivos.push(path);
                        }
                    }
                }
            }
            Err(_) => return Ok(Vec::new()),
        }

        Ok(archivos)
    }

    /// Cargar configuración base y aplicar override
    pub fn cargar_con_override(
        &self,
        archivo_base: &str,
        archivo_override: Option<&str>,
    ) -> ResultadoElap<ConfiguracionAvanzada> {
        let mut config = self.cargar_toml(archivo_base)?;

        if let Some(override_file) = archivo_override {
            let override_config = self.cargar_o_defecto(override_file);
            config.entorno = override_config.entorno;
            config.logging = override_config.logging;
            config.base_datos = override_config.base_datos;
            config.seguridad = override_config.seguridad;
            config.plugins = override_config.plugins;
        }

        Ok(config)
    }

    /// Cargar configuración desde variable de entorno
    pub fn desde_entorno(entorno: &str) -> ResultadoElap<ConfiguracionAvanzada> {
        match entorno {
            "produccion" => Ok(ConfiguracionAvanzada::produccion()),
            "testing" => Ok(ConfiguracionAvanzada::testing()),
            _ => Ok(ConfiguracionAvanzada::defecto()),
        }
    }

    /// Crear directorio de configuración si no existe
    pub fn crear_directorio(&self) -> ResultadoElap<()> {
        if !self.ruta_base.exists() {
            fs::create_dir_all(&self.ruta_base)
                ?;
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    fn crear_archivo_toml(dir: &TempDir, nombre: &str) -> PathBuf {
        let ruta = dir.path().join(nombre);
        let contenido = r#"
version = "1.0.0"
entorno = "testing"

[logging]
nivel = "debug"
formato = "json"
guardar_archivo = false
ruta_archivo = "./logs/elap.log"
tamaño_maximo_mb = 100

[base_datos]
tipo = "sqlite"
archivo = ":memory:"
pool_maximo = 10
timeout_segundos = 30

[seguridad]
requiere_autenticacion = true
rbac_habilitado = true
auditoria_habilitada = true
cifrado_habilitado = true
algoritmo_cifrado = "AES-256-GCM"

[plugins]
habilitados = true
directorio = "./plugins"
cargar_automaticamente = true
maximo_plugins = 50
"#;
        fs::write(&ruta, contenido).unwrap();
        ruta
    }

    #[test]
    fn test_crear_cargador() {
        let temp = TempDir::new().unwrap();
        let cargador = CargadorConfiguracion::nuevo(temp.path().to_path_buf());
        assert_eq!(cargador.ruta_base(), &temp.path().to_path_buf());
    }

    #[test]
    fn test_cargar_toml_valido() {
        let temp = TempDir::new().unwrap();
        let cargador = CargadorConfiguracion::nuevo(temp.path().to_path_buf());

        // Crear config válida y guardarla
        let config_original = ConfiguracionAvanzada::testing();
        assert!(cargador.guardar_toml("config.toml", &config_original).is_ok());

        // Cargarla nuevamente
        let resultado = cargador.cargar_toml("config.toml");
        assert!(resultado.is_ok());

        let config = resultado.unwrap();
        assert_eq!(config.version, config_original.version);
    }

    #[test]
    fn test_cargar_toml_inexistente() {
        let temp = TempDir::new().unwrap();
        let cargador = CargadorConfiguracion::nuevo(temp.path().to_path_buf());

        let resultado = cargador.cargar_toml("no_existe.toml");
        assert!(resultado.is_err());
    }

    #[test]
    fn test_cargar_o_defecto_existe() {
        let temp = TempDir::new().unwrap();
        let cargador = CargadorConfiguracion::nuevo(temp.path().to_path_buf());

        let config_original = ConfiguracionAvanzada::testing();
        assert!(cargador.guardar_toml("config.toml", &config_original).is_ok());

        let config = cargador.cargar_o_defecto("config.toml");
        assert_eq!(config.entorno, "testing");
    }

    #[test]
    fn test_cargar_o_defecto_no_existe() {
        let temp = TempDir::new().unwrap();
        let cargador = CargadorConfiguracion::nuevo(temp.path().to_path_buf());

        let config = cargador.cargar_o_defecto("no_existe.toml");
        assert_eq!(config.entorno, "desarrollo");
    }

    #[test]
    fn test_guardar_toml() {
        let temp = TempDir::new().unwrap();
        let cargador = CargadorConfiguracion::nuevo(temp.path().to_path_buf());
        let config = ConfiguracionAvanzada::testing();

        assert!(cargador.guardar_toml("saved.toml", &config).is_ok());

        let ruta = temp.path().join("saved.toml");
        assert!(ruta.exists());
    }

    #[test]
    fn test_round_trip_toml() {
        let temp = TempDir::new().unwrap();
        let cargador = CargadorConfiguracion::nuevo(temp.path().to_path_buf());
        let config_original = ConfiguracionAvanzada::testing();

        assert!(cargador.guardar_toml("test.toml", &config_original).is_ok());
        let config_cargado = cargador.cargar_toml("test.toml").unwrap();

        assert_eq!(config_original.entorno, config_cargado.entorno);
        assert_eq!(config_original.version, config_cargado.version);
    }

    #[test]
    fn test_descubrir_archivos() {
        let temp = TempDir::new().unwrap();
        let cargador = CargadorConfiguracion::nuevo(temp.path().to_path_buf());

        let config = ConfiguracionAvanzada::testing();
        assert!(cargador.guardar_toml("config1.toml", &config).is_ok());
        assert!(cargador.guardar_toml("config2.toml", &config).is_ok());

        let archivos = cargador.descubrir().unwrap();
        assert_eq!(archivos.len(), 2);
    }

    #[test]
    fn test_descubrir_directorio_inexistente() {
        let cargador = CargadorConfiguracion::nuevo(PathBuf::from("./no_existe"));
        let archivos = cargador.descubrir().unwrap();
        assert!(archivos.is_empty());
    }

    #[test]
    fn test_cargar_con_override() {
        let temp = TempDir::new().unwrap();
        let cargador = CargadorConfiguracion::nuevo(temp.path().to_path_buf());

        let base = ConfiguracionAvanzada::defecto();
        let override_config = ConfiguracionAvanzada::testing();

        assert!(cargador.guardar_toml("base.toml", &base).is_ok());
        assert!(cargador.guardar_toml("override.toml", &override_config).is_ok());

        let config = cargador.cargar_con_override("base.toml", Some("override.toml")).unwrap();
        assert_eq!(config.entorno, "testing");
    }

    #[test]
    fn test_desde_entorno() {
        let config_prod = CargadorConfiguracion::desde_entorno("produccion").unwrap();
        assert_eq!(config_prod.entorno, "produccion");

        let config_test = CargadorConfiguracion::desde_entorno("testing").unwrap();
        assert_eq!(config_test.entorno, "testing");

        let config_dev = CargadorConfiguracion::desde_entorno("desconocido").unwrap();
        assert_eq!(config_dev.entorno, "desarrollo");
    }

    #[test]
    fn test_crear_directorio() {
        let temp = TempDir::new().unwrap();
        let ruta_nueva = temp.path().join("config");
        let cargador = CargadorConfiguracion::nuevo(ruta_nueva.clone());

        assert!(!ruta_nueva.exists());
        assert!(cargador.crear_directorio().is_ok());
        assert!(ruta_nueva.exists());
    }
}
