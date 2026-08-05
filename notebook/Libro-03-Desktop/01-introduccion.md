# Libro 03: Desktop Runtime — Capítulo 1 — Introducción

**Tema central**: Cómo la interfaz gráfica habla con el corazón del sistema.

**Objetivo pedagógico**: Entender por qué separar UI del core y cómo se comunican.

---

## 🎯 La pregunta que responde este capítulo

> "¿Cómo hace el botón 'Iniciar' en la pantalla para que el Motor Central realmente se inicie?"

**Respuesta**: A través de un puente IPC que envía comandos serializados.

---

## 📖 Analogía: Teléfono entre dos oficinas

Imagina dos oficinas en pisos diferentes:

```
PISO 5: Oficina UI (Frontend)
│
│ Cliente llama por teléfono
│ "Quiero iniciar el motor"
│     ↓
│ PUENTE TELEFÓNICO (IPC)
│     ↓
PISO 1: Oficina Motor (Backend)
│
│ Encargado escucha
│ "OK, iniciando..."
│     ↓
│ Hace el trabajo
│     ↓
│ "Listo, motor iniciado"
│ (devuelve respuesta)
```

**IPC = Teléfono que conecta las dos oficinas**

---

## 🏗️ Estructura Desktop en ELAP

```
┌─────────────────────────────────────┐
│   Frontend (TypeScript/React)       │
│   ├─ Botones, ventanas, gráficos    │
│   └─ Tauri Bridge (comunicación)    │
│                                     │
├─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤
│   IPC Bridge (Rust)                 │
│   ├─ Commands (cmd_init_motor)      │
│   ├─ Errors (MotorNotInitialized)   │
│   └─ Serialización a JSON           │
│                                     │
├─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤
│   UI Components (Rust)              │
│   ├─ States (AppState, etc)         │
│   └─ Components (Window, Button...)  │
│                                     │
├─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤
│   Motor Central (Rust)              │
│   ├─ RBAC, Logging, Config          │
│   └─ Procesos, Tareas               │
└─────────────────────────────────────┘
```

---

## 🔌 IPC Bridge — El puente

**IPC = Inter-Process Communication**

Significa: "Dos procesos hablando entre sí"

```
Proceso Frontend                Proceso Backend
(TypeScript)                    (Rust Motor)
     │                               │
     │ "Dame estado"                 │
     ├──────────────────────────────>│
     │                               │
     │ ╔═══════════════════════╗     │
     │ ║ IPC Bridge (Tauri)   ║     │
     │ ║ • Serializa JSON     ║     │
     │ ║ • Envía por socket   ║     │
     │ ║ • Deserializa respuesta     │
     │ ║ • Entrega al frontend║     │
     │ ╚═══════════════════════╝     │
     │                               │
     │ "{motor_running: true}"       │
     │<──────────────────────────────┤
     │                               │
```

---

## 📋 Los 3 Comandos IPC

### 1. cmd_init_motor
**¿Qué hace?** Inicializa el Motor Central  
**Toma**: Nada (usa el motor ya existente)  
**Devuelve**: `{ success: true, message: "..." }`

```
Frontend: Usuario hace clic en "Iniciar"
   ↓
Frontend: cmd_init_motor()
   ↓
Backend: motor.iniciar().await
   ↓
Backend: Devuelve respuesta JSON
   ↓
Frontend: Actualiza botón a "Deteniendo disponible"
```

### 2. cmd_get_status
**¿Qué hace?** Obtiene el estado del motor  
**Toma**: Nada  
**Devuelve**: `{ motor_running: true, timestamp: 1234567 }`

Usado para:
- Mostrar indicador "Motor Activo" ✅
- Actualizar barra de estado
- Habilitar/deshabilitar botones

### 3. cmd_get_rbac_status
**¿Qué hace?** Obtiene permisos del usuario  
**Toma**: Nada  
**Devuelve**: `{ usuario_rol: "Admin", permisos_disponibles: [...] }`

Usado para:
- Mostrar qué herramientas puede usar
- Habilitar/deshabilitar acciones según permisos
- Validar antes de ejecutar

---

## 🗂️ Estados (State)

