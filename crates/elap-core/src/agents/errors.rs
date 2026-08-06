//! Errores de agentes

/// Error de agente
#[derive(Debug, Clone)]
pub enum AgentError {
    PlanVacio,
    NoHayPasoActual,
    EjecucionFallo(String),
    EstadoInvalido(String),
}

impl std::fmt::Display for AgentError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            AgentError::PlanVacio => write!(f, "Plan sin pasos"),
            AgentError::NoHayPasoActual => write!(f, "No hay paso actual"),
            AgentError::EjecucionFallo(msg) => write!(f, "Ejecución falló: {}", msg),
            AgentError::EstadoInvalido(msg) => write!(f, "Estado inválido: {}", msg),
        }
    }
}

impl std::error::Error for AgentError {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_display() {
        let error = AgentError::PlanVacio;
        assert!(error.to_string().contains("Plan"));
    }
}
