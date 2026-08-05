//! Integración de agentes con Tools y Models

use super::{Agent, Plan, ContextoAgente, EstadoAgente};
use crate::{ModelManager, EjecutorHerramientas, Tool};
use serde_json::{json, Value as JsonValue};
use crate::error::ResultadoElap;

/// Integración completa: Agent + Tools + Models
pub struct AgentIntegrado {
    pub agente: Agent,
    pub plan: Plan,
    pub contexto: ContextoAgente,
    pub model_manager: Option<ModelManager>,
}

impl AgentIntegrado {
    /// Crear nuevo agente integrado
    pub fn nuevo(nombre: String, rol: String, objetivo: String) -> Self {
        Self {
            agente: Agent::nuevo(nombre, rol),
            plan: Plan::nuevo(objetivo.clone()),
            contexto: ContextoAgente::nuevo(objetivo),
            model_manager: None,
        }
    }

    /// Conectar Model Manager
    pub fn con_model_manager(mut self, manager: ModelManager) -> Self {
        self.model_manager = Some(manager);
        self
    }

    /// Agregar paso que usa una herramienta
    pub fn agregar_paso_herramienta(
        &mut self,
        descripcion: String,
        tipo_herramienta: String,
        parametros: JsonValue,
    ) {
        self.plan.agregar_paso(descripcion, tipo_herramienta, parametros);
    }

    /// Ejecutar agente completo (simula ejecución real)
    pub fn ejecutar(&mut self) -> ResultadoElap<JsonValue> {
        self.agente.cambiar_estado(EstadoAgente::Ejecutando);
        self.agente.registrar_accion("Agente integrado iniciando".to_string());

        while !self.plan.completado {
            if let Some(paso) = self.plan.obtener_paso_actual() {
                let paso_clonado = paso.clone();

                self.agente.registrar_accion(format!(
                    "Ejecutando: {}",
                    paso_clonado.descripcion
                ));

                // Simular ejecución (en producción usaría herramientas reales)
                let resultado = json!({
                    "paso": paso_clonado.numero,
                    "herramienta": paso_clonado.tipo_accion,
                    "estado": "completado",
                });

                self.plan.completar_paso_actual(resultado.clone());
                self.contexto.set_variable(
                    format!("paso_{}_resultado", paso_clonado.numero),
                    resultado,
                );
            } else {
                break;
            }
        }

        self.agente.cambiar_estado(EstadoAgente::Reflexionando);
        let reflexion = format!(
            "Plan completado. {} pasos ejecutados.",
            self.plan.paso_actual
        );
        self.agente.registrar_reflexion(reflexion);

        self.agente.cambiar_estado(EstadoAgente::Completado);

        Ok(json!({
            "agente_id": self.agente.id,
            "plan_id": self.plan.id,
            "pasos_completados": self.plan.paso_actual,
            "acciones": self.agente.historial_acciones.len(),
            "reflexiones": self.agente.reflexiones.len(),
        }))
    }

    /// Obtener resumen del agente
    pub fn resumen(&self) -> JsonValue {
        json!({
            "agente": self.agente.resumen(),
            "plan_objetivo": self.plan.objetivo,
            "pasos_totales": self.plan.pasos.len(),
            "pasos_completados": self.plan.paso_actual,
            "progreso": self.plan.progreso(),
            "variables_contexto": self.contexto.variables.len(),
            "restricciones": self.contexto.obtener_restricciones().len(),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_agente_integrado() {
        let agente = AgentIntegrado::nuevo(
            "Analizador".to_string(),
            "Analista".to_string(),
            "Analizar datos".to_string(),
        );

        assert_eq!(agente.agente.nombre, "Analizador");
        assert_eq!(agente.plan.pasos.len(), 0);
    }

    #[test]
    fn test_agregar_pasos() {
        let mut agente = AgentIntegrado::nuevo(
            "Test".to_string(),
            "Test".to_string(),
            "Test".to_string(),
        );

        agente.agregar_paso_herramienta(
            "Paso 1".to_string(),
            "archivo".to_string(),
            json!({"operacion": "leer"}),
        );

        assert_eq!(agente.plan.pasos.len(), 1);
    }

    #[test]
    fn test_ejecutar_agente() {
        let mut agente = AgentIntegrado::nuevo(
            "Test".to_string(),
            "Test".to_string(),
            "Test".to_string(),
        );

        agente.agregar_paso_herramienta(
            "Paso 1".to_string(),
            "herramienta".to_string(),
            json!({}),
        );

        let resultado = agente.ejecutar();
        assert!(resultado.is_ok());
        assert!(agente.plan.completado);
        assert_eq!(agente.agente.estado, EstadoAgente::Completado);
    }

    #[test]
    fn test_resumen() {
        let agente = AgentIntegrado::nuevo(
            "Test".to_string(),
            "Role".to_string(),
            "Objetivo".to_string(),
        );

        let resumen = agente.resumen();
        assert!(resumen["agente"]["nombre"].is_string());
        assert_eq!(resumen["plan_objetivo"], "Objetivo");
    }
}
