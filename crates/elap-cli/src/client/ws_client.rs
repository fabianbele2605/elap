//! Cliente WebSocket para monitoreo en vivo

use anyhow::Result;
use futures::StreamExt;
use serde_json::Value;
use tokio_tungstenite::{connect_async, tungstenite::Message};

/// Cliente WebSocket
pub struct WsClient {
    ws: tokio_tungstenite::WebSocketStream<
        tokio_tungstenite::MaybeTlsStream<tokio::net::TcpStream>,
    >,
}

impl WsClient {
    /// Conectar a WebSocket
    pub async fn conectar(url: &str) -> Result<Self> {
        let (ws, _) = connect_async(url).await?;
        Ok(Self { ws })
    }

    /// Obtener próximo evento
    pub async fn proxima_evento(&mut self) -> Option<Result<Value>> {
        loop {
            match self.ws.next().await {
                Some(Ok(Message::Text(texto))) => {
                    match serde_json::from_str::<Value>(&texto) {
                        Ok(json) => return Some(Ok(json)),
                        Err(e) => return Some(Err(e.into())),
                    }
                }
                Some(Ok(_)) => continue,
                Some(Err(e)) => return Some(Err(e.into())),
                None => return None,
            }
        }
    }
}
