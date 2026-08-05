//! Herramienta para operar con archivos

use super::tool_trait::Tool;
use serde_json::{json, Value};
use std::fs;
use std::path::{Path, PathBuf};
use crate::error::{ResultadoElap, ElapError};

/// Herramienta para lectura y escritura de archivos
pub struct FileTool {
    base_path: PathBuf,
}

impl FileTool {
    /// Crear nueva herramienta de archivos con ruta base
    pub fn nuevo(base_path: impl AsRef<Path>) -> Self {
        Self {
            base_path: base_path.as_ref().to_path_buf(),
        }
    }

    /// Validar que la ruta está dentro de la ruta base
    fn validar_ruta(&self, ruta: &str) -> ResultadoElap<PathBuf> {
        let path = self.base_path.join(ruta);

        let base_canonical = self.base_path.canonicalize()
            .unwrap_or_else(|_| self.base_path.clone());

        let path_canonical = if path.exists() {
            path.canonicalize()
                .map_err(|e| ElapError::Validacion(format!("No se puede resolver ruta: {}", e)))?
        } else {
            let parent = path.parent().unwrap_or(&self.base_path);
            let parent_canonical = if parent.exists() {
                parent.canonicalize().unwrap_or_else(|_| parent.to_path_buf())
            } else {
                parent.to_path_buf()
            };

            let file_name = path.file_name().unwrap_or_default();
            parent_canonical.join(file_name)
        };

        if !path_canonical.starts_with(&base_canonical) {
            return Err(ElapError::Validacion("Ruta fuera de sandbox".to_string()));
        }

        Ok(path_canonical)
    }

    /// Leer archivo
    fn leer(&self, parametros: &Value) -> ResultadoElap<Value> {
        let ruta = parametros
            .get("ruta")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'ruta' requerido".to_string()))?;

        let path = self.validar_ruta(ruta)?;

        let contenido = fs::read_to_string(&path)
            .map_err(|e| ElapError::Otro(format!("Error al leer archivo: {}", e)))?;

        Ok(json!({
            "ruta": ruta,
            "contenido": contenido,
            "bytes": contenido.len(),
            "timestamp": chrono::Utc::now().to_rfc3339(),
        }))
    }

    /// Escribir archivo
    fn escribir(&self, parametros: &Value) -> ResultadoElap<Value> {
        let ruta = parametros
            .get("ruta")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'ruta' requerido".to_string()))?;

        let contenido = parametros
            .get("contenido")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'contenido' requerido".to_string()))?;

        let path = self.validar_ruta(ruta)?;

        if let Some(padre) = path.parent() {
            fs::create_dir_all(padre)
                .map_err(|e| ElapError::Otro(format!("Error al crear directorio: {}", e)))?;
        }

        fs::write(&path, contenido)
            .map_err(|e| ElapError::Otro(format!("Error al escribir archivo: {}", e)))?;

        Ok(json!({
            "ruta": ruta,
            "bytes_escritos": contenido.len(),
            "timestamp": chrono::Utc::now().to_rfc3339(),
        }))
    }

    /// Listar directorio
    fn listar(&self, parametros: &Value) -> ResultadoElap<Value> {
        let ruta = parametros
            .get("ruta")
            .and_then(|v| v.as_str())
            .unwrap_or(".");

        let path = self.validar_ruta(ruta)?;

        let mut archivos = Vec::new();
        let entries = fs::read_dir(&path)
            .map_err(|e| ElapError::Otro(format!("Error al leer directorio: {}", e)))?;

        for entry in entries {
            let entry = entry.map_err(|e| ElapError::Otro(format!("Error en entrada: {}", e)))?;
            let nombre = entry.file_name();
            let metadata = entry.metadata()
                .map_err(|e| ElapError::Otro(format!("Error al obtener metadata: {}", e)))?;

            archivos.push(json!({
                "nombre": nombre.to_string_lossy(),
                "es_directorio": metadata.is_dir(),
                "bytes": metadata.len(),
            }));
        }

        Ok(json!({
            "ruta": ruta,
            "archivos": archivos,
            "total": archivos.len(),
        }))
    }
}

impl Tool for FileTool {
    fn nombre(&self) -> &str {
        "archivo"
    }

    fn descripcion(&self) -> &str {
        "Leer, escribir y listar archivos con sandboxing"
    }

    fn ejecutar(&self, parametros: &Value) -> ResultadoElap<Value> {
        let operacion = parametros
            .get("operacion")
            .and_then(|v| v.as_str())
            .ok_or(ElapError::Validacion("Parámetro 'operacion' requerido".to_string()))?;

        match operacion {
            "leer" => self.leer(parametros),
            "escribir" => self.escribir(parametros),
            "listar" => self.listar(parametros),
            _ => Err(ElapError::Validacion(format!("Operación desconocida: {}", operacion))),
        }
    }

    fn validar_parametros(&self, parametros: &Value) -> ResultadoElap<()> {
        if !parametros.is_object() {
            return Err(ElapError::Validacion("Los parámetros deben ser un objeto JSON".to_string()));
        }

        let operacion = parametros
            .get("operacion")
            .and_then(|v| v.as_str());

        if operacion.is_none() {
            return Err(ElapError::Validacion("Parámetro 'operacion' requerido".to_string()));
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_crear_herramienta() {
        let tool = FileTool::nuevo(".");
        assert_eq!(tool.nombre(), "archivo");
        assert!(!tool.descripcion().is_empty());
    }

    #[test]
    fn test_leer_archivo() {
        let temp = TempDir::new().unwrap();
        let test_file = temp.path().join("test.txt");
        fs::write(&test_file, "contenido de prueba").unwrap();

        let tool = FileTool::nuevo(temp.path());
        let params = json!({
            "operacion": "leer",
            "ruta": "test.txt"
        });

        let resultado = tool.ejecutar(&params).unwrap();
        assert_eq!(resultado["contenido"], "contenido de prueba");
    }

    #[test]
    fn test_escribir_archivo() {
        let temp = TempDir::new().unwrap();
        let tool = FileTool::nuevo(temp.path());

        let params = json!({
            "operacion": "escribir",
            "ruta": "nuevo.txt",
            "contenido": "nuevo contenido"
        });

        let resultado = tool.ejecutar(&params).unwrap();
        assert_eq!(resultado["bytes_escritos"], 15);

        let contenido = fs::read_to_string(temp.path().join("nuevo.txt")).unwrap();
        assert_eq!(contenido, "nuevo contenido");
    }

    #[test]
    fn test_validar_ruta_fuera_sandbox() {
        let temp = TempDir::new().unwrap();
        let tool = FileTool::nuevo(temp.path());

        let params = json!({
            "operacion": "leer",
            "ruta": "../../../etc/passwd"
        });

        let resultado = tool.ejecutar(&params);
        assert!(resultado.is_err());
    }

    #[test]
    fn test_listar_directorio() {
        let temp = TempDir::new().unwrap();
        fs::write(temp.path().join("a.txt"), "a").unwrap();
        fs::write(temp.path().join("b.txt"), "b").unwrap();

        let tool = FileTool::nuevo(temp.path());
        let params = json!({
            "operacion": "listar",
            "ruta": "."
        });

        let resultado = tool.ejecutar(&params).unwrap();
        assert_eq!(resultado["total"], 2);
    }

    #[test]
    fn test_validar_parametros() {
        let tool = FileTool::nuevo(".");

        assert!(tool.validar_parametros(&json!({ "operacion": "leer" })).is_ok());
        assert!(tool.validar_parametros(&json!({})).is_err());
        assert!(tool.validar_parametros(&json!([])).is_err());
    }
}
