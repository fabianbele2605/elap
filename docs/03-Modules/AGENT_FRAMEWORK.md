# Agent Framework — Orquestación Inteligente de Agentes

**Autor**: ELAP Development Team  
**Fecha**: 2026-08-05  
**Versión**: 1.0  
**Fase**: 8

## Índice

1. [Descripción General](#descripción-general)
2. [Arquitectura](#arquitectura)
3. [Componentes Principales](#componentes-principales)
4. [Integración](#integración)
5. [Ejemplos](#ejemplos)
6. [Benchmarks](#benchmarks)
7. [Seguridad](#seguridad)

---

## Descripción General

El **Agent Framework** es el sistema de orquestación inteligente que permite que agentes autónomos coordinen herramientas, consulten modelos de IA y ejecuten planes complejos.

### Características

- ✅ **Agentes con estado**: 6 estados posibles (Inactivo, Planificando, Ejecutando, Reflexionando, Completado, Error)
- ✅ **Planes secuenciales**: Pasos con validación, ejecución y progreso
- ✅ **Contexto dinámico**: Variables y restricciones que cambian durante la ejecución
- ✅ **Memoria dual**: Corto plazo (últimas N interacciones) + Largo plazo (patrones aprendidos)
- ✅ **Integración Tools**: Agentes pueden ejecutar herramientas del Tool Engine
- ✅ **Integración Models**: Agentes pueden consultar LLMs del Model Manager
- ✅ **Reflexión**: Análisis post-ejecución de resultados

---

## Arquitectura

```
┌─────────────────────────────────────────┐
│         Agent Framework                 │
├─────────────────────────────────────────┤
│                                         │
│  AgentIntegrado (Orquestador)          │
│  ├── Agent (Estado + Historia)         │
│  ├── Plan (Pasos secuenciales)         │
│  ├── ContextoAgente (Variables)        │
│  └── ModelManager (Opcional)           │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  EjecutorAgente                        │
│  └── ejecutar_plan()                   │
│  └── reflexionar()                     │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  SistemaMemoria                        │
│  ├── MemoriaCortoTermino (VecDeque)    │
│  └── MemoriaLargoTermino (Patrones)    │
│                                         │
└─────────────────────────────────────────┘
        ↓ Integración
┌─────────────────────────────────────────┐
│  Tool Engine      │      Model Manager  │
└─────────────────────────────────────────┘
```

---

## Componentes Principales

### 1. Agent (Agente)

```rust
pub struct Agent {
    pub id: String,                      // UUID único
    pub nombre: String,
    pub rol: String,
    pub estado: EstadoAgente,            // Estado actual
    pub historial_acciones: Vec<String>, // Qué hizo
    pub reflexiones: Vec<String>,        // Qué aprendió
}
```

**Estados posibles:**
- `Inactivo`: Esperando tarea
- `Planificando`: Preparando pasos
- `Ejecutando`: Ejecutando pasos
- `Reflexionando`: Analizando resultados
- `Completado`: Tarea completada
- `Error`: Falló

### 2. Plan (Plan de Ejecución)

```rust
pub struct Plan {
    pub id: String,              // UUID único
    pub objetivo: String,        // ¿Qué se quiere lograr?
    pub pasos: Vec<Paso>,        // Pasos a ejecutar
    pub paso_actual: usize,      // Índice del paso actual
    pub completado: bool,        // ¿Terminado?
}

pub struct Paso {
    pub numero: usize,           // 1, 2, 3, ...
    pub descripcion: String,     // Texto descriptivo
    pub tipo_accion: String,     // Tipo de herramienta
    pub parametros: JsonValue,   // Config de la herramienta
    pub completado: bool,
    pub resultado: Option<JsonValue>,
}
```

**Métodos principales:**
- `agregar_paso()`: Agregar paso al plan
- `obtener_paso_actual()`: Paso que se está ejecutando
- `completar_paso_actual()`: Marcar como completado
- `progreso()`: Retorna 0.0 a 1.0

### 3. ContextoAgente (Contexto de Ejecución)

```rust
pub struct ContextoAgente {
    pub objetivo: String,           // Objetivo del agente
    pub variables: HashMap<String, JsonValue>,  // Estado mutable
    pub restricciones: Vec<String>, // Limitaciones
    pub timestamp_inicio: i64,      // Cuándo empezó
}
```

**Métodos:**
- `set_variable(key, value)`: Guardar variable
- `get_variable(key)`: Obtener variable
- `obtener_restricciones()`: Listar restricciones

### 4. SistemaMemoria (Memoria Dual)

#### MemoriaCortoTermino

```rust
pub struct MemoriaCortoTermino {
    historial: VecDeque<JsonValue>,  // Últimas N interacciones
    max_items: usize,
}
```

- Almacena eventos recientes
- Se limpia automáticamente al exceder límite
- Útil para contexto inmediato

#### MemoriaLargoTermino

```rust
pub struct MemoriaLargoTermino {
    patrones: Vec<PatronMemoria>,
    max_patrones: usize,
}

pub struct PatronMemoria {
    descripcion: String,      // Qué es el patrón
    contexto: JsonValue,      // Dónde ocurrió
    leccion: String,         // Qué aprender
    ocurrencias: usize,      // Cuántas veces
    ultimo_acceso: i64,      // Timestamp
}
```

- Almacena patrones aprendidos
- Persiste lecciones clave
- Útil para optimizar futuras ejecuciones

### 5. AgentIntegrado (Orquestador)

```rust
pub struct AgentIntegrado {
    pub agente: Agent,
    pub plan: Plan,
    pub contexto: ContextoAgente,
    pub model_manager: Option<ModelManager>,  // Integración opcional
}
```

**Métodos:**
- `con_model_manager()`: Conectar Model Manager
- `agregar_paso_herramienta()`: Agregar paso con herramienta
- `ejecutar()`: Ejecutar plan completo
- `resumen()`: Resumen de ejecución

---

## Integración

### Con Tool Engine

```rust
// Agente agregando pasos con herramientas
let mut agente = AgentIntegrado::nuevo(...);

agente.agregar_paso_herramienta(
    "Leer archivo".to_string(),
    "archivo".to_string(),  // Tipo de herramienta
    json!({"operacion": "leer", "ruta": "/datos/input.txt"}),
);

agente.agregar_paso_herramienta(
    "Ejecutar comando".to_string(),
    "sistema".to_string(),
    json!({"comando": "ls"}),
);

let resultado = agente.ejecutar();
```

### Con Model Manager

```rust
// Agente con acceso a LLM
let model_manager = ModelManager::nuevo();
let mut agente = AgentIntegrado::nuevo(...)
    .con_model_manager(model_manager);

// El agente puede llamar al LLM durante pasos
agente.agregar_paso_herramienta(
    "Consultar modelo".to_string(),
    "llm".to_string(),
    json!({"prompt": "¿Qué hacer con estos datos?"}),
);
```

---

## Ejemplos

### Ejemplo 1: Plan Simple

```rust
let mut agente = AgentIntegrado::nuevo(
    "Analizador de Datos".to_string(),
    "Data Scientist".to_string(),
    "Procesar archivo CSV".to_string(),
);

// Agregar pasos
agente.agregar_paso_herramienta(
    "Leer CSV".to_string(),
    "archivo".to_string(),
    json!({"operacion": "leer", "ruta": "datos.csv"}),
);

agente.agregar_paso_herramienta(
    "Validar estructura".to_string(),
    "sistema".to_string(),
    json!({"validar": true}),
);

agente.agregar_paso_herramienta(
    "Guardar resultados".to_string(),
    "archivo".to_string(),
    json!({"operacion": "escribir", "ruta": "resultados.json"}),
);

// Ejecutar
let resultado = agente.ejecutar()?;
println!("Plan completado: {:?}", resultado);
```

### Ejemplo 2: Con Memoria

```rust
let sistema = SistemaMemoria::nuevo(10, 5);

// Registrar eventos durante ejecución
sistema.registrar_evento(json!({
    "tipo": "inicio",
    "agente": "Analizador",
    "timestamp": chrono::Utc::now().to_rfc3339(),
}));

// Guardar patrón aprendido
sistema.largo_plazo.guardar_patron(
    "Los CSVs sin encabezado necesitan preprocesamiento".to_string(),
    json!({"tipo": "csv", "tiene_encabezado": false}),
    "Siempre validar estructura antes de procesar".to_string(),
);
```

### Ejemplo 3: Múltiples Agentes

```rust
let sistema = SistemaMemoria::nuevo(20, 10);

// Agente 1: Recopilador
let mut agente1 = AgentIntegrado::nuevo(
    "Recopilador".to_string(),
    "DataCollector".to_string(),
    "Recopilar datos".to_string(),
);

// Agente 2: Procesador
let mut agente2 = AgentIntegrado::nuevo(
    "Procesador".to_string(),
    "DataProcessor".to_string(),
    "Procesar datos".to_string(),
);

// Ejecutar secuencialmente
agente1.ejecutar()?;
sistema.registrar_evento(json!({"agente": "Recopilador", "status": "completado"}));

agente2.ejecutar()?;
sistema.registrar_evento(json!({"agente": "Procesador", "status": "completado"}));
```

---

## Benchmarks

| Métrica | Valor | Condiciones |
|---------|-------|------------|
| Crear agente | <1ms | Memory allocation |
| Ejecutar 10 pasos | ~5ms | Sin I/O real |
| Agregar a memoria corto plazo | <0.1ms | VecDeque append |
| Guardar patrón largo plazo | <1ms | Con serialización |
| Reflexionar | <2ms | Análisis de resultado |

### Prueba de Carga

```bash
cargo test --lib agents -- --nocapture
# Resultado: 29 tests, 0 failures
```

---

## Seguridad

### RBAC en Pasos

Cuando un agente ejecuta un paso con una herramienta:

1. ✅ Validar permisos del usuario
2. ✅ Validar RBAC para la herramienta
3. ✅ Validar parámetros
4. ✅ Ejecutar con sandbox
5. ✅ Registrar en auditoría

### Aislamiento de Contexto

Cada agente tiene su propio:
- Contexto de ejecución independiente
- Variables locales
- Historial de acciones
- UUID único

### Límites de Memoria

- Memoria corto plazo: Máximo configurable (default 10 eventos)
- Memoria largo plazo: Máximo configurable (default 5 patrones)
- Historial de acciones: Se limpia per-agente

---

## Próximos Pasos

- **Fase 9**: Web API REST para agentes
- **Fase 10**: Streaming WebSocket para ejecución en tiempo real
- **Fase 11**: Persistencia de agentes en base de datos
- **Fase 12**: Dashboard de monitoreo en vivo

---

**Última actualización**: 2026-08-05
