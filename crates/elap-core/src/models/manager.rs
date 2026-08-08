//! Model Manager: orquestador de modelos con memoria

use super::{OllamaClient, RegistroModelos, CacheEmbeddings, ModelMetadata, TipoModelo};
use serde_json::{json, Value as JsonValue};
use crate::error::{ResultadoElap, ElapError};
use std::collections::VecDeque;

/// Entrada de memoria corta
#[derive(Debug, Clone)]
pub struct MemoriaCorta {
    pub rol: String,      // "usuario" o "asistente"
    pub contenido: String,
    pub timestamp: String,
}

/// Model Manager: orquestador central
#[derive(Clone)]
pub struct ModelManager {
    cliente: OllamaClient,
    registro: RegistroModelos,
    cache: CacheEmbeddings,
    memoria_corta: VecDeque<MemoriaCorta>,
    modelo_activo: Option<String>,
    max_memoria: usize,
}

impl ModelManager {
    /// Crear nuevo Model Manager
    pub fn nuevo(
        url_ollama: impl Into<String>,
        max_memoria: usize,
    ) -> Self {
        Self {
            cliente: OllamaClient::nuevo(url_ollama, 30),
            registro: RegistroModelos::nuevo(),
            cache: CacheEmbeddings::nuevo(1000),
            memoria_corta: VecDeque::new(),
            modelo_activo: None,
            max_memoria,
        }
    }

    /// Registrar modelo disponible
    pub fn registrar_modelo(&self, metadata: ModelMetadata) -> ResultadoElap<()> {
        self.registro.registrar(metadata)?;
        Ok(())
    }

    /// Establecer modelo activo
    pub fn set_modelo_activo(&mut self, nombre: &str) -> ResultadoElap<()> {
        let modelo = self.registro.obtener(nombre)?;
        self.modelo_activo = Some(modelo.nombre);
        Ok(())
    }

    /// Generar texto
    pub fn generar(&self, prompt: &str, temperatura: f32) -> ResultadoElap<String> {
        let modelo = self.modelo_activo.as_ref()
            .ok_or(ElapError::ValidationError("No hay modelo activo".to_string()))?;

        self.cliente.generar(modelo, prompt, temperatura)
    }

    /// Generar embeddings con cache
    pub fn embeddings(&self, texto: &str) -> ResultadoElap<Vec<f32>> {
        let modelo = self.modelo_activo.as_ref()
            .ok_or(ElapError::ValidationError("No hay modelo activo".to_string()))?;

        // Intentar obtener del cache
        if let Ok(Some(cached)) = self.cache.obtener(modelo, texto) {
            return Ok(cached);
        }

        // Generar nuevo
        let embeddings = self.cliente.embeddings(modelo, texto)?;

        // Guardar en cache
        let _ = self.cache.guardar(modelo, texto, embeddings.clone());

        Ok(embeddings)
    }

    /// Chat con memoria
    pub fn chat(&mut self, usuario: &str) -> ResultadoElap<String> {
        let modelo = self.modelo_activo.as_ref()
            .ok_or(ElapError::ValidationError("No hay modelo activo".to_string()))?;

        // Agregar a memoria corta
        self.memoria_corta.push_back(MemoriaCorta {
            rol: "usuario".to_string(),
            contenido: usuario.to_string(),
            timestamp: chrono::Utc::now().to_rfc3339(),
        });

        // Limitar memoria
        while self.memoria_corta.len() > self.max_memoria {
            self.memoria_corta.pop_front();
        }

        // Convertir memoria a historial
        let historial: Vec<(&str, &str)> = self.memoria_corta
            .iter()
            .map(|m| (m.rol.as_str(), m.contenido.as_str()))
            .collect();

        // Obtener respuesta
        let respuesta = self.cliente.chat(modelo, &historial)?;

        // Agregar respuesta a memoria
        self.memoria_corta.push_back(MemoriaCorta {
            rol: "asistente".to_string(),
            contenido: respuesta.clone(),
            timestamp: chrono::Utc::now().to_rfc3339(),
        });

        Ok(respuesta)
    }

