# Módulo Desktop Runtime

**Versión**: 0.1.0  
**Estado**: Implementado ✅  
**Ubicación**: `crates/elap-desktop/`  
**Responsable**: Desktop UI (Rust + Tauri)

---

## 1. Descripción general

Capa de interfaz gráfica (UI) para ELAP usando Tauri.
Proporciona puente IPC (Inter-Process Communication) entre frontend y MotorCentral.

Todos los componentes son serializables a JSON para comunicación con frontend.

---

## 2. Responsabilidades

- ✅ Gestionar ciclo de vida de aplicación desktop
- ✅ Proporcionar IPC bridge para comandos
- ✅ Definir estructura de UI components
- ✅ Integración con MotorCentral (Arc<MotorCentral>)
- ✅ Serialización de estados y respuestas

---

## 3. Componentes

### 3.1 Módulo IPC

**Ubicación**: `src/ipc/`

#### errors.rs
Tipos de error para comunicación IPC:

| Error | Uso |
|-------|-----|
| `MotorNotInitialized` | Motor aún no inicializado |
| `PermissionDenied(String)` | Usuario sin permisos |
| `InvalidOperation(String)` | Operación no válida |
| `MotorError(String)` | Error del MotorCentral |

#### commands.rs
Comandos disponibles para frontend:

**cmd_init_motor**
```rust
pub async fn cmd_init_motor(motor: Arc<MotorCentral>) -> IpcResult<InitResponse>
```
- Inicializa MotorCentral
- Retorna: `InitResponse { success: bool, message: String }`

**cmd_get_status**
```rust
pub async fn cmd_get_status(motor: Arc<MotorCentral>) -> IpcResult<StatusResponse>
```
- Obtiene estado del motor
- Retorna: `StatusResponse { motor_running: bool, timestamp: u64 }`

**cmd_get_rbac_status**
```rust
pub async fn cmd_get_rbac_status(motor: Arc<MotorCentral>) -> IpcResult<RbacStatusResponse>
```
- Obtiene permisos RBAC del usuario
- Retorna: `RbacStatusResponse { usuario_rol: String, permisos_disponibles: Vec<String> }`

### 3.2 Módulo UI

**Ubicación**: `src/ui/`

#### state.rs
Estados serializables de la UI:

**AppState**
- `motor_running: bool` — Motor activo
- `timestamp: u64` — Timestamp actual
- `mode: String` — "desarrollo" o "producción"

**ToolbarState**
- `can_start: bool` — Permitir iniciar
- `can_stop: bool` — Permitir detener
- `can_execute_tools: bool` — Permitir ejecutar herramientas

**StatusBarState**
- `message: String` — Mensaje para usuario
- `level: String` — "info", "warning", "error"
- `timestamp: u64` — Cuándo ocurrió

#### components.rs
Componentes visuales serializables:

**WindowComponent**
```rust
pub struct WindowComponent {
    pub title: String,
    pub width: u32,
    pub height: u32,
    pub resizable: bool,
}
```

**ButtonComponent**
```rust
pub struct ButtonComponent {
    pub id: String,
    pub label: String,
    pub enabled: bool,
    pub action: String,
}
```

**LogPanelComponent**
```rust
pub struct LogPanelComponent {
    pub logs: Vec<LogEntry>,
    pub max_lines: usize,
}

pub struct LogEntry {
    pub timestamp: u64,
    pub level: String,
    pub message: String,
}
```

---

## 4. Testing

**Total: 4 tests** (3 IPC + 1 integration)

```
✅ test_cmd_init_motor — Verifica inicialización real
✅ test_cmd_get_status — Verifica estado del motor
✅ test_cmd_get_rbac_status — Verifica permisos RBAC
✅ test_desktop_runtime_creation — Ciclo vida desktop
```

**Ejecución**:
```bash
cargo test -p elap-desktop
```

---

## 5. Integración con MotorCentral

Todos los comandos reciben `Arc<MotorCentral>` para:

```rust
let motor = Arc::new(MotorCentral::nuevo(config));
let response = cmd_init_motor(motor.clone()).await?;
```

Esto permite:
- Iniciar/detener motor desde UI
- Consultar estado RBAC en tiempo real
- Obtener información del sistema

---

## 6. Flujo de comunicación

```
Frontend (TypeScript/React)
        ↓
    Tauri Bridge
        ↓
    IPC Commands
        ↓
    MotorCentral (Arc)
        ↓
    Response (JSON)
        ↓
Frontend (actualizado)
```

---

## 7. Limitaciones y futuro

**Actual (Paso 5)**:
- IPC commands sin Tauri real (placeholder)
- UI states definidos pero sin UI real
- Solo 3 comandos básicos

**Fase 3 (Desktop UI)**:
- Implementar frontend en React/TypeScript
- Conectar Tauri bridge real
- Agregar más comandos
- Crear interfaz visual completa

---

**Última actualización**: 2026-08-05  
**Próximo módulo**: Plugin System (Fase 3)
