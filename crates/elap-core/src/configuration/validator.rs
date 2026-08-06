//! Validador de configuración

use super::config_struct::ConfiguracionAvanzada;

/// Validador de configuración
pub struct ValidadorConfiguracion;

/// Resultado de validación
#[derive(Debug, Clone)]
pub struct ResultadoValidacion {
    pub valido: bool,
    pub errores: Vec<String>,
    pub advertencias: Vec<String>,
}

impl ResultadoValidacion {
    /// Crear resultado válido
    pub fn valido() -> Self {
        Self {
            valido: true,
            errores: Vec::new(),
            advertencias: Vec::new(),
        }
    }

    /// Crear resultado inválido
    pub fn invalido(error: String) -> Self {
        Self {
            valido: false,
            errores: vec![error],
            advertencias: Vec::new(),
        }
    }

    /// Agregar error
    pub fn agregar_error(&mut self, error: String) {
        self.errores.push(error);
        self.valido = false;
    }

    /// Agregar advertencia
    pub fn agregar_advertencia(&mut self, advertencia: String) {
        self.advertencias.push(advertencia);
    }
}

impl ValidadorConfiguracion {
    /// Validar configuración completa
    pub fn validar(config: &ConfiguracionAvanzada) -> ResultadoValidacion {
        let mut resultado = ResultadoValidacion::valido();

        Self::validar_basico(config, &mut resultado);
        Self::validar_logging(config, &mut resultado);
        Self::validar_base_datos(config, &mut resultado);
        Self::validar_seguridad(config, &mut resultado);
        Self::validar_plugins(config, &mut resultado);

        resultado
    }

    fn validar_basico(config: &ConfiguracionAvanzada, resultado: &mut ResultadoValidacion) {
        if config.version.is_empty() {
            resultado.agregar_error("Versión no puede estar vacía".to_string());
        }

        if config.entorno.is_empty() {
            resultado.agregar_error("Entorno no puede estar vacío".to_string());
        }

        let entornos_validos = vec!["desarrollo", "testing", "produccion"];
        if !entornos_validos.contains(&config.entorno.as_str()) {
            resultado.agregar_advertencia(
                format!("Entorno '{}' no es estándar", config.entorno)
            );
        }
    }

    fn validar_logging(config: &ConfiguracionAvanzada, resultado: &mut ResultadoValidacion) {
        let niveles_validos = vec!["debug", "info", "warn", "error"];
        if !niveles_validos.contains(&config.logging.nivel.as_str()) {
            resultado.agregar_error(
                format!("Nivel de logging '{}' no válido", config.logging.nivel)
            );
        }

        if config.logging.guardar_archivo && config.logging.ruta_archivo.is_none() {
            resultado.agregar_advertencia(
                "Guardar archivo habilitado pero ruta no especificada".to_string()
            );
        }

        if config.logging.tamaño_maximo_mb == 0 {
            resultado.agregar_error("Tamaño máximo debe ser > 0".to_string());
        }
    }

    fn validar_base_datos(config: &ConfiguracionAvanzada, resultado: &mut ResultadoValidacion) {
        let tipos_validos = vec!["sqlite", "postgresql", "mysql"];
        if !tipos_validos.contains(&config.base_datos.tipo.as_str()) {
            resultado.agregar_error(
                format!("Tipo de BD '{}' no válido", config.base_datos.tipo)
            );
        }

        if config.base_datos.pool_maximo == 0 {
            resultado.agregar_error("Pool máximo debe ser > 0".to_string());
        }

        if config.base_datos.timeout_segundos == 0 {
            resultado.agregar_error("Timeout debe ser > 0".to_string());
        }

        if config.base_datos.tipo == "sqlite" && config.base_datos.archivo.is_none() {
            resultado.agregar_error("SQLite requiere especificar archivo".to_string());
        }

        if config.base_datos.tipo != "sqlite" && config.base_datos.url.is_none() {
            resultado.agregar_error("BD remota requiere URL de conexión".to_string());
        }
    }

    fn validar_seguridad(_config: &ConfiguracionAvanzada, _resultado: &mut ResultadoValidacion) {
        // Validaciones futuras
    }

    fn validar_plugins(config: &ConfiguracionAvanzada, resultado: &mut ResultadoValidacion) {
        if config.plugins.maximo_plugins == 0 {
            resultado.agregar_error("Máximo de plugins debe ser > 0".to_string());
        }

        if config.plugins.directorio.is_empty() {
            resultado.agregar_error("Directorio de plugins no puede estar vacío".to_string());
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validar_configuracion_defecto() {
        let config = ConfiguracionAvanzada::defecto();
        let resultado = ValidadorConfiguracion::validar(&config);
        assert!(resultado.valido);
        assert!(resultado.errores.is_empty());
    }

    #[test]
    fn test_validar_version_vacia() {
        let mut config = ConfiguracionAvanzada::defecto();
        config.version = "".to_string();
        let resultado = ValidadorConfiguracion::validar(&config);
        assert!(!resultado.valido);
        assert!(!resultado.errores.is_empty());
    }

    #[test]
    fn test_validar_nivel_logging_invalido() {
        let mut config = ConfiguracionAvanzada::defecto();
        config.logging.nivel = "invalido".to_string();
        let resultado = ValidadorConfiguracion::validar(&config);
        assert!(!resultado.valido);
    }

    #[test]
    fn test_validar_entorno_advertencia() {
        let mut config = ConfiguracionAvanzada::defecto();
        config.entorno = "custom".to_string();
        let resultado = ValidadorConfiguracion::validar(&config);
        assert!(resultado.valido);
        assert!(!resultado.advertencias.is_empty());
    }

    #[test]
    fn test_validar_base_datos_sqlite_sin_archivo() {
        let mut config = ConfiguracionAvanzada::defecto();
        config.base_datos.archivo = None;
        let resultado = ValidadorConfiguracion::validar(&config);
        assert!(!resultado.valido);
    }

    #[test]
    fn test_validar_plugins_maximo_cero() {
        let mut config = ConfiguracionAvanzada::defecto();
        config.plugins.maximo_plugins = 0;
        let resultado = ValidadorConfiguracion::validar(&config);
        assert!(!resultado.valido);
    }

    #[test]
    fn test_resultado_validacion_agregar_error() {
        let mut resultado = ResultadoValidacion::valido();
        resultado.agregar_error("Error test".to_string());
        assert!(!resultado.valido);
        assert_eq!(resultado.errores.len(), 1);
    }

    #[test]
    fn test_resultado_validacion_agregar_advertencia() {
        let mut resultado = ResultadoValidacion::valido();
        resultado.agregar_advertencia("Advertencia test".to_string());
        assert!(resultado.valido);
        assert_eq!(resultado.advertencias.len(), 1);
    }
}
