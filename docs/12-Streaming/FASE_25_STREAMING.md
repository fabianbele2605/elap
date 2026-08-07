# Fase 25: Streaming Responses

**Estado**: ✅ COMPLETADA  
**Fecha**: 2026-08-06  
**Componentes**: Rust API, Python gRPC, Tauri UI
**Commit**: ed4140f

---

## Problema Actual

```
Usuario envía tarea → Ollama genera respuesta → [Espera 79 segundos] → Usuario ve respuesta
```

**Problema**: El usuario espera 79 segundos sin ver nada.

---

## Solución: Streaming en Tiempo Real

```
Usuario envía tarea
    ↓
Ollama comienza a generar
    ↓
WebSocket abre conexión
    ↓
Tokens fluyen en tiempo real
    ↓
UI actualiza mientras se genera
    ↓
"Presupuesto Q3: $50k. Gastado hasta ahora: $32k. Disponible..."
 ▓▓▓▓░░ (escribiendo en tiempo real)
```

---

## Cambios Necesarios

### 1. **Actualizar .proto para Streaming**

```protobuf
// Antes: respuesta completa
rpc ExecuteAgent(ExecuteAgentRequest) 
  returns (ExecuteAgentResponse);

// Después: stream de tokens
rpc ExecuteAgentStreaming(ExecuteAgentRequest) 
  returns (stream ExecuteAgentChunk);

message ExecuteAgentChunk {
  string agent_id = 1;
  string chunk = 2;  // Token o fragmento
  float progress = 3;
}
```

### 2. **Actualizar Python para Streaming**

```python
async def generar_streaming(self, modelo: str, prompt: str):
    """Genera texto en streaming"""
    async for chunk in ollama.generate_streaming(modelo, prompt):
        yield chunk  # Envía cada token al cliente
```

### 3. **Actualizar Rust para WebSocket**

```rust
// Endpoint WebSocket
ws://localhost:3000/agents/{id}/execute/stream

// Recibe tarea, envía tokens en vivo
```

### 4. **Actualizar Tauri UI**

```javascript
// Conectar WebSocket
const ws = new WebSocket('ws://localhost:3000/agents/{id}/execute/stream');

// Recibir tokens en tiempo real
ws.onmessage = (event) => {
  response += event.data;  // Acumula respuesta
  UI.actualiza(response);  // Actualiza en vivo
};
```

---

## Beneficios

| Aspecto | Antes | Después |
|---------|-------|---------|
| Latencia inicial | 79s | <2s (primer token) |
| UX | Esperar en blanco | Ver escritura en vivo |
| Cancelación | No posible | Cierra WebSocket |
| Interrupción | No posible | Usuario puede detener |

---

## Arquitectura

```
Tauri UI
  │
  └─ WebSocket Connection ──────┐
                                 │
Rust Core (localhost:3000)       │
  │                              │
  ├─ ws://stream endpoint ◄──────┘
  │
  └─ gRPC Client ──────────────────┐
                                   │
Python AI Runtime                  │
  │                                │
  ├─ ExecuteAgentStreaming ◄───────┘
  │
  └─ Ollama (streaming chunks)
        │
        └─ yield token ─► Python ─► Rust ─► WebSocket ─► UI
```

---

## Plan de Implementación

### Step 1: Actualizar .proto
- [ ] Agregar `ExecuteAgentStreaming` RPC
- [ ] Definir `ExecuteAgentChunk` mensaje
- [ ] Regenerar código gRPC

### Step 2: Python Streaming
- [ ] Actualizar `ollama_client.py` para streaming
- [ ] Implementar `generar_streaming()`
- [ ] Agregar tests

### Step 3: Rust WebSocket
- [ ] Agregar dependencia `tokio-tungstenite`
- [ ] Crear `/agents/{id}/execute/stream` endpoint
- [ ] Integrar con gRPC client

### Step 4: Tauri UI
- [ ] Crear componente `StreamingResponse.jsx`
- [ ] Conectar WebSocket
- [ ] Mostrar tokens en tiempo real

### Step 5: Tests E2E
- [ ] Test streaming completo
- [ ] Test cancelación
- [ ] Test reconexión

---

## Estimación

| Componente | Tiempo |
|-----------|--------|
| Proto + Codegen | 15min |
| Python streaming | 20min |
| Rust WebSocket | 30min |
| Tauri UI | 25min |
| Tests E2E | 20min |
| **Total** | **110min (~2h)** |

---

## Beneficio Final

**Antes**:
```
Usuario: "¿Presupuesto?"
[Espera 79 segundos en blanco]
Respuesta: "Presupuesto Q3: $50k..."
```

**Después**:
```
Usuario: "¿Presupuesto?"
[2 segundos, aparece primer token]
Presupuesto Q3: $50k. Gastado: $32k. 
[Escritura en vivo mientras Ollama genera]
Disponible: $18k. Tendencia: +5% mes anterior.
[Terminado en 60 segundos, pero usuario vio desde segundo 2]
```

---

## Próximos Pasos

1. ¿Empezamos Step 1 (actualizar .proto)?
2. ¿O prefieres otra abordaje?

---

**Versión**: v1.5.0 (planeada)  
**Prioridad**: Alta (UX crítica)
