//! ELAP CLI - Dashboard en Terminal

mod commands;
mod client;

use clap::{Parser, Subcommand};
use anyhow::Result;
use colored::*;

#[derive(Parser)]
#[command(name = "elap")]
#[command(about = "ELAP CLI - Dashboard de Agentes en Terminal", long_about = None)]
#[command(version)]
struct Cli {
    /// URL del servidor ELAP
    #[arg(global = true, short, long, default_value = "http://localhost:3000")]
    server: String,

    /// Token JWT (o setear ELAP_TOKEN env var)
    #[arg(global = true, short, long)]
    token: Option<String>,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Gestionar agentes
    Agents {
        #[command(subcommand)]
        action: AgentsAction,
    },
    /// Operaciones de un agente específico
    Agent {
        /// ID del agente
        id: String,

        #[command(subcommand)]
        action: AgentAction,
    },
    /// Información del servidor
    Info,
}

#[derive(Subcommand)]
enum AgentsAction {
    /// Listar todos los agentes
    List,
    /// Crear nuevo agente
    Create {
        /// Nombre del agente
        #[arg(short, long)]
        nombre: String,

        /// Rol del agente
        #[arg(short, long)]
        rol: String,

        /// Objetivo
        #[arg(short, long)]
        objetivo: String,
    },
}

#[derive(Subcommand)]
enum AgentAction {
    /// Información del agente
    Info,
    /// Monitorear agente en vivo (WebSocket)
    Watch,
    /// Ejecutar plan del agente
    Execute,
    /// Ver estado actual
    Status,
    /// Eliminar agente
    Delete,
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    // Obtener token de env o argumento
    let token = cli.token.or_else(|| std::env::var("ELAP_TOKEN").ok());

    match cli.command {
        Commands::Agents { action } => {
            match action {
                AgentsAction::List => {
                    commands::agents::listar(&cli.server, &token).await?;
                }
                AgentsAction::Create { nombre, rol, objetivo } => {
                    commands::agents::crear(&cli.server, &token, nombre, rol, objetivo)
                        .await?;
                }
            }
        }
        Commands::Agent { id, action } => {
            match action {
                AgentAction::Info => {
                    commands::agent::info(&cli.server, &token, &id).await?;
                }
                AgentAction::Watch => {
                    commands::agent::watch(&cli.server, &token, &id).await?;
                }
                AgentAction::Execute => {
                    commands::agent::execute(&cli.server, &token, &id).await?;
                }
                AgentAction::Status => {
                    commands::agent::status(&cli.server, &token, &id).await?;
                }
                AgentAction::Delete => {
                    commands::agent::delete(&cli.server, &token, &id).await?;
                }
            }
        }
        Commands::Info => {
            println!("{}", "ELAP CLI v0.1.0".bright_cyan().bold());
            println!("{}", "Dashboard de Agentes en Terminal".bright_white());
            println!();
            println!("  {} Use 'elap --help' para ver todos los comandos", "→".bright_green());
            println!("  {} Servidor por defecto: http://localhost:3000", "→".bright_green());
            println!("  {} Token: setear variable ELAP_TOKEN o usar --token", "→".bright_green());
        }
    }

    Ok(())
}
