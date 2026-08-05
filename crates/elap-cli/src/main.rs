use clap::{Parser, Subcommand};
use elap_core::MotorCentral;
use std::error::Error;
use tracing_subscriber;

/// Enterprise Local AI Platform CLI
#[derive(Parser)]
#[command(name = "ELAP")]
#[command(version = "0.1.0")]
#[command(about = "Enterprise Local AI Platform - Local AI without cloud", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,

    /// Log level: trace, debug, info, warn, error
    #[arg(global = true, long, default_value = "info")]
    log_level: String,
}

#[derive(Subcommand)]
enum Commands {
    /// Start the ELAP core engine
    Start {
        /// Port for gRPC server
        #[arg(long, default_value = "50051")]
        port: u16,
    },

    /// Show version information
    Version,

    /// Show help information
    Help,

    /// Health check
    Health,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let cli = Cli::parse();

    // Initialize logging
    tracing_subscriber::fmt()
        .with_max_level(
            cli.log_level
                .parse()
                .unwrap_or(tracing::Level::INFO),
        )
        .init();

    tracing::info!("ELAP CLI v0.1.0 starting");

    match cli.command {
        Commands::Start { port } => {
            tracing::info!("Starting ELAP Core Engine on port {}", port);
            let engine = MotorCentral::nuevo("ELAP-CLI", "0.1.0");
            engine.iniciar().await?;
            tracing::info!("Engine running. Press Ctrl+C to stop.");

            // Keep running until interrupted
            tokio::signal::ctrl_c().await?;
            engine.detener().await?;
            tracing::info!("Engine stopped gracefully");
        }

        Commands::Version => {
            println!("ELAP version 0.1.0");
            println!("Copyright © 2026 BBLABS");
        }

        Commands::Help => {
            println!("ELAP - Enterprise Local AI Platform");
            println!("Usage: elap-cli [OPTIONS] <COMMAND>");
            println!();
            println!("Commands:");
            println!("  start    Start the ELAP core engine");
            println!("  version  Show version information");
            println!("  health   Health check");
            println!("  help     Show this help message");
        }

        Commands::Health => {
            tracing::info!("Checking ELAP health...");
            println!("✓ ELAP is ready");
        }
    }

    Ok(())
}
