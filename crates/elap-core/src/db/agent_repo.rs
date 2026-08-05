//! Repositorio de agentes

use super::schema::{AgenteBD, EjecucionBD, AccionBD};
use super::Database;
use crate::error::ResultadoElap;
use uuid::Uuid;

/// Repositorio para operaciones con agentes
pub struct RepositorioAgente;

impl RepositorioAgente {
    /// Guardar agente
    pub async fn guardar(
        db: &Database,
        id: String,
        nombre: String,
        rol: String,
        objetivo: String,
        estado: String,
    ) -> ResultadoElap<()> {
        sqlx::query(
            "INSERT INTO agentes (id, nombre, rol, objetivo, estado)
             VALUES (?, ?, ?, ?, ?)
             ON CONFLICT(id) DO UPDATE SET
             nombre = excluded.nombre,
             rol = excluded.rol,
             objetivo = excluded.objetivo,
             estado = excluded.estado,
             updated_at = CURRENT_TIMESTAMP"
        )
        .bind(id)
        .bind(nombre)
        .bind(rol)
        .bind(objetivo)
        .bind(estado)
        .execute(db)
        .await?;

        Ok(())
    }

    /// Obtener agente por ID
    pub async fn obtener(db: &Database, id: &str) -> ResultadoElap<Option<AgenteBD>> {
        let agente = sqlx::query_as::<_, AgenteBD>(
            "SELECT id, nombre, rol, objetivo, estado, created_at, updated_at
             FROM agentes WHERE id = ?"
        )
        .bind(id)
        .fetch_optional(db)
        .await?;

        Ok(agente)
    }

    /// Listar todos los agentes
    pub async fn listar(db: &Database) -> ResultadoElap<Vec<AgenteBD>> {
        let agentes = sqlx::query_as::<_, AgenteBD>(
            "SELECT id, nombre, rol, objetivo, estado, created_at, updated_at
             FROM agentes ORDER BY created_at DESC"
        )
        .fetch_all(db)
        .await?;

        Ok(agentes)
    }

    /// Eliminar agente
    pub async fn eliminar(db: &Database, id: &str) -> ResultadoElap<()> {
        sqlx::query("DELETE FROM agentes WHERE id = ?")
            .bind(id)
            .execute(db)
            .await?;

        Ok(())
    }

    /// Registrar ejecución
    pub async fn registrar_ejecucion(
        db: &Database,
        agente_id: String,
        pasos_completados: i32,
        progreso: f32,
        resultado: Option<String>,
    ) -> ResultadoElap<()> {
        let ejecucion_id = Uuid::new_v4().to_string();

        sqlx::query(
            "INSERT INTO execuciones (id, agente_id, pasos_completados, progreso, resultado)
             VALUES (?, ?, ?, ?, ?)"
        )
        .bind(ejecucion_id)
        .bind(agente_id)
        .bind(pasos_completados)
        .bind(progreso)
        .bind(resultado)
        .execute(db)
        .await?;

        Ok(())
    }

    /// Obtener historial de ejecuciones
    pub async fn obtener_ejecuciones(
        db: &Database,
        agente_id: &str,
    ) -> ResultadoElap<Vec<EjecucionBD>> {
        let ejecuciones = sqlx::query_as::<_, EjecucionBD>(
            "SELECT id, agente_id, pasos_completados, progreso, resultado, created_at
             FROM execuciones WHERE agente_id = ? ORDER BY created_at DESC"
        )
        .bind(agente_id)
        .fetch_all(db)
        .await?;

        Ok(ejecuciones)
    }

    /// Registrar acción
    pub async fn registrar_accion(
        db: &Database,
        agente_id: String,
        descripcion: String,
    ) -> ResultadoElap<()> {
        let accion_id = Uuid::new_v4().to_string();

        sqlx::query(
            "INSERT INTO acciones (id, agente_id, descripcion)
             VALUES (?, ?, ?)"
        )
        .bind(accion_id)
        .bind(agente_id)
        .bind(descripcion)
        .execute(db)
        .await?;

        Ok(())
    }

    /// Obtener acciones de agente
    pub async fn obtener_acciones(
        db: &Database,
        agente_id: &str,
    ) -> ResultadoElap<Vec<AccionBD>> {
        let acciones = sqlx::query_as::<_, AccionBD>(
            "SELECT id, agente_id, descripcion, created_at
             FROM acciones WHERE agente_id = ? ORDER BY created_at DESC"
        )
        .bind(agente_id)
        .fetch_all(db)
        .await?;

        Ok(acciones)
    }

    /// Contar total de agentes
    pub async fn contar(db: &Database) -> ResultadoElap<i64> {
        let result: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM agentes")
            .fetch_one(db)
            .await?;

        Ok(result.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_repositorio_interfaz() {
        // Test que verifica que los métodos existen y tienen las firmas correctas
        // (Testing real requiere DB)
        let _ = RepositorioAgente::contar;
        let _ = RepositorioAgente::guardar;
        let _ = RepositorioAgente::obtener;
        let _ = RepositorioAgente::listar;
        let _ = RepositorioAgente::eliminar;
    }
}
