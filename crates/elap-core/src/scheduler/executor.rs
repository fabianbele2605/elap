//! Planificador y ejecutor de tareas

use super::queue::ColaTareas;
use super::task::{Tarea, IdTarea, PrioridadTarea};
use tokio::sync::Mutex;
use std::sync::Arc;

/// Planificador principal de tareas
///
/// Gestiona la ejecución de tareas con el runtime de Tokio.
/// Maneja encolar, desencolar y rastrear el estado de las tareas.
pub struct PlanificadorTareas {
    cola: Arc<Mutex<ColaTareas>>,
    maximo_concurrentes: usize,
}

impl PlanificadorTareas {
    /// Crear un nuevo planificador de tareas
    pub fn nuevo(maximo_concurrentes: usize) -> Self {
        Self {
            cola: Arc::new(Mutex::new(ColaTareas::nueva(maximo_concurrentes))),
            maximo_concurrentes,
        }
    }

    /// Enviar una tarea a la cola
    pub async fn enviar_tarea(&self, tarea: Tarea) -> IdTarea {
        let mut cola = self.cola.lock().await;
        cola.encolar(tarea)
    }

    /// Enviar una tarea simple por nombre
    pub async fn enviar(&self, nombre: impl Into<String>) -> IdTarea {
        self.enviar_tarea(Tarea::nueva(nombre)).await
    }

    /// Enviar una tarea de alta prioridad
    pub async fn enviar_alta_prioridad(&self, nombre: impl Into<String>) -> IdTarea {
        let tarea = Tarea::nueva(nombre).con_prioridad(PrioridadTarea::Alta);
        self.enviar_tarea(tarea).await
    }

    /// Obtener estado de una tarea
    pub async fn obtener_estado_tarea(&self, id_tarea: IdTarea) -> Option<String> {
        let cola = self.cola.lock().await;
        cola.obtener_tarea(id_tarea).map(|t| t.estado.to_string())
    }

    /// Marcar tarea como completada
    pub async fn completar_tarea(&self, id_tarea: IdTarea) {
        let mut cola = self.cola.lock().await;
        cola.marcar_completada(id_tarea);
    }

    /// Marcar tarea como fallida
    pub async fn fallar_tarea(&self, id_tarea: IdTarea) {
        let mut cola = self.cola.lock().await;
        cola.marcar_fallida(id_tarea);
    }

    /// Obtener estadísticas de la cola
    pub async fn estadisticas(&self) -> EstadisticasPlanificador {
        let cola = self.cola.lock().await;
        EstadisticasPlanificador {
            pendientes: cola.cantidad_pendientes(),
            ejecutando: cola.cantidad_ejecutando(),
            total: cola.cantidad_total(),
            maximo_concurrentes: self.maximo_concurrentes,
        }
    }

    /// Obtener la siguiente tarea a ejecutar
    pub async fn proxima_tarea(&self) -> Option<Tarea> {
        let mut cola = self.cola.lock().await;
        cola.desencolar()
    }
}

/// Estadísticas del planificador
#[derive(Debug, Clone)]
pub struct EstadisticasPlanificador {
    /// Tareas pendientes en la cola
    pub pendientes: usize,
    /// Tareas ejecutándose actualmente
    pub ejecutando: usize,
    /// Total de tareas gestionadas
    pub total: usize,
    /// Máximo de tareas concurrentes permitidas
    pub maximo_concurrentes: usize,
}

impl std::fmt::Display for EstadisticasPlanificador {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Tareas - Pendientes: {}, Ejecutando: {}/{}, Total: {}",
            self.pendientes, self.ejecutando, self.maximo_concurrentes, self.total
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_creacion_planificador() {
        let planificador = PlanificadorTareas::nuevo(4);
        let stats = planificador.estadisticas().await;
        assert_eq!(stats.pendientes, 0);
        assert_eq!(stats.ejecutando, 0);
        assert_eq!(stats.maximo_concurrentes, 4);
    }

    #[tokio::test]
    async fn test_enviar_tarea() {
        let planificador = PlanificadorTareas::nuevo(4);
        let id_tarea = planificador.enviar("tarea_test").await;

        let stats = planificador.estadisticas().await;
        assert_eq!(stats.total, 1);
    }

    #[tokio::test]
    async fn test_proxima_tarea() {
        let planificador = PlanificadorTareas::nuevo(4);
        planificador.enviar("tarea1").await;

        let tarea = planificador.proxima_tarea().await;
        assert!(tarea.is_some());

        let stats = planificador.estadisticas().await;
        assert_eq!(stats.pendientes, 0);
        assert_eq!(stats.ejecutando, 1);
    }

    #[tokio::test]
    async fn test_completar_tarea() {
        let planificador = PlanificadorTareas::nuevo(4);
        let id = planificador.enviar("tarea").await;

        planificador.proxima_tarea().await;
        planificador.completar_tarea(id).await;

        let stats = planificador.estadisticas().await;
        assert_eq!(stats.ejecutando, 0);
    }

    #[tokio::test]
    async fn test_alta_prioridad() {
        let planificador = PlanificadorTareas::nuevo(100);

        planificador.enviar("baja").await;
        let id_alta = planificador.enviar_alta_prioridad("alta").await;
        planificador.enviar("normal").await;

        let primera = planificador.proxima_tarea().await.unwrap();
        assert_eq!(primera.id, id_alta);
    }
}
