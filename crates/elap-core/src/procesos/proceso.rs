use std::time::{SystemTime, UNIX_EPOCH};
use uuid::Uuid;

/// Identificador único de un proceso.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct IdProceso(Uuid);

impl IdProceso {
    pub fn nueva() -> Self {
        IdProceso(Uuid::new_v4())
    }

    pub fn como_string(&self) -> String {
        self.0.to_string()
    }
}

impl std::fmt::Display for IdProceso {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

/// Estado actual de un proceso.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EstadoProceso {
    /// Esperando ser ejecutado.
    Pendiente,
    /// Actualmente en ejecución.
    Ejecutando,
    /// Completado exitosamente.
    Completado,
    /// Falló durante la ejecución.
    Fallo,
}

impl std::fmt::Display for EstadoProceso {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            EstadoProceso::Pendiente => write!(f, "Pendiente"),
            EstadoProceso::Ejecutando => write!(f, "Ejecutando"),
            EstadoProceso::Completado => write!(f, "Completado"),
            EstadoProceso::Fallo => write!(f, "Fallo"),
        }
    }
}

/// Representa un proceso del sistema operativo.
#[derive(Debug, Clone)]
pub struct Proceso {
    /// Identificador único.
    pub id: IdProceso,
    /// Nombre descriptivo del proceso.
    pub nombre: String,
    /// Comando a ejecutar.
    pub comando: String,
    /// Argumentos del comando.
    pub argumentos: Vec<String>,
    /// Estado actual.
    pub estado: EstadoProceso,
    /// Código de salida (si ya finalizó).
    pub codigo_salida: Option<i32>,
    /// Timestamp de creación (segundos desde época).
    pub creado_en: u64,
    /// Timestamp cuando inició la ejecución.
    pub iniciado_en: Option<u64>,
    /// Timestamp cuando finalizó.
    pub finalizado_en: Option<u64>,
}

impl Proceso {
    /// Crea un nuevo proceso.
    pub fn nueva(nombre: String, comando: String) -> Self {
        let ahora = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();

        Proceso {
            id: IdProceso::nueva(),
            nombre,
            comando,
            argumentos: Vec::new(),
            estado: EstadoProceso::Pendiente,
            codigo_salida: None,
            creado_en: ahora,
            iniciado_en: None,
            finalizado_en: None,
        }
    }

    /// Establece los argumentos del comando.
    pub fn con_argumentos(mut self, args: Vec<String>) -> Self {
        self.argumentos = args;
        self
    }

    /// Cambia el estado del proceso y actualiza timestamps.
    pub fn establecer_estado(&mut self, estado: EstadoProceso) {
        self.estado = estado;

        match estado {
            EstadoProceso::Ejecutando => {
                self.iniciado_en = Some(
                    SystemTime::now()
                        .duration_since(UNIX_EPOCH)
                        .unwrap_or_default()
                        .as_secs(),
                );
            }
            EstadoProceso::Completado | EstadoProceso::Fallo => {
                self.finalizado_en = Some(
                    SystemTime::now()
                        .duration_since(UNIX_EPOCH)
                        .unwrap_or_default()
                        .as_secs(),
                );
            }
            _ => {}
        }
    }

    /// Retorna cuántos segundos lleva en ejecución.
    pub fn tiempo_transcurrido(&self) -> Option<u64> {
        self.iniciado_en.map(|inicio| {
            let fin = self.finalizado_en.unwrap_or_else(|| {
                SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_secs()
            });
            fin - inicio
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_proceso() {
        let proceso = Proceso::nueva("test_proc".to_string(), "ls".to_string());
        assert_eq!(proceso.nombre, "test_proc");
        assert_eq!(proceso.comando, "ls");
        assert_eq!(proceso.estado, EstadoProceso::Pendiente);
    }

    #[test]
    fn test_id_proceso_unica() {
        let p1 = IdProceso::nueva();
        let p2 = IdProceso::nueva();
        assert_ne!(p1, p2);
    }

    #[test]
    fn test_con_argumentos() {
        let proceso = Proceso::nueva("test".to_string(), "echo".to_string())
            .con_argumentos(vec!["hola".to_string(), "mundo".to_string()]);
        assert_eq!(proceso.argumentos.len(), 2);
    }

    #[test]
    fn test_cambiar_estado() {
        let mut proceso = Proceso::nueva("test".to_string(), "ls".to_string());
        proceso.establecer_estado(EstadoProceso::Ejecutando);
        assert_eq!(proceso.estado, EstadoProceso::Ejecutando);
        assert!(proceso.iniciado_en.is_some());

        proceso.establecer_estado(EstadoProceso::Completado);
        assert_eq!(proceso.estado, EstadoProceso::Completado);
        assert!(proceso.finalizado_en.is_some());
    }
}
