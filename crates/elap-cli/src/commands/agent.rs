//! Comandos para operar sobre un agente específico

use anyhow::Result;
use colored::*;
use crate::client::http_client::HttpClient;
use crate::client::ws_client::WsClient;
use indicatif::{ProgressBar, ProgressStyle};

/// Información del agente
pub async fn info(server: &str, token: &Option<String>, id: &str) -> Result<()> {
    let client = HttpClient::nuevo(server, token.clone());

    println!("{}", format!("📊 Información del agente {}...", id).bright_cyan());

    match client.obtener_agente(id).await {
        Ok(agente) => {
            println!();
            println!("  {} {}", "ID:".bright_white().bold(), agente["id"].as_str().unwrap_or("?").bright_cyan());
            println!("  {} {}", "Nombre:".bright_white().bold(), agente["nombre"].as_str().unwrap_or("?").bright_white());
            println!("  {} {}", "Rol:".bright_white().bold(), agente["rol"].as_str().unwrap_or("?").bright_white());
            println!("  {} {}", "Objetivo:".bright_white().bold(), agente["objetivo"].as_str().unwrap_or("?").bright_white());
            println!("  {} {}", "Estado:".bright_white().bold(), agente["estado"].as_str().unwrap_or("?").bright_yellow());
            let progreso_pct = format!("{:.0}%", agente["progreso"].as_f64().unwrap_or(0.0) * 100.0);
            println!("  {} {}", "Progreso:".bright_white().bold(), progreso_pct.bright_cyan());
            println!();
        }
        Err(e) => {
            println!("{} Error: {}", "✗".bright_red(), e);
        }
    }

    Ok(())
}

/// Monitorear agente en vivo
pub async fn watch(server: &str, token: &Option<String>, id: &str) -> Result<()> {
    let ws_url = format!("ws://{}/agents/{}/watch",
        server.replace("http://", "").replace("https://", ""),
        id
    );

    println!("{}", format!("👁️  Monitoreando agente {}...", id).bright_cyan());
    println!("{}", "Presiona Ctrl+C para detener".bright_yellow());
    println!();

    match WsClient::conectar(&ws_url).await {
        Ok(mut ws) => {
            while let Some(evento) = ws.proxima_evento().await {
                match evento {
                    Ok(evento) => {
                        let tipo = evento["tipo"].as_str().unwrap_or("?");
                        match tipo {
                            "estado" => {
                                let estado = evento["datos"]["estado"].as_str().unwrap_or("?");
                                println!("{} Estado: {}", "•".bright_cyan(), estado.bright_yellow());
                            }
                            "progreso" => {
                                let progreso = evento["datos"]["progreso"].as_f64().unwrap_or(0.0);
                                let pasos = evento["datos"]["pasos_completados"].as_u64().unwrap_or(0);
                                let total = evento["datos"]["total"].as_u64().unwrap_or(1);
                                println!("{} Progreso: {}/{} ({:.0}%)", "▓".bright_green(), pasos, total, progreso * 100.0);
                            }
                            "accion" => {
                                let desc = evento["datos"]["descripcion"].as_str().unwrap_or("?");
                                println!("{} {}", "→".bright_white(), desc);
                            }
                            "reflexion" => {
                                let content = evento["datos"]["contenido"].as_str().unwrap_or("?");
                                println!("{} {}", "💭".bright_magenta(), content);
                            }
                            "latido" => {
                                // Latidos silenciosos
                            }
                            "error" => {
                                let msg = evento["datos"]["mensaje"].as_str().unwrap_or("?");
                                println!("{} Error: {}", "✗".bright_red(), msg);
                            }
                            _ => {}
                        }
                    }
                    Err(e) => {
                        println!("{} Error: {}", "✗".bright_red(), e);
                        break;
                    }
                }
            }
        }
        Err(e) => {
            println!("{} Error conectando: {}", "✗".bright_red(), e);
        }
    }

    Ok(())
}

/// Ejecutar plan del agente
pub async fn execute(server: &str, token: &Option<String>, id: &str) -> Result<()> {
    let client = HttpClient::nuevo(server, token.clone());

    println!("{}", format!("⚡ Ejecutando agente {}...", id).bright_cyan());

    let pb = ProgressBar::new_spinner();
    pb.set_style(ProgressStyle::default_spinner()
        .template("{spinner:.green} {msg}")
        .unwrap());
    pb.set_message("Ejecutando...");

    match client.ejecutar_agente(id).await {
        Ok(resultado) => {
            pb.finish_with_message("✓ Completado");
            println!();
            println!("{} Ejecución completada", "✓".bright_green());
            if let Some(pasos) = resultado["pasos_completados"].as_u64() {
                println!("  {} {} pasos completados", "→".bright_cyan(), pasos);
            }
            if let Some(progreso) = resultado["progreso"].as_f64() {
                println!("  {} {:.0}% completado", "→".bright_cyan(), progreso * 100.0);
            }
        }
        Err(e) => {
            pb.finish_with_message(format!("✗ {}", e));
        }
    }

    Ok(())
}

/// Estado del agente
pub async fn status(server: &str, token: &Option<String>, id: &str) -> Result<()> {
    let client = HttpClient::nuevo(server, token.clone());

    match client.obtener_status(id).await {
        Ok(status) => {
            println!();
            println!("{} {}", "Estado:".bright_white().bold(), status["estado"].as_str().unwrap_or("?").bright_yellow());

            if let Some(pasos) = status["pasos"].as_object() {
                let completados = pasos["completados"].as_u64().unwrap_or(0);
                let total = pasos["total"].as_u64().unwrap_or(1);
                let progreso = pasos["progreso"].as_str().unwrap_or("0%");

                println!("{} {}/{} pasos", "Progreso:".bright_white().bold(), completados, total);
                println!("{} {}", "Porcentaje:".bright_white().bold(), progreso.bright_cyan());
            }

            if let Some(historial) = status["historial"].as_object() {
                let acciones = historial["acciones"].as_u64().unwrap_or(0);
                let reflexiones = historial["reflexiones"].as_u64().unwrap_or(0);

                println!("{} {} acciones", "Historial:".bright_white().bold(), acciones);
                println!("{} {} reflexiones", "Aprendizaje:".bright_white().bold(), reflexiones);
            }
            println!();
        }
        Err(e) => {
            println!("{} Error: {}", "✗".bright_red(), e);
        }
    }

    Ok(())
}

/// Eliminar agente
pub async fn delete(server: &str, token: &Option<String>, id: &str) -> Result<()> {
    let client = HttpClient::nuevo(server, token.clone());

    println!("{}", format!("🗑️  Eliminando agente {}...", id).bright_red());

    match client.eliminar_agente(id).await {
        Ok(_) => {
            println!("{} Agente eliminado", "✓".bright_green());
        }
        Err(e) => {
            println!("{} Error: {}", "✗".bright_red(), e);
        }
    }

    Ok(())
}
