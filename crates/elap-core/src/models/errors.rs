//! Errores del Model Manager

/// Error de modelo
#[derive(Debug, Clone)]
pub enum ModelError {
    NoEncontrado(String),
    NoDisponible(String),
    ParametrosInvalidos(String),
    ErrorGeneracion(String),
}

impl std::fmt::Display for ModelError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ModelError::NoEncontrado(msg) => write!(f, "Modelo no encontrado: {}", msg),
            ModelError::NoDisponible(msg) => write!(f, "Modelo no disponible: {}", msg),
            ModelError::ParametrosInvalidos(msg) => write!(f, "Parámetros inválidos: {}", msg),
            ModelError::ErrorGeneracion(msg) => write!(f, "Error en generación: {}", msg),
        }
    }
}

impl std::error::Error for ModelError {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_display() {
        let error = ModelError::NoEncontrado("llama2".to_string());
        assert!(error.to_string().contains("no encontrado"));
    }
}
