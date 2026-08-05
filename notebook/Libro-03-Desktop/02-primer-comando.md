# Libro 03: Desktop Runtime — Capítulo 2 — Implementar tu primer comando IPC

**Tema**: Crear un comando personalizado que conecte UI con el motor.

---

## 🎯 Objetivo

Crear un comando IPC que permita al usuario ejecutar una operación personalizada desde la UI.

---

## 📋 Plan

```
1. Definir comando: obtener_estado_sistema()
2. Implementar en ipc/commands.rs
3. Crear estructura de respuesta
4. Agregar test
5. Integrar en UI
```

---

## ✍️ Paso 1: Definir estructura de respuesta

En `crates/elap-desktop/src/ipc/commands.rs`, agrega:

```rust
/// Respuesta de estado del sistema
#[derive(serde::Serialize)]
pub struct EstadoSistemaResponse {
    pub uptime_segundos: u64,
    pub memoria_usada_mb: u32,
    pub procesos_activos: u32,
    pub timestamp: u64,
}
```

---

## 🛠️ Paso 2: Implementar comando

```rust
pub async fn cmd_obtener_estado_sistema(
    _motor: Arc<MotorCentral>
) -> IpcResult<EstadoSistemaResponse> {
    // Simulado (en producción consultar sysinfo)
    Ok(EstadoSistemaResponse {
        uptime_segundos: 3600,
        memoria_usada_mb: 256,
        procesos_activos: 8,
        timestamp: std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs(),
    })
}
```

---

## 🧪 Paso 3: Agregar test

```rust
#[tokio::test]
async fn test_cmd_obtener_estado_sistema() {
    let config = Configuracion::defecto();
    let motor = Arc::new(MotorCentral::nuevo(config));
    
    let resultado = cmd_obtener_estado_sistema(motor).await;
    assert!(resultado.is_ok());
    
    let response = resultado.unwrap();
    assert!(response.uptime_segundos > 0);
    assert_eq!(response.procesos_activos, 8);
}
```

---

## 🎨 Paso 4: Usar en UI

Desde el frontend React:

```javascript
async function mostrarEstadoSistema() {
    const estado = await invoke('cmd_obtener_estado_sistema');
    
    document.getElementById('uptime').textContent = 
        `${estado.uptime_segundos}s`;
    document.getElementById('memoria').textContent = 
        `${estado.memoria_usada_mb}MB`;
}
```

---

## ✅ Verificación

```bash
cargo test -p elap-desktop test_cmd_obtener_estado_sistema
# test result: ok. 1 passed
```

---

**Próximo paso**: Expandir con más comandos (listar archivos, ejecutar herramientas, etc.)
