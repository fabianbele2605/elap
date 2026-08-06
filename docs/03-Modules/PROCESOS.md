# Módulo Gestor de Procesos (Procesos)

**Versión**: 0.1.0  
**Estado**: Implementado ✅  
**Ubicación**: `crates/elap-core/src/procesos/`  
**Responsable**: Motor Central (Rust)

---

## 1. Descripción general

El módulo `procesos` permite crear y ejecutar **procesos del sistema operativo** de forma segura y concurrente desde Rust.

Mientras el Planificador ordena tareas, el Gestor de Procesos las **ejecuta como procesos aislados del SO**, permitiendo:

- Ejecución segura de comandos externos
- Aislamiento de fallos (si un proceso falla, el Motor sigue)
- Rastreo completo de estado y tiempos
- API thread-safe para múltiples threads simultáneos

---

## 2. Responsabilidades

- ✅ Crear procesos con nombre y comando
- ✅ Ejecutar procesos de forma sincrónica (bloqueante)
- ✅ Rastrear estado: Pendiente → Ejecutando → Completado/Fallo
- ✅ Capturar códigos de salida
- ✅ Registrar timestamps de creación, inicio y finalización
- ✅ Permitir listar procesos y contar por estado
- ✅ Thread-safe: múltiples threads pueden usar simultáneamente

---

## 3. Componentes

### 3.1 Módulo `proceso.rs`

Define qué es un proceso.

**Tipos principales**:

```rust
pub struct IdProceso(Uuid)              // Identificador único
pub enum EstadoProceso                  // Pendiente, Ejecutando, Completado, Fallo
pub struct Proceso                      // La metadata completa
```

**Estructura de Proceso**:

```rust
pub struct Proceso {
    pub id: IdProceso,                  // UUID único
    pub nombre: String,                 // Nombre descriptivo
    pub comando: String,                // Comando a ejecutar (ej. "ls", "python")
    pub argumentos: Vec<String>,        // Argumentos del comando
    pub estado: EstadoProceso,          // Estado actual
    pub codigo_salida: Option<i32>,     // Código de salida (0=éxito)
    pub creado_en: u64,                 // Timestamp creación (segundos época)
    pub iniciado_en: Option<u64>,       // Timestamp cuando comenzó
    pub finalizado_en: Option<u64>,     // Timestamp cuando terminó
}
```

**Métodos clave**:

```rust
Proceso::nueva(nombre, comando)         // Crear proceso
proceso.con_argumentos(args)            // Establecer argumentos
proceso.establecer_estado(estado)       // Cambiar estado
proceso.tiempo_transcurrido()           // Segundos ejecutando
```

**Ejemplo**:

```rust
let proceso = Proceso::nueva("listar_archivos".to_string(), "ls".to_string())
    .con_argumentos(vec!["-la".to_string(), "/tmp".to_string()]);
```

### 3.2 Módulo `spawner.rs`

Implementa la creación y ejecución de procesos del SO.

**Tipo principal**:

```rust
pub struct Spawner;
```

**Métodos**:

```rust
Spawner::ejecutar(proceso)              // Crea e inicia un proceso
Spawner::esperar_completacion(child)    // Espera a que termine
```

**Algoritmo**:

1. `Spawner::ejecutar()` llama a `std::process::Command`
2. Genera un `Child` (handle del proceso del SO)
3. Devuelve el `Child` para que el código lo espere

**Ejemplo**:

```rust
let proceso = Proceso::nueva("echo".to_string(), "echo".to_string())
    .con_argumentos(vec!["Hola ELAP".to_string()]);

let child = Spawner::ejecutar(&proceso)?;
let codigo = Spawner::esperar_completacion(child)?;
println!("Código de salida: {}", codigo);  // 0 = éxito
```

### 3.3 Módulo `ejecutor.rs`

La API pública que usan otros módulos.

**Tipo principal**:

```rust
pub struct GestorProcesos {
    procesos: Arc<Mutex<HashMap<IdProceso, Proceso>>>,
}
```

