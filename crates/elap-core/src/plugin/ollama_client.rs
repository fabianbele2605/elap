//! Ollama Integration - Llamar a modelos locales de Ollama
//!
//! Integración con Ollama en puerto 11434 para enriquecer respuestas
//! de plugins con análisis basado en LLM.

use reqwest::Client;
use serde::{Deserialize, Serialize};
use crate::error::{ElapError, ResultadoElap};

/// Request para Ollama
#[derive(Debug, Serialize)]
pub struct OllamaRequest {
    pub model: String,
    pub prompt: String,
    pub stream: bool,
}

/// Response de Ollama
#[derive(Debug, Deserialize)]
pub struct OllamaResponse {
    pub response: String,
    pub model: String,
    pub done: bool,
}

/// Cliente de Ollama
pub struct OllamaClient {
    base_url: String,
    model: String,
    client: Client,
}

impl OllamaClient {
    /// Crear cliente de Ollama
    pub fn new(model: &str) -> Self {
        Self {
            base_url: "http://localhost:11434".to_string(),
            model: model.to_string(),
            client: Client::new(),
        }
    }

    /// Llamar a Ollama con prompt
    pub async fn generate(&self, prompt: &str) -> ResultadoElap<String> {
        let request = OllamaRequest {
            model: self.model.clone(),
            prompt: prompt.to_string(),
            stream: false,
        };

        match self.client
            .post(format!("{}/api/generate", self.base_url))
            .json(&request)
            .timeout(std::time::Duration::from_secs(30))
            .send()
            .await
        {
            Ok(response) => {
                match response.json::<OllamaResponse>().await {
                    Ok(data) => Ok(data.response.trim().to_string()),
                    Err(e) => Err(ElapError::ValidationError(
                        format!("Error parsing Ollama response: {}", e)
                    )),
                }
            }
            Err(e) => Err(ElapError::IoError {
                context: "Ollama API call".to_string(),
                source: format!("Ollama call failed: {}. Is Ollama running on 11434?", e),
            }),
        }
    }

    /// Generar análisis con Ollama
    pub async fn analyze(&self, data: &str, analysis_type: &str) -> ResultadoElap<String> {
        let prompt = match analysis_type {
            "salary" => format!(
                "Analiza estos datos salariales y proporciona insights: {}\n\
                Responde en español, sé conciso y profesional.",
                data
            ),
            "benefits" => format!(
                "Analiza estos datos de beneficios y proporciona recomendaciones: {}\n\
                Responde en español con cálculos y explicaciones.",
                data
            ),
            "recruitment" => format!(
                "Evalúa este perfil de candidato y proporciona análisis: {}\n\
                Responde en español, incluye fortalezas y áreas de mejora.",
                data
            ),
            "finance" => format!(
                "Analiza estos datos financieros y proporciona insights: {}\n\
                Responde en español con análisis y recomendaciones.",
                data
            ),
            _ => format!("Analiza esto: {}", data),
        };

        self.generate(&prompt).await
    }
}

/// Helper para detectar si Ollama está disponible
pub async fn ollama_available() -> bool {
    let client = Client::new();
    client
        .get("http://localhost:11434/api/tags")
        .timeout(std::time::Duration::from_secs(2))
        .send()
        .await
        .is_ok()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ollama_client_new() {
        let client = OllamaClient::new("glm4:9b");
        assert_eq!(client.model, "glm4:9b");
        assert_eq!(client.base_url, "http://localhost:11434");
    }

    #[tokio::test]
    async fn test_ollama_available_check() {
        // Este test solo verifica que la función se ejecute
        let _ = ollama_available().await;
    }
}
