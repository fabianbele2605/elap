//! Plugin Orchestrator - Fase 6: Multi-Agent Plugin Runtime
//!
//! Coordinador centralizado para agentes especializados y plugins dinámicos.
//! Cada agente/plugin tiene responsabilidades claras, tools específicas, y RAG dedicado.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use crate::error::{ElapError, ResultadoElap};
use crate::tools::ToolMetadata;

/// Intent detectado en una query de usuario
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum Intent {
    /// Generar documentos (contratos, políticas)
    DocumentGeneration,
    /// Análisis de nómina y salarios
    PayrollAnalysis,
    /// Gestión de beneficios
    BenefitsManagement,
    /// Procesos de hiring
    Recruitment,
    /// Consulta general
    General,
}

/// Información de salud de un plugin
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginHealthStatus {
    pub name: String,
    pub health_score: f32,  // 0.0 - 1.0
    pub error_count: u32,
    pub success_count: u32,
    pub is_healthy: bool,
}

/// Configuración de un plugin especializado
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginConfig {
    pub id: String,
    pub name: String,
    pub version: String,
    pub description: String,
    pub enabled: bool,
    pub timeout_ms: u64,
    pub max_retries: u32,
}

/// Metadata de colección RAG
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RAGCollection {
    pub name: String,
    pub description: String,
    pub document_count: usize,
    pub indexed: bool,
}

/// Configuración de un agente especializado
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpecializedAgent {
    pub id: String,
    pub name: String,
    pub role: String,
    pub description: String,
    pub tools: Vec<ToolMetadata>,
    pub rag_collections: Vec<RAGCollection>,
    pub health: PluginHealthStatus,
    pub enabled: bool,
}

/// Solicitud de ejecución para un plugin/agente
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionRequest {
    pub query: String,
    pub context: Option<String>,
    pub user_id: Option<String>,
    pub request_id: Option<String>,
}

/// Respuesta de ejecución
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionResponse {
    pub success: bool,
    pub agent_id: String,
    pub result: String,
    pub execution_time_ms: u64,
    pub tools_used: Vec<String>,
    pub rag_sources: Vec<String>,
}

/// Plugin Orchestrator - Coordinador central
pub struct PluginOrchestrator {
    /// Agentes especializados registrados
    agents: HashMap<String, SpecializedAgent>,

    /// Plugins dinámicos cargados
    plugins: HashMap<String, PluginConfig>,

    /// Health monitoring de cada plugin
    health_status: HashMap<String, PluginHealthStatus>,

    /// Mapeo de intent a agente
    intent_routing: HashMap<Intent, String>,

    /// Historial de ejecuciones
    execution_history: Vec<ExecutionResponse>,
}

impl PluginOrchestrator {
    /// Crear nuevo orchestrator
    pub fn new() -> Self {
        let mut orchestrator = Self {
            agents: HashMap::new(),
            plugins: HashMap::new(),
            health_status: HashMap::new(),
            intent_routing: HashMap::new(),
            execution_history: Vec::new(),
        };

        // Configurar routing por defecto
        orchestrator.intent_routing.insert(
            Intent::DocumentGeneration,
            "hr_agent".to_string(),
        );
        orchestrator.intent_routing.insert(
            Intent::PayrollAnalysis,
            "payroll_plugin".to_string(),
        );
        orchestrator.intent_routing.insert(
            Intent::BenefitsManagement,
            "benefits_plugin".to_string(),
        );
        orchestrator.intent_routing.insert(
            Intent::Recruitment,
            "recruitment_plugin".to_string(),
        );

        orchestrator
    }

    /// Registrar agente especializado
    pub fn register_agent(&mut self, agent: SpecializedAgent) -> ResultadoElap<()> {
        if self.agents.contains_key(&agent.id) {
            return Err(ElapError::Conflict(
                format!("Agent {} ya está registrado", agent.id),
            ));
        }

        let agent_id = agent.id.clone();
        let health = agent.health.clone();
        self.agents.insert(agent_id.clone(), agent);
        self.health_status.insert(agent_id, health);

        Ok(())
    }

