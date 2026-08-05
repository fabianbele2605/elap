//! Sistemas avanzados de memoria para agentes

use std::collections::VecDeque;
use serde_json::{json, Value as JsonValue};
use std::sync::{Arc, Mutex};

/// Memoria de corto plazo (últimas N interacciones)
pub struct MemoriaCortoTermino {
    historial: Arc<Mutex<VecDeque<JsonValue>>>,
    max_items: usize,
}

impl MemoriaCortoTermino {
    /// Crear nueva memoria a corto plazo
    pub fn nueva(max_items: usize) -> Self {
        Self {
            historial: Arc::new(Mutex::new(VecDeque::new())),
            max_items,
        }
    }

    /// Agregar evento a la memoria
    pub fn agregar(&self, evento: JsonValue) {
        if let Ok(mut hist) = self.historial.lock() {
            hist.push_back(evento);
            while hist.len() > self.max_items {
                hist.pop_front();
            }
        }
    }

    /// Obtener últimos N eventos
    pub fn obtener_ultimos(&self, n: usize) -> Vec<JsonValue> {
        if let Ok(hist) = self.historial.lock() {
            hist.iter().rev().take(n).cloned().collect()
        } else {
            Vec::new()
        }
    }

    /// Limpiar memoria
    pub fn limpiar(&self) {
        if let Ok(mut hist) = self.historial.lock() {
            hist.clear();
        }
    }

    /// Contar items
    pub fn contar(&self) -> usize {
        if let Ok(hist) = self.historial.lock() {
            hist.len()
        } else {
            0
        }
    }
}

/// Memoria de largo plazo (patrones y lecciones)
pub struct MemoriaLargoTermino {
    patrones: Arc<Mutex<Vec<PatronMemoria>>>,
    max_patrones: usize,
}

/// Patrón guardado en memoria
#[derive(Debug, Clone)]
pub struct PatronMemoria {
    /// Descripción del patrón
    pub descripcion: String,
    /// Contexto donde ocurrió
    pub contexto: JsonValue,
    /// Lección aprendida
    pub leccion: String,
    /// Contador de ocurrencias
    pub ocurrencias: usize,
    /// Timestamp de último acceso
    pub ultimo_acceso: i64,
}

impl MemoriaLargoTermino {
    /// Crear nueva memoria a largo plazo
    pub fn nueva(max_patrones: usize) -> Self {
        Self {
            patrones: Arc::new(Mutex::new(Vec::new())),
            max_patrones,
        }
    }

    /// Guardar patrón
    pub fn guardar_patron(
        &self,
        descripcion: String,
        contexto: JsonValue,
        leccion: String,
    ) {
        if let Ok(mut patrones) = self.patrones.lock() {
            let patron = PatronMemoria {
                descripcion,
                contexto,
                leccion,
                ocurrencias: 1,
                ultimo_acceso: chrono::Utc::now().timestamp(),
            };
            patrones.push(patron);

            if patrones.len() > self.max_patrones {
                patrones.remove(0);
            }
        }
    }

    /// Obtener patrones relevantes
    pub fn obtener_patrones(&self) -> Vec<PatronMemoria> {
        if let Ok(patrones) = self.patrones.lock() {
            patrones.clone()
        } else {
            Vec::new()
        }
    }

    /// Contar patrones
    pub fn contar(&self) -> usize {
        if let Ok(patrones) = self.patrones.lock() {
            patrones.len()
        } else {
            0
        }
    }
}

/// Sistema integrado de memoria
pub struct SistemaMemoria {
    pub corto_plazo: MemoriaCortoTermino,
    pub largo_plazo: MemoriaLargoTermino,
}

impl SistemaMemoria {
    /// Crear nuevo sistema de memoria
    pub fn nuevo(max_corto: usize, max_largo: usize) -> Self {
        Self {
            corto_plazo: MemoriaCortoTermino::nueva(max_corto),
            largo_plazo: MemoriaLargoTermino::nueva(max_largo),
        }
    }

    /// Registrar evento
    pub fn registrar_evento(&self, evento: JsonValue) {
        self.corto_plazo.agregar(evento);
    }

    /// Resumen del sistema
    pub fn resumen(&self) -> JsonValue {
        json!({
            "corto_plazo": self.corto_plazo.contar(),
            "largo_plazo": self.largo_plazo.contar(),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_memoria_corto_plazo() {
        let mem = MemoriaCortoTermino::nueva(3);
        mem.agregar(json!({"evento": 1}));
        mem.agregar(json!({"evento": 2}));
        mem.agregar(json!({"evento": 3}));

        assert_eq!(mem.contar(), 3);
    }

    #[test]
    fn test_memoria_limite() {
        let mem = MemoriaCortoTermino::nueva(2);
        mem.agregar(json!({"evento": 1}));
        mem.agregar(json!({"evento": 2}));
        mem.agregar(json!({"evento": 3}));

        assert_eq!(mem.contar(), 2);
    }

    #[test]
    fn test_obtener_ultimos() {
        let mem = MemoriaCortoTermino::nueva(5);
        mem.agregar(json!({"n": 1}));
        mem.agregar(json!({"n": 2}));
        mem.agregar(json!({"n": 3}));

        let ultimos = mem.obtener_ultimos(2);
        assert_eq!(ultimos.len(), 2);
    }

    #[test]
    fn test_memoria_largo_plazo() {
        let mem = MemoriaLargoTermino::nueva(5);
        mem.guardar_patron(
            "Patrón 1".to_string(),
            json!({"contexto": "test"}),
            "Lección 1".to_string(),
        );

        assert_eq!(mem.contar(), 1);
    }

    #[test]
    fn test_sistema_memoria() {
        let sistema = SistemaMemoria::nuevo(5, 5);
        sistema.registrar_evento(json!({"dato": "test"}));

        let resumen = sistema.resumen();
        assert_eq!(resumen["corto_plazo"], 1);
    }

    #[test]
    fn test_limpiar_memoria() {
        let mem = MemoriaCortoTermino::nueva(5);
        mem.agregar(json!({"test": 1}));
        mem.agregar(json!({"test": 2}));
        mem.limpiar();

        assert_eq!(mem.contar(), 0);
    }
}
