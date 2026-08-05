pub mod error;
pub mod configuracion;

pub use configuracion::{Configuracion, ConfigBaseDatos, ConfigSeguridad, ConfigIA};
pub use error::{ErrorConfig, ResultadoConfig};
