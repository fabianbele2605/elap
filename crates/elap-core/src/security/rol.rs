/// Roles de usuario en ELAP.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Rol {
    /// Acceso total al sistema.
    Admin,
    /// Acceso normal a herramientas y datos.
    Usuario,
    /// Acceso limitado, solo lectura.
    Invitado,
    /// Agente de IA ejecutando tareas.
    Agente,
}

impl std::fmt::Display for Rol {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Rol::Admin => write!(f, "Admin"),
            Rol::Usuario => write!(f, "Usuario"),
            Rol::Invitado => write!(f, "Invitado"),
            Rol::Agente => write!(f, "Agente"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rol_display_admin() {
        assert_eq!(Rol::Admin.to_string(), "Admin");
    }

    #[test]
    fn test_rol_display_usuario() {
        assert_eq!(Rol::Usuario.to_string(), "Usuario");
    }

    #[test]
    fn test_rol_display_invitado() {
        assert_eq!(Rol::Invitado.to_string(), "Invitado");
    }

    #[test]
    fn test_rol_display_agente() {
        assert_eq!(Rol::Agente.to_string(), "Agente");
    }

    #[test]
    fn test_rol_comparacion() {
        let rol1 = Rol::Admin;
        let rol2 = Rol::Admin;
        assert_eq!(rol1, rol2);
    }
}
