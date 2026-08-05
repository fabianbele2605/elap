//! Planificación y ejecución de tareas
//!
//! Gestiona la ejecución concurrente de tareas usando Tokio.
//! Proporciona capacidades de cola, planificación y ejecución.

pub mod task;
pub mod queue;
pub mod executor;

pub use executor::PlanificadorTareas;
pub use task::{Tarea, IdTarea, EstadoTarea, PrioridadTarea};
pub use queue::ColaTareas;