    /// Registrar plugin dinámico
    pub fn register_plugin(&mut self, plugin: PluginConfig) -> ResultadoElap<()> {
        if self.plugins.contains_key(&plugin.id) {
            return Err(ElapError::Conflict(
                format!("Plugin {} ya está registrado", plugin.id),
            ));
        }

        let plugin_id = plugin.id.clone();
        let plugin_name = plugin.name.clone();

        let health = PluginHealthStatus {
            name: plugin_name,
            health_score: 1.0,
            error_count: 0,
            success_count: 0,
            is_healthy: true,
        };

        self.plugins.insert(plugin_id.clone(), plugin);
        self.health_status.insert(plugin_id, health);

        Ok(())
    }

    /// Detectar intent de una query
    pub fn detect_intent(&self, query: &str) -> Intent {
        let query_lower = query.to_lowercase();

        // Keywords para detección de intent
        if query_lower.contains("contrato")
            || query_lower.contains("política")
            || query_lower.contains("documento")
            || query_lower.contains("generar")
        {
            return Intent::DocumentGeneration;
        }

        if query_lower.contains("salario")
            || query_lower.contains("nómina")
            || query_lower.contains("salarios")
            || query_lower.contains("promedio")
            || query_lower.contains("impuesto")
        {
            return Intent::PayrollAnalysis;
        }

        if query_lower.contains("beneficio")
            || query_lower.contains("seguro")
            || query_lower.contains("pensión")
            || query_lower.contains("eps")
        {
            return Intent::BenefitsManagement;
        }

        if query_lower.contains("contratar")
            || query_lower.contains("cv")
            || query_lower.contains("candidato")
            || query_lower.contains("trabajo")
        {
            return Intent::Recruitment;
        }

        Intent::General
    }

    /// Obtener agente/plugin para un intent
    pub fn route_to_agent(&self, intent: Intent) -> ResultadoElap<String> {
        match self.intent_routing.get(&intent) {
            Some(agent_id) => {
                if self.agents.contains_key(agent_id) || self.plugins.contains_key(agent_id) {
                    Ok(agent_id.clone())
                } else {
                    Err(ElapError::AgentNotFound(
                        format!("Agente/Plugin {} no encontrado", agent_id),
                    ))
                }
            }
            None => Err(ElapError::NotFound(
                "No hay agente disponible para este intent".to_string(),
            )),
        }
    }

    /// Ejecutar query contra agente/plugin
    pub async fn execute(
        &mut self,
        request: ExecutionRequest,
    ) -> ResultadoElap<ExecutionResponse> {
        let intent = self.detect_intent(&request.query);
        let agent_id = self.route_to_agent(intent)?;

        // Verificar salud del agente
        if let Some(health) = self.health_status.get(&agent_id) {
            if !health.is_healthy {
                return Err(ElapError::ServiceUnavailable(
                    format!("Agente {} no está saludable", agent_id),
                ));
            }
        }

        // Simular ejecución (en producción, llamaría al agente/plugin real)
        let response = ExecutionResponse {
            success: true,
            agent_id: agent_id.clone(),
            result: format!("Procesado por {}", agent_id),
            execution_time_ms: 100,
            tools_used: vec![],
            rag_sources: vec![],
        };

        self.execution_history.push(response.clone());
        Ok(response)
    }

    /// Obtener agentes disponibles
    pub fn list_agents(&self) -> Vec<&SpecializedAgent> {
        self.agents.values().filter(|a| a.enabled).collect()
    }

    /// Obtener plugins disponibles
    pub fn list_plugins(&self) -> Vec<&PluginConfig> {
        self.plugins.values().filter(|p| p.enabled).collect()
    }

    /// Obtener health status de todos los agentes/plugins
    pub fn get_health_status(&self) -> Vec<PluginHealthStatus> {
        self.health_status.values().cloned().collect()
    }

    /// Actualizar health status
    pub fn update_health(&mut self, agent_id: &str, success: bool) {
        if let Some(health) = self.health_status.get_mut(agent_id) {
            if success {
                health.success_count += 1;
            } else {
                health.error_count += 1;
            }

            // Recalcular score: success_rate sobre último 100 eventos
            let total = health.success_count + health.error_count;
            if total > 0 {
                health.health_score = health.success_count as f32 / total as f32;
                health.is_healthy = health.health_score > 0.7;
            }
        }
    }

    /// Obtener historial de ejecuciones
    pub fn get_execution_history(&self, limit: usize) -> Vec<ExecutionResponse> {
        self.execution_history
            .iter()
            .rev()
            .take(limit)
            .cloned()
            .collect()
    }
}

