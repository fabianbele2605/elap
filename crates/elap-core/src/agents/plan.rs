//! Planes y pasos de ejecución

use serde_json::{json, Value as JsonValue};

/// Paso en un plan
#[derive(Debug, Clone)]
pub struct Paso {
    /// Número del paso
    pub numero: usize,
    /// Descripción
    pub descripcion: String,
    /// Tipo de acción (herramienta a usar)
    pub tipo_accion: String,
    /// Parámetros
    pub parametros: JsonValue,
    /// ¿Completado?
    pub completado: bool,
    /// Resultado si está completado
    pub resultado: Option<JsonValue>,
}

impl Paso {
    /// Crear nuevo paso
    pub fn nuevo(
        numero: usize,
        descripcion: String,
        tipo_accion: String,
        parametros: JsonValue,
    ) -> Self {
        Self {
            numero,
            descripcion,
            tipo_accion,
            parametros,
            completado: false,
            resultado: None,
        }
    }

    /// Marcar como completado
    pub fn completar(&mut self, resultado: JsonValue) {
        self.completado = true;
        self.resultado = Some(resultado);
    }
}

/// Plan de ejecución
pub struct Plan {
    /// Identificador
    pub id: String,
    /// Objetivo del plan
    pub objetivo: String,
    /// Pasos del plan
    pub pasos: Vec<Paso>,
    /// Paso actual
    pub paso_actual: usize,
    /// ¿Plan completado?
    pub completado: bool,
}

impl Plan {
    /// Crear nuevo plan
    pub fn nuevo(objetivo: String) -> Self {
        Self {
            id: uuid::Uuid::new_v4().to_string(),
            objetivo,
            pasos: Vec::new(),
            paso_actual: 0,
            completado: false,
        }
    }

    /// Agregar paso al plan
    pub fn agregar_paso(
        &mut self,
        descripcion: String,
        tipo_accion: String,
        parametros: JsonValue,
    ) {
        let numero = self.pasos.len() + 1;
        let paso = Paso::nuevo(numero, descripcion, tipo_accion, parametros);
        self.pasos.push(paso);
    }

    /// Obtener paso actual
    pub fn obtener_paso_actual(&self) -> Option<&Paso> {
        if self.paso_actual < self.pasos.len() {
            Some(&self.pasos[self.paso_actual])
        } else {
            None
        }
    }

    /// Completar paso actual
    pub fn completar_paso_actual(&mut self, resultado: JsonValue) {
        if let Some(paso) = self.pasos.get_mut(self.paso_actual) {
            paso.completar(resultado);
            self.paso_actual += 1;

            if self.paso_actual >= self.pasos.len() {
                self.completado = true;
            }
        }
    }

    /// Progreso del plan
    pub fn progreso(&self) -> f32 {
        if self.pasos.is_empty() {
            0.0
        } else {
            self.paso_actual as f32 / self.pasos.len() as f32
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_plan() {
        let plan = Plan::nuevo("Objetivo test".to_string());
        assert_eq!(plan.objetivo, "Objetivo test");
        assert_eq!(plan.pasos.len(), 0);
    }

    #[test]
    fn test_agregar_pasos() {
        let mut plan = Plan::nuevo("Test".to_string());
        plan.agregar_paso(
            "Paso 1".to_string(),
            "herramienta1".to_string(),
            json!({}),
        );
        plan.agregar_paso(
            "Paso 2".to_string(),
            "herramienta2".to_string(),
            json!({}),
        );

        assert_eq!(plan.pasos.len(), 2);
    }

    #[test]
    fn test_obtener_paso_actual() {
        let mut plan = Plan::nuevo("Test".to_string());
        plan.agregar_paso("Paso 1".to_string(), "tool".to_string(), json!({}));

        let paso = plan.obtener_paso_actual();
        assert!(paso.is_some());
        assert_eq!(paso.unwrap().numero, 1);
    }

    #[test]
    fn test_completar_paso() {
        let mut plan = Plan::nuevo("Test".to_string());
        plan.agregar_paso("Paso 1".to_string(), "tool".to_string(), json!({}));
        plan.agregar_paso("Paso 2".to_string(), "tool".to_string(), json!({}));

        plan.completar_paso_actual(json!({"resultado": "ok"}));
        assert_eq!(plan.paso_actual, 1);
        assert!(!plan.completado);

        plan.completar_paso_actual(json!({"resultado": "ok"}));
        assert!(plan.completado);
    }

    #[test]
    fn test_progreso() {
        let mut plan = Plan::nuevo("Test".to_string());
        plan.agregar_paso("P1".to_string(), "t".to_string(), json!({}));
        plan.agregar_paso("P2".to_string(), "t".to_string(), json!({}));

        assert_eq!(plan.progreso(), 0.0);
        plan.completar_paso_actual(json!({}));
        assert_eq!(plan.progreso(), 0.5);
    }
}
