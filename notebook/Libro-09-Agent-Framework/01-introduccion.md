# Libro 09: Agent Framework — Agentes Inteligentes Autónomos

## Capítulo 1: ¿Qué son los Agentes?

### La Visión

Imagina que tienes un asistente que puede:

1. **Pensar** - Planificar qué hacer
2. **Actuar** - Ejecutar herramientas (leer archivos, hacer HTTP requests, etc.)
3. **Reflexionar** - Aprender de los resultados
4. **Recordar** - Guardar lecciones para el futuro

Ese es un **Agente Inteligente** en ELAP.

### Analogía del Mundo Real

```
┌─────────────────────────────────────────────┐
│  UN EMPLEADO DE OFICINA (El Agente)        │
├─────────────────────────────────────────────┤
│                                             │
│  Tiene un OBJETIVO:                        │
│  "Procesar 100 pedidos de clientes"        │
│                                             │
│  Tiene un PLAN:                            │
│  1. Leer archivo con pedidos               │
│  2. Validar estructura                     │
│  3. Procesar cada uno                      │
│  4. Guardar resultados                     │
│                                             │
│  Usa HERRAMIENTAS:                         │
│  - Teléfono (HTTP tool)                    │
│  - Correo (HTTP tool)                      │
│  - Excel (Archivo)                         │
│  - Acceso a BD (SQL)                       │
│                                             │
│  APRENDE:                                  │
│  "La próxima vez validaré esto primero"    │
│                                             │
│  RECUERDA:                                 │
│  Últimas 10 tareas (corto plazo)           │
│  Patrones aprendidos (largo plazo)         │
│                                             │
└─────────────────────────────────────────────┘
```

### ¿Por qué Agentes?

En ELAP queremos ir más allá que solo:

```bash
# ❌ Esto es una herramienta simple
herramienta_archivo leer /datos/input.txt
```

Queremos:

```python
# ✅ Esto es un agente inteligente
agente "Procesar reportes" {
    paso 1: leer archivo
    paso 2: validar datos
    paso 3: procesar en LLM
    paso 4: guardar resultado
    aprender: patrones para optimizar
}
```

---

## Capítulo 2: Anatomía de un Agente

### Los 6 Estados

Un agente es una **máquina de estados** que pasa por 6 fases:

```
    [Inactivo]
        ↓ (usuario le da tarea)
    [Planificando]
        ↓
    [Ejecutando] ← (ejecuta pasos)
        ↓
    [Reflexionando] ← (analiza resultados)
        ↓
    [Completado] o [Error]
```

**Ejemplo práctico**:

```rust
// 1. INACTIVO - Agente creado, sin hacer nada
let agente = Agent::nuevo(
    "DataProcessor".to_string(),
    "Data Scientist".to_string(),
);
assert_eq!(agente.estado, EstadoAgente::Inactivo);

// 2. PLANIFICANDO - (Interno, el framework lo hace)
// 3. EJECUTANDO - Cuando comienza a ejecutar pasos
// 4. REFLEXIONANDO - Después de terminar, analiza
// 5. COMPLETADO - Listo
```

### Los 4 Componentes Clave

#### 1️⃣ **Agent** - Identidad y Estado

```rust
pub struct Agent {
    pub id: String,                  // UUID: "a1b2c3d4-..."
    pub nombre: String,              // "Analizador de Datos"
    pub rol: String,                 // "Data Scientist"
    pub estado: EstadoAgente,        // Inactivo, Ejecutando, etc.
    pub historial_acciones: Vec<String>,  // "Leyó archivo", "Procesó 100 registros"
    pub reflexiones: Vec<String>,    // "Aprendí que los CSVs sin header..."
}
```

**¿Para qué sirve?**
- Identidad única (UUID)
- Rol para determinar permisos
- Registro de todo lo que hizo
- Lecciones aprendidas

#### 2️⃣ **Plan** - Qué Hacer

```rust
pub struct Plan {
    pub id: String,              // UUID único
    pub objetivo: String,        // "Procesar 100 pedidos"
    pub pasos: Vec<Paso>,        // Lista de pasos
    pub paso_actual: usize,      // En cuál paso estamos
    pub completado: bool,        // ¿Terminó?
}

pub struct Paso {
    pub numero: usize,           // 1, 2, 3...
    pub descripcion: String,     // "Validar estructura del CSV"
    pub tipo_accion: String,     // "archivo", "sql", "http"...
    pub parametros: JsonValue,   // Configuración específica
    pub completado: bool,        // ¿Lo hizo?
    pub resultado: Option<JsonValue>,  // Qué pasó?
}
```

**Analogía**: El Plan es como una **lista de tareas escrita**:

