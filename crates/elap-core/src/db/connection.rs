//! Conexión a base de datos

use sqlx::sqlite::{SqlitePool, SqlitePoolOptions};
use std::path::PathBuf;
use crate::error::ResultadoElap;

/// Pool de conexiones
pub type Database = SqlitePool;

/// Obtener directorio de datos de la aplicación
fn obtener_directorio_datos() -> ResultadoElap<PathBuf> {
    let dirs = directories::ProjectDirs::from("io", "bblabs", "elap")
        .ok_or_else(|| crate::error::ElapError::Otro(
            "No se pudo determinar directorio de datos".to_string()
        ))?;

    let data_dir = dirs.data_dir();

    // Crear directorio si no existe
    if !data_dir.exists() {
        std::fs::create_dir_all(data_dir)?;
    }

    Ok(data_dir.to_path_buf())
}

/// Conectar a la base de datos
pub async fn obtener_db() -> ResultadoElap<Database> {
    let data_dir = obtener_directorio_datos()?;
    let db_path = data_dir.join("elap.db");

    let db_url = format!("sqlite://{}", db_path.display());

    let pool = SqlitePoolOptions::new()
        .max_connections(5)
        .connect(&db_url)
        .await?;

    // Ejecutar migrations
    sqlx::query(
        "CREATE TABLE IF NOT EXISTS agentes (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            rol TEXT NOT NULL,
            objetivo TEXT NOT NULL,
            estado TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )"
    )
    .execute(&pool)
    .await?;

    sqlx::query(
        "CREATE TABLE IF NOT EXISTS execuciones (
            id TEXT PRIMARY KEY,
            agente_id TEXT NOT NULL,
            pasos_completados INTEGER NOT NULL,
            progreso REAL NOT NULL,
            resultado TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(agente_id) REFERENCES agentes(id)
        )"
    )
    .execute(&pool)
    .await?;

    sqlx::query(
        "CREATE TABLE IF NOT EXISTS acciones (
            id TEXT PRIMARY KEY,
            agente_id TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(agente_id) REFERENCES agentes(id)
        )"
    )
    .execute(&pool)
    .await?;

    Ok(pool)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_obtener_directorio() {
        let dir = obtener_directorio_datos();
        assert!(dir.is_ok());
    }

    #[tokio::test]
    async fn test_conectar_db_memoria() {
        // Test con BD en memoria para no contaminar sistema
        let pool = SqlitePoolOptions::new()
            .connect("sqlite::memory:")
            .await;
        assert!(pool.is_ok());
    }
}
