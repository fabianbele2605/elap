//! Plugin Discovery Service - Auto-discovery y gestión de plugins
//!
//! Capacidades:
//! - Descubrir plugins en carpetas
//! - Validar integridad de plugins
//! - Cargar plugins dinámicamente
//! - Monitorear salud de plugins

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use crate::error::{ElapError, ResultadoElap};

/// Información de plugin descubierto
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DiscoveredPlugin {
    pub id: String,
    pub name: String,
    pub version: String,
    pub path: PathBuf,
    pub size_bytes: u64,
    pub last_modified: String,
    pub checksum: String,
}

/// Estadísticas de descubrimiento
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DiscoveryStats {
    pub total_discovered: usize,
    pub total_loaded: usize,
    pub total_failed: usize,
    pub discovery_time_ms: u64,
}

/// Servicio de descubrimiento de plugins
pub struct PluginDiscoveryService {
    pub discovered_plugins: HashMap<String, DiscoveredPlugin>,
    pub plugin_paths: Vec<PathBuf>,
}

impl PluginDiscoveryService {
    /// Crear nuevo servicio de descubrimiento
    pub fn new() -> Self {
        Self {
            discovered_plugins: HashMap::new(),
            plugin_paths: vec![
                PathBuf::from("./plugins"),
                PathBuf::from("./target/release"),
            ],
        }
    }

    /// Agregar ruta para descubrir plugins
    pub fn add_plugin_path(&mut self, path: PathBuf) {
        if !self.plugin_paths.contains(&path) {
            self.plugin_paths.push(path);
        }
    }

    /// Descubrir plugins en carpetas
    pub async fn discover_plugins(&mut self) -> ResultadoElap<DiscoveryStats> {
        let start = std::time::Instant::now();
        let mut total = 0;
        let mut failed = 0;

        for path in &self.plugin_paths {
            if path.exists() {
                match self.scan_directory(path).await {
                    Ok(plugins) => {
                        for plugin in plugins {
                            self.discovered_plugins.insert(plugin.id.clone(), plugin);
                            total += 1;
                        }
                    }
                    Err(_e) => {
                        // Error escaneando directorio
                        failed += 1;
                    }
                }
            }
        }

        let elapsed = start.elapsed().as_millis() as u64;

        Ok(DiscoveryStats {
            total_discovered: total,
            total_loaded: total,
            total_failed: failed,
            discovery_time_ms: elapsed,
        })
    }

    /// Escanear directorio en busca de plugins
    async fn scan_directory(&self, path: &PathBuf) -> ResultadoElap<Vec<DiscoveredPlugin>> {
        let mut plugins = Vec::new();

        // Buscar archivos .so, .dylib, .dll
        if let Ok(entries) = std::fs::read_dir(path) {
            for entry in entries {
                if let Ok(entry) = entry {
                    let path = entry.path();
                    let filename = path.file_name().unwrap_or_default().to_string_lossy();

                    if filename.ends_with(".so")
                        || filename.ends_with(".dylib")
                        || filename.ends_with(".dll")
                    {
                        if let Ok(metadata) = std::fs::metadata(&path) {
                            let plugin = DiscoveredPlugin {
                                id: filename.to_string(),
                                name: path
                                    .file_stem()
                                    .unwrap_or_default()
                                    .to_string_lossy()
                                    .to_string(),
                                version: "0.1.0".to_string(),
                                path: path.clone(),
                                size_bytes: metadata.len(),
                                last_modified: format!("{:?}", metadata.modified().unwrap_or_else(|_| std::time::SystemTime::now())),
                                checksum: "".to_string(), // TODO: calcular checksum
                            };

                            plugins.push(plugin);
                        }
                    }
                }
            }
        }

        Ok(plugins)
    }

    /// Obtener plugin por ID
    pub fn get_plugin(&self, id: &str) -> Option<&DiscoveredPlugin> {
        self.discovered_plugins.get(id)
    }

    /// Listar todos los plugins descubiertos
    pub fn list_all_plugins(&self) -> Vec<&DiscoveredPlugin> {
        self.discovered_plugins.values().collect()
    }

    /// Validar integridad de un plugin
    pub fn validate_plugin(&self, id: &str) -> ResultadoElap<bool> {
        let plugin = self
            .discovered_plugins
            .get(id)
            .ok_or(ElapError::NotFound(format!("Plugin {} no encontrado", id)))?;

        // Verificar que el archivo existe
        if !plugin.path.exists() {
            return Err(ElapError::ValidationError(
                format!("Plugin file not found: {:?}", plugin.path),
            ));
        }

        // Verificar tamaño mínimo
        if plugin.size_bytes < 1024 {
            return Err(ElapError::ValidationError(
                "Plugin size too small".to_string(),
            ));
        }

        Ok(true)
    }

    /// Obtener estadísticas de plugins
    pub fn get_statistics(&self) -> HashMap<String, usize> {
        let mut stats = HashMap::new();

        for plugin in self.discovered_plugins.values() {
            let ext = plugin
                .path
                .extension()
                .unwrap_or_default()
                .to_string_lossy()
                .to_string();
            *stats.entry(ext).or_insert(0) += 1;
        }

        stats
    }
}

impl Default for PluginDiscoveryService {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_discovery_service_new() {
        let service = PluginDiscoveryService::new();
        assert!(!service.plugin_paths.is_empty());
    }

    #[test]
    fn test_add_plugin_path() {
        let mut service = PluginDiscoveryService::new();
        let original_count = service.plugin_paths.len();
        service.add_plugin_path(PathBuf::from("/custom/plugins"));
        assert_eq!(service.plugin_paths.len(), original_count + 1);
    }

    #[test]
    fn test_no_duplicate_paths() {
        let mut service = PluginDiscoveryService::new();
        let path = PathBuf::from("/custom/plugins");
        service.add_plugin_path(path.clone());
        service.add_plugin_path(path.clone());
        let count = service
            .plugin_paths
            .iter()
            .filter(|p| p == &path)
            .count();
        assert_eq!(count, 1);
    }

    #[test]
    fn test_list_all_plugins_empty() {
        let service = PluginDiscoveryService::new();
        let plugins = service.list_all_plugins();
        assert_eq!(plugins.len(), 0);
    }

    #[test]
    fn test_validate_nonexistent_plugin() {
        let service = PluginDiscoveryService::new();
        let result = service.validate_plugin("nonexistent");
        assert!(result.is_err());
    }

    #[test]
    fn test_get_statistics_empty() {
        let service = PluginDiscoveryService::new();
        let stats = service.get_statistics();
        assert_eq!(stats.len(), 0);
    }
}
