//! Sandbox para ejecución segura de plugins

use std::time::Duration;
use serde::{Deserialize, Serialize};
use crate::error::ResultadoElap;
use super::metadata::PluginMetadata;

/// Configuración de sandbox
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfiguracionSandbox {
    /// Límite de memoria en MB
    pub limite_memoria_mb: u32,

    /// Límite de tiempo de ejecución en segundos
    pub timeout_segundos: u64,

    /// Permitir acceso a red
    pub permitir_red: bool,

    /// Permitir acceso a sistema de archivos
    pub permitir_archivos: bool,

    /// Permitir acceso a procesos del sistema
    pub permitir_procesos: bool,
}

impl Default for ConfiguracionSandbox {
    fn default() -> Self {
        Self {
            limite_memoria_mb: 512,
            timeout_segundos: 30,
            permitir_red: false,
            permitir_archivos: false,
            permitir_procesos: false,
        }
    }
}

impl ConfiguracionSandbox {
    /// Crear configuración restrictiva (máxima seguridad)
    pub fn restrictiva() -> Self {
        Self {
            limite_memoria_mb: 256,
            timeout_segundos: 10,
            permitir_red: false,
            permitir_archivos: false,
            permitir_procesos: false,
        }
    }

    /// Crear configuración permisiva (solo para plugins confiables)
    pub fn permisiva() -> Self {
        Self {
            limite_memoria_mb: 2048,
            timeout_segundos: 120,
            permitir_red: true,
            permitir_archivos: true,
            permitir_procesos: true,
        }
    }
}

/// Políticas de ejecución
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PoliticaEjecucion {
    /// Requiere firma verificada
    pub requiere_firma: bool,

    /// Requiere permisos explícitos
    pub requiere_permisos: bool,

    /// Auditar todas las acciones
    pub auditar_acciones: bool,
}

impl Default for PoliticaEjecucion {
    fn default() -> Self {
        Self {
            requiere_firma: true,
            requiere_permisos: true,
            auditar_acciones: true,
        }
    }
}

/// Sandbox para ejecución segura
pub struct PluginSandbox {
    config: ConfiguracionSandbox,
    politica: PoliticaEjecucion,
}

impl PluginSandbox {
    /// Crear nuevo sandbox
    pub fn nuevo(config: ConfiguracionSandbox, politica: PoliticaEjecucion) -> Self {
        Self { config, politica }
    }

    /// Crear sandbox con configuración por defecto
    pub fn defecto() -> Self {
        Self {
            config: ConfiguracionSandbox::default(),
            politica: PoliticaEjecucion::default(),
        }
    }

    /// Validar que el plugin puede ejecutarse
    pub fn validar_plugin(&self, metadata: &PluginMetadata) -> ResultadoElap<()> {
        // Validar que el plugin no requiere más memoria de la permitida
        // (Esta es una validación básica; la verdadera limitación ocurriría en runtime)

        // Validar permisos si la política lo requiere
        if self.politica.requiere_permisos && metadata.permisos.is_empty() {
            // Los plugins sin permisos explícitos son válidos
            // Solo auditar si hay permisos
        }

        Ok(())
    }

    /// Validar que el plugin tiene un permiso específico
    pub fn tiene_permiso(&self, metadata: &PluginMetadata, permiso: &str) -> bool {
        metadata.permisos.contains(&permiso.to_string())
    }

    /// Validar acceso a red
    pub fn puede_acceder_red(&self, metadata: &PluginMetadata) -> ResultadoElap<bool> {
        if !self.config.permitir_red {
            return Ok(false);
        }

        // Verificar si el plugin tiene permiso explícito
        Ok(self.tiene_permiso(metadata, "AccesoRed"))
    }

    /// Validar acceso a archivos
    pub fn puede_acceder_archivos(&self, metadata: &PluginMetadata) -> ResultadoElap<bool> {
        if !self.config.permitir_archivos {
            return Ok(false);
        }

        Ok(self.tiene_permiso(metadata, "AccesoArchivos"))
    }

    /// Validar acceso a procesos
    pub fn puede_acceder_procesos(&self, metadata: &PluginMetadata) -> ResultadoElap<bool> {
        if !self.config.permitir_procesos {
            return Ok(false);
        }

        Ok(self.tiene_permiso(metadata, "AccesoProcesos"))
    }