```
[ ] Paso 1: Leer archivo CSV de /datos/pedidos.csv
[ ] Paso 2: Validar que tenga columnas: ID, Cliente, Monto
[ ] Paso 3: Procesar cada fila en la BD
[ ] Paso 4: Guardar reporte en /resultados/
```

#### 3️⃣ **ContextoAgente** - Variables Dinámicas

```rust
pub struct ContextoAgente {
    pub objetivo: String,
    pub variables: HashMap<String, JsonValue>,  // Estado mutable
    pub restricciones: Vec<String>,             // "Sin acceso a BD de producción"
    pub timestamp_inicio: i64,
}
```

**Ejemplo práctico**:

```rust
let mut contexto = ContextoAgente::nuevo("Procesar datos");

// Registrar datos mientras ejecuta
contexto.set_variable("total_leido", json!(1000));
contexto.set_variable("total_procesado", json!(950));
contexto.set_variable("errores", json!(50));

// El agente puede leer esto después
let total = contexto.get_variable("total_leido");  // json!(1000)
```

#### 4️⃣ **SistemaMemoria** - Aprender

```rust
pub struct SistemaMemoria {
    pub corto_plazo: MemoriaCortoTermino,  // Últimos 10 eventos
    pub largo_plazo: MemoriaLargoTermino,  // Patrones aprendidos
}
```

**Memoria Corto Plazo** (Como tu memoria inmediata):
```
Últimas 10 cosas que hice:
1. Leí archivo (10:00)
2. Validé estructura (10:02)
3. Procesé 100 filas (10:05)
```

**Memoria Largo Plazo** (Como el conocimiento):
```
Patrón aprendido: "Los CSVs sin encabezado necesitan preprocesamiento"
- Dónde: Tarea "Procesar_datos_2024"
- Cuándo: Hace 3 días
- Lección: "Siempre validar estructura primero"
- Usado: 5 veces
```

---

## Capítulo 3: El Flujo Completo

### De Principio a Fin

```
INICIO
  ↓
[1] Crear agente con nombre, rol, objetivo
  ↓
[2] Agregar pasos al plan
  ↓
[3] EJECUTAR
    └─→ Para cada paso:
        ├─ Cambiar estado a EJECUTANDO
        ├─ Registrar: "Ejecutando paso X"
        ├─ Hacer el paso (ejecutar herramienta)
        ├─ Guardar resultado en contexto
        ├─ Registrar: "Paso X completado"
        └─ Pasar al siguiente
  ↓
[4] REFLEXIONAR
    └─→ Cambiar estado a REFLEXIONANDO
    └─→ Analizar resultados
    └─→ Guardar patrones en memoria largo plazo
  ↓
[5] COMPLETADO
    └─→ Cambiar estado a COMPLETADO
    └─→ Resumen final
  ↓
FIN
```

### Código Real

```rust
// Paso 1: Crear
let mut agente = AgentIntegrado::nuevo(
    "Vendedor Automático".to_string(),
    "Sales Bot".to_string(),
    "Procesar 50 pedidos de ventas".to_string(),
);

// Paso 2: Agregar pasos
agente.agregar_paso_herramienta(
    "Descargar lista de pedidos".to_string(),
    "archivo".to_string(),
    json!({"operacion": "leer", "ruta": "/pedidos.csv"}),
);

agente.agregar_paso_herramienta(
    "Validar cada pedido en BD".to_string(),
    "sql".to_string(),
    json!({
        "query": "SELECT * FROM clientes WHERE ID = ?",
        "validar": true
    }),
);

agente.agregar_paso_herramienta(
    "Guardar confirmación".to_string(),
    "archivo".to_string(),
    json!({"operacion": "escribir", "ruta": "/confirmacion.json"}),
);

// Paso 3: EJECUTAR
let resultado = agente.ejecutar();

// El framework automáticamente:
// - Cambió estado a EJECUTANDO
// - Ejecutó paso 1, 2, 3 en orden
// - Guardó resultados en contexto
// - Reflexionó sobre lo que pasó
// - Cambió estado a COMPLETADO
```

---

## Capítulo 4: Integración con Herramientas

### El Agente como Coordinador

Un agente coordina **herramientas del Tool Engine**:

```
┌─────────────────────┐
│  AgentIntegrado     │
│  "Procesar datos"   │
└──────────┬──────────┘
           │ "Necesito leer un archivo"
           ↓
        ┌──────────────────────┐
        │  Tool Engine         │
        │                      │
        │  ├─ FileTool ────→ lee archivo
        │  ├─ SqlTool ─────→ consulta BD
        │  ├─ HttpTool ────→ API externa
        │  └─ SshTool ─────→ servidor remoto
        │                      │
        └──────────────────────┘
           ↓ resultado
    ┌──────────────────┐
    │ {"status": "ok"} │
    └──────────────────┘
```

