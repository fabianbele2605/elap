# Capítulo 3 — Gestor de Procesos

**Tema central**: Cómo ejecutar comandos del sistema operativo desde ELAP de forma segura.

**Objetivo pedagógico**: Entender la diferencia entre tareas y procesos, y por qué los necesitamos.

---

## 🎯 La pregunta que responde este capítulo

> "El Planificador ordena tareas, pero ¿cómo se ejecutan realmente esas tareas?"

**Respuesta**: El Gestor de Procesos crea y ejecuta procesos del sistema operativo.

---

## 📖 Analogía: Jefe de proyecto vs empleados

En una empresa:

```
JEFE DE PROYECTO (Planificador)
├─ Recibe solicitudes
├─ Las ordena por prioridad
└─ Asigna a empleados

EMPLEADOS (Gestor de Procesos)
├─ Cada uno ejecuta su tarea
├─ Pueden fallar o tener éxito
├─ Reportan cuándo terminan
└─ Si uno falla, los otros siguen
```

**El Planificador** es el jefe que **ordena el trabajo**.
**El Gestor de Procesos** es quien **lo ejecuta realmente**.

---

## 🔧 ¿Qué es un Proceso?

Un **proceso** es un programa ejecutándose en el sistema operativo.

Ejemplos:

```bash
ls -la /tmp              ← Proceso: listar archivos
python script.py         ← Proceso: ejecutar script Python
curl https://api.com     ← Proceso: descargar datos
docker run image         ← Proceso: ejecutar contenedor
```

### En ELAP, un Proceso es:

```rust
┌─────────────────────────────────────┐
│         PROCESO EN ELAP             │
├─────────────────────────────────────┤
│ ID: uuid-9999                       │ ← Identificador único
│ Nombre: "descargar_pdf"             │ ← Qué hace
│ Comando: "curl"                     │ ← Programa a ejecutar
│ Argumentos: ["https://..."]         │ ← Parámetros
│ Estado: Ejecutando                  │ ← Dónde está
│ Creado en: 2026-08-04 10:00:00      │ ← Cuándo lo creamos
│ Iniciado en: 2026-08-04 10:00:05    │ ← Cuándo empezó
│ Finalizado en: -                    │ ← Aún no termina
│ Código de salida: -                 │ ← Aún sin resultado
└─────────────────────────────────────┘
```

---

## 🔄 Relación: Tarea → Proceso

```
FLUJO COMPLETO:
───────────────

1. Usuario abre ELAP
   ↓
2. Planificador crea TAREA
   (Pendiente)
   ↓
3. Motor obtiene siguiente tarea
   ↓
4. Gestor crea PROCESO para esa tarea
   (Pendiente)
   ↓
5. Gestor EJECUTA el proceso
   (Ejecutando)
   ↓
6. Proceso termina
   (Completado o Fallo)
   ↓
7. Planificador marca tarea como completada
```

### Diferencias clave

| Concepto | Tarea | Proceso |
|----------|-------|---------|
| **Qué es** | Unidad de trabajo en ELAP | Programa ejecutándose en el SO |
| **Cómo se crea** | Planificador | Gestor de Procesos |
| **Aislamiento** | No isolado | Isolado por el SO |
| **Si falla** | Motor sigue, marca como fallida | Motor sigue, marca como fallida |
| **Ciclo de vida** | Solo metadata | Proceso real del SO |

---

## 🚀 El API del Gestor (GestorProcesos)

### 1. Crear el gestor

```rust
let gestor = GestorProcesos::nuevo().await;
```

### 2. Crear un proceso

**Sin argumentos:**
```rust
let id = gestor.crear_proceso(
    "mi_proceso".to_string(),   // Nombre
    "echo".to_string()          // Comando
).await;
```

**Con argumentos:**
```rust
let id = gestor.crear_proceso_con_args(
    "copiar_archivo".to_string(),       // Nombre
    "cp".to_string(),                   // Comando
    vec!["origen.txt".to_string(), "destino.txt".to_string()],  // Args
).await;
```

### 3. Ejecutar el proceso

```rust
match gestor.ejecutar_proceso(id).await {
    Ok(0) => println!("✅ Éxito"),
    Ok(code) => println!("❌ Falló con código {}", code),
    Err(e) => println!("❌ Error: {}", e),
}
```

**¿Qué significa código 0?**
- En Unix/Linux: 0 = éxito, cualquier otro número = error
- Es un estándar del SO

### 4. Ver estado actual

```rust
let estado = gestor.obtener_estado(id).await?;
println!("Estado: {}", estado);
// Output: "Estado: Completado"
```

### 5. Ver proceso completo