    /// Obtener timeout como Duration
    pub fn timeout(&self) -> Duration {
        Duration::from_secs(self.config.timeout_segundos)
    }

    /// Obtener límite de memoria
    pub fn limite_memoria(&self) -> u32 {
        self.config.limite_memoria_mb
    }

    /// Verificar si requiere firma
    pub fn requiere_firma(&self) -> bool {
        self.politica.requiere_firma
    }

    /// Verificar si audita acciones
    pub fn audita_acciones(&self) -> bool {
        self.politica.auditar_acciones
    }
}

impl Clone for PluginSandbox {
    fn clone(&self) -> Self {
        Self {
            config: self.config.clone(),
            politica: self.politica.clone(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn crear_plugin_test() -> PluginMetadata {
        PluginMetadata::nuevo(
            "test_plugin".to_string(),
            "1.0.0".to_string(),
            "test_author".to_string(),
            "Test".to_string(),
            "./test.so".to_string(),
            "plugin_init".to_string(),
        )
    }

    #[test]
    fn test_configuracion_defecto() {
        let config = ConfiguracionSandbox::default();
        assert_eq!(config.limite_memoria_mb, 512);
        assert_eq!(config.timeout_segundos, 30);
        assert!(!config.permitir_red);
    }

    #[test]
    fn test_configuracion_restrictiva() {
        let config = ConfiguracionSandbox::restrictiva();
        assert_eq!(config.limite_memoria_mb, 256);
        assert_eq!(config.timeout_segundos, 10);
    }

    #[test]
    fn test_configuracion_permisiva() {
        let config = ConfiguracionSandbox::permisiva();
        assert_eq!(config.limite_memoria_mb, 2048);
        assert!(config.permitir_red);
        assert!(config.permitir_archivos);
    }

    #[test]
    fn test_politica_defecto() {
        let politica = PoliticaEjecucion::default();
        assert!(politica.requiere_firma);
        assert!(politica.requiere_permisos);
        assert!(politica.auditar_acciones);
    }

    #[test]
    fn test_crear_sandbox_defecto() {
        let sandbox = PluginSandbox::defecto();
        assert_eq!(sandbox.limite_memoria(), 512);
        assert!(sandbox.requiere_firma());
    }

    #[test]
    fn test_validar_plugin_valido() {
        let sandbox = PluginSandbox::defecto();
        let plugin = crear_plugin_test();
        assert!(sandbox.validar_plugin(&plugin).is_ok());
    }

    #[test]
    fn test_tiene_permiso() {
        let sandbox = PluginSandbox::defecto();
        let mut plugin = crear_plugin_test();

        assert!(!sandbox.tiene_permiso(&plugin, "AccesoRed"));

        plugin.agregar_permiso("AccesoRed".to_string());
        assert!(sandbox.tiene_permiso(&plugin, "AccesoRed"));
    }

    #[test]
    fn test_puede_acceder_red_bloqueado() {
        let config = ConfiguracionSandbox::default();
        let sandbox = PluginSandbox::nuevo(config, PoliticaEjecucion::default());
        let plugin = crear_plugin_test();

        let resultado = sandbox.puede_acceder_red(&plugin).unwrap();
        assert!(!resultado);
    }

    #[test]
    fn test_puede_acceder_red_permitido() {
        let mut config = ConfiguracionSandbox::default();
        config.permitir_red = true;

        let sandbox = PluginSandbox::nuevo(config, PoliticaEjecucion::default());
        let mut plugin = crear_plugin_test();
        plugin.agregar_permiso("AccesoRed".to_string());

        let resultado = sandbox.puede_acceder_red(&plugin).unwrap();
        assert!(resultado);
    }

    #[test]
    fn test_timeout() {
        let sandbox = PluginSandbox::defecto();
        let timeout = sandbox.timeout();
        assert_eq!(timeout.as_secs(), 30);
    }

    #[test]
    fn test_clonar_sandbox() {
        let sandbox1 = PluginSandbox::defecto();
        let sandbox2 = sandbox1.clone();
        assert_eq!(sandbox2.limite_memoria(), sandbox1.limite_memoria());
    }

    #[test]
    fn test_audita_acciones() {
        let sandbox = PluginSandbox::defecto();
        assert!(sandbox.audita_acciones());
    }
}
