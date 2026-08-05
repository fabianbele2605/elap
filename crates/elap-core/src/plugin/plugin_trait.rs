//! Trait base para plugins

use std::any::Any;

/// Trait que todos los plugins deben implementar
pub trait Plugin: Send + Sync {
    /// Nombre del plugin
    fn nombre(&self) -> &str;
    
    /// Versión del plugin
    fn version(&self) -> &str;
    
    /// Descripción del plugin
    fn descripcion(&self) -> &str;
    
    /// Inicializar el plugin
    fn inicializar(&mut self) -> Result<(), String>;
    
    /// Ejecutar una función del plugin
    fn ejecutar(&self, comando: &str, args: &[String]) -> Result<String, String>;
    
    /// Finalizar el plugin
    fn finalizar(&mut self) -> Result<(), String>;
    
    /// Obtener una referencia genérica (para downcasting)
    fn as_any(&self) -> &dyn Any;
}
