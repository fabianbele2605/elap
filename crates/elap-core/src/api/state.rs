//! Estado compartido de la aplicación

use std::sync::Arc;
use std::collections::HashMap;
use tokio::sync::RwLock;
use crate::AgentIntegrado;

/// Estado de la aplicación
#[derive(Clone)]
pub struct AppState {
    /// Almacén de agentes
    pub agentes: Arc<RwLock<HashMap<String, AgentIntegrado>>>,
}

impl AppState {
    /// Crear nuevo estado
    pub fn nuevo() -> Self {
        Self {
            agentes: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Guardar agente
    pub async fn guardar_agente(&self, id: String, agente: AgentIntegrado) {
        let mut agentes = self.agentes.write().await;
        agentes.insert(id, agente);
    }

    /// Obtener agente
    pub async fn obtener_agente(&self, id: &str) -> Option<AgentIntegrado> {
        let agentes = self.agentes.read().await;
        agentes.get(id).cloned()
    }

    /// Listar todos los agentes
    pub async fn listar_agentes(&self) -> Vec<(String, String, String)> {
        let agentes = self.agentes.read().await;
        agentes
            .iter()
            .map(|(id, agente)| (id.clone(), agente.agente.nombre.clone(), agente.agente.rol.clone()))
            .collect()
    }

    /// Eliminar agente
    pub async fn eliminar_agente(&self, id: &str) {
        let mut agentes = self.agentes.write().await;
        agentes.remove(id);
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_guardar_obtener_agente() {
        let state = AppState::nuevo();
        let agente = AgentIntegrado::nuevo(
            "Test".to_string(),
            "Role".to_string(),
            "Objetivo".to_string(),
        );

        state.guardar_agente("id1".to_string(), agente.clone()).await;
        let obtenido = state.obtener_agente("id1").await;

        assert!(obtenido.is_some());
    }

    #[tokio::test]
    async fn test_listar_agentes() {
        let state = AppState::nuevo();
        let agente = AgentIntegrado::nuevo(
            "Test".to_string(),
            "Role".to_string(),
            "Objetivo".to_string(),
        );

        state.guardar_agente("id1".to_string(), agente).await;
        let lista = state.listar_agentes().await;

        assert_eq!(lista.len(), 1);
        assert_eq!(lista[0].2, "Role"); // Verificar que devuelve el rol
    }
}
