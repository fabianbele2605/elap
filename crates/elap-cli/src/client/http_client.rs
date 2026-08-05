//! Cliente HTTP para API REST

use anyhow::Result;
use reqwest::Client;
use serde_json::{json, Value};

/// Cliente HTTP para ELAP API
pub struct HttpClient {
    base_url: String,
    client: Client,
    token: Option<String>,
}

impl HttpClient {
    /// Crear nuevo cliente
    pub fn nuevo(base_url: &str, token: Option<String>) -> Self {
        Self {
            base_url: base_url.trim_end_matches('/').to_string(),
            client: Client::new(),
            token,
        }
    }

    /// Agregar headers de autenticación
    fn headers(&self) -> reqwest::header::HeaderMap {
        let mut headers = reqwest::header::HeaderMap::new();
        if let Some(token) = &self.token {
            headers.insert(
                reqwest::header::AUTHORIZATION,
                format!("Bearer {}", token).parse().unwrap(),
            );
        }
        headers
    }

    /// Listar agentes
    pub async fn listar_agentes(&self) -> Result<Value> {
        let url = format!("{}/agents", self.base_url);
        let respuesta = self.client
            .get(&url)
            .headers(self.headers())
            .send()
            .await?
            .json()
            .await?;
        Ok(respuesta)
    }

    /// Obtener agente
    pub async fn obtener_agente(&self, id: &str) -> Result<Value> {
        let url = format!("{}/agents/{}", self.base_url, id);
        let respuesta = self.client
            .get(&url)
            .headers(self.headers())
            .send()
            .await?
            .json()
            .await?;
        Ok(respuesta)
    }

    /// Crear agente
    pub async fn crear_agente(&self, nombre: &str, rol: &str, objetivo: &str) -> Result<Value> {
        let url = format!("{}/agents", self.base_url);
        let body = json!({
            "nombre": nombre,
            "rol": rol,
            "objetivo": objetivo,
        });

        let respuesta = self.client
            .post(&url)
            .headers(self.headers())
            .json(&body)
            .send()
            .await?
            .json()
            .await?;
        Ok(respuesta)
    }

    /// Ejecutar agente
    pub async fn ejecutar_agente(&self, id: &str) -> Result<Value> {
        let url = format!("{}/agents/{}/execute", self.base_url, id);
        let respuesta = self.client
            .post(&url)
            .headers(self.headers())
            .send()
            .await?
            .json()
            .await?;
        Ok(respuesta)
    }

    /// Obtener status
    pub async fn obtener_status(&self, id: &str) -> Result<Value> {
        let url = format!("{}/agents/{}/status", self.base_url, id);
        let respuesta = self.client
            .get(&url)
            .headers(self.headers())
            .send()
            .await?
            .json()
            .await?;
        Ok(respuesta)
    }

    /// Eliminar agente
    pub async fn eliminar_agente(&self, id: &str) -> Result<()> {
        let url = format!("{}/agents/{}", self.base_url, id);
        self.client
            .delete(&url)
            .headers(self.headers())
            .send()
            .await?;
        Ok(())
    }
}