Un **State** es un "snapshot" (foto) del sistema en un momento.

### AppState — "Foto general del sistema"
```json
{
  "motor_running": true,
  "timestamp": 1234567890,
  "mode": "producción"
}
```

Dice: "En este momento (timestamp), el motor está activo y estamos en producción"

### ToolbarState — "¿Qué botones debo mostrar?"
```json
{
  "can_start": false,
  "can_stop": true,
  "can_execute_tools": true
}
```

Si `motor_running: true`, entonces `can_start: false` (no tiene sentido iniciar si ya está activo)

### StatusBarState — "¿Qué le digo al usuario?"
```json
{
  "message": "Motor iniciado correctamente",
  "level": "info",
  "timestamp": 1234567890
}
```

Aparece en la barra inferior: "✅ Motor iniciado correctamente"

---

## 🧩 Componentes

Un **Componente** es un "bloque de construcción" de UI.

### WindowComponent
```json
{
  "title": "ELAP - Enterprise Local AI Platform",
  "width": 1200,
  "height": 800,
  "resizable": true
}
```

Define la ventana principal: tamaño, título, etc.

### ButtonComponent
```json
{
  "id": "btn_start",
  "label": "Iniciar Motor",
  "enabled": true,
  "action": "cmd_init_motor"
}
```

Cuando el usuario hace clic:
1. Se llama a `cmd_init_motor()`
2. Botón se deshabilita mientras ejecuta
3. Actualiza estado cuando termina

### LogPanelComponent
```json
{
  "logs": [
    { "timestamp": 1234567890, "level": "info", "message": "Motor iniciado" },
    { "timestamp": 1234567891, "level": "debug", "message": "Validación OK" }
  ],
  "max_lines": 100
}
```

Panel que muestra logs en vivo. Mantiene máximo 100 líneas (elimina las viejas).

---

## 💬 Conversación real: Usuario hace clic en "Iniciar"

```
1. Frontend: Usuario hace clic en botón "Iniciar"
   
2. Frontend → IPC: cmd_init_motor()
   
3. Backend: Recibe comando
   motor.iniciar().await
   
4. Backend ejecuta:
   - Carga config
   - Inicializa logging
   - Valida RBAC
   - Arranca planificador
   
5. Backend: Devuelve JSON
   { "success": true, "message": "Motor inicializado correctamente" }
   
6. Frontend: Recibe respuesta
   
7. Frontend: Actualiza UI
   - Botón "Iniciar" → deshabilitado
   - Botón "Detener" → habilitado
   - StatusBar: "✅ Motor activo"
   - AppState.motor_running = true
```

**Todo ocurre en < 1 segundo**

---

## 🔐 Seguridad: Cada comando valida RBAC

```
Usuario hace clic en "Ejecutar Herramienta"
   ↓
Frontend: cmd_execute_tool()
   ↓
Backend: ¿Usuario tiene permiso?
   - Si NO → Devuelve IpcError::PermissionDenied
   - Si SÍ → Ejecuta herramienta
   ↓
Frontend: Muestra resultado o error
```

---

## 🎓 Lecciones clave

1. **Separación**: Frontend y Backend son procesos independientes
2. **Comunicación**: IPC Bridge permite que hablen sin acoplarse
3. **JSON**: Formato estándar que todos entienden
4. **Async**: Los comandos no bloquean la UI
5. **Serialización**: Convertir objetos Rust a JSON y viceversa

---

## 📚 Conexión con Libro 02

```
Libro 02: Core Runtime (Rust backend)
  ├─ Motor Central
  ├─ Planificador
  ├─ RBAC
  └─ Logging

        ↓ (IPC Bridge)

Libro 03: Desktop Runtime (UI)
  ├─ Commands IPC
  ├─ UI Components
  ├─ States
  └─ Frontend (próximo)
```

El Frontend **consume** lo que el Backend proporciona.

---

## 🔜 Próximo: Capítulo 2

**"Implementar tu primer comando"**

Crearemos un nuevo comando desde cero:
1. Función en backend
2. Tests
3. Serialización
4. Consumir desde frontend

---

**Capítulo siguiente**: 02-primer-comando.md (Coming soon)
