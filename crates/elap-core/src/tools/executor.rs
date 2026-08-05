//! Ejecutor seguro de herramientas con auditoría

use super::tool_trait::Tool;
use super::sandbox::{ContextoEjecucion, ValidadorSeguridad};
use serde_json::Value as JsonValue;
use crate::error::{ResultadoElap, ElapError};
use std::time::Instant;

/// Resultado de ejecución de una herramienta
#[derive(Debug, Clone, serde::Serialize)]
pub struct ResultadoEjecucion {
    pub herramienta: String,
    pub exitoso: bool,
    pub datos: JsonValue,
    pub error: Option<String>,
    pub duracion_ms: u128,
    pub usuario: String,
}

/// Ejecutor de herramientas con validación RBAC y auditoría
pub struct EjecutorHerramientas;

impl EjecutorHerramientas {
    /// Ejecutar herramienta con contexto de seguridad
    pub fn ejecutar(
        herramienta: &dyn Tool,
        parametros: &JsonValue,
        contexto: &ContextoEjecucion,
    ) -> ResultadoElap<ResultadoEjecucion> {
        let inicio = Instant::now();

        // 1. Validar política
        ValidadorSeguridad::validar_politica(&contexto.sandbox.politica, &contexto.permisos)?;

        // 2. Validar parámetros
        ValidadorSeguridad::validar_tamaño_parametros(
            parametros,
            contexto.sandbox.limite_memoria_mb,
        )?;

        // 3. Ejecutar herramienta
        let resultado = herramienta.ejecutar(parametros);

        let duracion_ms = inicio.elapsed().as_millis();

        match resultado {
            Ok(datos) => Ok(ResultadoEjecucion {
                herramienta: herramienta.nombre().to_string(),
                exitoso: true,
                datos,
                error: None,
                duracion_ms,
                usuario: contexto.usuario_id.clone(),
            }),
            Err(e) => Ok(ResultadoEjecucion {
                herramienta: herramienta.nombre().to_string(),
                exitoso: false,
                datos: JsonValue::Null,
                error: Some(e.to_string()),
                duracion_ms,
                usuario: contexto.usuario_id.clone(),
            }),
        }
    }

    /// Ejecutar lote de herramientas
    pub fn ejecutar_lote(
        herramientas: Vec<(&dyn Tool, &JsonValue)>,
        contexto: &ContextoEjecucion,
    ) -> Vec<ResultadoEjecucion> {
        herramientas
            .into_iter()
            .filter_map(|(herr, params)| {
                Self::ejecutar(herr, params, contexto).ok()
            })
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::system_tool::SystemTool;
    use super::super::sandbox::SandboxHerramienta;
    use crate::security::Permiso;

    #[test]
    fn test_resultado_ejecucion() {
        let resultado = ResultadoEjecucion {
            herramienta: "test".to_string(),
            exitoso: true,
            datos: serde_json::json!({}),
            error: None,
            duracion_ms: 100,
            usuario: "usuario_123".to_string(),
        };

        assert!(resultado.exitoso);
        assert_eq!(resultado.herramienta, "test");
    }

    #[test]
    fn test_ejecutar_herramienta() {
        let tool = SystemTool::nuevo(false);
        let params = serde_json::json!({ "operacion": "info" });
        let contexto = ContextoEjecucion::nuevo(
            "usuario_123".to_string(),
            vec![Permiso::EjecutarHerramientas],
            SandboxHerramienta::default(),
        );

        let resultado = EjecutorHerramientas::ejecutar(&tool, &params, &contexto);
        assert!(resultado.is_ok());
    }

    #[test]
    fn test_ejecutar_sin_permiso() {
        let tool = SystemTool::nuevo(false);
        let params = serde_json::json!({ "operacion": "info" });
        let contexto = ContextoEjecucion::nuevo(
            "usuario_123".to_string(),
            vec![], // Sin permisos
            SandboxHerramienta::default(),
        );

        let resultado = EjecutorHerramientas::ejecutar(&tool, &params, &contexto);
        assert!(resultado.is_err());
    }

    #[test]
    fn test_resultado_con_error() {
        let tool = SystemTool::nuevo(false);
        let params = serde_json::json!({ "operacion": "invalida" });
        let contexto = ContextoEjecucion::nuevo(
            "usuario_123".to_string(),
            vec![Permiso::EjecutarHerramientas],
            SandboxHerramienta::default(),
        );

        let resultado = EjecutorHerramientas::ejecutar(&tool, &params, &contexto);
        if let Ok(res) = resultado {
            assert!(!res.exitoso);
            assert!(res.error.is_some());
        }
    }
}
