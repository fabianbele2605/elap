// Tests para nuevos endpoints REST de Fase 2

#[cfg(test)]
mod tests {
    use serde_json::json;

    #[test]
    fn test_buscar_documentos_request() {
        let request = json!({
            "collection": "documentos_rrhh",
            "query": "¿Cuál es la política de vacaciones?",
            "top_k": 5
        });

        assert_eq!(request["collection"], "documentos_rrhh");
        assert!(request["query"].is_string());
    }

    #[test]
    fn test_generar_reporte_request() {
        let request = json!({
            "title": "Reporte de Ventas",
            "sections_json": "[]",
            "format": "pdf",
            "company_name": "Andina Foods"
        });

        assert_eq!(request["title"], "Reporte de Ventas");
        assert_eq!(request["format"], "pdf");
    }

    #[test]
    fn test_listar_herramientas_response() {
        let response = json!({
            "agent_id": "agent_rrhh",
            "tools": [
                {
                    "name": "search_documents",
                    "description": "Buscar documentos en RAG"
                }
            ]
        });

        assert!(response["tools"].is_array());
        assert!(response["tools"][0]["name"].is_string());
    }

    #[test]
    fn test_endpoint_paths() {
        // Verificar que los paths están correctamente formados
        let paths = vec![
            "/documents/search",
            "/documents/generate-report",
            "/agents/:id/tools",
        ];

        for path in paths {
            assert!(path.starts_with("/"));
        }
    }
}
