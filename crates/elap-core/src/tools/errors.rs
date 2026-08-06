//! Errores de herramientas

/// Error de herramienta
#[derive(Debug, Clone)]
pub enum ToolError {
    NoEncontrada(String),
    AccesoDenegado(String),
    ParametrosInvalidos(String),
    EjecucionFallo(String),
}

impl std::fmt::Display for ToolError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ToolError::NoEncontrada(msg) => write!(f, "Herramienta no encontrada: {}", msg),
            ToolError::AccesoDenegado(msg) => write!(f, "Acceso denegado: {}", msg),
            ToolError::ParametrosInvalidos(msg) => write!(f, "Parámetros inválidos: {}", msg),
            ToolError::EjecucionFallo(msg) => write!(f, "Ejecución falló: {}", msg),
        }
    }
}

impl std::error::Error for ToolError {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tool_error_display() {
        let error = ToolError::NoEncontrada("test".to_string());
        assert!(error.to_string().contains("no encontrada"));
    }
}
