//! Registro de modelos disponibles

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use super::model_metadata::ModelMetadata;
use crate::error::ResultadoElap;

/// Registro central de modelos
pub struct RegistroModelos {
    modelos: Arc<Mutex<HashMap<String, ModelMetadata>>>,
}

impl RegistroModelos {
    /// Crear nuevo registro
    pub fn nuevo() -> Self {
        Self {
            modelos: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Registrar modelo
    pub fn registrar(&self, metadata: ModelMetadata) -> ResultadoElap<()> {
        let mut modelos = self.modelos.lock().map_err(|_| {
            crate::error::ElapError::Otro("No se pudo adquirir lock".to_string())
        })?;

        if modelos.contains_key(&metadata.nombre) {
            return Err(crate::error::ElapError::Validacion(format!(
                "Modelo {} ya existe",
                metadata.nombre
            )));
        }

        modelos.insert(metadata.nombre.clone(), metadata);
        Ok(())
    }

    /// Obtener modelo
    pub fn obtener(&self, nombre: &str) -> ResultadoElap<ModelMetadata> {
        let modelos = self.modelos.lock().map_err(|_| {
            crate::error::ElapError::Otro("No se pudo adquirir lock".to_string())
        })?;

        modelos
            .get(nombre)
            .cloned()
            .ok_or_else(|| crate::error::ElapError::Validacion(format!(
                "Modelo {} no encontrado",
                nombre
            )))
    }

    /// Listar todos los modelos
    pub fn listar(&self) -> ResultadoElap<Vec<ModelMetadata>> {
        let modelos = self.modelos.lock().map_err(|_| {
            crate::error::ElapError::Otro("No se pudo adquirir lock".to_string())
        })?;

        Ok(modelos.values().cloned().collect())
    }

    /// Contar modelos
    pub fn contar(&self) -> ResultadoElap<usize> {
        let modelos = self.modelos.lock().map_err(|_| {
            crate::error::ElapError::Otro("No se pudo adquirir lock".to_string())
        })?;

        Ok(modelos.len())
    }

    /// Listar modelos descargados
    pub fn listar_descargados(&self) -> ResultadoElap<Vec<ModelMetadata>> {
        let modelos = self.modelos.lock().map_err(|_| {
            crate::error::ElapError::Otro("No se pudo adquirir lock".to_string())
        })?;

        Ok(modelos
            .values()
            .filter(|m| m.descargado)
            .cloned()
            .collect())
    }
}

impl Clone for RegistroModelos {
    fn clone(&self) -> Self {
        Self {
            modelos: self.modelos.clone(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::model_metadata::TipoModelo;

    #[test]
    fn test_crear_registro() {
        let registro = RegistroModelos::nuevo();
        assert_eq!(registro.contar().unwrap(), 0);
    }

    #[test]
    fn test_registrar_modelo() {
        let registro = RegistroModelos::nuevo();
        let metadata = ModelMetadata::nuevo(
            "llama2:7b".to_string(),
            TipoModelo::Chat,
            "Llama 2 7B".to_string(),
            "7B".to_string(),
        );

        assert!(registro.registrar(metadata).is_ok());
        assert_eq!(registro.contar().unwrap(), 1);
    }

    #[test]
    fn test_obtener_modelo() {
        let registro = RegistroModelos::nuevo();
        let metadata = ModelMetadata::nuevo(
            "llama2:7b".to_string(),
            TipoModelo::Chat,
            "Test".to_string(),
            "7B".to_string(),
        );

        registro.registrar(metadata).unwrap();
        let obtenido = registro.obtener("llama2:7b");
        assert!(obtenido.is_ok());
    }

    #[test]
    fn test_listar_modelos() {
        let registro = RegistroModelos::nuevo();
        let m1 = ModelMetadata::nuevo(
            "llama2:7b".to_string(),
            TipoModelo::Chat,
            "Test".to_string(),
            "7B".to_string(),
        );
        let m2 = ModelMetadata::nuevo(
            "mistral".to_string(),
            TipoModelo::TextoGenerativo,
            "Test".to_string(),
            "7B".to_string(),
        );

        registro.registrar(m1).unwrap();
        registro.registrar(m2).unwrap();
        assert_eq!(registro.listar().unwrap().len(), 2);
    }

    #[test]
    fn test_modelo_duplicado() {
        let registro = RegistroModelos::nuevo();
        let metadata = ModelMetadata::nuevo(
            "llama2:7b".to_string(),
            TipoModelo::Chat,
            "Test".to_string(),
            "7B".to_string(),
        );

        registro.registrar(metadata.clone()).unwrap();
        let resultado = registro.registrar(metadata);
        assert!(resultado.is_err());
    }

    #[test]
    fn test_listar_descargados() {
        let registro = RegistroModelos::nuevo();
        let mut m1 = ModelMetadata::nuevo(
            "llama2:7b".to_string(),
            TipoModelo::Chat,
            "Test".to_string(),
            "7B".to_string(),
        );
        m1.marcar_descargado(3500);

        let m2 = ModelMetadata::nuevo(
            "mistral".to_string(),
            TipoModelo::TextoGenerativo,
            "Test".to_string(),
            "7B".to_string(),
        );

        registro.registrar(m1).unwrap();
        registro.registrar(m2).unwrap();

        let descargados = registro.listar_descargados().unwrap();
        assert_eq!(descargados.len(), 1);
    }
}
