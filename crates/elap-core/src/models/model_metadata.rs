//! Metadatos de modelos de IA

use serde::{Deserialize, Serialize};

/// Tipo de modelo
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum TipoModelo {
    /// LLM para generación de texto
    TextoGenerativo,
    /// Modelo para embeddings
    Embedding,
    /// Modelo de lenguaje conversacional
    Chat,
}

impl std::fmt::Display for TipoModelo {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            TipoModelo::TextoGenerativo => write!(f, "texto_generativo"),
            TipoModelo::Embedding => write!(f, "embedding"),
            TipoModelo::Chat => write!(f, "chat"),
        }
    }
}

/// Metadatos de un modelo de IA
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelMetadata {
    /// Nombre del modelo (ej: "llama2:7b")
    pub nombre: String,
    /// Tipo de modelo
    pub tipo: TipoModelo,
    /// Descripción
    pub descripcion: String,
    /// Tamaño en MB
    pub tamaño_mb: u32,
    /// Parámetros (ej: 7B, 13B)
    pub parametros: String,
    /// Versión
    pub version: String,
    /// ¿Descargado localmente?
    pub descargado: bool,
    /// Última actualización
    pub ultima_actualizacion: String,
}

impl ModelMetadata {
    /// Crear nuevos metadatos
    pub fn nuevo(
        nombre: String,
        tipo: TipoModelo,
        descripcion: String,
        parametros: String,
    ) -> Self {
        Self {
            nombre,
            tipo,
            descripcion,
            tamaño_mb: 0,
            parametros,
            version: "1.0".to_string(),
            descargado: false,
            ultima_actualizacion: chrono::Utc::now().to_rfc3339(),
        }
    }

    /// Marcar como descargado
    pub fn marcar_descargado(&mut self, tamaño_mb: u32) {
        self.descargado = true;
        self.tamaño_mb = tamaño_mb;
        self.ultima_actualizacion = chrono::Utc::now().to_rfc3339();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tipo_modelo_display() {
        assert_eq!(TipoModelo::TextoGenerativo.to_string(), "texto_generativo");
        assert_eq!(TipoModelo::Embedding.to_string(), "embedding");
        assert_eq!(TipoModelo::Chat.to_string(), "chat");
    }

    #[test]
    fn test_crear_metadata() {
        let metadata = ModelMetadata::nuevo(
            "llama2:7b".to_string(),
            TipoModelo::Chat,
            "Llama 2 7B para chat".to_string(),
            "7B".to_string(),
        );

        assert_eq!(metadata.nombre, "llama2:7b");
        assert_eq!(metadata.tipo, TipoModelo::Chat);
        assert!(!metadata.descargado);
    }

    #[test]
    fn test_marcar_descargado() {
        let mut metadata = ModelMetadata::nuevo(
            "llama2:7b".to_string(),
            TipoModelo::Chat,
            "Test".to_string(),
            "7B".to_string(),
        );

        metadata.marcar_descargado(3500);

        assert!(metadata.descargado);
        assert_eq!(metadata.tamaño_mb, 3500);
    }
}
