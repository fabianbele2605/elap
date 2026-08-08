//! Cache de embeddings

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use crate::error::ResultadoElap;

/// Entrada en cache de embeddings
#[derive(Debug, Clone)]
pub struct EntradaCache {
    pub texto: String,
    pub embedding: Vec<f32>,
    pub timestamp: String,
    pub modelo: String,
}

/// Cache de embeddings para evitar recalcular
pub struct CacheEmbeddings {
    cache: Arc<Mutex<HashMap<String, EntradaCache>>>,
    max_entries: usize,
}

impl CacheEmbeddings {
    /// Crear nuevo cache
    pub fn nuevo(max_entries: usize) -> Self {
        Self {
            cache: Arc::new(Mutex::new(HashMap::new())),
            max_entries,
        }
    }

    /// Generar clave de cache
    fn generar_clave(modelo: &str, texto: &str) -> String {
        format!("{}:{}", modelo, texto)
    }

    /// Obtener embedding del cache
    pub fn obtener(&self, modelo: &str, texto: &str) -> ResultadoElap<Option<Vec<f32>>> {
        let cache = self.cache.lock().map_err(|_| {
            crate::error::ElapError::InternalError("No se pudo adquirir lock".to_string())
        })?;

        let clave = Self::generar_clave(modelo, texto);
        Ok(cache.get(&clave).map(|e| e.embedding.clone()))
    }

    /// Guardar embedding en cache
    pub fn guardar(
        &self,
        modelo: &str,
        texto: &str,
        embedding: Vec<f32>,
    ) -> ResultadoElap<()> {
        let mut cache = self.cache.lock().map_err(|_| {
            crate::error::ElapError::InternalError("No se pudo adquirir lock".to_string())
        })?;

        // Limpiar si alcanzamos max
        if cache.len() >= self.max_entries {
            cache.clear();
        }

        let clave = Self::generar_clave(modelo, texto);
        let entrada = EntradaCache {
            texto: texto.to_string(),
            embedding,
            timestamp: chrono::Utc::now().to_rfc3339(),
            modelo: modelo.to_string(),
        };

        cache.insert(clave, entrada);
        Ok(())
    }

    /// Vaciar cache
    pub fn limpiar(&self) -> ResultadoElap<()> {
        let mut cache = self.cache.lock().map_err(|_| {
            crate::error::ElapError::InternalError("No se pudo adquirir lock".to_string())
        })?;

        cache.clear();
        Ok(())
    }

    /// Contar entradas
    pub fn contar(&self) -> ResultadoElap<usize> {
        let cache = self.cache.lock().map_err(|_| {
            crate::error::ElapError::InternalError("No se pudo adquirir lock".to_string())
        })?;

        Ok(cache.len())
    }
}

impl Clone for CacheEmbeddings {
    fn clone(&self) -> Self {
        Self {
            cache: self.cache.clone(),
            max_entries: self.max_entries,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_cache() {
        let cache = CacheEmbeddings::nuevo(100);
        assert_eq!(cache.contar().unwrap(), 0);
    }

    #[test]
    fn test_guardar_obtener() {
        let cache = CacheEmbeddings::nuevo(100);
        let embedding = vec![0.1, 0.2, 0.3];

        cache
            .guardar("all-minilm", "texto de prueba", embedding.clone())
            .unwrap();

        let obtenido = cache.obtener("all-minilm", "texto de prueba").unwrap();
        assert_eq!(obtenido, Some(embedding));
    }

    #[test]
    fn test_no_encontrado() {
        let cache = CacheEmbeddings::nuevo(100);
        let obtenido = cache.obtener("all-minilm", "texto inexistente").unwrap();
        assert_eq!(obtenido, None);
    }

    #[test]
    fn test_limpiar_cache() {
        let cache = CacheEmbeddings::nuevo(100);
        cache
            .guardar("all-minilm", "texto1", vec![0.1])
            .unwrap();
        cache
            .guardar("all-minilm", "texto2", vec![0.2])
            .unwrap();

        assert_eq!(cache.contar().unwrap(), 2);
        cache.limpiar().unwrap();
        assert_eq!(cache.contar().unwrap(), 0);
    }

    #[test]
    fn test_max_entries() {
        let cache = CacheEmbeddings::nuevo(2);
        cache.guardar("model", "texto1", vec![0.1]).unwrap();
        cache.guardar("model", "texto2", vec![0.2]).unwrap();
        cache.guardar("model", "texto3", vec![0.3]).unwrap(); // Debería limpiar

        assert_eq!(cache.contar().unwrap(), 1);
    }
}