**Métodos públicos** (todos async):

```rust
pub async fn nuevo()                                    // Constructor
pub async fn crear_proceso(nombre, comando)            // Crear (sin args)
pub async fn crear_proceso_con_args(nombre, cmd, args) // Crear (con args)
pub async fn ejecutar_proceso(id)                      // Ejecutar sincrónico
pub async fn obtener_estado(id)                        // Ver estado actual
pub async fn obtener_proceso(id)                       // Obtener proceso completo
pub async fn listar_procesos()                         // Todos los procesos
pub async fn contar_ejecutando()                       // Cuántos se ejecutan
pub async fn contar_completados()                      // Cuántos terminaron bien
pub async fn contar_fallidos()                         // Cuántos fallaron
```

**Ejemplo de uso**:

```rust
let gestor = GestorProcesos::nuevo().await;

// 1. Crear proceso
let id = gestor.crear_proceso_con_args(
    "copiar".to_string(),
    "cp".to_string(),
    vec!["archivo.txt".to_string(), "backup.txt".to_string()],
).await;

// 2. Ejecutar (bloqueante)
match gestor.ejecutar_proceso(id).await {
    Ok(codigo) if codigo == 0 => println!("Éxito"),
    Ok(codigo) => println!("Falló con código {}", codigo),
    Err(e) => println!("Error: {}", e),
}

// 3. Verificar estado final
let proceso = gestor.obtener_proceso(id).await?;
println!("Estado: {}", proceso.estado);
println!("Tiempo: {}s", proceso.tiempo_transcurrido().unwrap_or(0));
```

### 3.4 Módulo `error.rs`

Errores específicos de procesos.

```rust
pub enum ErrorProceso {
    NoSePudoCrear(String),       // Fallo al crear
    ProcesoNoEncontrado(String), // ID no existe
    FalloIO(String),             // Error del SO
    ProcesoFallo(i32),           // Salió con código != 0
}
```

---

## 4. Patrón de uso

### Paso 1: Crear el gestor

```rust
let gestor = GestorProcesos::nuevo().await;
```

### Paso 2: Crear un proceso

```rust
let id = gestor.crear_proceso_con_args(
    "test_cmd".to_string(),
    "bash".to_string(),
    vec!["-c".to_string(), "echo 'Hola'".to_string()],
).await;
```

### Paso 3: Ejecutar (sincrónico - bloqueante)

```rust
match gestor.ejecutar_proceso(id).await {
    Ok(0) => println!("Éxito"),
    Ok(code) => println!("Falló: {}", code),
    Err(e) => println!("Error: {}", e),
}
```

### Paso 4: Consultar estado y metadata

```rust
let proceso = gestor.obtener_proceso(id).await?;
println!("Estado: {}", proceso.estado);
println!("Tiempo ejecutando: {}s", proceso.tiempo_transcurrido().unwrap_or(0));
println!("Código de salida: {:?}", proceso.codigo_salida);
```

### Paso 5: Monitoreo global

```rust
let stats = (
    gestor.contar_ejecutando().await,
    gestor.contar_completados().await,
    gestor.contar_fallidos().await,
);
println!("Ejecutando: {}, Completados: {}, Fallidos: {}", 
    stats.0, stats.1, stats.2);
```

---

## 5. Estados de un proceso

```
Creación
    ↓
┌─────────────┐
│  Pendiente  │ ← Recién creado, no ejecutado
└─────────────┘
    ↓
Ejecución (ejecutar_proceso())
    ↓
┌─────────────────────────────┐
│     Ejecutando              │ ← Proceso en marcha
└─────────────────────────────┘
    ↓ (proceso termina)
    ├─→ Completado (código = 0) ✅
    └─→ Fallo (código != 0)     ❌
```

---

## 6. Seguridad y concurrencia

### Thread-safe

- `GestorProcesos` usa `Arc<Mutex<HashMap<>>>`
- Múltiples threads pueden llamar métodos simultáneamente
- El `Mutex` serializa acceso al mapa de procesos

