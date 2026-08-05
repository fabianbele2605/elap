use std::process::{Command, Child};
use crate::procesos::error::{ErrorProceso, ResultadoProceso};
use crate::procesos::proceso::Proceso;

/// Crea y ejecuta procesos del sistema operativo.
pub struct Spawner;

impl Spawner {
    /// Crea e inicia un nuevo proceso.
    pub fn ejecutar(proceso: &Proceso) -> ResultadoProceso<Child> {
        let mut cmd = Command::new(&proceso.comando);

        for arg in &proceso.argumentos {
            cmd.arg(arg);
        }

        cmd.spawn().map_err(|e| {
            ErrorProceso::NoSePudoCrear(format!(
                "Proceso '{}' ({}): {}",
                proceso.nombre, proceso.comando, e
            ))
        })
    }

    /// Espera a que un proceso termine y devuelve su código de salida.
    pub fn esperar_completacion(mut child: Child) -> ResultadoProceso<i32> {
        let status = child.wait()?;

        status
            .code()
            .ok_or_else(|| {
                ErrorProceso::ProcesoFallo(-1)
            })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Duration;
    use std::thread;

    #[test]
    fn test_ejecutar_comando_simple() {
        let proceso = Proceso::nueva("echo_test".to_string(), "echo".to_string())
            .con_argumentos(vec!["prueba".to_string()]);

        let resultado = Spawner::ejecutar(&proceso);
        assert!(resultado.is_ok());
    }

    #[test]
    fn test_comando_no_existe() {
        let proceso = Proceso::nueva(
            "comando_inexistente".to_string(),
            "comando_que_no_existe_12345".to_string(),
        );

        let resultado = Spawner::ejecutar(&proceso);
        assert!(resultado.is_err());
    }

    #[test]
    fn test_esperar_completacion_exitosa() {
        let proceso = Proceso::nueva("true_test".to_string(), "true".to_string());
        let child = Spawner::ejecutar(&proceso).expect("Debería crear el proceso");

        let codigo = Spawner::esperar_completacion(child);
        assert!(codigo.is_ok());
        assert_eq!(codigo.unwrap(), 0);
    }

    #[test]
    fn test_esperar_completacion_fallida() {
        let proceso = Proceso::nueva("false_test".to_string(), "false".to_string());
        let child = Spawner::ejecutar(&proceso).expect("Debería crear el proceso");

        let codigo = Spawner::esperar_completacion(child);
        assert!(codigo.is_ok());
        assert_eq!(codigo.unwrap(), 1);
    }
}
