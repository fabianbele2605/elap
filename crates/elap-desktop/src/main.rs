// Punto de entrada de aplicación Desktop (placeholder Tauri)

use elap_core::{MotorCentral, Configuracion, crear_router, AppState};
use axum::serve;
use tokio::net::TcpListener;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Crear configuración por defecto
    let config = Configuracion::defecto();
    let motor = MotorCentral::nuevo(config);

    // Iniciar motor central con logging y configuración
    motor.iniciar().await?;

    println!("✅ ELAP Desktop runtime iniciado");
    println!("📝 Inicializando servidor REST en localhost:3000...");

    // Crear estado de la aplicación
    let app_state = AppState::nuevo();

    // Crear router
    let router = crear_router(app_state);

    // Configurar servidor
    let listener = TcpListener::bind("127.0.0.1:3000").await?;
    println!("🚀 Servidor escuchando en http://127.0.0.1:3000");

    // Iniciar servidor
    serve(listener, router).await?;

    // Detener motor de forma limpia
    motor.detener().await?;

    Ok(())
}
