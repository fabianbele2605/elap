use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::Mutex;

use crate::procesos::error::ResultadoProceso;
use crate::procesos::proceso::{Proceso, EstadoProceso, IdProceso};
use crate::procesos::spawner::Spawner;

/// Gestor central de procesos del sistema.
#[derive(Clone)]
pub struct GestorProcesos {
    procesos: Arc<Mutex<HashMap<IdProceso, Proceso>>>,
}

impl GestorProcesos {
    /// Crea un nuevo gestor de procesos.
    pub async fn nuevo() -> Self {
        GestorProcesos {
            procesos: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Crea un nuevo proceso sin argumentos.
    pub async fn crear_proceso(
        &self,
        nombre: String,
        comando: String,
    ) -> IdProceso {
        let proceso = Proceso::nueva(nombre, comando);
        let id = proceso.id;

        let mut procesos = self.procesos.lock().await;
        procesos.insert(id, proceso);

        id
    }

    /// Crea un nuevo proceso con argumentos.
    pub async fn crear_proceso_con_args(
        &self,
        nombre: String,
        comando: String,
        args: Vec<String>,
    ) -> IdProceso {
        let proceso = Proceso::nueva(nombre, comando).con_argumentos(args);
        let id = proceso.id;

        let mut procesos = self.procesos.lock().await;
        procesos.insert(id, proceso);

        id
    }

    /// Ejecuta un proceso de forma sincrónica (bloqueante).
    pub async fn ejecutar_proceso(&self, id: IdProceso) -> ResultadoProceso<i32> {
        let mut procesos = self.procesos.lock().await;

        let proceso = procesos
            .get_mut(&id)
            .ok_or_else(|| {
                crate::procesos::error::ErrorProceso::ProcesoNoEncontrado(id.to_string())
            })?;

        proceso.establecer_estado(EstadoProceso::Ejecutando);
        let proceso_copia = proceso.clone();

        drop(procesos);

        let resultado = Spawner::ejecutar(&proceso_copia);

        match resultado {
            Ok(child) => {
                let codigo = Spawner::esperar_completacion(child);

                let mut procesos = self.procesos.lock().await;
                if let Some(p) = procesos.get_mut(&id) {
                    match &codigo {
                        Ok(0) => {
                            p.codigo_salida = Some(0);
                            p.establecer_estado(EstadoProceso::Completado);
                        }
                        Ok(code) => {
                            p.codigo_salida = Some(*code);
                            p.establecer_estado(EstadoProceso::Fallo);
                        }
                        Err(_) => {
                            p.codigo_salida = Some(-1);
                            p.establecer_estado(EstadoProceso::Fallo);
                        }
                    }
                }

                codigo
            }
            Err(e) => {
                let mut procesos = self.procesos.lock().await;
                if let Some(p) = procesos.get_mut(&id) {
                    p.codigo_salida = Some(-1);
                    p.establecer_estado(EstadoProceso::Fallo);
                }
                Err(e)
            }
        }
    }

    /// Obtiene el estado actual de un proceso.
    pub async fn obtener_estado(&self, id: IdProceso) -> ResultadoProceso<EstadoProceso> {
        let procesos = self.procesos.lock().await;
        procesos
            .get(&id)
            .map(|p| p.estado)
            .ok_or_else(|| {
                crate::procesos::error::ErrorProceso::ProcesoNoEncontrado(id.to_string())
            })
    }

    /// Obtiene el proceso completo por ID.
    pub async fn obtener_proceso(&self, id: IdProceso) -> ResultadoProceso<Proceso> {
        let procesos = self.procesos.lock().await;
        procesos
            .get(&id)
            .cloned()
            .ok_or_else(|| {
                crate::procesos::error::ErrorProceso::ProcesoNoEncontrado(id.to_string())
            })
    }

    /// Lista todos los procesos.
    pub async fn listar_procesos(&self) -> Vec<Proceso> {
        let procesos = self.procesos.lock().await;
        procesos.values().cloned().collect()
    }

    /// Cuenta cuántos procesos están en ejecución.
    pub async fn contar_ejecutando(&self) -> usize {
        let procesos = self.procesos.lock().await;
        procesos
            .values()
            .filter(|p| p.estado == EstadoProceso::Ejecutando)
            .count()
    }

    /// Cuenta cuántos procesos se completaron exitosamente.
    pub async fn contar_completados(&self) -> usize {
        let procesos = self.procesos.lock().await;
        procesos
            .values()
            .filter(|p| p.estado == EstadoProceso::Completado)
            .count()
    }

    /// Cuenta cuántos procesos fallaron.
    pub async fn contar_fallidos(&self) -> usize {
        let procesos = self.procesos.lock().await;
        procesos
            .values()
            .filter(|p| p.estado == EstadoProceso::Fallo)
            .count()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_crear_proceso() {
        let gestor = GestorProcesos::nuevo().await;
        let id = gestor
            .crear_proceso("test".to_string(), "echo".to_string())
            .await;

        let proceso = gestor.obtener_proceso(id).await.unwrap();
        assert_eq!(proceso.nombre, "test");
        assert_eq!(proceso.estado, EstadoProceso::Pendiente);
    }

    #[tokio::test]
    async fn test_crear_con_argumentos() {
        let gestor = GestorProcesos::nuevo().await;
        let id = gestor
            .crear_proceso_con_args(
                "test_args".to_string(),
                "echo".to_string(),
                vec!["hola".to_string()],
            )
            .await;

        let proceso = gestor.obtener_proceso(id).await.unwrap();
        assert_eq!(proceso.argumentos.len(), 1);
    }

    #[tokio::test]
    async fn test_obtener_estado() {
        let gestor = GestorProcesos::nuevo().await;
        let id = gestor
            .crear_proceso("test_estado".to_string(), "echo".to_string())
            .await;

        let estado = gestor.obtener_estado(id).await.unwrap();
        assert_eq!(estado, EstadoProceso::Pendiente);
    }

    #[tokio::test]
    async fn test_ejecutar_proceso_exitoso() {
        let gestor = GestorProcesos::nuevo().await;
        let id = gestor
            .crear_proceso("true_test".to_string(), "true".to_string())
            .await;

        let resultado = gestor.ejecutar_proceso(id).await;
        assert!(resultado.is_ok());
        assert_eq!(resultado.unwrap(), 0);

        let proceso = gestor.obtener_proceso(id).await.unwrap();
        assert_eq!(proceso.estado, EstadoProceso::Completado);
    }

    #[tokio::test]
    async fn test_ejecutar_proceso_fallido() {
        let gestor = GestorProcesos::nuevo().await;
        let id = gestor
            .crear_proceso("false_test".to_string(), "false".to_string())
            .await;

        let resultado = gestor.ejecutar_proceso(id).await;
        assert!(resultado.is_ok());
        assert_eq!(resultado.unwrap(), 1);

        let proceso = gestor.obtener_proceso(id).await.unwrap();
        assert_eq!(proceso.estado, EstadoProceso::Fallo);
    }

    #[tokio::test]
    async fn test_listar_procesos() {
        let gestor = GestorProcesos::nuevo().await;
        gestor
            .crear_proceso("proc1".to_string(), "echo".to_string())
            .await;
        gestor
            .crear_proceso("proc2".to_string(), "echo".to_string())
            .await;

        let procesos = gestor.listar_procesos().await;
        assert_eq!(procesos.len(), 2);
    }

    #[tokio::test]
    async fn test_contar_completados() {
        let gestor = GestorProcesos::nuevo().await;
        let id = gestor
            .crear_proceso("test".to_string(), "true".to_string())
            .await;

        gestor.ejecutar_proceso(id).await.unwrap();

        let completados = gestor.contar_completados().await;
        assert_eq!(completados, 1);
    }
}
