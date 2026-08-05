//! Implementación de cola de tareas

use super::task::{Tarea, IdTarea, PrioridadTarea, EstadoTarea};
use std::collections::{BinaryHeap, HashMap};
use std::cmp::Ordering;

/// Envoltura para ordenamiento de cola de prioridad (mayor prioridad = se ejecuta primero)
#[derive(Debug, Clone)]
struct TareaPrioritizada(Tarea);

impl PartialEq for TareaPrioritizada {
    fn eq(&self, otro: &Self) -> bool {
        self.0.id == otro.0.id
    }
}

impl Eq for TareaPrioritizada {}

impl PartialOrd for TareaPrioritizada {
    fn partial_cmp(&self, otro: &Self) -> Option<Ordering> {
        Some(self.cmp(otro))
    }
}

impl Ord for TareaPrioritizada {
    fn cmp(&self, otro: &Self) -> Ordering {
        // Mayor prioridad primero
        match self.0.prioridad.cmp(&otro.0.prioridad) {
            Ordering::Equal => self.0.creada_en.cmp(&otro.0.creada_en),
            orden => orden,
        }
    }
}

/// Cola de tareas thread-safe con ordenamiento por prioridad
#[derive(Debug)]
pub struct ColaTareas {
    /// Cola de prioridad de tareas pendientes
    cola: BinaryHeap<TareaPrioritizada>,
    /// Todas las tareas por ID (para rastrear estado)
    tareas: HashMap<IdTarea, Tarea>,
    /// Máximo de tareas concurrentes permitidas
    maximo_concurrentes: usize,
    /// Contador de tareas ejecutándose actualmente
    contador_ejecutando: usize,
}

impl ColaTareas {
    /// Crear una nueva cola de tareas
    pub fn nueva(maximo_concurrentes: usize) -> Self {
        Self {
            cola: BinaryHeap::new(),
            tareas: HashMap::new(),
            maximo_concurrentes,
            contador_ejecutando: 0,
        }
    }

    /// Encolar una tarea
    pub fn encolar(&mut self, tarea: Tarea) -> IdTarea {
        let id = tarea.id;
        self.cola.push(TareaPrioritizada(tarea.clone()));
        self.tareas.insert(id, tarea);
        id
    }

    /// Desencolar la siguiente tarea (si está disponible y dentro del límite de concurrencia)
    pub fn desencolar(&mut self) -> Option<Tarea> {
        if self.contador_ejecutando >= self.maximo_concurrentes {
            return None;
        }

        if let Some(TareaPrioritizada(mut tarea)) = self.cola.pop() {
            tarea.establecer_estado(EstadoTarea::Ejecutando);
            self.tareas.insert(tarea.id, tarea.clone());
            self.contador_ejecutando += 1;
            return Some(tarea);
        }

        None
    }

    /// Marcar tarea como completada
    pub fn marcar_completada(&mut self, id_tarea: IdTarea) {
        if let Some(tarea) = self.tareas.get_mut(&id_tarea) {
            tarea.establecer_estado(EstadoTarea::Completada);
        }
        if self.contador_ejecutando > 0 {
            self.contador_ejecutando -= 1;
        }
    }

    /// Marcar tarea como fallida
    pub fn marcar_fallida(&mut self, id_tarea: IdTarea) {
        if let Some(tarea) = self.tareas.get_mut(&id_tarea) {
            tarea.establecer_estado(EstadoTarea::Falló);
        }
        if self.contador_ejecutando > 0 {
            self.contador_ejecutando -= 1;
        }
    }

    /// Obtener estado de una tarea
    pub fn obtener_tarea(&self, id_tarea: IdTarea) -> Option<&Tarea> {
        self.tareas.get(&id_tarea)
    }

    /// Obtener cantidad de tareas pendientes
    pub fn cantidad_pendientes(&self) -> usize {
        self.cola.len()
    }

    /// Obtener cantidad de tareas ejecutándose
    pub fn cantidad_ejecutando(&self) -> usize {
        self.contador_ejecutando
    }

    /// Obtener total de tareas gestionadas
    pub fn cantidad_total(&self) -> usize {
        self.tareas.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_creacion_cola() {
        let cola = ColaTareas::nueva(4);
        assert_eq!(cola.cantidad_pendientes(), 0);
        assert_eq!(cola.cantidad_ejecutando(), 0);
    }

    #[test]
    fn test_encolar_tarea() {
        let mut cola = ColaTareas::nueva(4);
        let tarea = Tarea::nueva("tarea_test");
        let id = cola.encolar(tarea);
        assert_eq!(cola.cantidad_pendientes(), 1);
        assert!(cola.obtener_tarea(id).is_some());
    }

    #[test]
    fn test_desencolar_tarea() {
        let mut cola = ColaTareas::nueva(4);
        let tarea = Tarea::nueva("tarea_test");
        cola.encolar(tarea);

        let desencolada = cola.desencolar();
        assert!(desencolada.is_some());
        assert_eq!(cola.cantidad_pendientes(), 0);
        assert_eq!(cola.cantidad_ejecutando(), 1);
    }

    #[test]
    fn test_ordenamiento_prioridad() {
        let mut cola = ColaTareas::nueva(100);

        let baja = Tarea::nueva("baja").con_prioridad(PrioridadTarea::Baja);
        let alta = Tarea::nueva("alta").con_prioridad(PrioridadTarea::Alta);
        let normal = Tarea::nueva("normal").con_prioridad(PrioridadTarea::Normal);

        cola.encolar(baja);
        cola.encolar(normal);
        cola.encolar(alta);

        // Debe desencolar en orden de prioridad: alta, normal, baja
        let primera = cola.desencolar().unwrap();
        assert_eq!(primera.prioridad, PrioridadTarea::Alta);

        let segunda = cola.desencolar().unwrap();
        assert_eq!(segunda.prioridad, PrioridadTarea::Normal);

        let tercera = cola.desencolar().unwrap();
        assert_eq!(tercera.prioridad, PrioridadTarea::Baja);
    }

    #[test]
    fn test_limite_concurrencia() {
        let mut cola = ColaTareas::nueva(2);

        let tarea1 = Tarea::nueva("tarea1");
        let tarea2 = Tarea::nueva("tarea2");
        let tarea3 = Tarea::nueva("tarea3");

        cola.encolar(tarea1);
        cola.encolar(tarea2);
        cola.encolar(tarea3);

        // Puede desencolar 2 tareas
        assert!(cola.desencolar().is_some());
        assert!(cola.desencolar().is_some());

        // 3ª tarea espera (contador_ejecutando >= maximo_concurrentes)
        assert!(cola.desencolar().is_none());
        assert_eq!(cola.cantidad_pendientes(), 1);
        assert_eq!(cola.cantidad_ejecutando(), 2);
    }

    #[test]
    fn test_marcar_completada() {
        let mut cola = ColaTareas::nueva(4);
        let tarea = Tarea::nueva("test");
        let id = cola.encolar(tarea);

        cola.desencolar();
        assert_eq!(cola.cantidad_ejecutando(), 1);

        cola.marcar_completada(id);
        assert_eq!(cola.cantidad_ejecutando(), 0);

        let actualizada = cola.obtener_tarea(id).unwrap();
        assert_eq!(actualizada.estado, EstadoTarea::Completada);
    }
}
