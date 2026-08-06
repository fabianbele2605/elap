# REST API — Interfaz HTTP para Agentes

**Autor**: ELAP Development Team  
**Fecha**: 2026-08-05  
**Versión**: 1.0  
**Fase**: 9 - Paso 1

## Índice

1. [Descripción General](#descripción-general)
2. [Endpoints](#endpoints)
3. [Ejemplos](#ejemplos)
4. [Respuestas](#respuestas)
5. [Estado del Servidor](#estado-del-servidor)

---

## Descripción General

La **REST API** proporciona interfaz HTTP para crear, ejecutar y monitorear agentes ELAP.

### Stack Tecnológico

- **Framework**: Axum 0.7 (async, Tower middleware)
- **Async Runtime**: Tokio 1.35
- **Serialización**: serde_json
- **Logging**: tower-http
- **CORS**: tower-http CorsLayer

### Características

- ✅ **CRUD completo** de agentes
- ✅ **Ejecución asincrónica** de planes
- ✅ **Monitoreo en vivo** de estado
- ✅ **CORS configurado** para desarrollo
- ✅ **Response types tipados** con serde

---

## Endpoints

### 1. POST /agents — Crear Agente

**Descripción**: Crear un nuevo agente inteligente

**Request**:
```json
{
  "nombre": "Analizador de Ventas",
  "rol": "Data Scientist",
  "objetivo": "Procesar 100 pedidos"
}
```

**Response** (201 Created):
```json
{
  "id": "a1b2c3d4-e5f6-4g7h-i8j9-k0l1m2n3o4p5",
  "nombre": "Analizador de Ventas",
  "rol": "Data Scientist",
  "objetivo": "Procesar 100 pedidos",
  "estado": "Inactivo",
  "progreso": 0.0
}
```

---

### 2. GET /agents — Listar Agentes

**Descripción**: Obtener lista de todos los agentes

**Response** (200 OK):
```json
{
  "total": 3,
  "agentes": [
    {
      "id": "a1b2c3d4-...",
      "nombre": "Analizador de Ventas"
    },
    {
      "id": "e5f6g7h8-...",
      "nombre": "Procesador de Datos"
    }
  ]
}
```

---

### 3. GET /agents/{id} — Obtener Agente

**Descripción**: Obtener detalles de un agente específico

**Parámetros**:
- `id` (path): UUID del agente

**Response** (200 OK):
```json
{
  "id": "a1b2c3d4-...",
  "nombre": "Analizador de Ventas",
  "rol": "Data Scientist",
  "objetivo": "Procesar 100 pedidos",
  "estado": "Inactivo",
  "progreso": 0.0
}
```

**Errores**:
- `404 Not Found`: Agente no existe

---

### 4. POST /agents/{id}/pasos — Agregar Paso

**Descripción**: Agregar paso al plan del agente

**Request**:
```json
{
  "descripcion": "Leer archivo de ventas",
  "tipo_herramienta": "archivo",
  "parametros": {
    "operacion": "leer",
    "ruta": "/datos/ventas.csv"
  }
}
```

**Response** (200 OK):
```json
{
  "paso_agregado": true,
  "descripcion": "Leer archivo de ventas"
}
```

---

### 5. POST /agents/{id}/execute — Ejecutar Agente

**Descripción**: Ejecutar el plan del agente

**Response** (200 OK):
```json
{
  "agente_id": "a1b2c3d4-...",
  "estado": "Completado",
  "pasos_completados": 4,
  "progreso": 1.0
}
```

**Estados posibles**:
- `Inactivo` - Esperando
- `Ejecutando` - En proceso
- `Completado` - Exitoso
- `Error` - Falló

---

### 6. GET /agents/{id}/status — Obtener Estado

**Descripción**: Estado en vivo del agente

**Response** (200 OK):
```json
{
  "agente_id": "a1b2c3d4-...",
  "nombre": "Analizador de Ventas",
  "estado": "Ejecutando",
  "pasos": {
    "total": 4,
    "completados": 2,
    "progreso": "50%"
  },
  "historial": {
    "acciones": 5,
    "reflexiones": 1
  }
}
```

---

### 7. DELETE /agents/{id} — Eliminar Agente

**Descripción**: Eliminar un agente

**Response** (204 No Content)

---

## Ejemplos

### Ejemplo 1: Crear y Ejecutar Agente

```bash
# 1. Crear agente
curl -X POST http://localhost:3000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Bot de Ventas",
    "rol": "Sales Agent",
    "objetivo": "Procesar pedidos"
  }'

# Respuesta: { "id": "abc123..." }

# 2. Agregar pasos
curl -X POST http://localhost:3000/agents/abc123/pasos \
  -H "Content-Type: application/json" \
  -d '{
    "descripcion": "Validar pedidos",
    "tipo_herramienta": "sql",
    "parametros": {"query": "SELECT * FROM pedidos"}
  }'

# 3. Ejecutar
curl -X POST http://localhost:3000/agents/abc123/execute

# 4. Monitorear
curl http://localhost:3000/agents/abc123/status
```

### Ejemplo 2: Monitoreo Continuo

```bash
# Script para monitorear progreso cada 2 segundos
while true; do
  curl http://localhost:3000/agents/abc123/status | jq '.pasos.progreso'
  sleep 2
done
```

---

## Respuestas

### Success (2xx)

| Status | Respuesta | Caso |
|--------|-----------|------|
| 200 | JSON | GET, POST (sin crear) |
| 201 | JSON + header Location | POST (crear recurso) |
| 204 | (vacío) | DELETE exitoso |

### Errores (4xx/5xx)

| Status | Descripción |
|--------|------------|
| 400 | Bad Request - Parámetros inválidos |
| 404 | Not Found - Recurso no existe |
| 500 | Internal Server Error - Error del servidor |

---

## Estado del Servidor

### Configuración

```rust
pub struct ConfiguracionServidor {
    pub puerto: u16,        // Default: 3000
    pub host: String,       // Default: 127.0.0.1
}
```

### Iniciar Servidor

```rust
use elap_core::{AppState, crear_router};
use axum::Server;

#[tokio::main]
async fn main() {
    let state = AppState::nuevo();
    let router = crear_router(state);
    let addr = "127.0.0.1:3000".parse().unwrap();
    
    Server::bind(&addr)
        .serve(router.into_make_service_with_connect_info::<std::net::SocketAddr>())
        .await
        .unwrap();
}
```

---

## CORS

API tiene CORS permisivo para desarrollo:
- ✅ Acceso desde cualquier origen
- ✅ Todos los métodos permitidos
- ✅ Headers permitidos

En producción, restringir a dominios específicos.

---

## Próximas Fases

- **Fase 9 Paso 2**: WebSocket streaming para ejecución en tiempo real
- **Fase 10**: Autenticación y autorización
- **Fase 11**: Rate limiting y throttling

---

**Última actualización**: 2026-08-05