```rust
let proceso = gestor.obtener_proceso(id).await?;
println!("Nombre: {}", proceso.nombre);
println!("Estado: {}", proceso.estado);
println!("Código salida: {:?}", proceso.codigo_salida);
println!("Tiempo ejecutando: {}s", proceso.tiempo_transcurrido().unwrap_or(0));
```

### 6. Ver estadísticas globales

```rust
let ejecutando = gestor.contar_ejecutando().await;
let completados = gestor.contar_completados().await;
let fallidos = gestor.contar_fallidos().await;

println!("Ejecutando: {}", ejecutando);
println!("Completados: {}", completados);
println!("Fallidos: {}", fallidos);
```

---

## 🔄 Flujo paso a paso: Ejecutar un comando

Imagina que el usuario quiere ejecutar `ls -la /tmp`:

```
PASO 1: Crear el proceso
─────────────────────────
GestorProcesos::crear_proceso_con_args(
    "listar_tmp".to_string(),
    "ls".to_string(),
    vec!["-la".to_string(), "/tmp".to_string()],
).await
    → ID: uuid-1234

PROCESO RESULTANTE:
{
    id: uuid-1234,
    nombre: "listar_tmp",
    comando: "ls",
    argumentos: ["-la", "/tmp"],
    estado: Pendiente,
    ...
}

        ↓

PASO 2: Ejecutar
───────────────
gestor.ejecutar_proceso(uuid-1234).await

PROCESO RESULTANTE:
{
    ...
    estado: Ejecutando,      ← Cambió
    iniciado_en: Some(1625...) ← Timestamp guardado
    ...
}

        ↓

(El SO ejecuta: ls -la /tmp)
(Muestra archivos de /tmp)

        ↓

PASO 3: Proceso termina (después de 0.5 segundos)
──────────────────────────────────────────────────

PROCESO RESULTANTE:
{
    ...
    estado: Completado,          ← Cambió
    finalizado_en: Some(1625...) ← Timestamp guardado
    codigo_salida: Some(0),      ← ¡Éxito!
    tiempo_transcurrido: 1s
    ...
}
```

---

## 🛡️ Seguridad: ¿Qué protege?

### Aislamiento del SO

Cada proceso es **independiente**:

```
┌──────────────────────────────┐
│ ELAP (Proceso principal)     │
├──────────────────────────────┤
│                              │
│  ┌────────────────────────┐  │
│  │ Subproceso: curl       │  │
│  │ (si falla, ELAP sigue) │  │
│  └────────────────────────┘  │
│                              │
│  ┌────────────────────────┐  │
│  │ Subproceso: python     │  │
│  │ (si crash, ELAP sigue) │  │
│  └────────────────────────┘  │
│                              │
└──────────────────────────────┘
```

**Ventaja**: Si un subproceso falla, ELAP sigue funcionando.

### Thread-safe

Múltiples threads pueden usar el Gestor simultáneamente:

```rust
// Thread A
let gestor_a = Arc::clone(&gestor);
task::spawn(async move {
    gestor_a.ejecutar_proceso(id_a).await;
});

// Thread B
let gestor_b = Arc::clone(&gestor);
task::spawn(async move {
    gestor_b.ejecutar_proceso(id_b).await;
});

// Ambos pueden ejecutarse sin conflicto
```

---

## 📊 Estados de un Proceso

```
Creación
    ↓
┌─────────────┐
│  Pendiente  │ ← Recién creado, no ejecutado
└─────────────┘
    ↓ (llamar ejecutar_proceso)
┌─────────────────────────────┐
│     Ejecutando              │ ← Proceso en marcha
└─────────────────────────────┘
    ↓ (el SO termina el proceso)
    ├─→ ✅ Completado (código = 0)
    └─→ ❌ Fallo (código != 0 o error)
```

### Transiciones de estado

```rust
// Crear → Pendiente
let id = gestor.crear_proceso(...).await;
let proceso = gestor.obtener_proceso(id).await?;
assert_eq!(proceso.estado, EstadoProceso::Pendiente);

// Ejecutar → Ejecutando → Completado
gestor.ejecutar_proceso(id).await?;
let proceso = gestor.obtener_proceso(id).await?;
assert_eq!(proceso.estado, EstadoProceso::Completado);
```

---

## 📊 Códigos de salida

El **código de salida** es un número que devuelve cada proceso:

```
Código 0:     ✅ Éxito (siempre significa OK)
Código 1-255: ❌ Error (significado depende del programa)

Ejemplos reales:
─────────────
comando ls -la                  → código 0 (éxito)
comando ls /directorio/inexist  → código 2 (error)
comando false                   → código 1 (fallo)
comando true                    → código 0 (éxito)
```