### Ejemplo: Agente que Integra Tools

```rust
// Crear agente
let mut agente = AgentIntegrado::nuevo(
    "Sincronizador".to_string(),
    "Integration Bot".to_string(),
    "Sincronizar datos entre sistemas".to_string(),
);

// Paso 1: Leer de archivo local (FileTool)
agente.agregar_paso_herramienta(
    "Leer datos de fuente local".to_string(),
    "archivo".to_string(),
    json!({
        "operacion": "leer",
        "ruta": "/datos/fuente.json"
    }),
);

// Paso 2: Enviar a API externa (HttpTool)
agente.agregar_paso_herramienta(
    "Sincronizar con sistema externo".to_string(),
    "http".to_string(),
    json!({
        "metodo": "POST",
        "url": "https://api.externa.com/sync",
        "headers": {"Authorization": "Bearer token"}
    }),
);

// Paso 3: Guardar confirmación (FileTool)
agente.agregar_paso_herramienta(
    "Registrar sincronización".to_string(),
    "archivo".to_string(),
    json!({
        "operacion": "escribir",
        "ruta": "/logs/sync_complete.json"
    }),
);

// Ejecutar: el agente coordinará las 3 herramientas
let resultado = agente.ejecutar()?;
// {
//   "agente_id": "...",
//   "pasos_completados": 3,
//   "acciones": 3,
//   "reflexiones": 1
// }
```

---

## Capítulo 5: Memoria - Aprendiendo

### Memoria Corto Plazo en Acción

```rust
let sistema = SistemaMemoria::nuevo(5, 3);  // Max 5 eventos recientes, 3 patrones

// Registrar lo que hace el agente
sistema.registrar_evento(json!({
    "tipo": "inicio_agente",
    "agente": "Procesador",
    "timestamp": "2026-08-05T10:00:00Z"
}));

sistema.registrar_evento(json!({
    "tipo": "paso_completado",
    "paso": 1,
    "duracion_ms": 150
}));

sistema.registrar_evento(json!({
    "tipo": "error",
    "mensaje": "CSV sin encabezado",
    "timestamp": "2026-08-05T10:05:00Z"
}));

// Obtener los últimos 2 eventos
let ultimos = sistema.corto_plazo.obtener_ultimos(2);
// Retorna los 2 más recientes en orden inverso
```

### Memoria Largo Plazo - Aprender del Error

```rust
// Cuando ocurre un error o patrón interesante,
// guardar en memoria largo plazo

sistema.largo_plazo.guardar_patron(
    "CSV sin encabezado falla validación".to_string(),
    json!({
        "archivo": "pedidos.csv",
        "error": "No tiene columna 'ID'",
        "tamaño_bytes": 1024000
    }),
    "SIEMPRE validar encabezado ANTES de procesar".to_string(),
);

// Después, el agente puede acceder a esto
let patrones = sistema.largo_plazo.obtener_patrones();
for patron in patrones {
    println!("Patrón: {}", patron.descripcion);
    println!("Lección: {}", patron.leccion);
    println!("Ocurrencias: {}", patron.ocurrencias);
}
```

---

## Resumen del Capítulo

### Conceptos Clave

| Concepto | ¿Qué es? | Ejemplo |
|----------|----------|---------|
| **Agent** | Identidad del agente | "Vendedor Automático", rol "Sales Bot" |
| **Plan** | Qué hacer | 3 pasos: leer → procesar → guardar |
| **Contexto** | Variables que cambian | total_procesado = 950 |
| **Memoria Corto Plazo** | Últimas N cosas | Últimos 10 eventos de ejecución |
| **Memoria Largo Plazo** | Patrones aprendidos | "CSV sin header → siempre validar" |
| **Paso** | Una tarea específica | "Leer archivo de /datos.csv" |
| **Herramienta** | Qué usa para hacer el paso | FileTool, SqlTool, HttpTool |

### Preguntas Frecuentes

**P: ¿Un agente puede ejecutar dos pasos en paralelo?**
R: No, los pasos se ejecutan **secuencialmente**. Fase futura: paralelismo.

**P: ¿Qué pasa si un paso falla?**
R: El agente cambia a estado "Error" y se detiene. Luego reflexiona sobre qué pasó.

**P: ¿Dónde se guardan los agentes?**
R: Ahora en memoria. Fase 11: persistencia en BD.

**P: ¿Cuántos agentes puedo tener?**
R: Los que quieras. Cada uno es independiente.

---

**Próximo Capítulo**: Práctica con Agentes Reales