impl Default for PluginOrchestrator {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_orchestrator() {
        let orchestrator = PluginOrchestrator::new();
        assert_eq!(orchestrator.list_agents().len(), 0);
        assert_eq!(orchestrator.list_plugins().len(), 0);
    }

    #[test]
    fn test_register_agent() {
        let mut orchestrator = PluginOrchestrator::new();
        let agent = SpecializedAgent {
            id: "hr_agent".to_string(),
            name: "HR Agent".to_string(),
            role: "Documentos laborales".to_string(),
            description: "Genera contratos y políticas".to_string(),
            tools: vec![],
            rag_collections: vec![],
            health: PluginHealthStatus {
                name: "HR Agent".to_string(),
                health_score: 1.0,
                error_count: 0,
                success_count: 0,
                is_healthy: true,
            },
            enabled: true,
        };

        assert!(orchestrator.register_agent(agent).is_ok());
        assert_eq!(orchestrator.list_agents().len(), 1);
    }

    #[test]
    fn test_detect_intent_document() {
        let orchestrator = PluginOrchestrator::new();
        assert_eq!(
            orchestrator.detect_intent("¿Cómo genero un contrato?"),
            Intent::DocumentGeneration
        );
    }

    #[test]
    fn test_detect_intent_payroll() {
        let orchestrator = PluginOrchestrator::new();
        assert_eq!(
            orchestrator.detect_intent("¿Cuál es el salario promedio?"),
            Intent::PayrollAnalysis
        );
    }

    #[test]
    fn test_detect_intent_benefits() {
        let orchestrator = PluginOrchestrator::new();
        assert_eq!(
            orchestrator.detect_intent("Información de beneficios"),
            Intent::BenefitsManagement
        );
    }

    #[test]
    fn test_routing() {
        let mut orchestrator = PluginOrchestrator::new();

        // Registrar agente HR
        let agent = SpecializedAgent {
            id: "hr_agent".to_string(),
            name: "HR Agent".to_string(),
            role: "Test".to_string(),
            description: "Test".to_string(),
            tools: vec![],
            rag_collections: vec![],
            health: PluginHealthStatus {
                name: "HR Agent".to_string(),
                health_score: 1.0,
                error_count: 0,
                success_count: 0,
                is_healthy: true,
            },
            enabled: true,
        };

        orchestrator.register_agent(agent).unwrap();

        let result = orchestrator.route_to_agent(Intent::DocumentGeneration);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), "hr_agent");
    }

    #[test]
    fn test_health_update() {
        let mut orchestrator = PluginOrchestrator::new();
        let agent = SpecializedAgent {
            id: "test_agent".to_string(),
            name: "Test".to_string(),
            role: "Test".to_string(),
            description: "Test".to_string(),
            tools: vec![],
            rag_collections: vec![],
            health: PluginHealthStatus {
                name: "Test".to_string(),
                health_score: 1.0,
                error_count: 0,
                success_count: 0,
                is_healthy: true,
            },
            enabled: true,
        };

        orchestrator.register_agent(agent).unwrap();

        orchestrator.update_health("test_agent", true);
        let health = orchestrator
            .health_status
            .get("test_agent")
            .unwrap();
        assert_eq!(health.success_count, 1);
    }

    #[tokio::test]
    async fn test_execute() {
        let mut orchestrator = PluginOrchestrator::new();
        let agent = SpecializedAgent {
            id: "hr_agent".to_string(),
            name: "HR Agent".to_string(),
            role: "Test".to_string(),
            description: "Test".to_string(),
            tools: vec![],
            rag_collections: vec![],
            health: PluginHealthStatus {
                name: "HR Agent".to_string(),
                health_score: 1.0,
                error_count: 0,
                success_count: 0,
                is_healthy: true,
            },
            enabled: true,
        };

        orchestrator.register_agent(agent).unwrap();

        let request = ExecutionRequest {
            query: "Generar contrato".to_string(),
            context: None,
            user_id: None,
            request_id: None,
        };

        let response = orchestrator.execute(request).await;
        assert!(response.is_ok());
        assert_eq!(response.unwrap().agent_id, "hr_agent");
    }

    #[test]
    fn test_execution_history() {
        let orchestrator = PluginOrchestrator::new();
        let history = orchestrator.get_execution_history(10);
        assert_eq!(history.len(), 0);
    }
}
