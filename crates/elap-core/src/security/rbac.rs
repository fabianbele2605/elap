use std::collections::HashMap;
use super::{Rol, Permiso};
use crate::error::{ElapError, ResultadoElap};

/// Gestor de control de acceso basado en roles (RBAC).
#[derive(Debug)]
pub struct GestorRbac {
    /// Mapeo de rol → lista de permisos.
    permisos_por_rol: HashMap<Rol, Vec<Permiso>>,
}

impl GestorRbac {
    /// Crea un nuevo gestor RBAC con permisos predeterminados.
    pub fn nuevo() -> Self {
        let mut permisos_por_rol = HashMap::new();

        // Admin: todos los permisos
        permisos_por_rol.insert(
            Rol::Admin,
            vec![
                Permiso::LeerArchivos,
                Permiso::EscribirArchivos,
                Permiso::EjecutarProcesos,
                Permiso::EjecutarHerramientas,
                Permiso::CambiarConfiguracion,
            ],
        );

        // Usuario: casi todo excepto cambiar config
        permisos_por_rol.insert(
            Rol::Usuario,
            vec![
                Permiso::LeerArchivos,
                Permiso::EscribirArchivos,
                Permiso::EjecutarProcesos,
                Permiso::EjecutarHerramientas,
            ],
        );

        // Invitado: solo lectura
        permisos_por_rol.insert(
            Rol::Invitado,
            vec![Permiso::LeerArchivos],
        );

        // Agente: ejecutar herramientas y leer
        permisos_por_rol.insert(
            Rol::Agente,
            vec![
                Permiso::LeerArchivos,
                Permiso::EjecutarHerramientas,
            ],
        );

        Self { permisos_por_rol }
    }

    /// Valida si un rol tiene un permiso específico.
    pub fn validar_permiso(&self, rol: Rol, permiso: Permiso) -> ResultadoElap<()> {
        let permisos = self.permisos_por_rol
            .get(&rol)
            .ok_or_else(|| ElapError::Validacion(format!("Rol no encontrado: {}", rol)))?;

        if permisos.contains(&permiso) {
            Ok(())
        } else {
            Err(ElapError::Validacion(
                format!("Rol {} no tiene permiso para: {}", rol, permiso)
            ))
        }
    }

    /// Obtiene lista de permisos para un rol.
    pub fn permisos_del_rol(&self, rol: Rol) -> ResultadoElap<Vec<Permiso>> {
        self.permisos_por_rol
            .get(&rol)
            .cloned()
            .ok_or_else(|| ElapError::Validacion(format!("Rol no encontrado: {}", rol)))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_gestor_rbac() {
        let rbac = GestorRbac::nuevo();
        assert!(rbac.validar_permiso(Rol::Admin, Permiso::LeerArchivos).is_ok());
    }

    #[test]
    fn test_rol_admin_tiene_todos_permisos() {
        let rbac = GestorRbac::nuevo();
        assert!(rbac.validar_permiso(Rol::Admin, Permiso::LeerArchivos).is_ok());
        assert!(rbac.validar_permiso(Rol::Admin, Permiso::EscribirArchivos).is_ok());
        assert!(rbac.validar_permiso(Rol::Admin, Permiso::EjecutarProcesos).is_ok());
        assert!(rbac.validar_permiso(Rol::Admin, Permiso::EjecutarHerramientas).is_ok());
        assert!(rbac.validar_permiso(Rol::Admin, Permiso::CambiarConfiguracion).is_ok());
    }

    #[test]
    fn test_rol_usuario_tiene_permisos_limitados() {
        let rbac = GestorRbac::nuevo();
        assert!(rbac.validar_permiso(Rol::Usuario, Permiso::LeerArchivos).is_ok());
        assert!(rbac.validar_permiso(Rol::Usuario, Permiso::EjecutarHerramientas).is_ok());
        assert!(rbac.validar_permiso(Rol::Usuario, Permiso::CambiarConfiguracion).is_err());
    }

    #[test]
    fn test_rol_invitado_sin_permisos_escritura() {
        let rbac = GestorRbac::nuevo();
        assert!(rbac.validar_permiso(Rol::Invitado, Permiso::LeerArchivos).is_ok());
        assert!(rbac.validar_permiso(Rol::Invitado, Permiso::EscribirArchivos).is_err());
    }

    #[test]
    fn test_validar_permiso_ok() {
        let rbac = GestorRbac::nuevo();
        let resultado = rbac.validar_permiso(Rol::Admin, Permiso::LeerArchivos);
        assert!(resultado.is_ok());
    }

    #[test]
    fn test_validar_permiso_denegado() {
        let rbac = GestorRbac::nuevo();
        let resultado = rbac.validar_permiso(Rol::Invitado, Permiso::CambiarConfiguracion);
        assert!(resultado.is_err());
    }

    #[test]
    fn test_permisos_del_rol_admin() {
        let rbac = GestorRbac::nuevo();
        let permisos = rbac.permisos_del_rol(Rol::Admin).unwrap();
        assert_eq!(permisos.len(), 5);
    }

    #[test]
    fn test_permisos_del_rol_invitado() {
        let rbac = GestorRbac::nuevo();
        let permisos = rbac.permisos_del_rol(Rol::Invitado).unwrap();
        assert_eq!(permisos.len(), 1);
    }
}
