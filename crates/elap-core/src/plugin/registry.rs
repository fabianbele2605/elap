//! Registro central de plugins

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use super::metadata::PluginMetadata;
use crate::error::ResultadoElap;

/// Registro central de plugins
pub struct RegistroPlugins {
    plugins: Arc<Mutex<HashMap<String, PluginMetadata>>>,
}

impl RegistroPlugins {
    /// Crear nuevo registro
    pub fn nuevo() -> Self {
        Self {
            plugins: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Registrar un plugin
    pub fn registrar(&self, metadata: PluginMetadata) -> ResultadoElap<()> {
        let mut plugins = self.plugins.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock del registro".to_string()
            ))?;

        if plugins.contains_key(&metadata.nombre) {
            return Err(crate::error::ElapError::Validacion(
                format!("Plugin '{}' ya está registrado", metadata.nombre)
            ));
        }

        plugins.insert(metadata.nombre.clone(), metadata);
        Ok(())
    }

    /// Desregistrar un plugin
    pub fn desregistrar(&self, nombre: &str) -> ResultadoElap<()> {
        let mut plugins = self.plugins.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock del registro".to_string()
            ))?;

        if plugins.remove(nombre).is_none() {
            return Err(crate::error::ElapError::Validacion(
                format!("Plugin '{}' no encontrado", nombre)
            ));
        }

        Ok(())
    }

    /// Obtener plugin por nombre
    pub fn obtener(&self, nombre: &str) -> ResultadoElap<PluginMetadata> {
        let plugins = self.plugins.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock del registro".to_string()
            ))?;

        plugins.get(nombre)
            .cloned()
            .ok_or_else(|| crate::error::ElapError::Validacion(
                format!("Plugin '{}' no encontrado", nombre)
            ))
    }

    /// Listar todos los plugins
    pub fn listar(&self) -> ResultadoElap<Vec<PluginMetadata>> {
        let plugins = self.plugins.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock del registro".to_string()
            ))?;

        Ok(plugins.values().cloned().collect())
    }

    /// Contar plugins registrados
    pub fn contar(&self) -> ResultadoElap<usize> {
        let plugins = self.plugins.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock del registro".to_string()
            ))?;

        Ok(plugins.len())
    }

    /// Verificar si plugin existe
    pub fn existe(&self, nombre: &str) -> ResultadoElap<bool> {
        let plugins = self.plugins.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock del registro".to_string()
            ))?;

        Ok(plugins.contains_key(nombre))
    }

    /// Buscar plugins por autor
    pub fn buscar_por_autor(&self, autor: &str) -> ResultadoElap<Vec<PluginMetadata>> {
        let plugins = self.plugins.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock del registro".to_string()
            ))?;

        let resultados = plugins.values()
            .filter(|p| p.autor.contains(autor))
            .cloned()
            .collect();

        Ok(resultados)
    }

    /// Buscar plugins por permiso requerido
    pub fn buscar_por_permiso(&self, permiso: &str) -> ResultadoElap<Vec<PluginMetadata>> {
        let plugins = self.plugins.lock()
            .map_err(|_| crate::error::ElapError::Otro(
                "No se pudo adquirir lock del registro".to_string()
            ))?;

        let resultados = plugins.values()
            .filter(|p| p.permisos.contains(&permiso.to_string()))
            .cloned()
            .collect();

        Ok(resultados)
    }
}

