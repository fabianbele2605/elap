//! Orquestador de múltiples agentes - Fase 24

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use crate::error::ResultadoElap;

/// Tipos de agentes disponibles
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum TipoAgente {
    Sales,
    HR,
    Accounting,
    IT,
    Legal,
    Support,
    Analytics,
    Custom(String),
}

impl TipoAgente {
    /// Obtener descripción del tipo de agente
    pub fn descripcion(&self) -> &str {
        match self {
            TipoAgente::Sales => "Agente de ventas - negocios, productos, clientes",
            TipoAgente::HR => "Agente de RRHH - empleados, nómina, políticas",
            TipoAgente::Accounting => "Agente contable - finanzas, presupuesto, reportes",
            TipoAgente::IT => "Agente de IT - sistemas, infraestructura, soporte",
            TipoAgente::Legal => "Agente legal - contratos, cumplimiento, riesgos",
            TipoAgente::Support => "Agente de soporte - clientes, tickets, problemas",
            TipoAgente::Analytics => "Agente de analytics - datos, reportes, KPIs",
            TipoAgente::Custom(nombre) => nombre,
        }
    }
}

/// Información de un agente registrado
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InfoAgente {
    pub id: String,
    pub nombre: String,
    pub tipo: TipoAgente,
    pub objetivo: String,
    pub disponible: bool,
}

/// Solicitud de delegación a otro agente
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SolicitudDelegacion {
    pub agente_origen: String,
    pub agente_destino: String,
    pub tarea: String,
    pub contexto: String,
}

/// Respuesta de delegación
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RespuestaDelegacion {
    pub exitoso: bool,
    pub resultado: String,
    pub agente_que_respondio: String,
}

/// Orquestador central de agentes
pub struct AgentOrchestrator {
    /// Registro de agentes disponibles
    agentes: HashMap<String, InfoAgente>,

    /// Historial de delegaciones
    historial_delegaciones: Vec<SolicitudDelegacion>,
}

impl AgentOrchestrator {
    /// Crear nuevo orquestador
    pub fn nuevo() -> Self {
        Self {
            agentes: HashMap::new(),
            historial_delegaciones: Vec::new(),
        }
    }

    /// Registrar un agente en el orquestador
    pub fn registrar_agente(&mut self, agente: InfoAgente) -> ResultadoElap<()> {
        if self.agentes.contains_key(&agente.id) {
            return Err(crate::error::ElapError::Config(
                format!("Agente {} ya está registrado", agente.id),
            ));
        }
        self.agentes.insert(agente.id.clone(), agente);
        Ok(())
    }

    /// Obtener todos los agentes disponibles
    pub fn listar_agentes_disponibles(&self) -> Vec<InfoAgente> {
        self.agentes
            .values()
            .filter(|a| a.disponible)
            .cloned()
            .collect()
    }

    /// Encontrar mejor agente para una tarea basado en tipo
    pub fn encontrar_mejor_agente(&self, tipo_requerido: &TipoAgente) -> Option<InfoAgente> {
        self.agentes
            .values()
            .find(|a| a.tipo == *tipo_requerido && a.disponible)
            .cloned()
    }

    /// Sugerir agentes para una tarea basado en palabras clave
    pub fn sugerir_agentes_para_tarea(&self, tarea: &str) -> Vec<InfoAgente> {
        let palabras_clave = tarea.to_lowercase();

        let mut sugerencias = Vec::new();

        // Mapeo de palabras clave a tipos de agentes
        if palabras_clave.contains("venta") || palabras_clave.contains("cliente") {
            if let Some(agente) = self.encontrar_mejor_agente(&TipoAgente::Sales) {
                sugerencias.push(agente);
            }
        }

        if palabras_clave.contains("empleado")
            || palabras_clave.contains("nómina")
            || palabras_clave.contains("rrhh") {
            if let Some(agente) = self.encontrar_mejor_agente(&TipoAgente::HR) {
                sugerencias.push(agente);
            }
        }

        if palabras_clave.contains("presupuesto")
            || palabras_clave.contains("finanza")
            || palabras_clave.contains("contable") {
            if let Some(agente) = self.encontrar_mejor_agente(&TipoAgente::Accounting) {
                sugerencias.push(agente);
            }
        }

        if palabras_clave.contains("sistema")
            || palabras_clave.contains("infraestructura")
            || palabras_clave.contains("it") {
            if let Some(agente) = self.encontrar_mejor_agente(&TipoAgente::IT) {
                sugerencias.push(agente);
            }
        }

        if palabras_clave.contains("dato") || palabras_clave.contains("análisis") {
            if let Some(agente) = self.encontrar_mejor_agente(&TipoAgente::Analytics) {
                sugerencias.push(agente);
            }
        }

        sugerencias
    }

