//! Cargador dinámico de plugins

use std::path::PathBuf;
use std::fs;
use crate::error::ResultadoElap;
use super::metadata::PluginMetadata;

/// Cargador de plugins con validación
pub struct PluginLoader {
    directorio_plugins: PathBuf,
}

impl PluginLoader {
    /// Crear nuevo cargador
    pub fn nuevo(directorio: PathBuf) -> Self {
        Self {
            directorio_plugins: directorio,
        }
    }

    /// Validar que el binario existe
    pub fn validar_binario(&self, ruta: &PathBuf) -> ResultadoElap<()> {
        if !ruta.exists() {
            return Err(crate::error::ElapError::ValidationError(
                format!("Plugin no encontrado: {:?}", ruta)
            ));
        }
        Ok(())
    }

    /// Validar metadatos del plugin
    pub fn validar_metadata(&self, metadata: &PluginMetadata) -> ResultadoElap<()> {
        if metadata.nombre.is_empty() {
            return Err(crate::error::ElapError::ValidationError(
                "Nombre del plugin vacío".to_string()
            ));
        }

        if metadata.version.is_empty() {
            return Err(crate::error::ElapError::ValidationError(
                "Versión del plugin vacía".to_string()
            ));
        }

        if metadata.punto_entrada.is_empty() {
            return Err(crate::error::ElapError::ValidationError(
                "Punto de entrada vacío".to_string()
            ));
        }

        Ok(())
    }

    /// Cargar plugin desde metadatos
    pub fn cargar(&self, metadata: PluginMetadata) -> ResultadoElap<PluginMetadata> {
        self.validar_binario(&PathBuf::from(&metadata.ruta_binario))?;
        self.validar_metadata(&metadata)?;

        Ok(metadata)
    }

    /// Descubrir plugins en directorio (extensión .so, .dll, .dylib)
    pub fn descubrir(&self) -> ResultadoElap<Vec<PathBuf>> {
        if !self.directorio_plugins.exists() {
            return Ok(Vec::new());
        }

        let mut plugins = Vec::new();

        match fs::read_dir(&self.directorio_plugins) {
            Ok(entries) => {
                for entry in entries.flatten() {
                    let path = entry.path();
                    if let Some(ext) = path.extension() {
                        let ext_str = ext.to_string_lossy();
                        if ext_str == "so" || ext_str == "dll" || ext_str == "dylib" {
                            plugins.push(path);
                        }
                    }
                }
            }
            Err(_) => return Ok(Vec::new()),
        }

        Ok(plugins)
    }

    /// Cargar plugin por nombre desde directorio
    pub fn cargar_por_nombre(&self, nombre: &str) -> ResultadoElap<PathBuf> {
        let plugins = self.descubrir()?;

        for plugin_path in plugins {
            if let Some(file_name) = plugin_path.file_name() {
                let file_str = file_name.to_string_lossy();
                if file_str.contains(nombre) {
                    return Ok(plugin_path);
                }
            }
        }

        Err(crate::error::ElapError::ValidationError(
            format!("Plugin '{}' no encontrado en directorio", nombre)
        ))
    }

    /// Calcular hash SHA256 de un archivo
    pub fn calcular_hash(&self, ruta: &PathBuf) -> ResultadoElap<String> {
        use std::io::Read;

        let mut file = fs::File::open(ruta)?;

        let mut contenido = Vec::new();
        file.read_to_end(&mut contenido)?;

        let digest = ring::digest::digest(&ring::digest::SHA256, &contenido);
        Ok(hex::encode(digest.as_ref()))
    }

    /// Directorio de plugins
    pub fn directorio(&self) -> &PathBuf {
        &self.directorio_plugins
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_loader() {
        let loader = PluginLoader::nuevo(PathBuf::from("./plugins"));
        assert_eq!(
            loader.directorio_plugins,
            PathBuf::from("./plugins")
        );
    }

    #[test]
    fn test_validar_metadata_valida() {
        let loader = PluginLoader::nuevo(PathBuf::from("./plugins"));
        let metadata = PluginMetadata::nuevo(
            "test".to_string(),
            "1.0.0".to_string(),
            "autor".to_string(),
            "desc".to_string(),
            "./test.so".to_string(),
            "plugin_init".to_string(),
        );

        assert!(loader.validar_metadata(&metadata).is_ok());
    }

    #[test]
    fn test_validar_metadata_nombre_vacio() {
        let loader = PluginLoader::nuevo(PathBuf::from("./plugins"));
        let metadata = PluginMetadata::nuevo(
            "".to_string(),
            "1.0.0".to_string(),
            "autor".to_string(),
            "desc".to_string(),
            "./test.so".to_string(),
            "plugin_init".to_string(),
        );

        assert!(loader.validar_metadata(&metadata).is_err());
    }

    #[test]
    fn test_descubrir_plugins_directorio_inexistente() {
        let loader = PluginLoader::nuevo(PathBuf::from("./no_existe"));
        let result = loader.descubrir();
        assert!(result.is_ok());
        assert!(result.unwrap().is_empty());
    }

    #[test]
    fn test_cargar_por_nombre_no_encontrado() {
        let loader = PluginLoader::nuevo(PathBuf::from("./no_existe"));
        let result = loader.cargar_por_nombre("inexistente");
        assert!(result.is_err());
    }

    #[test]
    fn test_directorio_getter() {
        let dir = PathBuf::from("./plugins");
        let loader = PluginLoader::nuevo(dir.clone());
        assert_eq!(loader.directorio(), &dir);
    }

    #[test]
    fn test_validar_metadata_version_vacia() {
        let loader = PluginLoader::nuevo(PathBuf::from("./plugins"));
        let metadata = PluginMetadata::nuevo(
            "test".to_string(),
            "".to_string(),
            "autor".to_string(),
            "desc".to_string(),
            "./test.so".to_string(),
            "plugin_init".to_string(),
        );

        assert!(loader.validar_metadata(&metadata).is_err());
    }

    #[test]
    fn test_validar_metadata_punto_entrada_vacio() {
        let loader = PluginLoader::nuevo(PathBuf::from("./plugins"));
        let metadata = PluginMetadata::nuevo(
            "test".to_string(),
            "1.0.0".to_string(),
            "autor".to_string(),
            "desc".to_string(),
            "./test.so".to_string(),
            "".to_string(),
        );

        assert!(loader.validar_metadata(&metadata).is_err());
    }

    #[test]
    fn test_calcular_hash_archivo_inexistente() {
        let loader = PluginLoader::nuevo(PathBuf::from("./plugins"));
        let resultado = loader.calcular_hash(&PathBuf::from("./archivo_no_existe.so"));
        assert!(resultado.is_err());
    }

    #[test]
    fn test_calcular_hash_archivo_valido() {
        use std::io::Write;
        use tempfile::NamedTempFile;

        let loader = PluginLoader::nuevo(PathBuf::from("./plugins"));
        let mut temp_file = NamedTempFile::new().unwrap();
        temp_file.write_all(b"contenido_test").unwrap();

        let resultado = loader.calcular_hash(&temp_file.path().to_path_buf());
        assert!(resultado.is_ok());

        let hash = resultado.unwrap();
        assert!(!hash.is_empty());
        assert_eq!(hash.len(), 64);
    }
}
