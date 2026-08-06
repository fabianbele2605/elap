//! Esquema de configuración para validación

use serde_json::json;
use serde_json::Value as JsonValue;

/// Esquema JSON para validación de configuración
pub struct EsquemaConfiguracion;

impl EsquemaConfiguracion {
    /// Obtener esquema JSON completo
    pub fn obtener() -> JsonValue {
        json!({
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Esquema de Configuración ELAP",
            "type": "object",
            "required": ["version", "entorno"],
            "properties": {
                "version": {
                    "type": "string",
                    "description": "Versión semántica",
                    "pattern": "^\\d+\\.\\d+\\.\\d+$"
                },
                "entorno": {
                    "type": "string",
                    "enum": ["desarrollo", "testing", "produccion"],
                    "description": "Entorno de ejecución"
                },
                "logging": {
                    "type": "object",
                    "required": ["nivel", "formato"],
                    "properties": {
                        "nivel": {
                            "type": "string",
                            "enum": ["debug", "info", "warn", "error"],
                            "description": "Nivel de logging"
                        },
                        "formato": {
                            "type": "string",
                            "enum": ["json", "plaintext"],
                            "description": "Formato de salida"
                        },
                        "guardar_archivo": {
                            "type": "boolean",
                            "default": true
                        },
                        "ruta_archivo": {
                            "type": ["string", "null"]
                        },
                        "tamaño_maximo_mb": {
                            "type": "integer",
                            "minimum": 1,
                            "default": 100
                        }
                    }
                },
                "base_datos": {
                    "type": "object",
                    "required": ["tipo"],
                    "properties": {
                        "tipo": {
                            "type": "string",
                            "enum": ["sqlite", "postgresql", "mysql"],
                            "description": "Tipo de base de datos"
                        },
                        "url": {
                            "type": ["string", "null"],
                            "description": "URL de conexión (para BD remota)"
                        },
                        "archivo": {
                            "type": ["string", "null"],
                            "description": "Ruta de archivo (para SQLite)"
                        },
                        "pool_maximo": {
                            "type": "integer",
                            "minimum": 1,
                            "default": 10
                        },
                        "timeout_segundos": {
                            "type": "integer",
                            "minimum": 1,
                            "default": 30
                        }
                    }
                },
                "seguridad": {
                    "type": "object",
                    "properties": {
                        "requiere_autenticacion": {
                            "type": "boolean",
                            "default": true
                        },
                        "rbac_habilitado": {
                            "type": "boolean",
                            "default": true
                        },
                        "auditoria_habilitada": {
                            "type": "boolean",
                            "default": true
                        },
                        "cifrado_habilitado": {
                            "type": "boolean",
                            "default": true
                        },
                        "algoritmo_cifrado": {
                            "type": "string",
                            "enum": ["AES-256-GCM", "AES-128-GCM"],
                            "default": "AES-256-GCM"
                        }
                    }
                },
                "plugins": {
                    "type": "object",
                    "properties": {
                        "habilitados": {
                            "type": "boolean",
                            "default": true
                        },
                        "directorio": {
                            "type": "string",
                            "default": "./plugins"
                        },
                        "cargar_automaticamente": {
                            "type": "boolean",
                            "default": true
                        },
                        "maximo_plugins": {
                            "type": "integer",
                            "minimum": 1,
                            "default": 50
                        }
                    }
                }
            }
        })
    }

    /// Obtener esquema en formato string JSON
    pub fn obtener_string() -> String {
        serde_json::to_string_pretty(&Self::obtener()).unwrap_or_default()
    }

    /// Validar JSON contra el esquema
    pub fn validar_json(valor: &JsonValue) -> Result<(), String> {
        let schema = Self::obtener();

        // Validar propiedades requeridas
        if let Some(obj) = valor.as_object() {
            if !obj.contains_key("version") {
                return Err("Campo requerido 'version' falta".to_string());
            }
            if !obj.contains_key("entorno") {
                return Err("Campo requerido 'entorno' falta".to_string());
            }

            // Validar entorno
            if let Some(entorno) = obj.get("entorno").and_then(|e| e.as_str()) {
                if !["desarrollo", "testing", "produccion"].contains(&entorno) {
                    return Err(format!("Entorno '{}' no es válido", entorno));
                }
            }

            // Validar version formato semántico
            if let Some(version) = obj.get("version").and_then(|v| v.as_str()) {
                let partes: Vec<&str> = version.split('.').collect();
                if partes.len() != 3 {
                    return Err("Versión debe ser formato X.Y.Z".to_string());
                }
                for parte in partes {
                    if parte.parse::<u32>().is_err() {
                        return Err("Versión debe contener números".to_string());
                    }
                }
            }
        } else {
            return Err("Configuración debe ser un objeto".to_string());
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_obtener_esquema() {
        let schema = EsquemaConfiguracion::obtener();
        assert!(schema.is_object());
        assert!(schema.get("$schema").is_some());
        assert!(schema.get("properties").is_some());
    }

    #[test]
    fn test_obtener_esquema_string() {
        let schema_str = EsquemaConfiguracion::obtener_string();
        assert!(!schema_str.is_empty());
        assert!(schema_str.contains("version"));
        assert!(schema_str.contains("entorno"));
    }

    #[test]
    fn test_validar_json_valido() {
        let valor = json!({
            "version": "1.0.0",
            "entorno": "testing",
            "logging": {
                "nivel": "debug",
                "formato": "json"
            },
            "base_datos": {
                "tipo": "sqlite",
                "archivo": ":memory:",
                "pool_maximo": 10,
                "timeout_segundos": 30
            },
            "seguridad": {
                "requiere_autenticacion": true,
                "rbac_habilitado": true
            },
            "plugins": {
                "habilitados": true,
                "directorio": "./plugins"
            }
        });

        assert!(EsquemaConfiguracion::validar_json(&valor).is_ok());
    }

    #[test]
    fn test_validar_json_falta_version() {
        let valor = json!({
            "entorno": "testing"
        });

        assert!(EsquemaConfiguracion::validar_json(&valor).is_err());
    }

    #[test]
    fn test_validar_json_entorno_invalido() {
        let valor = json!({
            "version": "1.0.0",
            "entorno": "invalido"
        });

        assert!(EsquemaConfiguracion::validar_json(&valor).is_err());
    }

    #[test]
    fn test_validar_json_version_formato() {
        let valor_bueno = json!({
            "version": "1.2.3",
            "entorno": "testing"
        });
        assert!(EsquemaConfiguracion::validar_json(&valor_bueno).is_ok());

        let valor_malo = json!({
            "version": "1.2",
            "entorno": "testing"
        });
        assert!(EsquemaConfiguracion::validar_json(&valor_malo).is_err());
    }

    #[test]
    fn test_validar_json_no_es_objeto() {
        let valor = json!("no es objeto");
        assert!(EsquemaConfiguracion::validar_json(&valor).is_err());
    }
}
