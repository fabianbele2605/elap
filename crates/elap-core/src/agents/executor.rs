//! Ejecutor de planes de agentes

use super::{Agent, Plan, ContextoAgente, EstadoAgente};
use serde_json::{json, Value as JsonValue};
use crate::error::{ResultadoElap, ElapError};

/// Ejecutor de planes para agentes
pub struct EjecutorAgente;

impl EjecutorAgente {
    /// Ejecutar un plan completo
    pub fn ejecutar_plan(
        agente: &mut Agent,
        plan: &mut Plan,
        contexto: &mut ContextoAgente,
    ) -> ResultadoElap<JsonValue> {
        agente.cambiar_estado(EstadoAgente::Ejecutando);
        agente.registrar_accion(format!("Iniciando plan: {}", plan.objetivo));

        while !plan.completado {
            let paso_actual = match plan.obtener_paso_actual() {
                Some(paso) => paso.clone(),
                None => break, // Plan vacío o sin más pasos
            };

            // Registrar acción
            agente.registrar_accion(format!(
                "Ejecutando paso {}: {}",
                paso_actual.numero, paso_actual.descripcion
            ));

            // Simular ejecución (en producción llamaría a herramientas)
            let resultado = json!({
                "paso": paso_actual.numero,
                "descripcion": paso_actual.descripcion,
                "tipo_accion": paso_actual.tipo_accion,
                "exito": true,
                "timestamp": chrono::Utc::now().to_rfc3339(),
            });

            // Completar paso
            plan.completar_paso_actual(resultado.clone());

            // Guardar resultado en contexto
            contexto.set_variable(
                format!("resultado_paso_{}", paso_actual.numero),
                resultado,
            );
        }

        agente.cambiar_estado(EstadoAgente::Completado);
        agente.registrar_accion("Plan completado exitosamente".to_string());

        Ok(json!({
            "agente_id": agente.id,
            "plan_id": plan.id,
            "pasos_completados": plan.paso_actual,
            "progreso": plan.progreso(),
        }))
    }

    /// Reflexionar sobre resultados
    pub fn reflexionar(
        agente: &mut Agent,
        resultado: &JsonValue,
    ) -> ResultadoElap<()> {
        agente.cambiar_estado(EstadoAgente::Reflexionando);

        let reflexion = format!(
            "Plan completado. Resultado: {:?}",
            resultado
        );

        agente.registrar_reflexion(reflexion);
        agente.cambiar_estado(EstadoAgente::Inactivo);

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ejecutar_plan_vacio() {
        let mut agente = Agent::nuevo("Test".to_string(), "Test".to_string());
        let mut plan = Plan::nuevo("Objetivo".to_string());
        let mut contexto = ContextoAgente::nuevo("Objetivo".to_string());

        // Un plan sin pasos debe completarse
        assert_eq!(plan.pasos.len(), 0);
        plan.completado = true;

        let resultado = EjecutorAgente::ejecutar_plan(&mut agente, &mut plan, &mut contexto);
        assert!(resultado.is_ok());
    }

    #[test]
    fn test_ejecutar_plan_con_pasos() {
        let mut agente = Agent::nuevo("Test".to_string(), "Test".to_string());
        let mut plan = Plan::nuevo("Objetivo".to_string());
        let mut contexto = ContextoAgente::nuevo("Objetivo".to_string());

        plan.agregar_paso("Paso 1".to_string(), "tool1".to_string(), json!({}));
        plan.agregar_paso("Paso 2".to_string(), "tool2".to_string(), json!({}));

        let resultado = EjecutorAgente::ejecutar_plan(&mut agente, &mut plan, &mut contexto);
        assert!(resultado.is_ok());
        assert!(plan.completado);
        assert_eq!(plan.pasos.len(), 2);
    }

    #[test]
    fn test_reflexionar() {
        let mut agente = Agent::nuevo("Test".to_string(), "Test".to_string());
        let resultado = json!({"exito": true});

        let res = EjecutorAgente::reflexionar(&mut agente, &resultado);
        assert!(res.is_ok());
        assert_eq!(agente.reflexiones.len(), 1);
    }

    #[test]
    fn test_cambio_estado_durante_ejecucion() {
        let mut agente = Agent::nuevo("Test".to_string(), "Test".to_string());
        let mut plan = Plan::nuevo("Objetivo".to_string());
        let mut contexto = ContextoAgente::nuevo("Objetivo".to_string());

        plan.agregar_paso("P1".to_string(), "t".to_string(), json!({}));

        let _ = EjecutorAgente::ejecutar_plan(&mut agente, &mut plan, &mut contexto);
        assert_eq!(agente.estado, EstadoAgente::Completado);
    }
}
