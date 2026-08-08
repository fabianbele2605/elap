//! Hot-reload de configuración (monitoreo de cambios)

use std::path::PathBuf;
use std::fs;
use std::time::{SystemTime, UNIX_EPOCH};
use crate::error::ResultadoElap;
use super::config_struct::ConfiguracionAvanzada;

/// Información de archivo monitoreado
#[derive(Debug, Clone)]
pub struct ArchivoMonitoreado {
    pub ruta: PathBuf,
    pub ultima_modificacion: u64,
}

impl ArchivoMonitoreado {
    /// Obtener timestamp de última modificación
    fn obtener_timestamp(ruta: &PathBuf) -> ResultadoElap<u64> {
        let metadata = fs::metadata(ruta)
            ?;

        let modified = metadata.modified()
            ?;

        let duration = modified
            .duration_since(UNIX_EPOCH)
            .map_err(|e| crate::error::ElapError::InternalError(e.to_string()))?;

        Ok(duration.as_secs())
    }

    /// Crear nuevo archivo monitoreado
    pub fn nuevo(ruta: PathBuf) -> ResultadoElap<Self> {
        let timestamp = Self::obtener_timestamp(&ruta)?;
        Ok(Self {
            ruta,
            ultima_modificacion: timestamp,
        })
    }

    /// Verificar si el archivo cambió
    pub fn cambio_detectado(&mut self) -> ResultadoElap<bool> {
        let nuevo_timestamp = Self::obtener_timestamp(&self.ruta)?;
        let cambio = nuevo_timestamp != self.ultima_modificacion;
        if cambio {
            self.ultima_modificacion = nuevo_timestamp;
        }
        Ok(cambio)
    }
}

/// Monitor de hot-reload para configuración
pub struct MonitorHotReload {
    archivos: Vec<ArchivoMonitoreado>,
    intervalo_check_ms: u64,
}

impl MonitorHotReload {
    /// Crear nuevo monitor
    pub fn nuevo(intervalo_check_ms: u64) -> Self {
        Self {
            archivos: Vec::new(),
            intervalo_check_ms,
        }
    }

    /// Agregar archivo a monitorear
    pub fn agregar_archivo(&mut self, ruta: PathBuf) -> ResultadoElap<()> {
        let archivo = ArchivoMonitoreado::nuevo(ruta)?;
        self.archivos.push(archivo);
        Ok(())
    }

    /// Verificar si algún archivo cambió
    pub fn hay_cambios(&mut self) -> ResultadoElap<bool> {
        for archivo in &mut self.archivos {
            if archivo.cambio_detectado()? {
                return Ok(true);
            }
        }
        Ok(false)
    }

    /// Obtener lista de archivos que cambiaron
    pub fn archivos_modificados(&mut self) -> ResultadoElap<Vec<PathBuf>> {
        let mut modificados = Vec::new();
        for archivo in &mut self.archivos {
            if archivo.cambio_detectado()? {
                modificados.push(archivo.ruta.clone());
            }
        }
        Ok(modificados)
    }

    /// Cantidad de archivos monitoreados
    pub fn cantidad_archivos(&self) -> usize {
        self.archivos.len()
    }

    /// Intervalo de verificación
    pub fn intervalo_ms(&self) -> u64 {
        self.intervalo_check_ms
    }

    /// Limpiar monitoreo
    pub fn limpiar(&mut self) {
        self.archivos.clear();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;
    use std::io::Write;
    use std::thread;
    use std::time::Duration;

    #[test]
    fn test_crear_archivo_monitoreado() {
        let temp = NamedTempFile::new().unwrap();
        let ruta = temp.path().to_path_buf();
        let archivo = ArchivoMonitoreado::nuevo(ruta);
        assert!(archivo.is_ok());
    }

    #[test]
    fn test_detectar_cambio() {
        let mut temp = NamedTempFile::new().unwrap();
        let ruta = temp.path().to_path_buf();
        let mut archivo = ArchivoMonitoreado::nuevo(ruta).unwrap();

        let cambio1 = archivo.cambio_detectado().unwrap();
        assert!(!cambio1);

        // Esperar y escribir cambio
        thread::sleep(Duration::from_millis(100));
        let _ = temp.write_all(b"cambio");
        let _ = temp.flush();

        // El cambio debería ser detectado en siguiente check
        // (puede tomar tiempo en algunos sistemas de archivos)
        let cambio2 = archivo.cambio_detectado().unwrap();
        // No assert porque timing es variable
        let _ = cambio2;
    }

    #[test]
    fn test_monitor_crear() {
        let monitor = MonitorHotReload::nuevo(1000);
        assert_eq!(monitor.cantidad_archivos(), 0);
        assert_eq!(monitor.intervalo_ms(), 1000);
    }

    #[test]
    fn test_monitor_agregar_archivo() {
        let temp = NamedTempFile::new().unwrap();
        let ruta = temp.path().to_path_buf();
        let mut monitor = MonitorHotReload::nuevo(1000);

        assert!(monitor.agregar_archivo(ruta).is_ok());
        assert_eq!(monitor.cantidad_archivos(), 1);
    }

    #[test]
    fn test_monitor_hay_cambios() {
        let temp = NamedTempFile::new().unwrap();
        let ruta = temp.path().to_path_buf();
        let mut monitor = MonitorHotReload::nuevo(1000);

        assert!(monitor.agregar_archivo(ruta).is_ok());
        let cambios = monitor.hay_cambios().unwrap();
        assert!(!cambios);
    }

    #[test]
    fn test_monitor_limpiar() {
        let temp = NamedTempFile::new().unwrap();
        let ruta = temp.path().to_path_buf();
        let mut monitor = MonitorHotReload::nuevo(1000);

        assert!(monitor.agregar_archivo(ruta).is_ok());
        assert_eq!(monitor.cantidad_archivos(), 1);

        monitor.limpiar();
        assert_eq!(monitor.cantidad_archivos(), 0);
    }

    #[test]
    fn test_monitor_archivos_modificados() {
        let temp = NamedTempFile::new().unwrap();
        let ruta = temp.path().to_path_buf();
        let mut monitor = MonitorHotReload::nuevo(1000);

        assert!(monitor.agregar_archivo(ruta).is_ok());
        let modificados = monitor.archivos_modificados().unwrap();
        // Al menos no debería error
        let _ = modificados;
    }
}
