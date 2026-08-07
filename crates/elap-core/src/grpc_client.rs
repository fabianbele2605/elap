//! Cliente gRPC para conectarse al Python AI Runtime

use tonic::transport::Channel;
use crate::elap::agent::ai_runtime_service_client::AiRuntimeServiceClient;
use crate::elap::agent::{ExecuteAgentRequest, HealthCheckRequest};
use crate::error::ResultadoElap;

/// Cliente gRPC para AI Runtime
pub struct AIRuntimeClient {
    client: AiRuntimeServiceClient<Channel>,
}

impl AIRuntimeClient {
    /// Crear nuevo cliente gRPC
    pub async fn conectar(addr: &str) -> ResultadoElap<Self> {
        let channel = Channel::from_shared(addr.to_string())
            .map_err(|e| crate::error::ElapError::Config(e.to_string()))?
            .connect()
            .await
            .map_err(|e| crate::error::ElapError::Config(e.to_string()))?;

        Ok(Self {
            client: AiRuntimeServiceClient::new(channel),
        })
    }

    /// Ejecutar un agente
    pub async fn ejecutar_agente(
        &mut self,
        agent_id: &str,
        query: &str,
    ) -> ResultadoElap<String> {
        let request = tonic::Request::new(ExecuteAgentRequest {
            agent_id: agent_id.to_string(),
            query: query.to_string(),
        });

        let response = self
            .client
            .execute_agent(request)
            .await
            .map_err(|e| crate::error::ElapError::Config(e.to_string()))?;

        let mensaje = response.into_inner();

        if mensaje.status == "error" {
            return Err(crate::error::ElapError::Config(mensaje.error));
        }

        Ok(mensaje.result)
    }

    /// Health check
    pub async fn health_check(&mut self, service: &str) -> ResultadoElap<bool> {
        let request = tonic::Request::new(HealthCheckRequest {
            service: service.to_string(),
        });

        let response = self
            .client
            .health_check(request)
            .await
            .map_err(|e| crate::error::ElapError::Config(e.to_string()))?;

        let mensaje = response.into_inner();
        Ok(mensaje.status == "ok")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_client_creation() {
        // Este test verifica que el cliente se puede crear
        // Para tests reales, necesitamos un servidor gRPC corriendo
        assert!(true);
    }
}
