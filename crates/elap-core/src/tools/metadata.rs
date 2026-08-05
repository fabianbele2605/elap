//! Metadatos de herramientas

use serde::{Deserialize, Serialize};

/// Tipo de herramienta
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum TipoHerramienta {
    Archivo,
    Http,
    BaseDatos,
    Ssh,
    Sistema,
}

impl std::fmt::Display for TipoHerramienta {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            TipoHerramienta::Archivo => write!(f, "archivo"),
            TipoHerramienta::Http => write!(f, "http"),
            TipoHerramienta::BaseDatos => write!(f, "base_datos"),
            TipoHerramienta::Ssh => write!(f, "ssh"),
            TipoHerramienta::Sistema => write!(f, "sistema"),
        }
    }
}

/// Metadatos de una herramienta
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolMetadata {
    pub nombre: String,
    pub tipo_herramienta: TipoHerramienta,
    pub descripcion: String,
    pub version: String,
    pub permisos_requeridos: Vec<String>,
    pub habilitada: bool,
}

impl ToolMetadata {
    /// Crear nuevos metadatos
    pub fn nuevo(
        nombre: String,
        tipo_herramienta: TipoHerramienta,
        descripcion: String,
    ) -> Self {
        Self {
            nombre,
            tipo_herramienta,
            descripcion,
            version: "1.0.0".to_string(),
            permisos_requeridos: Vec::new(),
            habilitada: true,
        }
    }

    /// Agregar permiso requerido
    pub fn agregar_permiso(&mut self, permiso: String) {
        self.permisos_requeridos.push(permiso);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tipo_herramienta_display() {
        assert_eq!(TipoHerramienta::Archivo.to_string(), "archivo");
        assert_eq!(TipoHerramienta::Http.to_string(), "http");
    }

    #[test]
    fn test_crear_metadata() {
        let metadata = ToolMetadata::nuevo(
            "lectura_archivos".to_string(),
            TipoHerramienta::Archivo,
            "Lee archivos del sistema".to_string(),
        );

        assert_eq!(metadata.nombre, "lectura_archivos");
        assert!(metadata.habilitada);
    }

    #[test]
    fn test_agregar_permiso() {
        let mut metadata = ToolMetadata::nuevo(
            "test".to_string(),
            TipoHerramienta::Archivo,
            "test".to_string(),
        );

        metadata.agregar_permiso("LeerArchivos".to_string());
        assert_eq!(metadata.permisos_requeridos.len(), 1);
    }
}
