//! Módulo de seguridad y control de acceso.

pub mod rol;
pub mod permisos;
pub mod rbac;
pub mod auditor;

pub use rol::Rol;
pub use permisos::Permiso;
pub use rbac::GestorRbac;
pub use auditor::{RegistroAuditoria, AuditorRbac};