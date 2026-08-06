//! Comandos para listar y crear agentes

use anyhow::Result;
use colored::*;
use prettytable::{Table, row, cell};
use crate::client::http_client::HttpClient;

/// Listar todos los agentes
pub async fn listar(server: &str, token: &Option<String>) -> Result<()> {
    let client = HttpClient::nuevo(server, token.clone());

    println!("{}", "📋 Listando agentes...".bright_cyan());

    match client.listar_agentes().await {
        Ok(respuesta) => {
            if respuesta["agentes"].is_array() {
                let agentes = respuesta["agentes"].as_array().unwrap();

                if agentes.is_empty() {
                    println!("{}", "  ℹ️  No hay agentes creados".bright_yellow());
                    return Ok(());
                }

                let mut table = Table::new();
                table.add_row(row![
                    "ID (primeros 8)".bright_green().bold(),
                    "Nombre".bright_green().bold(),
                ]);

                for agente in agentes {
                    let id = agente["id"].as_str().unwrap_or("?");
                    let nombre = agente["nombre"].as_str().unwrap_or("?");
                    let id_short = id.chars().take(8).collect::<String>();

                    table.add_row(row![
                        id_short.bright_cyan(),
                        nombre.bright_white(),
                    ]);
                }

                table.printstd();
                println!();
                println!("{} {} agentes encontrados",
                    "✓".bright_green(),
                    agentes.len().to_string().bright_cyan()
                );
            }
        }
        Err(e) => {
            println!("{} Error: {}", "✗".bright_red(), e);
        }
    }

    Ok(())
}

/// Crear nuevo agente
pub async fn crear(
    server: &str,
    token: &Option<String>,
    nombre: String,
    rol: String,
    objetivo: String,
) -> Result<()> {
    let client = HttpClient::nuevo(server, token.clone());

    println!("{}", "🚀 Creando agente...".bright_cyan());

    match client.crear_agente(&nombre, &rol, &objetivo).await {
        Ok(respuesta) => {
            let id = respuesta["id"].as_str().unwrap_or("?");
            println!();
            println!("{} Agente creado exitosamente", "✓".bright_green());
            println!("  {} {}", "ID:".bright_white().bold(), id.bright_cyan());
            println!("  {} {}", "Nombre:".bright_white().bold(), nombre.bright_white());
            println!("  {} {}", "Rol:".bright_white().bold(), rol.bright_white());
            println!("  {} {}", "Objetivo:".bright_white().bold(), objetivo.bright_white());
            println!();
            println!("{} Próximo: elap agent {} watch", "→".bright_green(), id.chars().take(8).collect::<String>());
        }
        Err(e) => {
            println!("{} Error: {}", "✗".bright_red(), e);
        }
    }

    Ok(())
}
