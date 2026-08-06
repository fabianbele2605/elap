# Capítulo 2 — Planificador de Tareas (Task Scheduler)

**Tema central**: Cómo ELAP ejecuta múltiples solicitudes de usuarios sin que se bloqueen unas a otras.

**Objetivo pedagógico**: Entender por qué el Planificador es el corazón del Motor Central.

---

## 🎯 La pregunta que responde este capítulo

> "Si 100 usuarios abren ELAP al mismo tiempo y piden ayuda a diferentes agentes, ¿cómo el sistema procesa todos sin que uno espere eternamente al otro?"

**Respuesta corta**: El Planificador de Tareas, usando una cola inteligente y ejecución concurrente.

---

## 📖 Analogía: Una cafetería muy ocupada

Imagina una cafetería pequeña con **1 barista** y **muchos clientes**:

```
Opción A (malo):
- Cliente 1 llega → barista lo atiende 5 minutos
- Cliente 2 espera
- Cliente 3 espera
- Cliente 4 espera
→ Mucho tiempo de espera

Opción B (mejor - nuestro Planificador):
- Cliente 1 pide café (tarea 1) → barista empieza
- Cliente 2 pide café (tarea 2) → se encola
- Cliente 3 pide café (tarea 3) → se encola
- Cliente 4 pide café CON PRIORIDAD (tarea 4) → se pone adelante
- Barista termina tarea 1 → toma la siguiente
- Los clientes reciben en orden pero TODOS se atienden
```

**El Planificador es ese barista inteligente que:**
- Acepta múltiples pedidos simultáneamente
- Los ordena por prioridad
- Ejecuta uno por uno pero sin que el siguiente espere al anterior

---

## 🔧 ¿Qué es una tarea (Tarea)?

Una **tarea** en ELAP es cualquier solicitud de usuario que el sistema debe procesar:

```rust
┌─────────────────────────────────┐
│         TAREA                   │
├─────────────────────────────────┤
│ ID: uuid-1234                   │ ← Identificador único
│ Nombre: "consulta_agente_ventas"│ ← Qué debe hacer
│ Prioridad: Alta                 │ ← Cuán urgente es
│ Estado: Ejecutando              │ ← Dónde está ahora
│ Creada en: 2026-08-04 10:30:00  │ ← Cuándo llegó
│ Tiempo ejecutando: 2.5s         │ ← Cuánto ha tardado
└─────────────────────────────────┘
```

### Estados de una tarea

```
Pendiente     ─→ Ejecutando ─→ Completada ✅
                      ↓
                    Falló ❌
```

- **Pendiente**: Llegó pero no se ejecuta aún (espera su turno)
- **Ejecutando**: El Motor la está procesando ahora
- **Completada**: Terminó exitosamente
- **Falló**: Hubo un error durante la ejecución

### Prioridades

```
┌────────────────────────────────────────┐
│ PRIORIDADES (de mayor a menor)         │
├────────────────────────────────────────┤
│ Alta    │ Alertas, emergencias        │ ⚡
│ Normal  │ Consultas normales          │ 📋
│ Baja    │ Tareas de fondo, limpieza   │ 🧹
└────────────────────────────────────────┘
```

**Ejemplo real en ELAP:**

```
Usuario pide:           Prioridad:
─────────────────────────────────
1. "Quiero hablar"      Normal   │─┐
2. "¡Alerta de virus!"  Alta     │─┤─ Se ordena
3. "Limpiar cache"      Baja     │─┤  por prioridad
                                   │─┘
                                   
Orden de ejecución: 2 → 1 → 3
```

---

## 📊 La cola de tareas (ColaTareas)

La **cola** es una estructura de datos especial que **ordena automáticamente por prioridad**.

### Cómo funciona internamente

```rust
ColaTareas {
    cola: [ Tarea(Alta), Tarea(Normal), Tarea(Baja) ]
    maximo_concurrentes: 256
    contador_ejecutando: 3
}
```

### Visualización

```
Lluvia de tareas que llegan:
        ↓ (Normal)
        ↓ (Baja)
        ↓ (Alta)
        ↓ (Normal)

        Cola inteligente:
        ┌─────────────────┐
        │ Tarea(Alta)     │ ← Sale primero
        │ Tarea(Normal)   │
        │ Tarea(Normal)   │
        │ Tarea(Baja)     │
        └─────────────────┘
```

**Algoritmo**: Usa una estructura llamada **BinaryHeap** (montículo binario):
- Encontrar la tarea de mayor prioridad: O(1) - ¡muy rápido!
- Agregar una tarea nueva: O(log n) - también rápido
- Funciona aunque haya 10,000 tareas en la cola

---

## 🚀 El API del Planificador (PlanificadorTareas)

El Planificador expone métodos simples que otros módulos usan:

### 1. Crear el planificador

```rust
let planificador = PlanificadorTareas::nuevo(256);
//                                           ^^^
//                                    Max 256 tareas
//                                    simultáneas
```

### 2. Enviar una tarea

