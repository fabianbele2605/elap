//! Definición de tareas y seguimiento de estado

use std::fmt;
use uuid::Uuid;

/// Identificador único de tarea
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct IdTarea(Uuid);

impl IdTarea {
    /// Crear un nuevo ID de tarea aleatorio
    pub fn nuevo() -> Self {
        Self(Uuid::new_v4())
    }
}

impl Default for IdTarea {
    fn default() -> Self {
        Self::nuevo()
    }
}

impl fmt::Display for IdTarea {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

/// Nivel de prioridad de la tarea
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum PrioridadTarea {
    /// Prioridad baja (tareas de fondo)
    Baja = 0,
    /// Prioridad normal (por defecto)
    Normal = 1,
    /// Prioridad alta (tareas que requieren respuesta rápida)
    Alta = 2,
}

impl Default for PrioridadTarea {
    fn default() -> Self {
        PrioridadTarea::Normal
    }
}

/// Estado de ejecución de la tarea
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EstadoTarea {
    /// Esperando en la cola
    Pendiente,
    /// Se está ejecutando actualmente
    Ejecutando,
    /// Completada exitosamente
    Completada,
    /// Falló con error
    Falló,
    /// Cancelada por el usuario
    Cancelada,
}

impl fmt::Display for EstadoTarea {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            EstadoTarea::Pendiente => write!(f, "pendiente"),
            EstadoTarea::Ejecutando => write!(f, "ejecutando"),
            EstadoTarea::Completada => write!(f, "completada"),
            EstadoTarea::Falló => write!(f, "falló"),
            EstadoTarea::Cancelada => write!(f, "cancelada"),
        }
    }
}

/// Una tarea a ser ejecutada
#[derive(Debug, Clone)]
pub struct Tarea {
    /// Identificador único
    pub id: IdTarea,
    /// Nombre de la tarea para logging
    pub nombre: String,
    /// Nivel de prioridad
    pub prioridad: PrioridadTarea,
    /// Estado actual
    pub estado: EstadoTarea,
    /// Marca de tiempo de creación
    pub creada_en: chrono::DateTime<chrono::Utc>,
    /// Última actualización de estado
    pub actualizada_en: chrono::DateTime<chrono::Utc>,
}

impl Tarea {
    /// Crear una nueva tarea
    pub fn nueva(nombre: impl Into<String>) -> Self {
        let ahora = chrono::Utc::now();
        Self {
            id: IdTarea::nuevo(),
            nombre: nombre.into(),
            prioridad: PrioridadTarea::default(),
            estado: EstadoTarea::Pendiente,
            creada_en: ahora,
            actualizada_en: ahora,
        }
    }

    /// Establecer prioridad de la tarea
    pub fn con_prioridad(mut self, prioridad: PrioridadTarea) -> Self {
        self.prioridad = prioridad;
        self
    }

    /// Actualizar estado de la tarea
    pub fn establecer_estado(&mut self, estado: EstadoTarea) {
        self.estado = estado;
        self.actualizada_en = chrono::Utc::now();
    }

    /// Obtener tiempo transcurrido desde la creación
    pub fn tiempo_transcurrido(&self) -> chrono::Duration {
        chrono::Utc::now() - self.creada_en
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_creacion_tarea() {
        let tarea = Tarea::nueva("tarea_test");
        assert_eq!(tarea.nombre, "tarea_test");
        assert_eq!(tarea.estado, EstadoTarea::Pendiente);
        assert_eq!(tarea.prioridad, PrioridadTarea::Normal);
    }

    #[test]
    fn test_tarea_con_prioridad() {
        let tarea = Tarea::nueva("prioridad_alta").con_prioridad(PrioridadTarea::Alta);
        assert_eq!(tarea.prioridad, PrioridadTarea::Alta);
    }

    #[test]
    fn test_actualizar_estado_tarea() {
        let mut tarea = Tarea::nueva("test");
        tarea.establecer_estado(EstadoTarea::Ejecutando);
        assert_eq!(tarea.estado, EstadoTarea::Ejecutando);
    }

    #[test]
    fn test_id_tarea_unico() {
        let tarea1 = Tarea::nueva("tarea1");
        let tarea2 = Tarea::nueva("tarea2");
        assert_ne!(tarea1.id, tarea2.id);
    }

    #[test]
    fn test_tiempo_transcurrido() {
        let tarea = Tarea::nueva("test");
        std::thread::sleep(std::time::Duration::from_millis(10));
        assert!(tarea.tiempo_transcurrido().num_milliseconds() >= 10);
    }
}
