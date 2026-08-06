use tracing::{info, warn};
use tracing_subscriber::fmt;
use std::path::Path;

/// Inicializa el sistema de logging con archivo de salida.
pub fn inicializar_logging(ruta_logs: &str, nivel: &str) -> Result<(), Box<dyn std::error::Error>> {
    // Crear directorio de logs si no existe
    if let Some(parent) = Path::new(ruta_logs).parent() {
        if !parent.exists() {
            std::fs::create_dir_all(parent)?;
        }
    }

    // Configurar nivel de logging
    let nivel_filtro = match nivel {
        "trace" => tracing_subscriber::filter::LevelFilter::TRACE,
        "debug" => tracing_subscriber::filter::LevelFilter::DEBUG,
        "info" => tracing_subscriber::filter::LevelFilter::INFO,
        "warn" => tracing_subscriber::filter::LevelFilter::WARN,
        "error" => tracing_subscriber::filter::LevelFilter::ERROR,
        _=> tracing_subscriber::filter::LevelFilter::INFO,
    };

    // Crear subscriber que escribe a archivo en formato JSON
    let file = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(ruta_logs)?;
    
    tracing_subscriber::fmt()
        .with_writer(file)
        .with_level(true)
        .with_target(true)
        .with_thread_ids(true)
        .with_thread_names(true)
        .json()
        .with_max_level(nivel_filtro)
        .init();

    info!("Sistema de logging inicializado: {}", ruta_logs);
    Ok(())
}