# Módulo Planificador de Tareas (Scheduler)

**Versión**: 0.1.0  
**Estado**: Implementado ✅  
**Ubicación**: `crates/elap-core/src/scheduler/`  
**Responsable**: Motor Central (Rust)

---

## 1. Descripción general

El módulo `scheduler` es el **corazón del Motor Central**. Gestiona la ejecución concurrente de tareas usando Tokio como runtime async.

Es el componente que permite que ELAP ejecute múltiples solicitudes de usuarios simultáneamente sin bloqueos.

---

## 2. Responsabilidades

- ✅ Aceptar tareas en una cola con prioridad
- ✅ Ejecutar tareas de forma concurrente (respetando límite configurable)
- ✅ Rastrear estado de cada tarea (pendiente, ejecutando, completada, falló)
- ✅ Proporcionar estadísticas en tiempo real
- ✅ Permitir cancelación de tareas

---

## 3. Componentes

### 3.1 Módulo `tarea.rs`

Define qué es una tarea en el sistema.

**Tipos principales**:

```rust
pub struct IdTarea(Uuid)           // Identificador único
pub enum PrioridadTarea             // Baja, Normal, Alta
pub enum EstadoTarea                // Pendiente, Ejecutando, Completada, Falló
pub struct Tarea                    // La tarea completa
```

**Métodos clave**:

```rust
Tarea::nueva(nombre)               // Crear tarea
tarea.con_prioridad(prio)          // Establecer prioridad
tarea.establecer_estado(estado)    // Cambiar estado
tarea.tiempo_transcurrido()        // Cuánto tiempo lleva
```

**Ejemplo de uso**:

```rust
let tarea = Tarea::nueva("procesar_agente")
    .con_prioridad(PrioridadTarea::Alta);
```

### 3.2 Módulo `cola.rs`

Implementa la cola de tareas con ordenamiento por prioridad.

**Tipo principal**:

```rust
pub struct ColaTareas {
    cola: BinaryHeap<TareaPrioritizada>,  // Max-heap
    tareas: HashMap<IdTarea, Tarea>,      // Registro de todas
    maximo_concurrentes: usize,           // Límite
    contador_ejecutando: usize,           // Actual
}
```

**Métodos clave**:

```rust
cola.encolar(tarea)                // Agregar tarea
cola.desencolar()                  // Obtener siguiente
cola.marcar_completada(id)         // Marcar como lista
cola.cantidad_pendientes()         // Cuántas esperan
cola.cantidad_ejecutando()         // Cuántas corren ahora
```

**Algoritmo**:

- BinaryHeap (max-heap) ordena por prioridad
- Alta prioridad → primero
- Misma prioridad → FIFO (por creación)
- Respeta límite de concurrencia (no desencola si estamos al límite)

### 3.3 Módulo `ejecutor.rs`

La API pública que usan otros módulos.

**Tipo principal**:

```rust
pub struct PlanificadorTareas {
    cola: Arc<Mutex<ColaTareas>>,
    maximo_concurrentes: usize,
}
```

**Métodos públicos** (todos async):

```rust
pub async fn nuevo(max_concurrent)           // Constructor
pub async fn enviar(nombre)                  // Enviar tarea normal
pub async fn enviar_alta_prioridad(nombre)   // Enviar tarea prioritaria
pub async fn proxima_tarea()                 // Obtener siguiente
pub async fn completar_tarea(id)             // Marcar completada
pub async fn fallar_tarea(id)                // Marcar fallida
pub async fn estadisticas()                  // Obtener stats
pub async fn obtener_estado_tarea(id)        // Verificar estado
```

**Ejemplo de uso**:

```rust
let planificador = PlanificadorTareas::nuevo(256); // Max 256 tareas simultáneas

let id = planificador.enviar("tarea1").await;
let tarea = planificador.proxima_tarea().await;

if let Some(tarea) = tarea {
    // Procesar tarea...
    planificador.completar_tarea(tarea.id).await;
}
```

---

## 4. Patrón de uso

### Paso 1: Crear el planificador

```rust
let planificador = PlanificadorTareas::nuevo(256);
```

### Paso 2: Enviar tareas

```rust
let id1 = planificador.enviar("consulta_agente_ventas").await;
let id2 = planificador.enviar_alta_prioridad("alerta_sistema").await;
```

### Paso 3: Procesar tareas

