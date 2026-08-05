//! Sistema de gestión de modelos de IA locales
//!
//! Integración con Ollama para ejecutar modelos locales (Llama 2, Mistral, etc)
//! con caching de embeddings y memoria.

pub mod model_metadata;
pub mod ollama_client;
pub mod registry;
pub mod cache;
pub mod errors;

pub use model_metadata::{ModelMetadata, TipoModelo};
pub use ollama_client::OllamaClient;
pub use registry::RegistroModelos;
pub use cache::CacheEmbeddings;
pub use errors::ModelError;
