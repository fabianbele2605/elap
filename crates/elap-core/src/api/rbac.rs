//! Control de acceso basado en roles para API

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Rol de usuario en API
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum RolAPI {
    /// Administrador - acceso total
    Admin,
    /// Usuario - acceso a agentes propios
    User,
    /// Invitado - solo lectura
    Guest,
}

impl RolAPI {
    /// Parsear desde string
    pub fn from_str(s: &str) -> Self {
        match s.to_lowercase().as_str() {
            "admin" => RolAPI::Admin,
            "guest" => RolAPI::Guest,
            _ => RolAPI::User,
        }
    }
}

impl std::fmt::Display for RolAPI {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            RolAPI::Admin => write!(f, "Admin"),
            RolAPI::User => write!(f, "User"),
            RolAPI::Guest => write!(f, "Guest"),
        }
    }
}

/// Acción en API
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Accion {
    /// Crear recurso
    Crear,
    /// Leer recurso
    Leer,
    /// Actualizar recurso
    Actualizar,
    /// Eliminar recurso
    Eliminar,
    /// Ejecutar acción
    Ejecutar,
}

/// Validador RBAC para API
pub struct ValidadorRBAC {
    permisos: HashMap<RolAPI, Vec<Accion>>,
}

impl ValidadorRBAC {
    /// Crear validador con permisos por defecto
    pub fn nuevo() -> Self {
        let mut permisos = HashMap::new();

        // Admin: todo
        permisos.insert(
            RolAPI::Admin,
            vec![
                Accion::Crear,
                Accion::Leer,
                Accion::Actualizar,
                Accion::Eliminar,
                Accion::Ejecutar,
            ],
        );

        // User: CRUD básico
        permisos.insert(
            RolAPI::User,
            vec![
                Accion::Crear,
                Accion::Leer,
                Accion::Actualizar,
                Accion::Ejecutar,
            ],
        );

        // Guest: solo lectura
        permisos.insert(RolAPI::Guest, vec![Accion::Leer]);

        Self { permisos }
    }

    /// Validar si un rol puede realizar una acción
    pub fn puede_realizar(&self, rol: &RolAPI, accion: &Accion) -> bool {
        self.permisos
            .get(rol)
            .map(|acciones| acciones.contains(accion))
            .unwrap_or(false)
    }

    /// Obtener todas las acciones permitidas para un rol
    pub fn acciones_permitidas(&self, rol: &RolAPI) -> Vec<Accion> {
        self.permisos.get(rol).cloned().unwrap_or_default()
    }
}

impl Default for ValidadorRBAC {
    fn default() -> Self {
        Self::nuevo()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rol_from_str() {
        assert_eq!(RolAPI::from_str("admin"), RolAPI::Admin);
        assert_eq!(RolAPI::from_str("Admin"), RolAPI::Admin);
        assert_eq!(RolAPI::from_str("user"), RolAPI::User);
        assert_eq!(RolAPI::from_str("guest"), RolAPI::Guest);
    }

    #[test]
    fn test_rol_display() {
        assert_eq!(RolAPI::Admin.to_string(), "Admin");
        assert_eq!(RolAPI::User.to_string(), "User");
        assert_eq!(RolAPI::Guest.to_string(), "Guest");
    }

    #[test]
    fn test_admin_permisos() {
        let validador = ValidadorRBAC::nuevo();
        assert!(validador.puede_realizar(&RolAPI::Admin, &Accion::Crear));
        assert!(validador.puede_realizar(&RolAPI::Admin, &Accion::Eliminar));
    }

    #[test]
    fn test_user_permisos() {
        let validador = ValidadorRBAC::nuevo();
        assert!(validador.puede_realizar(&RolAPI::User, &Accion::Crear));
        assert!(!validador.puede_realizar(&RolAPI::User, &Accion::Eliminar));
    }

    #[test]
    fn test_guest_permisos() {
        let validador = ValidadorRBAC::nuevo();
        assert!(validador.puede_realizar(&RolAPI::Guest, &Accion::Leer));
        assert!(!validador.puede_realizar(&RolAPI::Guest, &Accion::Crear));
    }

    #[test]
    fn test_acciones_permitidas() {
        let validador = ValidadorRBAC::nuevo();
        let acciones = validador.acciones_permitidas(&RolAPI::Admin);
        assert_eq!(acciones.len(), 5);
    }
}
