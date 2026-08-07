use elap_core::{MotorCentral, Configuracion, crear_router, AppState};
use axum::{serve, Router, response::IntoResponse, http::StatusCode};
use tokio::net::TcpListener;
use std::path::PathBuf;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let config = Configuracion::defecto();
    let motor = MotorCentral::nuevo(config);
    motor.iniciar().await?;

    println!("✅ ELAP Desktop runtime iniciado");
    println!("🚀 Servidor escuchando en http://0.0.0.0:3000");

    let app_state = AppState::nuevo();
    let router = crear_router(app_state);
    let router = router.fallback(serve_static);

    let listener = TcpListener::bind("0.0.0.0:3000").await?;
    serve(listener, router).await?;

    motor.detener().await?;
    Ok(())
}

async fn serve_static(req: axum::extract::Request) -> impl IntoResponse {
    let path = req.uri().path().trim_start_matches('/');
    let path = if path.is_empty() {
        "index.html".to_string()
    } else {
        path.to_string()
    };

    let file_path = PathBuf::from("../../web/dist").join(&path);

    match tokio::fs::read(&file_path).await {
        Ok(content) => {
            let content_type = if path.ends_with(".js") {
                "application/javascript"
            } else if path.ends_with(".css") {
                "text/css"
            } else if path.ends_with(".html") {
                "text/html"
            } else {
                "application/octet-stream"
            };

            ([(axum::http::header::CONTENT_TYPE, content_type)], content).into_response()
        }
        Err(_) => {
            match tokio::fs::read("../../web/dist/index.html").await {
                Ok(content) => (
                    [(axum::http::header::CONTENT_TYPE, "text/html")],
                    content
                ).into_response(),
                Err(_) => (StatusCode::NOT_FOUND, "404 Not Found").into_response(),
            }
        }
    }
}