    /// Registrar una delegación en el historial
    pub fn registrar_delegacion(&mut self, solicitud: SolicitudDelegacion) {
        self.historial_delegaciones.push(solicitud);
    }

    /// Obtener historial de delegaciones
    pub fn obtener_historial_delegaciones(&self) -> &[SolicitudDelegacion] {
        &self.historial_delegaciones
    }

    /// Cambiar disponibilidad de un agente
    pub fn establecer_disponibilidad(
        &mut self,
        agente_id: &str,
        disponible: bool,
    ) -> ResultadoElap<()> {
        match self.agentes.get_mut(agente_id) {
            Some(agente) => {
                agente.disponible = disponible;
                Ok(())
            }
            None => Err(crate::error::ElapError::Config(
                format!("Agente {} no encontrado", agente_id),
            )),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_registrar_agente() {
        let mut orchestrator = AgentOrchestrator::nuevo();
        let agente = InfoAgente {
            id: "agent_1".to_string(),
            nombre: "Sales Agent".to_string(),
            tipo: TipoAgente::Sales,
            objetivo: "Vender".to_string(),
            disponible: true,
        };

        assert!(orchestrator.registrar_agente(agente.clone()).is_ok());
        assert_eq!(orchestrator.listar_agentes_disponibles().len(), 1);
    }

    #[test]
    fn test_sugerir_agentes_para_tarea() {
        let mut orchestrator = AgentOrchestrator::nuevo();

        let sales = InfoAgente {
            id: "sales_1".to_string(),
            nombre: "Sales Agent".to_string(),
            tipo: TipoAgente::Sales,
            objetivo: "Vender".to_string(),
            disponible: true,
        };

        let accounting = InfoAgente {
            id: "acc_1".to_string(),
            nombre: "Accounting Agent".to_string(),
            tipo: TipoAgente::Accounting,
            objetivo: "Finanzas".to_string(),
            disponible: true,
        };

        orchestrator.registrar_agente(sales).unwrap();
        orchestrator.registrar_agente(accounting).unwrap();

        let sugerencias = orchestrator.sugerir_agentes_para_tarea("¿Cuál es el presupuesto?");
        assert!(sugerencias.len() >= 1);
    }

    #[test]
    fn test_encontrar_mejor_agente() {
        let mut orchestrator = AgentOrchestrator::nuevo();
        let agente = InfoAgente {
            id: "hr_1".to_string(),
            nombre: "HR Agent".to_string(),
            tipo: TipoAgente::HR,
            objetivo: "RRHH".to_string(),
            disponible: true,
        };

        orchestrator.registrar_agente(agente).unwrap();
        let encontrado = orchestrator.encontrar_mejor_agente(&TipoAgente::HR);
        assert!(encontrado.is_some());
    }

    #[test]
    fn test_registrar_delegacion() {
        let mut orchestrator = AgentOrchestrator::nuevo();

        let delegacion = SolicitudDelegacion {
            agente_origen: "agent_1".to_string(),
            agente_destino: "agent_2".to_string(),
            tarea: "Procesar presupuesto".to_string(),
            contexto: "Q3 marketing".to_string(),
        };

        orchestrator.registrar_delegacion(delegacion);
        assert_eq!(orchestrator.obtener_historial_delegaciones().len(), 1);
    }
}
