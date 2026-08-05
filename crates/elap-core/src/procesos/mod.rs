pub mod error;
pub mod proceso;
pub mod spawner;
pub mod ejecutor;

pub use ejecutor::GestorProcesos;
pub use proceso::{Proceso, IdProceso, EstadoProceso};
pub use error::{ErrorProceso, ResultadoProceso};