    /// Limpiar memoria
    pub fn limpiar_memoria(&mut self) -> ResultadoElap<()> {
        self.memoria_corta.clear();
        Ok(())
    }

    /// Obtener historial de memoria
    pub fn obtener_historial(&self) -> Vec<MemoriaCorta> {
        self.memoria_corta.iter().cloned().collect()
    }

    /// Obtener tamaño de memoria
    pub fn tamaño_memoria(&self) -> usize {
        self.memoria_corta.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_manager() {
        let manager = ModelManager::nuevo("http://localhost:11434", 10);
        assert_eq!(manager.tamaño_memoria(), 0);
    }

    #[test]
    fn test_registrar_modelo() {
        let manager = ModelManager::nuevo("http://localhost:11434", 10);
        let metadata = ModelMetadata::nuevo(
            "llama2:7b".to_string(),
            TipoModelo::Chat,
            "Llama 2 7B".to_string(),
            "7B".to_string(),
        );

        assert!(manager.registrar_modelo(metadata).is_ok());
    }

    #[test]
    fn test_set_modelo_activo() {
        let mut manager = ModelManager::nuevo("http://localhost:11434", 10);
        let metadata = ModelMetadata::nuevo(
            "llama2:7b".to_string(),
            TipoModelo::Chat,
            "Test".to_string(),
            "7B".to_string(),
        );

        manager.registrar_modelo(metadata).unwrap();
        assert!(manager.set_modelo_activo("llama2:7b").is_ok());
    }

    #[test]
    fn test_generar_sin_modelo() {
        let manager = ModelManager::nuevo("http://localhost:11434", 10);
        let resultado = manager.generar("test", 0.7);
        assert!(resultado.is_err());
    }

    #[test]
    fn test_embeddings_con_cache() {
        let manager = ModelManager::nuevo("http://localhost:11434", 10);
        let metadata = ModelMetadata::nuevo(
            "all-minilm".to_string(),
            TipoModelo::Embedding,
            "Test".to_string(),
            "22M".to_string(),
        );

        manager.registrar_modelo(metadata).unwrap();
        let mut manager = manager;
        manager.set_modelo_activo("all-minilm").unwrap();

        let resultado1 = manager.embeddings("texto de prueba").unwrap();
        assert_eq!(resultado1.len(), 384);
    }

    #[test]
    fn test_chat_memoria() {
        let mut manager = ModelManager::nuevo("http://localhost:11434", 10);
        let metadata = ModelMetadata::nuevo(
            "llama2:7b".to_string(),
            TipoModelo::Chat,
            "Test".to_string(),
            "7B".to_string(),
        );

        manager.registrar_modelo(metadata).unwrap();
        manager.set_modelo_activo("llama2:7b").unwrap();

        let resultado = manager.chat("Hola");
        assert!(resultado.is_ok());
        assert_eq!(manager.tamaño_memoria(), 2); // usuario + asistente
    }

    #[test]
    fn test_limpiar_memoria() {
        let mut manager = ModelManager::nuevo("http://localhost:11434", 10);
        let metadata = ModelMetadata::nuevo(
            "llama2:7b".to_string(),
            TipoModelo::Chat,
            "Test".to_string(),
            "7B".to_string(),
        );

        manager.registrar_modelo(metadata).unwrap();
        manager.set_modelo_activo("llama2:7b").unwrap();
        manager.chat("test").unwrap();

        assert!(manager.tamaño_memoria() > 0);
        manager.limpiar_memoria().unwrap();
        assert_eq!(manager.tamaño_memoria(), 0);
    }

    #[test]
    fn test_historial() {
        let mut manager = ModelManager::nuevo("http://localhost:11434", 10);
        let metadata = ModelMetadata::nuevo(
            "llama2:7b".to_string(),
            TipoModelo::Chat,
            "Test".to_string(),
            "7B".to_string(),
        );

        manager.registrar_modelo(metadata).unwrap();
        manager.set_modelo_activo("llama2:7b").unwrap();

        manager.chat("msg1").unwrap();
        let historial = manager.obtener_historial();
        assert_eq!(historial.len(), 2); // usuario + asistente
    }
}