```rust
// Tarea normal
let id1 = planificador.enviar("consulta_ventas").await;

// Tarea de alta prioridad
let id2 = planificador.enviar_alta_prioridad("alerta").await;
```

**¿Qué ocurre internamente?**
1. Se crea una `Tarea` con ese nombre
2. Se añade a la `ColaTareas` (se ordena automáticamente)
3. Devuelve el ID para rastrear la tarea

### 3. Obtener la siguiente tarea

```rust
if let Some(tarea) = planificador.proxima_tarea().await {
    // Procesar la tarea...
    println!("Ejecutando: {}", tarea.nombre);
}
```

**¿Qué devuelve?**
- `Some(tarea)`: Hay tarea pendiente (la de mayor prioridad)
- `None`: No hay tareas (cola vacía)

### 4. Marcar como completada

```rust
planificador.completar_tarea(tarea.id).await;
```

Esto:
- Decrementa el contador de tareas ejecutándose
- Permite que se procese la siguiente tarea
- Registra que la tarea fue exitosa

### 5. Marcar como fallida

```rust
planificador.fallar_tarea(tarea.id).await;
```

Cuando algo sale mal, así se reporta.

### 6. Ver estadísticas

```rust
let stats = planificador.estadisticas().await;
println!("{}", stats);
// Output: "Tareas - Pendientes: 5, Ejecutando: 3/256, Total: 8"
```

---

## 🔄 Flujo completo: Paso a paso

Imagina que 3 usuarios usan ELAP simultáneamente:

```
PASO 1: Usuarios envían solicitudes
────────────────────────────────────
Usuario A: "Quiero una consulta de ventas"
Usuario B: "¡Alerta urgente de sistema!"
Usuario C: "Analizar este PDF"

        ↓

PASO 2: El Planificador los encola
────────────────────────────────────
ColaTareas:
┌────────────────────────────────────────┐
│ [Alerta urgente] (Alta)                │ ← Prioridad
│ [Consulta de ventas] (Normal)          │
│ [Analizar PDF] (Normal)                │
└────────────────────────────────────────┘

Estadísticas: Pendientes=3, Ejecutando=0/256

        ↓

PASO 3: Motor obtiene la siguiente tarea
────────────────────────────────────────
tarea = planificador.proxima_tarea().await
// Devuelve: [Alerta urgente]

Estadísticas: Pendientes=2, Ejecutando=1/256

        ↓

PASO 4: Motor procesa la tarea
────────────────────────────────────────
- Valida permisos del Usuario B
- Enruta a agente de Sistema
- Ejecuta en 2 segundos
- Envía respuesta a Usuario B

        ↓

PASO 5: Motor marca como completada
────────────────────────────────────────
planificador.completar_tarea(id_alerta).await

Estadísticas: Pendientes=2, Ejecutando=0/256

        ↓

PASO 6: Siguiente iteración - obtiene siguiente tarea
────────────────────────────────────────
tarea = planificador.proxima_tarea().await
// Devuelve: [Consulta de ventas]

... y así continúa, procesando las tareas en orden de prioridad
```

---

## 🛡️ Seguridad: ¿Qué protege al Planificador?

### Thread-safe

El Planificador puede ser usado desde **múltiples threads** simultáneamente:

```rust
let planificador = Arc::new(PlanificadorTareas::nuevo(256));

// Thread 1: Usuario A envía tarea
let plan1 = Arc::clone(&planificador);
task::spawn(async move {
    plan1.enviar("tarea_A").await;
});

// Thread 2: Usuario B envía tarea
let plan2 = Arc::clone(&planificador);
task::spawn(async move {
    plan2.enviar("tarea_B").await;
});

// Ambas tareas se encolan sin conflicto
```

**Mecanismo**: `Arc<Mutex<>>` (archivo, cadena con cerrojo)

### Sin crasheos silenciosos

Todos los métodos devuelven `Option` o `Result`:

```rust
// ✅ Seguro: Si la tarea no existe, devuelve None (no panic)
if let Some(tarea) = planificador.proxima_tarea().await {
    // procesar
}

// ❌ Inseguro: .unwrap() puede causar panic
let tarea = planificador.proxima_tarea().await.unwrap(); // ¡PELIGRO!
```

---

## 📈 Limitaciones y configuración

### ¿Cuántas tareas puedo tener?

```
Máximo simultáneas (ejecutando):  256 (configurable)
Máximo total encoladas:            Limitado por memoria disponible
```

**Ejemplo:**

```rust
// Para servidor pequeño
let planificador = PlanificadorTareas::nuevo(32);  // Más restrictivo

// Para servidor potente
let planificador = PlanificadorTareas::nuevo(512); // Más permisivo
```

### ¿Qué ocurre si se alcanza el máximo?

```
Si 256 tareas están ejecutándose:
- Tarea 257 llega: ❌ NO se procesa aún
- Tarea 258 llega: ❌ Sigue esperando
- Tarea 1 se completa: ✅ Ahora tarea 257 puede ejecutarse
```

---

