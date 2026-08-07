// Research Plugin - Expone la funcionalidad de búsqueda de información

use crate::plugin::Plugin;
use std::any::Any;

/// Plugin que proporciona capacidades de investigación
pub struct ResearchPlugin {
    nombre: String,
    version: String,
    descripcion: String,
    inicializado: bool,
}

impl ResearchPlugin {
    /// Crear nueva instancia del plugin
    pub fn new() -> Self {
        Self {
            nombre: "research-plugin".to_string(),
            version: "1.0.0".to_string(),
            descripcion: "Plugin de investigación que proporciona búsqueda de información y análisis".to_string(),
            inicializado: false,
        }
    }
}

impl Default for ResearchPlugin {
    fn default() -> Self {
        Self::new()
    }
}

impl Plugin for ResearchPlugin {
    fn nombre(&self) -> &str {
        &self.nombre
    }

    fn version(&self) -> &str {
        &self.version
    }

    fn descripcion(&self) -> &str {
        &self.descripcion
    }

    fn inicializar(&mut self) -> Result<(), String> {
        self.inicializado = true;
        Ok(())
    }

    fn ejecutar(&self, comando: &str, args: &[String]) -> Result<String, String> {
        if !self.inicializado {
            return Err("Plugin no inicializado".to_string());
        }

        match comando {
            "buscar" => self.buscar(args),
            "investigar" => self.investigar(args),
            "listar_fuentes" => self.listar_fuentes(),
            _ => Err(format!("Comando desconocido: {}", comando)),
        }
    }

    fn finalizar(&mut self) -> Result<(), String> {
        self.inicializado = false;
        Ok(())
    }

    fn as_any(&self) -> &dyn Any {
        self
    }
}

impl ResearchPlugin {
    /// Ejecutar búsqueda
    fn buscar(&self, args: &[String]) -> Result<String, String> {
        if args.is_empty() {
            return Err("Se requiere tema de búsqueda".to_string());
        }

        let tema = &args[0];

        Ok(format!(
            r#"{{"exito": true, "comando": "buscar", "tema": "{}", "resultados": 3}}"#,
            tema
        ))
    }

    /// Ejecutar investigación
    fn investigar(&self, args: &[String]) -> Result<String, String> {
        if args.is_empty() {
            return Err("Se requiere tema de investigación".to_string());
        }

        let tema = &args[0];
        let profundidad = args.get(1).map(|s| s.as_str()).unwrap_or("basica");

        Ok(format!(
            r#"{{"exito": true, "comando": "investigar", "tema": "{}", "profundidad": "{}", "fuentes": 5}}"#,
            tema, profundidad
        ))
    }

    /// Listar fuentes disponibles
    fn listar_fuentes(&self) -> Result<String, String> {
        Ok(r#"{"exito": true, "fuentes": ["Wikipedia", "Academic", "News"], "cantidad": 3}"#.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_plugin_creation() {
        let plugin = ResearchPlugin::new();
        assert_eq!(plugin.nombre(), "research-plugin");
        assert_eq!(plugin.version(), "1.0.0");
    }

    #[test]
    fn test_descripcion() {
        let plugin = ResearchPlugin::new();
        assert!(!plugin.descripcion().is_empty());
    }

    #[test]
    fn test_inicializar_y_finalizar() {
        let mut plugin = ResearchPlugin::new();
        assert!(plugin.inicializar().is_ok());
        assert!(plugin.finalizar().is_ok());
    }

    #[test]
    fn test_ejecutar_busqueda() {
        let mut plugin = ResearchPlugin::new();
        plugin.inicializar().unwrap();

        let args = vec!["inteligencia artificial".to_string()];
        let resultado = plugin.ejecutar("buscar", &args);

        assert!(resultado.is_ok());
        let respuesta = resultado.unwrap();
        assert!(respuesta.contains("inteligencia artificial"));
    }

    #[test]
    fn test_ejecutar_investigacion() {
        let mut plugin = ResearchPlugin::new();
        plugin.inicializar().unwrap();

        let args = vec!["machine learning".to_string(), "profunda".to_string()];
        let resultado = plugin.ejecutar("investigar", &args);

        assert!(resultado.is_ok());
        let respuesta = resultado.unwrap();
        assert!(respuesta.contains("machine learning"));
        assert!(respuesta.contains("profunda"));
    }

    #[test]
    fn test_listar_fuentes() {
        let mut plugin = ResearchPlugin::new();
        plugin.inicializar().unwrap();

        let resultado = plugin.ejecutar("listar_fuentes", &[]);
        assert!(resultado.is_ok());
        let respuesta = resultado.unwrap();
        assert!(respuesta.contains("Wikipedia"));
    }

    #[test]
    fn test_no_inicializado() {
        let plugin = ResearchPlugin::new();
        let args = vec!["tema".to_string()];
        let resultado = plugin.ejecutar("buscar", &args);

        assert!(resultado.is_err());
    }

    #[test]
    fn test_comando_desconocido() {
        let mut plugin = ResearchPlugin::new();
        plugin.inicializar().unwrap();

        let resultado = plugin.ejecutar("comando_inexistente", &[]);
        assert!(resultado.is_err());
    }
}
