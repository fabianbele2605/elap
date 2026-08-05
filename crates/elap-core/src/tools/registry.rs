//! Registro de herramientas

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use super::metadata::ToolMetadata;
use crate::error::ResultadoElap;

/// Registro central de herramientas
pub struct RegistroHerramientas {
    herramientas: Arc<Mutex<HashMap<String, ToolMetadata>>>,
}

impl RegistroHerramientas {
    /// Crear nuevo registro
    pub fn nuevo() -> Self {
        Self {
            herramientas: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Registrar herramienta
    pub fn registrar(&self, metadata: ToolMetadata) -> ResultadoElap<()> {
        let mut herramientas = self.herramientas.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock".to_string()
            ))?;

        if herramientas.contains_key(&metadata.nombre) {
            return Err(crate::error::ElapError::Validacion(
                format!("Herramienta {} ya existe", metadata.nombre)
            ));
        }

        herramientas.insert(metadata.nombre.clone(), metadata);
        Ok(())
    }

    /// Obtener herramienta
    pub fn obtener(&self, nombre: &str) -> ResultadoElap<ToolMetadata> {
        let herramientas = self.herramientas.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock".to_string()
            ))?;

        herramientas.get(nombre)
            .cloned()
            .ok_or_else(|| crate::error::ElapError::Validacion(
                format!("Herramienta {} no encontrada", nombre)
            ))
    }

    /// Listar todas las herramientas
    pub fn listar(&self) -> ResultadoElap<Vec<ToolMetadata>> {
        let herramientas = self.herramientas.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock".to_string()
            ))?;

        Ok(herramientas.values().cloned().collect())
    }

    /// Contar herramientas
    pub fn contar(&self) -> ResultadoElap<usize> {
        let herramientas = self.herramientas.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock".to_string()
            ))?;

        Ok(herramientas.len())
    }
}

impl Clone for RegistroHerramientas {
    fn clone(&self) -> Self {
        Self {
            herramientas: self.herramientas.clone(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::metadata::TipoHerramienta;

    #[test]
    fn test_crear_registro() {
        let registro = RegistroHerramientas::nuevo();
        assert_eq!(registro.contar().unwrap(), 0);
    }

    #[test]
    fn test_registrar_herramienta() {
        let registro = RegistroHerramientas::nuevo();
        let metadata = ToolMetadata::nuevo(
            "test".to_string(),
            TipoHerramienta::Archivo,
            "test".to_string(),
        );

        assert!(registro.registrar(metadata).is_ok());
        assert_eq!(registro.contar().unwrap(), 1);
    }

    #[test]
    fn test_obtener_herramienta() {
        let registro = RegistroHerramientas::nuevo();
        let metadata = ToolMetadata::nuevo(
            "test".to_string(),
            TipoHerramienta::Archivo,
            "test".to_string(),
        );

        assert!(registro.registrar(metadata).is_ok());
        let obtenida = registro.obtener("test");
        assert!(obtenida.is_ok());
    }

    #[test]
    fn test_listar_herramientas() {
        let registro = RegistroHerramientas::nuevo();
        let m1 = ToolMetadata::nuevo(
            "h1".to_string(),
            TipoHerramienta::Archivo,
            "test".to_string(),
        );
        let m2 = ToolMetadata::nuevo(
            "h2".to_string(),
            TipoHerramienta::Http,
            "test".to_string(),
        );

        assert!(registro.registrar(m1).is_ok());
        assert!(registro.registrar(m2).is_ok());
        assert_eq!(registro.listar().unwrap().len(), 2);
    }
}
