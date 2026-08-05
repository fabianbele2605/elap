use std::io;

/// Errores posibles durante la gestión de procesos.
#[derive(Debug)]
pub enum ErrorProceso {
    /// No se pudo crear el proceso.
    NoSePudoCrear(String),
    /// El proceso no fue encontrado.
    ProcesoNoEncontrado(String),
    /// Error de I/O del sistema.
    FalloIO(String),
    /// El proceso falló con un código de salida.
    ProcesoFallo(i32),
}

impl std::fmt::Display for ErrorProceso {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ErrorProceso::NoSePudoCrear(msg) => write!(f, "No se pudo crear proceso: {}", msg),
            ErrorProceso::ProcesoNoEncontrado(id) => write!(f, "Proceso no encontrado: {}", id),
            ErrorProceso::FalloIO(msg) => write!(f, "Error IO: {}", msg),
            ErrorProceso::ProcesoFallo(code) => write!(f, "Proceso falló con código: {}", code),
        }
    }
}

impl std::error::Error for ErrorProceso {}

impl From<io::Error> for ErrorProceso {
    fn from(err: io::Error) -> Self {
        ErrorProceso::FalloIO(err.to_string())
    }
}

/// Tipo para resultados de operaciones de procesos.
pub type ResultadoProceso<T> = Result<T, ErrorProceso>;