impl Clone for RegistroPlugins {
    fn clone(&self) -> Self {
        Self {
            plugins: self.plugins.clone(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn crear_plugin_test(nombre: &str) -> PluginMetadata {
        PluginMetadata::nuevo(
            nombre.to_string(),
            "1.0.0".to_string(),
            "autor_test".to_string(),
            "Plugin de prueba".to_string(),
            "./test.so".to_string(),
            "plugin_init".to_string(),
        )
    }

    #[test]
    fn test_crear_registro() {
        let registro = RegistroPlugins::nuevo();
        assert!(registro.contar().is_ok());
        assert_eq!(registro.contar().unwrap(), 0);
    }

    #[test]
    fn test_registrar_plugin() {
        let registro = RegistroPlugins::nuevo();
        let plugin = crear_plugin_test("plugin1");

        assert!(registro.registrar(plugin).is_ok());
        assert_eq!(registro.contar().unwrap(), 1);
    }

    #[test]
    fn test_registrar_duplicado() {
        let registro = RegistroPlugins::nuevo();
        let plugin = crear_plugin_test("plugin1");

        assert!(registro.registrar(plugin.clone()).is_ok());
        assert!(registro.registrar(plugin).is_err());
    }

    #[test]
    fn test_obtener_plugin() {
        let registro = RegistroPlugins::nuevo();
        let plugin = crear_plugin_test("plugin1");
        let nombre = plugin.nombre.clone();

        assert!(registro.registrar(plugin).is_ok());
        let resultado = registro.obtener(&nombre);
        assert!(resultado.is_ok());
        assert_eq!(resultado.unwrap().nombre, nombre);
    }

    #[test]
    fn test_obtener_no_existe() {
        let registro = RegistroPlugins::nuevo();
        let resultado = registro.obtener("no_existe");
        assert!(resultado.is_err());
    }

    #[test]
    fn test_desregistrar_plugin() {
        let registro = RegistroPlugins::nuevo();
        let plugin = crear_plugin_test("plugin1");
        let nombre = plugin.nombre.clone();

        assert!(registro.registrar(plugin).is_ok());
        assert_eq!(registro.contar().unwrap(), 1);

        assert!(registro.desregistrar(&nombre).is_ok());
        assert_eq!(registro.contar().unwrap(), 0);
    }

    #[test]
    fn test_desregistrar_no_existe() {
        let registro = RegistroPlugins::nuevo();
        assert!(registro.desregistrar("no_existe").is_err());
    }

    #[test]
    fn test_listar_plugins() {
        let registro = RegistroPlugins::nuevo();
        let plugin1 = crear_plugin_test("plugin1");
        let plugin2 = crear_plugin_test("plugin2");

        assert!(registro.registrar(plugin1).is_ok());
        assert!(registro.registrar(plugin2).is_ok());

        let lista = registro.listar().unwrap();
        assert_eq!(lista.len(), 2);
    }

    #[test]
    fn test_existe_plugin() {
        let registro = RegistroPlugins::nuevo();
        let plugin = crear_plugin_test("plugin1");

        assert_eq!(registro.existe("plugin1").unwrap(), false);
        assert!(registro.registrar(plugin).is_ok());
        assert_eq!(registro.existe("plugin1").unwrap(), true);
    }

    #[test]
    fn test_clonar_registro() {
        let registro1 = RegistroPlugins::nuevo();
        let plugin = crear_plugin_test("plugin1");
        assert!(registro1.registrar(plugin).is_ok());

        let registro2 = registro1.clone();
        assert_eq!(registro2.contar().unwrap(), 1);
    }

    #[test]
    fn test_buscar_por_autor() {
        let registro = RegistroPlugins::nuevo();
        let mut plugin1 = PluginMetadata::nuevo(
            "plugin1".to_string(),
            "1.0.0".to_string(),
            "autor_a".to_string(),
            "desc".to_string(),
            "./test1.so".to_string(),
            "init".to_string(),
        );
        let mut plugin2 = PluginMetadata::nuevo(
            "plugin2".to_string(),
            "1.0.0".to_string(),
            "autor_b".to_string(),
            "desc".to_string(),
            "./test2.so".to_string(),
            "init".to_string(),
        );

        assert!(registro.registrar(plugin1).is_ok());
        assert!(registro.registrar(plugin2).is_ok());

        let resultados = registro.buscar_por_autor("autor_a").unwrap();
        assert_eq!(resultados.len(), 1);
    }

    #[test]
    fn test_buscar_por_permiso() {
        let registro = RegistroPlugins::nuevo();
        let mut plugin1 = crear_plugin_test("plugin1");
        let mut plugin2 = crear_plugin_test("plugin2");

        plugin1.agregar_permiso("LeerArchivos".to_string());
        plugin2.agregar_permiso("EscribirArchivos".to_string());

        assert!(registro.registrar(plugin1).is_ok());
        assert!(registro.registrar(plugin2).is_ok());

        let resultados = registro.buscar_por_permiso("LeerArchivos").unwrap();
        assert_eq!(resultados.len(), 1);
    }

    #[test]
    fn test_buscar_sin_resultados() {
        let registro = RegistroPlugins::nuevo();
        let resultados = registro.buscar_por_autor("no_existe").unwrap();
        assert_eq!(resultados.len(), 0);
    }
}
