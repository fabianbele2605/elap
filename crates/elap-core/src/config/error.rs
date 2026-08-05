/// Errores de configuración.
#[derive(Debug)]
pub enum ErrorConfig {
    /// Error al leer archivo.
    NoSeLeyoArchivo(String),
    /// Error al parsear YAML.
    ErrorYaml(String),
    /// Error al escribir archivo.
    NoSeEscribioArchivo(String),
    /// Campo obligatorio faltante.
    CampoFaltante(String),
    /// Valor inválido.
    ValorInvalido(String),
}

impl std::fmt::Display for ErrorConfig {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ErrorConfig::NoSeLeyoArchivo(msg) => write!(f, "No se leyó archivo: {}", msg),
            ErrorConfig::ErrorYaml(msg) => write!(f, "Error YAML: {}", msg),
            ErrorConfig::NoSeEscribioArchivo(msg) => write!(f, "No se escribió archivo: {}", msg),
            ErrorConfig::CampoFaltante(campo) => write!(f, "Campo obligatorio faltante: {}", campo),
            ErrorConfig::ValorInvalido(msg) => write!(f, "Valor inválido: {}", msg),
        }
    }
}

impl std::error::Error for ErrorConfig {}

/// Tipo para resultados de operaciones de configuración.
pub type ResultadoConfig<T> = Result<T, ErrorConfig>;