## 🧪 Cómo probamos el Planificador

El Planificador tiene **23 tests automatizados**:

```bash
cargo test scheduler::
```

### Test ejemplo 1: Prioridades

```rust
#[tokio::test]
async fn test_ordena_por_prioridad() {
    let planificador = PlanificadorTareas::nuevo(256);
    
    // Enviar en este orden
    planificador.enviar("normal_1").await;
    planificador.enviar_alta_prioridad("urgente").await;
    planificador.enviar("normal_2").await;
    
    // Pero deberían salir en este orden
    let t1 = planificador.proxima_tarea().await.unwrap();
    assert_eq!(t1.nombre, "urgente"); // ← Sale primero (Alta)
    
    let t2 = planificador.proxima_tarea().await.unwrap();
    assert_eq!(t2.nombre, "normal_1"); // ← Normal después
}
```

### Test ejemplo 2: Concurrencia

```rust
#[tokio::test]
async fn test_maximo_concurrentes() {
    let planificador = PlanificadorTareas::nuevo(2); // Max 2
    
    // Enviar 5 tareas
    for i in 0..5 {
        planificador.enviar(&format!("tarea_{}", i)).await;
    }
    
    // Solo 2 deberían estar ejecutando
    let stats = planificador.estadisticas().await;
    assert_eq!(stats.ejecutando, 2);
    assert_eq!(stats.pendientes, 3);
}
```

---

## 💡 Preguntas frecuentes

### P: ¿Qué pasa si una tarea se cuelga y nunca termina?

R: En esta versión, el Planificador no tiene timeout. Es responsabilidad del código que **usa** el Planificador establecer un timeout:

```rust
let resultado = tokio::time::timeout(
    Duration::from_secs(30),
    procesar_tarea(&tarea)
).await;

if resultado.is_err() {
    planificador.fallar_tarea(tarea.id).await;
}
```

### P: ¿Puedo tener más tareas que el máximo de concurrentes?

R: **Sí.** Las tareas en exceso se quedan encoladas esperando:

```
Máximo = 3
Tareas enviadas = 10

┌──────────────┐
│ Ejecutando:  │
│ T1, T2, T3   │ ← 3 en ejecución
├──────────────┤
│ Esperando:   │
│ T4, T5, T6   │ ← 7 encoladas
│ T7, T8, T9   │
│ T10          │
└──────────────┘
```

Cuando T1 termina, automáticamente T4 comienza.

### P: ¿Se pierden tareas si falla el Motor?

R: **En esta versión no hay persistencia.** Si el Motor de IA falla:
- Las tareas encoladas en memoria se pierden
- Las tareas ya completadas están guardadas en la BD

Versiones futuras (Fase 3) agregarán persistencia.

### P: ¿Por qué no usar un canal de Rust en lugar de Arc<Mutex<>>?

R: Ambas son válidas. Elegimos `Arc<Mutex<>>` porque:
- Más fácil de entender
- Permite inspeccionar la cola (obtener estadísticas)
- Compatible con el resto del Motor

---

## 🎓 Lecciones clave

1. **Concurrencia sin bloqueos**: La cola permite que múltiples tareas se encolen sin esperar.

2. **Prioridades inteligentes**: Las tareas urgentes se procesan primero automáticamente.

3. **Escalabilidad**: El BinaryHeap es O(log n), así que 10,000 tareas funcionan sin degradación.

4. **Seguridad**: El `Arc<Mutex<>>` garantiza que múltiples threads puedan usar el Planificador simultáneamente.

5. **Responsabilidad dividida**: El Planificador ordena y controla concurrencia, pero el código que lo usa controla timeouts y errores.

---

## 📚 Conexión con el resto de ELAP

```
┌─────────────────────────────────────┐
│ Motor Central (MotorCentral)        │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐    │
│  │ Planificador de Tareas      │    │
│  │ (Este capítulo)             │    │
│  └─────────────────────────────┘    │
│           ↓                          │
│  ┌─────────────────────────────┐    │
│  │ Gestor de Procesos (Fase 1) │    │
│  │ Ejecuta tareas como subprc. │    │
│  └─────────────────────────────┘    │
│           ↓                          │
│  ┌─────────────────────────────┐    │
│  │ Gestor de Herramientas      │    │
│  │ (Fase 7)                    │    │
│  └─────────────────────────────┘    │
│                                     │
└─────────────────────────────────────┘
```

El Planificador es el **corazón**: todo lo demás depende de él para ejecutar trabajo.

---

## 🔜 Próximo: Gestor de Procesos (Fase 1 - Paso 2)

Ahora que tienes un planificador que ordena tareas, el siguiente paso es aprender cómo el **Gestor de Procesos** las ejecuta como subprocesos del sistema operativo.

**Adelanto:**
- Crear subprocesos sin bloquear el Motor
- Comunicación segura entre procesos
- Aislamiento de fallos (si un proceso falla, el Motor sigue)

---

**Capítulo siguiente**: 03-gestor-procesos.md (Coming soon)
