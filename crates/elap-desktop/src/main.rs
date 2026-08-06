// Punto de entrada de aplicación Desktop (placeholder Tauri)

use elap_core::{MotorCentral, Configuracion};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Crear configuración por defecto
    let config = Configuracion::defecto();
    let motor = MotorCentral::nuevo(config);

    // Iniciar motor central con logging y configuración
    motor.iniciar().await?;

    println!("✅ ELAP Desktop runtime iniciado");
    println!("📝 Nota: Interfaz Tauri será implementada en pasos posteriores");

    // Detener motor de forma limpia
    motor.detener().await?;

    Ok(())
}
