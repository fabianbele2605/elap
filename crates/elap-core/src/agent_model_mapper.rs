//! Mapeo automático de roles de agentes a modelos de IA

/// Obtener el modelo de IA recomendado para un rol de agente
pub fn rol_to_modelo(rol: &str) -> String {
    match rol.to_lowercase().as_str() {
        // Sales, Support, HR, Legal → glm4:9b (conversación general)
        "sales" | "vendedor" | "support" | "soporte" | "hr" | "recursos humanos" | "legal" => {
            "glm4:9b".to_string()
        }
        // IT, Accounting → qwen2.5-coder:7b (lógica, código)
        "it" | "informática" | "accounting" | "contabilidad" | "finance" | "finanzas" => {
            "qwen2.5-coder:7b".to_string()
        }
        // Analytics, Custom → qwen3:8b (razonamiento)
        "analytics" | "análisis" | "custom" | "personalizado" => {
            "qwen3:8b".to_string()
        }
        // Default
        _ => "glm4:9b".to_string(),
    }
}

/// Obtener descripción legible del mapeo
pub fn get_role_model_info(rol: &str) -> (String, String) {
    let modelo = rol_to_modelo(rol);
    let descripcion = match modelo.as_str() {
        "glm4:9b" => "Conversación general y atención al cliente",
        "qwen2.5-coder:7b" => "Lógica, análisis y procesamiento de código",
        "qwen3:8b" => "Razonamiento avanzado y análisis",
        _ => "Modelo general",
    };
    (modelo, descripcion.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sales_rol() {
        assert_eq!(rol_to_modelo("Sales"), "glm4:9b");
        assert_eq!(rol_to_modelo("Vendedor"), "glm4:9b");
    }

    #[test]
    fn test_it_rol() {
        assert_eq!(rol_to_modelo("IT"), "qwen2.5-coder:7b");
        assert_eq!(rol_to_modelo("Accounting"), "qwen2.5-coder:7b");
    }

    #[test]
    fn test_analytics_rol() {
        assert_eq!(rol_to_modelo("Analytics"), "qwen3:8b");
    }

    #[test]
    fn test_unknown_rol() {
        assert_eq!(rol_to_modelo("Unknown"), "glm4:9b");
    }
}
