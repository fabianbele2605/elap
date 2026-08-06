//! Esquema de base de datos

use serde::{Deserialize, Serialize};
use sqlx::FromRow;

/// Registro de agente en BD
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct AgenteBD {
    /// ID único
    pub id: String,
    /// Nombre del agente
    pub nombre: String,
    /// Rol del agente
    pub rol: String,
    /// Objetivo
    pub objetivo: String,
    /// Estado actual
    pub estado: String,
    /// Timestamp de creación
    pub created_at: String,
    /// Timestamp de actualización
    pub updated_at: String,
}

/// Registro de ejecución
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct EjecucionBD {
    /// ID único
    pub id: String,
    /// ID del agente
    pub agente_id: String,
    /// Pasos completados
    pub pasos_completados: i32,
    /// Progreso (0.0 a 1.0)
    pub progreso: f32,
    /// Resultado en JSON
    pub resultado: Option<String>,
    /// Timestamp de creación
    pub created_at: String,
}

/// Registro de acción
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct AccionBD {
    /// ID único
    pub id: String,
    /// ID del agente
    pub agente_id: String,
    /// Descripción de la acción
    pub descripcion: String,
    /// Timestamp
    pub created_at: String,
}

/// Resultado de schema
pub struct Schema;

impl Schema {
    /// Obtener SQL para crear tablas
    pub fn crear_tablas() -> Vec<&'static str> {
        vec![
            "CREATE TABLE IF NOT EXISTS agentes (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                rol TEXT NOT NULL,
                objetivo TEXT NOT NULL,
                estado TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )",
            "CREATE TABLE IF NOT EXISTS execuciones (
                id TEXT PRIMARY KEY,
                agente_id TEXT NOT NULL,
                pasos_completados INTEGER NOT NULL,
                progreso REAL NOT NULL,
                resultado TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(agente_id) REFERENCES agentes(id)
            )",
            "CREATE TABLE IF NOT EXISTS acciones (
                id TEXT PRIMARY KEY,
                agente_id TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(agente_id) REFERENCES agentes(id)
            )",
        ]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_tablas() {
        let tablas = Schema::crear_tablas();
        assert_eq!(tablas.len(), 3);
    }
}