**En ELAP:**

```rust
match gestor.ejecutar_proceso(id).await {
    Ok(0) => println!("✅ Éxito"),
    Ok(1) => println!("❌ Error general"),
    Ok(2) => println!("❌ Comando inválido"),
    Ok(code) => println!("❌ Código {}", code),
    Err(e) => println!("❌ Error: {}", e),
}
```

---

## ⏱️ Timestamps

El Gestor registra cuándo ocurre cada cosa:

```
2026-08-04 10:00:00 → creado_en
    ↓
Usuario llama ejecutar_proceso()
    ↓
2026-08-04 10:00:05 → iniciado_en
    ↓
(Proceso ejecutándose...)
    ↓
2026-08-04 10:00:35 → finalizado_en

tiempo_transcurrido = finalizado_en - iniciado_en = 30 segundos
```

**Para qué sirve:**

```rust
// Medir rendimiento
let tiempo = proceso.tiempo_transcurrido().unwrap_or(0);
if tiempo > 60 {
    tracing::warn!("Proceso tomó demasiado tiempo: {}s", tiempo);
}

// Logging
tracing::info!(
    "Proceso {} completado en {}s",
    proceso.nombre,
    tiempo
);
```

---

## 💡 Preguntas frecuentes

### P: ¿Qué pasa si el proceso tarda mucho?

R: En v0.1, el Gestor **no tiene timeout automático**. El proceso espera indefinidamente. Fase 2 agregará timeout configurable.

**Solución actual:**
```rust
tokio::time::timeout(
    Duration::from_secs(30),
    gestor.ejecutar_proceso(id)
).await?;
```

### P: ¿Puedo capturar STDOUT del proceso?

R: En v0.1 **no**. El Gestor solo captura el código de salida.

**Alternativa:** El proceso puede escribir a archivo mientras ELAP lee el archivo después.

Fase 2 agregará captura de STDOUT/STDERR en tiempo real.

### P: ¿Y si quiero ejecutar múltiples procesos simultáneamente?

R: Usa Tokio para spawning:

```rust
let gestor = Arc::new(GestorProcesos::nuevo().await);

let mut tasks = vec![];

for i in 0..5 {
    let g = Arc::clone(&gestor);
    let task = tokio::spawn(async move {
        let id = g.crear_proceso(...).await;
        g.ejecutar_proceso(id).await
    });
    tasks.push(task);
}

// Esperar a que todos terminen
for task in tasks {
    task.await?;
}
```

### P: ¿Se pierden los procesos si falla ELAP?

R: **Sí**, en v0.1 solo están en memoria. Si ELAP falla, se pierden.

Fase 3 agregará persistencia.

### P: ¿Puedo pasar variables de entorno?

R: En v0.1 **no**. Fase 2 lo agregará.

**Workaround actual:** El proceso puede leer archivos de configuración.

---

## 🎓 Lecciones clave

1. **Tarea vs Proceso**: Una tarea es metadata; un proceso es ejecución real.

2. **Aislamiento**: Si un proceso falla, ELAP sigue funcionando (beneficio del SO).

3. **Estados claros**: Pendiente → Ejecutando → Completado/Fallo.

4. **Códigos de salida**: 0 = éxito, cualquier otro = error.

5. **Thread-safe**: Múltiples threads pueden usar el Gestor sin conflicto.

6. **Timestamps**: Sabes exactamente cuándo ocurrió cada cosa.

---

## 📚 Conexión con los otros capítulos

```
┌────────────────────────────┐
│ Cap 1: Introducción        │
│ (¿Qué es el Motor Central?)│
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│ Cap 2: Planificador        │
│ (Ordena tareas)            │
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│ Cap 3: Gestor de Procesos  │ ← Estás aquí
│ (Ejecuta tareas)           │
└────────┬───────────────────┘
         ↓
┌────────────────────────────┐
│ Cap 4: Flujo Completo      │
│ (Todo junto)               │
└────────────────────────────┘
```

---

## 🔜 Próximo: Flujo Completo (Capítulo 4)

Ahora que sabes:
- Cómo el **Planificador** ordena tareas
- Cómo el **Gestor de Procesos** las ejecuta

El siguiente capítulo muestra **el flujo completo**: una solicitud del usuario desde el principio hasta el final.

**Adelanto:**
- Usuario abre ELAP
- Solicitud llega al Motor Central
- Planificador la ordena
- Gestor la ejecuta
- Resultado vuelve al usuario

---

**Capítulo siguiente**: 04-flujo-completo.md (Coming soon)