```rust
loop {
    if let Some(tarea) = planificador.proxima_tarea().await {
        // Ejecutar tarea
        let resultado = procesar(&tarea).await;
        
        if resultado.es_ok() {
            planificador.completar_tarea(tarea.id).await;
        } else {
            planificador.fallar_tarea(tarea.id).await;
        }
    }
}
```

### Paso 4: Monitoreo

```rust
let stats = planificador.estadisticas().await;
println!("{}", stats);
// Output: "Tareas - Pendientes: 5, Ejecutando: 3/256, Total: 8"
```

---

## 5. Seguridad y concurrencia

### Thread-safe

- `PlanificadorTareas` usa `Arc<Mutex<ColaTareas>>`
- Múltiples threads pueden llamar métodos simultáneamente
- `Mutex` garantiza acceso serializado a la cola

### Sin panics

- Todos los métodos devuelven `Option` o `Result`
- Nunca hace `.unwrap()` que pueda fallar
- Manejo seguro de IDs inexistentes

### Async-aware

- Todos los métodos son `async`
- Compatible con Tokio runtime
- No bloquea el thread (usa `.await`)

---

## 6. Testing

**23 tests en total**:

```
✅ task.rs:     5 tests
✅ queue.rs:    6 tests  
✅ executor.rs: 5 tests
✅ core.rs:     2 tests
✅ config.rs:   3 tests
✅ error.rs:    2 tests
```

**Cobertura**: >80%

**Ejecutar tests**:

```bash
cargo test scheduler::
cargo test scheduler:: -- --nocapture  # Ver output
```

---

## 7. Límites y configuración

| Parámetro | Valor | Configurable |
|-----------|-------|-------------|
| Max tareas concurrentes | 256 (default) | Sí |
| Número máximo de tareas totales | Memoria disponible | No |
| Timeout de tarea | Ninguno (responsabilidad del ejecutor) | N/A |
| Prioridades | 3 niveles (Baja, Normal, Alta) | No |

---

## 8. Integración con otros módulos

### Recibe de

- **Motor Central** (core.rs): crea el planificador en el startup

### Proporciona a

- **Motor Central**: API para encolar y procesar tareas
- **Futuro Motor de Procesos** (Fase 1-2): tareas para spawning de subprocesos
- **Futuro Motor de Plugins** (Fase 6): ejecución de plugins como tareas

---

## 9. Ejemplos avanzados

### Prioridades dinámicas

```rust
// Tarea urgente
let id_urgente = planificador.enviar_alta_prioridad("alerta").await;

// Tarea normal
let id_normal = planificador.enviar("consulta").await;

// Tarea de fondo
let id_fondo = planificador.enviar("limpieza").await;

// La urgente se procesa primero
```

### Manejo de fallos

```rust
match procesar(&tarea).await {
    Ok(resultado) => {
        planificador.completar_tarea(tarea.id).await;
    }
    Err(error) => {
        tracing::error!("Tarea {} falló: {}", tarea.id, error);
        planificador.fallar_tarea(tarea.id).await;
    }
}
```

### Monitoreo continuo

```rust
loop {
    let stats = planificador.estadisticas().await;
    
    if stats.pendientes > 100 {
        tracing::warn!("Cola con backlog alto: {}", stats);
    }
    
    tokio::time::sleep(Duration::from_secs(10)).await;
}
```

---

## 10. Decisiones de diseño

### ¿Por qué BinaryHeap?

- O(log n) insertion/removal vs O(n) para lista ordenada
- Escalable a miles de tareas
- Estándar en Rust

### ¿Por qué Arc<Mutex<>>?

- `Arc` permite múltiples propietarios (threads)
- `Mutex` serializa acceso a la cola
- Alternativa: canales (más complejo para este caso)

### ¿Por qué Tokio?

- Runtime superior a asyncio
- Mejor throughput para miles de tareas
- Ya usado por Motor Central

---

## 11. Roadmap futuro

| Fase | Mejora |
|------|--------|
| 1.1 | Metrics/observabilidad de la cola |
| 1.2 | Callback al completar tarea |
| 2.0 | Distribuir tareas entre workers (thread pool) |
| 3.0 | Persistencia de tareas (recovery) |

---

## 12. Referencias

- **Código**: `crates/elap-core/src/scheduler/`
- **Tests**: Mismos archivos, módulo `tests`
- **Arquitectura**: [ARCHITECTURE.md](../01-Architecture/ARCHITECTURE.md)
- **Decisiones**: [DECISIONS.md](../01-Architecture/DECISIONS.md)

---

**Última actualización**: 2026-08-04  
**Próximo módulo documentado**: Gestor de Procesos (Fase 1-2)
