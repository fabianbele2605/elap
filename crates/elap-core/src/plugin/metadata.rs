//! Metadatos de plugin

use serde::{Deserialize, Serialize};

/// Metadatos de un plugin
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginMetadata {
    /// Nombre único del plugin
    pub nombre: String,
    
    /// Versión semántica
    pub version: String,
    
    /// Autor del plugin
    pub autor: String,
    
    /// Descripción breve
    pub descripcion: String,
    
    /// Ruta al archivo .so / .dll
    pub ruta_binario: String,
    
    /// Función de entrada (symbol name)
    pub punto_entrada: String,
    
    /// Permisos requeridos
    pub permisos: Vec<String>,
    
    /// Hash SHA256 para verificación
    pub hash_verificacion: Option<String>,
}

impl PluginMetadata {
    /// Crear nuevos metadatos
    pub fn nuevo(
        nombre: String,
        version: String,
        autor: String,
        descripcion: String,
        ruta_binario: String,
        punto_entrada: String,
    ) -> Self {
        Self {
            nombre,
            version,
            autor,
            descripcion,
            ruta_binario,
            punto_entrada,
            permisos: Vec::new(),
            hash_verificacion: None,
        }
    }

    /// Agregar permiso requerido
    pub fn agregar_permiso(&mut self, permiso: String) {
        self.permisos.push(permiso);
    }
}
