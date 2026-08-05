/// Errores de ELAP Core.
#[derive(Debug)]
pub enum ElapError {
    /// Error de configuración.
    Config(String),
    /// Error de I/O.
    Io(std::io::Error),
    /// Error de validación.
    Validacion(String),
    /// Error de proceso.
    Proceso(String),
    /// Error no categorizado.
    Otro(String),
}

impl std::fmt::Display for ElapError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ElapError::Config(msg) => write!(f, "Error de configuración: {}", msg),
            ElapError::Io(err) => write!(f, "Error I/O: {}", err),
            ElapError::Validacion(msg) => write!(f, "Error de validación: {}", msg),
            ElapError::Proceso(msg) => write!(f, "Error de proceso: {}", msg),
            ElapError::Otro(msg) => write!(f, "Error: {}", msg),
        }
    }
}

impl std::error::Error for ElapError {}

impl From<std::io::Error> for ElapError {
    fn from(err: std::io::Error) -> Self {
        ElapError::Io(err)
    }
}

impl From<sqlx::Error> for ElapError {
    fn from(err: sqlx::Error) -> Self {
        ElapError::Otro(format!("Error de BD: {}", err))
    }
}

pub type ResultadoElap<T> = Result<T, ElapError>;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_display() {
        let error = ElapError::Config("Test error".to_string());
        assert_eq!(error.to_string(), "Error de configuración: Test error");
    }

    #[test]
    fn test_error_from_io() {
        let io_error = std::io::Error::new(std::io::ErrorKind::NotFound, "File not found");
        let elap_error = ElapError::from(io_error);
        assert!(matches!(elap_error, ElapError::Io(_)));
    }
}
