/// Permisos que se pueden validar en ELAP.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Permiso {
    /// Leer archivos del sistema.
    LeerArchivos,
    /// Escribir archivos del sistema.
    EscribirArchivos,
    /// Ejecutar procesos del SO.
    EjecutarProcesos,
    /// Ejecutar herramientas registradas.
    EjecutarHerramientas,
    /// Cambiar configuración del sistema.
    CambiarConfiguracion,
}

impl std::fmt::Display for Permiso {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Permiso::LeerArchivos => write!(f, "LeerArchivos"),
            Permiso::EscribirArchivos => write!(f, "EscribirArchivos"),
            Permiso::EjecutarProcesos => write!(f, "EjecutarProcesos"),
            Permiso::EjecutarHerramientas => write!(f, "EjecutarHerramientas"),
            Permiso::CambiarConfiguracion => write!(f, "CambiarConfiguracion"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_permiso_display_leer_archivos() {
        assert_eq!(Permiso::LeerArchivos.to_string(), "LeerArchivos");
    }

    #[test]
    fn test_permiso_display_escribir_archivos() {
        assert_eq!(Permiso::EscribirArchivos.to_string(), "EscribirArchivos");
    }

    #[test]
    fn test_permiso_display_ejecutar_procesos() {
        assert_eq!(Permiso::EjecutarProcesos.to_string(), "EjecutarProcesos");
    }

    #[test]
    fn test_permiso_display_ejecutar_herramientas() {
        assert_eq!(Permiso::EjecutarHerramientas.to_string(), "EjecutarHerramientas");
    }

    #[test]
    fn test_permiso_display_cambiar_config() {
        assert_eq!(Permiso::CambiarConfiguracion.to_string(), "CambiarConfiguracion");
    }

    #[test]
    fn test_permiso_comparacion() {
        let p1 = Permiso::LeerArchivos;
        let p2 = Permiso::LeerArchivos;
        assert_eq!(p1, p2);
    }
}