### Async-aware

- Todos los métodos son `async`
- Compatible con Tokio runtime
- No bloquea el thread

### Sin panics

- Todos los métodos devuelven `Option` o `Result`
- No hay `.unwrap()` que pueda fallar
- Manejo seguro de IDs inexistentes

---

## 7. Testing

**15 tests en total**:

```
✅ proceso.rs:    4 tests
✅ spawner.rs:    4 tests
✅ ejecutor.rs:   8 tests
```

**Ejecutar tests**:

```bash
cargo test procesos::
cargo test procesos:: -- --nocapture    # Ver output
```

**Ejemplo de test**:

```rust
#[tokio::test]
async fn test_ejecutar_proceso_exitoso() {
    let gestor = GestorProcesos::nuevo().await;
    let id = gestor.crear_proceso("true_test".to_string(), "true".to_string()).await;

    let resultado = gestor.ejecutar_proceso(id).await;
    assert!(resultado.is_ok());
    assert_eq!(resultado.unwrap(), 0);

    let proceso = gestor.obtener_proceso(id).await.unwrap();
    assert_eq!(proceso.estado, EstadoProceso::Completado);
}
```

---

## 8. Integración con Planificador

El Gestor de Procesos se integra con el Planificador de Tareas:

```rust
// 1. Planificador ordena tareas por prioridad
let id_tarea = planificador.enviar("mi_comando").await;

// 2. Motor obtiene siguiente tarea
if let Some(tarea) = planificador.proxima_tarea().await {
    // 3. Crear proceso a partir de tarea
    let id_proc = gestor.crear_proceso(
        tarea.nombre,
        "bash".to_string(), // o el comando de la tarea
    ).await;

    // 4. Ejecutar proceso
    match gestor.ejecutar_proceso(id_proc).await {
        Ok(_) => planificador.completar_tarea(tarea.id).await,
        Err(_) => planificador.fallar_tarea(tarea.id).await,
    }
}
```

---

## 9. Limitaciones actuales

| Aspecto | Limitación | Futuro |
|---------|-----------|--------|
| Ejecución | Sincrónica (bloqueante) | Async-spawning (Fase 2) |
| Pipes | No soporta STDIN/STDOUT en tiempo real | Streaming (Fase 2) |
| Timeout | Sin timeout automático | Fase 2 |
| Persistencia | Procesos en memoria solamente | Fase 3 |
| Env vars | Sin soporte para variables de entorno | Fase 2 |

---

## 10. Decisiones de diseño

### ¿Por qué Arc<Mutex<>>?

- `Arc` permite múltiples propietarios (threads)
- `Mutex` serializa acceso al mapa
- Alternativa considerada: canales (más complejo, no es necesario aquí)

### ¿Por qué sincrónico y no async?

- En v0.1 es más simple y predecible
- Fase 2 introducirá spawning asincrónico
- Permite feedback inmediato del código de salida

### ¿Por qué no capturar STDOUT/STDERR?

- Versión 0.1 enfocada en funcionalidad básica
- Fase 2 agregará streaming de salida
- Los procesos pueden escribir a archivos mientras tanto

---

## 11. Roadmap futuro

| Fase | Mejora |
|------|--------|
| 1.1 | Variables de entorno |
| 2.0 | Async spawning (no-bloqueante) |
| 2.1 | Captura de STDOUT/STDERR |
| 2.2 | Timeout automático |
| 3.0 | Persistencia de procesos completados |
| 3.1 | Monitoreo de recursos (CPU, memoria) |

---

## 12. Referencias

- **Código**: `crates/elap-core/src/procesos/`
- **Tests**: Mismos archivos, módulo `tests`
- **Arquitectura**: [ARCHITECTURE.md](../01-Architecture/ARCHITECTURE.md)
- **Comparación con Planificador**: [SCHEDULER.md](./SCHEDULER.md)

---

**Última actualización**: 2026-08-04  
**Próximo módulo**: Motor de Configuración (Fase 1, Paso 3)
