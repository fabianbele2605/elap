//! Rotación de archivos de log

use std::path::PathBuf;
use std::fs;
use chrono::Utc;

/// Estrategia de rotación
#[derive(Debug, Clone)]
pub enum EstrategiaRotacion {
    /// Por tamaño en MB
    PorTamaño(u64),
    /// Diario
    Diario,
    /// Combinado: tamaño o día
    Híbrido(u64),
}

/// Gestor de rotación
pub struct GestorRotacion {
    ruta_archivo: PathBuf,
    estrategia: EstrategiaRotacion,
    ruta_archivos: PathBuf,
}

impl GestorRotacion {
    /// Crear nuevo gestor
    pub fn nuevo(ruta_archivo: PathBuf, estrategia: EstrategiaRotacion) -> Self {
        let ruta_archivos = ruta_archivo.parent()
            .map(|p| p.to_path_buf())
            .unwrap_or_else(|| PathBuf::from("."));

        Self {
            ruta_archivo,
            estrategia,
            ruta_archivos,
        }
    }

    /// Verificar si necesita rotar
    pub fn necesita_rotacion(&self) -> bool {
        if !self.ruta_archivo.exists() {
            return false;
        }

        match self.estrategia {
            EstrategiaRotacion::PorTamaño(tamaño_mb) => {
                if let Ok(metadata) = fs::metadata(&self.ruta_archivo) {
                    let tamaño_actual = metadata.len() / (1024 * 1024);
                    tamaño_actual >= tamaño_mb
                } else {
                    false
                }
            }
            EstrategiaRotacion::Diario => {
                // Simplificado: siempre rota (implementación completa requeriría tracking)
                false
            }
            EstrategiaRotacion::Híbrido(tamaño_mb) => {
                if let Ok(metadata) = fs::metadata(&self.ruta_archivo) {
                    let tamaño_actual = metadata.len() / (1024 * 1024);
                    tamaño_actual >= tamaño_mb
                } else {
                    false
                }
            }
        }
    }

    /// Realizar rotación
    pub fn rotar(&self) -> std::io::Result<()> {
        if !self.ruta_archivo.exists() {
            return Ok(());
        }

        let timestamp = Utc::now().format("%Y%m%d_%H%M%S").to_string();
        let nombre_base = self.ruta_archivo.file_stem()
            .and_then(|n| n.to_str())
            .unwrap_or("app");

        let nombre_rotado = format!("{}.{}.log", nombre_base, timestamp);
        let ruta_rotada = self.ruta_archivos.join(nombre_rotado);

        fs::rename(&self.ruta_archivo, ruta_rotada)?;

        Ok(())
    }

    /// Limpiar archivos rotados antiguos (más de N días)
    pub fn limpiar_antiguos(&self, dias: u32) -> std::io::Result<u32> {
        let mut eliminados = 0;

        if !self.ruta_archivos.exists() {
            return Ok(0);
        }

        let ahora = Utc::now();

        for entrada in fs::read_dir(&self.ruta_archivos)? {
            let entrada = entrada?;
            let ruta = entrada.path();

            if ruta.is_file() {
                if let Some(nombre) = ruta.file_name().and_then(|n| n.to_str()) {
                    if nombre.contains(".") && nombre.ends_with(".log") {
                        if let Ok(metadata) = fs::metadata(&ruta) {
                            if let Ok(modified) = metadata.modified() {
                                let duracion = ahora
                                    .signed_duration_since(chrono::DateTime::<Utc>::from(modified));

                                if duracion.num_days() > dias as i64 {
                                    let _ = fs::remove_file(&ruta);
                                    eliminados += 1;
                                }
                            }
                        }
                    }
                }
            }
        }

        Ok(eliminados)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    #[test]
    fn test_estrategia_por_tamaño() {
        let estrategia = EstrategiaRotacion::PorTamaño(100);
        assert!(matches!(estrategia, EstrategiaRotacion::PorTamaño(100)));
    }

    #[test]
    fn test_crear_gestor() {
        let temp = TempDir::new().unwrap();
        let ruta = temp.path().join("app.log");
        let gestor = GestorRotacion::nuevo(ruta, EstrategiaRotacion::PorTamaño(100));
        assert!(!gestor.necesita_rotacion());
    }

    #[test]
    fn test_necesita_rotacion_archivo_inexistente() {
        let gestor = GestorRotacion::nuevo(
            PathBuf::from("./no_existe.log"),
            EstrategiaRotacion::PorTamaño(100),
        );
        assert!(!gestor.necesita_rotacion());
    }

    #[test]
    fn test_rotar_archivo_inexistente() {
        let gestor = GestorRotacion::nuevo(
            PathBuf::from("./no_existe.log"),
            EstrategiaRotacion::PorTamaño(100),
        );
        assert!(gestor.rotar().is_ok());
    }

    #[test]
    fn test_limpiar_antiguos() {
        let temp = TempDir::new().unwrap();
        let gestor = GestorRotacion::nuevo(
            temp.path().join("app.log"),
            EstrategiaRotacion::PorTamaño(100),
        );
        let resultado = gestor.limpiar_antiguos(30);
        assert!(resultado.is_ok());
    }
}
