// Web Search Tool - Búsqueda de información en internet

use crate::tools::Tool;
use crate::error::ResultadoElap;
use serde_json::json;

/// Herramienta para buscar información en internet
pub struct WebSearchTool;

impl Tool for WebSearchTool {
    fn nombre(&self) -> &str {
        "web_search"
    }

    fn descripcion(&self) -> &str {
        "Busca información en internet sobre un tema usando un motor de búsqueda simulado"
    }

    fn validar_parametros(&self, parametros: &serde_json::Value) -> ResultadoElap<()> {
        if !parametros.is_object() {
            return Err(crate::error::ElapError::ValidationError(
                "Parametros debe ser un objeto JSON".to_string(),
            ));
        }

        if parametros.get("query").is_none() {
            return Err(crate::error::ElapError::ValidationError(
                "Campo 'query' requerido".to_string(),
            ));
        }

        let query = parametros["query"]
            .as_str()
            .ok_or(crate::error::ElapError::ValidationError(
                "Query debe ser string".to_string(),
            ))?;

        if query.is_empty() {
            return Err(crate::error::ElapError::ValidationError(
                "Query no puede estar vacío".to_string(),
            ));
        }

        Ok(())
    }

    fn ejecutar(&self, parametros: &serde_json::Value) -> ResultadoElap<serde_json::Value> {
        self.validar_parametros(parametros)?;

        let query = parametros["query"].as_str().unwrap_or("desconocido");

        // Simular búsqueda (en producción, usar API real como DuckDuckGo, Google)
        let resultados = self.buscar_simulado(query);

        Ok(json!({
            "query": query,
            "resultados": resultados,
            "cantidad": resultados.len(),
            "fuente": "web_search_simulado"
        }))
    }
}

impl WebSearchTool {
    /// Búsqueda simulada (demostración)
    fn buscar_simulado(&self, query: &str) -> Vec<serde_json::Value> {
        vec![
            json!({
                "titulo": format!("Información sobre: {}", query),
                "url": "https://ejemplo.com/1",
                "extracto": "Este es un resultado de búsqueda simulado para demostración.",
                "relevancia": 0.95
            }),
            json!({
                "titulo": format!("Detalles sobre: {}", query),
                "url": "https://ejemplo.com/2",
                "extracto": "Otro resultado relacionado con tu búsqueda de información.",
                "relevancia": 0.87
            }),
            json!({
                "titulo": format!("Análisis: {}", query),
                "url": "https://ejemplo.com/3",
                "extracto": "Más información técnica sobre el tema.",
                "relevancia": 0.76
            }),
        ]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_nombre() {
        let tool = WebSearchTool;
        assert_eq!(tool.nombre(), "web_search");
    }

    #[test]
    fn test_descripcion() {
        let tool = WebSearchTool;
        assert!(!tool.descripcion().is_empty());
    }

    #[test]
    fn test_validar_parametros_valido() {
        let tool = WebSearchTool;
        let parametros = json!({"query": "rust programming"});
        assert!(tool.validar_parametros(&parametros).is_ok());
    }

    #[test]
    fn test_validar_parametros_sin_query() {
        let tool = WebSearchTool;
        let parametros = json!({"otro_campo": "valor"});
        assert!(tool.validar_parametros(&parametros).is_err());
    }

    #[test]
    fn test_validar_parametros_query_vacio() {
        let tool = WebSearchTool;
        let parametros = json!({"query": ""});
        assert!(tool.validar_parametros(&parametros).is_err());
    }

    #[test]
    fn test_ejecutar() {
        let tool = WebSearchTool;
        let parametros = json!({"query": "inteligencia artificial"});
        let resultado = tool.ejecutar(&parametros);

        assert!(resultado.is_ok());
        let datos = resultado.unwrap();
        assert!(datos["resultados"].is_array());
        assert_eq!(datos["cantidad"], 3);
    }

    #[test]
    fn test_buscar_simulado() {
        let tool = WebSearchTool;
        let resultados = tool.buscar_simulado("python");
        assert_eq!(resultados.len(), 3);
        assert!(resultados[0]["titulo"].is_string());
    }
}
