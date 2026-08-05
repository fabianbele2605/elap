// Desktop application entry point (Tauri placeholder)

use elap_core::{MotorCentral, Configuracion};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Crear configuración
    let config = Configuracion::defecto();
    let motor = MotorCentral::nuevo(config);

    // Iniciar motor central
    motor.iniciar().await?;

    println!("ELAP Desktop runtime iniciado");
    println!("Nota: Interfaz Tauri será implementada en pasos posteriores");

    // Detener
    motor.detener().await?;

    Ok(())
}
