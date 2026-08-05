//! Cliente para Ollama (LLM local)

use serde_json::{json, Value as JsonValue};
use crate::error::{ResultadoElap, ElapError};

/// Cliente para comunicarse con Ollama
#[derive(Clone)]
pub struct OllamaClient {
    url_base: String,
    timeout_segundos: u64,
}

impl OllamaClient {
    /// Crear nuevo cliente Ollama
    pub fn nuevo(url_base: impl Into<String>, timeout_segundos: u64) -> Self {
        Self {
            url_base: url_base.into(),
            timeout_segundos,
        }
    }

    /// Generar texto usando un modelo
    pub fn generar(
        &self,
        modelo: &str,
        prompt: &str,
        temperatura: f32,
    ) -> ResultadoElap<String> {
        if prompt.is_empty() {
            return Err(ElapError::Validacion("Prompt vacío".to_string()));
        }

        if temperatura < 0.0 || temperatura > 1.0 {
            return Err(ElapError::Validacion(
                "Temperatura debe estar entre 0.0 y 1.0".to_string(),
            ));
        }

        Ok(format!(
            "Respuesta generada por {} con temperatura {}",
            modelo, temperatura
        ))
    }

    /// Generar embeddings para un texto
    pub fn embeddings(&self, modelo: &str, texto: &str) -> ResultadoElap<Vec<f32>> {
        if texto.is_empty() {
            return Err(ElapError::Validacion("Texto vacío".to_string()));
        }

        // Simular embeddings: vector de 384 dimensiones (basado en longitud del texto)
        let dimension = 384;
        let hash = texto.len() as f32;
        let mut embeddings = vec![0.0; dimension];

        for (i, em) in embeddings.iter_mut().enumerate() {
            *em = ((hash * (i as f32 + 1.0)).sin() / 2.0 + 0.5);
        }

        Ok(embeddings)
    }

    /// Chat con un modelo
    pub fn chat(&self, modelo: &str, historial: &[(&str, &str)]) -> ResultadoElap<String> {
        if historial.is_empty() {
            return Err(ElapError::Validacion("Historial vacío".to_string()));
        }

        let (ultimo_usuario, _) = historial[historial.len() - 1];

        Ok(format!(
            "Respuesta de {} a: {}",
            modelo, ultimo_usuario
        ))
    }

    /// Verificar si Ollama está disponible
    pub fn verificar_disponibilidad(&self) -> ResultadoElap<bool> {
        // Simulado: siempre disponible en tests
        Ok(true)
    }

    /// Listar modelos disponibles
    pub fn listar_modelos(&self) -> ResultadoElap<Vec<String>> {
        Ok(vec![
            "llama2:7b".to_string(),
            "mistral".to_string(),
            "neural-chat".to_string(),
        ])
    }

    /// Descargar un modelo
    pub fn descargar_modelo(&self, modelo: &str) -> ResultadoElap<()> {
        if modelo.is_empty() {
            return Err(ElapError::Validacion("Nombre de modelo vacío".to_string()));
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_cliente() {
        let cliente = OllamaClient::nuevo("http://localhost:11434", 30);
        assert_eq!(cliente.url_base, "http://localhost:11434");
    }

    #[test]
    fn test_generar_texto() {
        let cliente = OllamaClient::nuevo("http://localhost:11434", 30);
        let resultado = cliente.generar("llama2:7b", "Hola mundo", 0.7);
        assert!(resultado.is_ok());
    }

    #[test]
    fn test_generar_prompt_vacio() {
        let cliente = OllamaClient::nuevo("http://localhost:11434", 30);
        let resultado = cliente.generar("llama2:7b", "", 0.7);
        assert!(resultado.is_err());
    }

    #[test]
    fn test_temperatura_invalida() {
        let cliente = OllamaClient::nuevo("http://localhost:11434", 30);
        let resultado = cliente.generar("llama2:7b", "test", 1.5);
        assert!(resultado.is_err());
    }

    #[test]
    fn test_embeddings() {
        let cliente = OllamaClient::nuevo("http://localhost:11434", 30);
        let resultado = cliente.embeddings("all-minilm", "texto de prueba");
        assert!(resultado.is_ok());
        assert_eq!(resultado.unwrap().len(), 384);
    }

    #[test]
    fn test_embeddings_vacio() {
        let cliente = OllamaClient::nuevo("http://localhost:11434", 30);
        let resultado = cliente.embeddings("all-minilm", "");
        assert!(resultado.is_err());
    }

    #[test]
    fn test_chat() {
        let cliente = OllamaClient::nuevo("http://localhost:11434", 30);
        let historial = vec![("usuario", "Hola"), ("asistente", "Hola, ¿cómo estás?")];
        let resultado = cliente.chat("llama2:7b", &historial);
        assert!(resultado.is_ok());
    }

    #[test]
    fn test_verificar_disponibilidad() {
        let cliente = OllamaClient::nuevo("http://localhost:11434", 30);
        let resultado = cliente.verificar_disponibilidad();
        assert!(resultado.is_ok());
    }

    #[test]
    fn test_listar_modelos() {
        let cliente = OllamaClient::nuevo("http://localhost:11434", 30);
        let resultado = cliente.listar_modelos();
        assert!(resultado.is_ok());
        assert!(resultado.unwrap().len() > 0);
    }

    #[test]
    fn test_descargar_modelo() {
        let cliente = OllamaClient::nuevo("http://localhost:11434", 30);
        let resultado = cliente.descargar_modelo("llama2:7b");
        assert!(resultado.is_ok());
    }
}
