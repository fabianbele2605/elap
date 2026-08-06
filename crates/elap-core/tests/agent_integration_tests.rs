//! Tests de integración: Agents + Tools + Models

use elap_core::{
    Agent, AgentIntegrado, EstadoAgente, Plan, ContextoAgente,
    SistemaMemoria, EjecutorAgente, RegistroModelos,
};
use serde_json::json;

#[test]
fn test_agente_con_plan_completo() {
    let mut agente = AgentIntegrado::nuevo(
        "TestAgent".to_string(),
        "Tester".to_string(),
        "Completar 3 pasos".to_string(),
    );

    agente.agregar_paso_herramienta(
        "Recopilar datos".to_string(),
        "archivo".to_string(),
        json!({"operacion": "leer"}),
    );
    agente.agregar_paso_herramienta(
        "Procesar datos".to_string(),
        "sistema".to_string(),
        json!({"tipo": "procesamiento"}),
    );
    agente.agregar_paso_herramienta(
        "Guardar resultados".to_string(),
        "archivo".to_string(),
        json!({"operacion": "escribir"}),
    );

    let resultado = agente.ejecutar();
    assert!(resultado.is_ok());
    assert!(agente.plan.completado);
    assert_eq!(agente.plan.pasos.len(), 3);
}

#[test]
fn test_agente_cambios_estado() {
    let mut agente = AgentIntegrado::nuevo(
        "Agent".to_string(),
        "Role".to_string(),
        "Test".to_string(),
    );

    agente.agregar_paso_herramienta(
        "Paso".to_string(),
        "herramienta".to_string(),
        json!({}),
    );

    assert_eq!(agente.agente.estado, EstadoAgente::Inactivo);

    let _ = agente.ejecutar();

    assert_eq!(agente.agente.estado, EstadoAgente::Completado);
}

#[test]
fn test_sistema_memoria_con_agente() {
    let sistema = SistemaMemoria::nuevo(10, 5);

    sistema.registrar_evento(json!({"tipo": "inicio", "agente": "test"}));
    sistema.registrar_evento(json!({"tipo": "paso", "numero": 1}));
    sistema.registrar_evento(json!({"tipo": "resultado", "status": "ok"}));

    assert_eq!(sistema.corto_plazo.contar(), 3);
    assert_eq!(sistema.largo_plazo.contar(), 0);
}

#[test]
fn test_contexto_agente_variables() {
    let mut contexto = ContextoAgente::nuevo("Test objetivo".to_string());

    contexto.set_variable("var1".to_string(), json!({"valor": 1}));
    contexto.set_variable("var2".to_string(), json!({"valor": 2}));

    let var1 = contexto.get_variable("var1");
    assert!(var1.is_some());
}

#[test]
fn test_plan_progreso() {
    let mut plan = Plan::nuevo("Objetivo".to_string());
    plan.agregar_paso("P1".to_string(), "tool".to_string(), json!({}));
    plan.agregar_paso("P2".to_string(), "tool".to_string(), json!({}));
    plan.agregar_paso("P3".to_string(), "tool".to_string(), json!({}));

    assert_eq!(plan.progreso(), 0.0);

    plan.completar_paso_actual(json!({}));
    assert_eq!(plan.progreso(), 1.0 / 3.0);

    plan.completar_paso_actual(json!({}));
    assert_eq!(plan.progreso(), 2.0 / 3.0);

    plan.completar_paso_actual(json!({}));
    assert_eq!(plan.progreso(), 1.0);
}

#[test]
fn test_ejecutor_agente_con_contexto() {
    let mut agente = Agent::nuevo("Test".to_string(), "Rol".to_string());
    let mut plan = Plan::nuevo("Objetivo".to_string());
    let mut contexto = ContextoAgente::nuevo("Objetivo".to_string());

    plan.agregar_paso("Paso 1".to_string(), "tool".to_string(), json!({}));
    plan.agregar_paso("Paso 2".to_string(), "tool".to_string(), json!({}));

    let resultado = EjecutorAgente::ejecutar_plan(&mut agente, &mut plan, &mut contexto);
    assert!(resultado.is_ok());

    let var = contexto.get_variable("resultado_paso_1");
    assert!(var.is_some());
}

#[test]
fn test_agente_resumen() {
    let agente = AgentIntegrado::nuevo(
        "Resumen Agent".to_string(),
        "Analista".to_string(),
        "Analizar datos".to_string(),
    );

    let resumen = agente.resumen();
    assert_eq!(resumen["plan_objetivo"], "Analizar datos");
    assert_eq!(resumen["pasos_totales"], 0);
    assert_eq!(resumen["pasos_completados"], 0);
}

#[test]
fn test_integracion_completa_flujo() {
    let mut agente = AgentIntegrado::nuevo(
        "FlujCompleto".to_string(),
        "Orquestador".to_string(),
        "Ejecutar flujo completo".to_string(),
    );

    let sistema = SistemaMemoria::nuevo(20, 10);

    agente.agregar_paso_herramienta(
        "Inicio del flujo".to_string(),
        "sistema".to_string(),
        json!({"accion": "iniciar"}),
    );

    sistema.registrar_evento(json!({
        "evento": "agente_creado",
        "agente_id": agente.agente.id,
        "timestamp": chrono::Utc::now().to_rfc3339(),
    }));

    let resultado = agente.ejecutar();

    assert!(resultado.is_ok());
    assert_eq!(sistema.corto_plazo.contar(), 1);

    let resumen = agente.resumen();
    assert!(resumen["agente"]["nombre"].is_string());
}

#[test]
fn test_multiples_agentes_independientes() {
    let agente1 = AgentIntegrado::nuevo(
        "Agente1".to_string(),
        "Role1".to_string(),
        "Tarea 1".to_string(),
    );

    let agente2 = AgentIntegrado::nuevo(
        "Agente2".to_string(),
        "Role2".to_string(),
        "Tarea 2".to_string(),
    );

    assert_ne!(agente1.agente.id, agente2.agente.id);
}

#[test]
fn test_historia_acciones() {
    let mut agente = AgentIntegrado::nuevo(
        "Historia".to_string(),
        "Role".to_string(),
        "Test".to_string(),
    );

    agente.agregar_paso_herramienta(
        "Paso 1".to_string(),
        "herramienta".to_string(),
        json!({}),
    );

    assert_eq!(agente.agente.historial_acciones.len(), 0);

    let _ = agente.ejecutar();

    assert!(agente.agente.historial_acciones.len() > 0);
}

#[test]
fn test_reflexiones() {
    let mut agente = Agent::nuevo("Test".to_string(), "Role".to_string());

    agente.registrar_reflexion("Primera reflexión".to_string());
    agente.registrar_reflexion("Segunda reflexión".to_string());

    assert_eq!(agente.reflexiones.len(), 2);
}

#[test]
fn test_registro_modelos_integracion() {
    let registro = RegistroModelos::nuevo();

    let modelo = elap_core::ModelMetadata::nuevo(
        "test-model".to_string(),
        elap_core::TipoModelo::TextoGenerativo,
        "Modelo de prueba".to_string(),
        "{}".to_string(),
    );

    let resultado = registro.registrar(modelo);
    assert!(resultado.is_ok());
    let modelos = registro.listar().expect("Error al listar");
    assert!(modelos.len() > 0);
}
