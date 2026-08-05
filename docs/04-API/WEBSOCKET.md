# WebSocket Streaming — Monitoreo en Vivo

**Autor**: ELAP Development Team  
**Fecha**: 2026-08-05  
**Versión**: 1.0  
**Fase**: 9 - Paso 2

## Descripción General

El **WebSocket Streaming** proporciona monitoreo en tiempo real de la ejecución de agentes.

### Características

- ✅ **Eventos en vivo** - Estado, progreso, acciones
- ✅ **Latidos periódicos** - Heartbeat cada 1 segundo
- ✅ **Historial completo** - Acciones y reflexiones
- ✅ **Bidireccional** - Preparado para comandos futuros
- ✅ **JSON tipado** - Mensajes estructurados

---

## Endpoint

```
GET ws://localhost:3000/agents/{id}/watch
```

**Parámetros**:
- `id` (path): UUID del agente

---

## Tipos de Eventos

### 1. Conectado

Se envía al establecer la conexión.

```json
{
  "tipo": "conectado",
  "datos": {
    "agente_id": "a1b2c3d4-...",
    "mensaje": "Monitoreo en vivo iniciado"
  },
  "timestamp": "2026-08-05T10:30:45.123Z"
}
```

### 2. Estado

Estado actual del agente.

```json
{
  "tipo": "estado",
  "datos": {
    "estado": "Ejecutando"
  },
  "timestamp": "2026-08-05T10:30:45.123Z"
}
```

**Estados posibles**:
- `Inactivo` - Esperando
- `Planificando` - Preparando
- `Ejecutando` - En proceso
- `Reflexionando` - Analizando
- `Completado` - Exitoso
- `Error` - Falló

### 3. Progreso

Actualización de progreso del plan.

```json
{
  "tipo": "progreso",
  "datos": {
    "pasos_completados": 2,
    "total": 4,
    "porcentaje": 50.0
  },
  "timestamp": "2026-08-05T10:30:45.123Z"
}
```

### 4. Acción

Historial de acciones realizadas.

```json
{
  "tipo": "accion",
  "datos": {
    "descripcion": "Ejecutando: Leer archivo de ventas"
  },
  "timestamp": "2026-08-05T10:30:45.123Z"
}
```

### 5. Reflexión

Reflexiones del agente.

```json
{
  "tipo": "reflexion",
  "datos": {
    "contenido": "Plan completado. 4 pasos ejecutados."
  },
  "timestamp": "2026-08-05T10:30:45.123Z"
}
```

### 6. Latido (Heartbeat)

Enviado cada segundo para mantener conexión viva.

```json
{
  "tipo": "latido",
  "datos": {
    "estado": "Ejecutando",
    "progreso": 0.5,
    "pasos": 2,
    "total": 4
  },
  "timestamp": "2026-08-05T10:30:45.123Z"
}
```

### 7. Error

Indica problema en el monitoreo.

```json
{
  "tipo": "error",
  "datos": {
    "mensaje": "Agente no encontrado"
  },
  "timestamp": "2026-08-05T10:30:45.123Z"
}
```

---

## Ejemplos

### Ejemplo 1: JavaScript en Navegador

```javascript
const agentId = "a1b2c3d4-e5f6-4g7h-i8j9-k0l1m2n3o4p5";
const ws = new WebSocket(`ws://localhost:3000/agents/${agentId}/watch`);

ws.onopen = () => {
  console.log("Conectado al monitoreo del agente");
};

ws.onmessage = (event) => {
  const evento = JSON.parse(event.data);
  
  switch(evento.tipo) {
    case 'conectado':
      console.log("Monitoreo iniciado:", evento.datos.mensaje);
      break;
    
    case 'progreso':
      console.log(`Progreso: ${evento.datos.porcentaje}%`);
      break;
    
    case 'accion':
      console.log("Acción:", evento.datos.descripcion);
      break;
    
    case 'latido':
      console.log(`Estado: ${evento.datos.estado}, Progreso: ${evento.datos.progreso}`);
      break;
    
    case 'error':
      console.error("Error:", evento.datos.mensaje);
      break;
  }
};

ws.onerror = (error) => {
  console.error("Error WebSocket:", error);
};

ws.onclose = () => {
  console.log("Conexión cerrada");
};
```

### Ejemplo 2: Rust con `tokio-tungstenite`

```rust
use tokio_tungstenite::connect_async;
use futures::stream::StreamExt;

#[tokio::main]
async fn main() {
    let agent_id = "a1b2c3d4-...";
    let ws_url = format!("ws://localhost:3000/agents/{}/watch", agent_id);
    
    let (ws_stream, _) = connect_async(&ws_url)
        .await
        .expect("Failed to connect");
    
    let (mut write, mut read) = ws_stream.split();
    
    while let Some(msg) = read.next().await {
        if let Ok(msg) = msg {
            if let Ok(text) = msg.to_text() {
                let evento: serde_json::Value = serde_json::from_str(text)
                    .expect("Failed to parse JSON");
                
                println!("Evento: {} - {}", 
                    evento["tipo"], 
                    evento["datos"]
                );
            }
        }
    }
}
```

### Ejemplo 3: Dashboard en Terminal

```bash
#!/bin/bash
AGENT_ID=$1

echo "Monitoreando agente: $AGENT_ID"
echo "Presiona Ctrl+C para detener"
echo ""

while true; do
  websocat ws://localhost:3000/agents/$AGENT_ID/watch
done
```

---

## Flujo Típico

```
[Client]
   ↓
[Conecta a ws://localhost:3000/agents/{id}/watch]
   ↓
[Servidor]
   ├─ Verifica existencia del agente
   ├─ Envía estado inicial (Inactivo/Ejecutando)
   ├─ Envía progreso inicial (0%)
   ├─ Envía historial de acciones
   ├─ Envía reflexiones previas
   ├─ Envía evento "conectado"
   └─ Inicia latidos (cada 1 segundo)
       ├─ latido con estado actual
       ├─ latido...
       └─ hasta que agente se elimine
```

---

## Características Avanzadas (Fase Futura)

- **Comandos bidireccionales**: Pausar/reanudar ejecución via WebSocket
- **Filtrado de eventos**: Suscribirse solo a tipos específicos
- **Compresión**: Mensaje binario para menos ancho de banda
- **Reentrada**: Reconectar sin perder historial

---

## Performance

| Métrica | Valor |
|---------|-------|
| Latencia | <10ms |
| Frecuencia latidos | 1 por segundo |
| Tamaño evento promedio | ~150 bytes |
| Conexiones concurrentes | Ilimitadas |

---

**Última actualización**: 2026-08-05
