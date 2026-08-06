//! Middleware para la API

use tower_http::cors::CorsLayer;
use std::net::SocketAddr;

/// Layer de logging - placeholder para fase futura
pub fn logging_layer() -> CorsLayer {
    CorsLayer::permissive()
}

/// Layer de CORS
pub fn cors_layer() -> CorsLayer {
    CorsLayer::permissive()
}

/// Configuración de servidor
pub struct ConfiguracionServidor {
    pub puerto: u16,
    pub host: String,
}

impl Default for ConfiguracionServidor {
    fn default() -> Self {
        Self {
            puerto: 3000,
            host: "127.0.0.1".to_string(),
        }
    }
}

impl ConfiguracionServidor {
    /// Obtener dirección del servidor
    pub fn obtener_addr(&self) -> SocketAddr {
        format!("{}:{}", self.host, self.puerto)
            .parse()
            .expect("Dirección inválida")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_configuracion_default() {
        let config = ConfiguracionServidor::default();
        assert_eq!(config.puerto, 3000);
    }

    #[test]
    fn test_obtener_addr() {
        let config = ConfiguracionServidor {
            puerto: 8080,
            host: "0.0.0.0".to_string(),
        };

        let addr = config.obtener_addr();
        assert_eq!(addr.port(), 8080);
    }
}
