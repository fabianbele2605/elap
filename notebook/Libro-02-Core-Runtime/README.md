# Libro 02: Motor Central (Core Runtime)

**Tipo de documento**: Libro didáctico para estudio  
**Versión**: 1.0-alpha  
**Objetivo**: Entender cómo funciona el corazón de ELAP  
**Audiencia**: Desarrolladores nuevos, integradores, curiosos  

---

## 📖 Tabla de contenidos

Este libro tiene varios capítulos que aprenderás progresivamente:

### Capítulo 1: Introducción al Motor Central
- ¿Qué es el Motor Central?
- ¿Por qué es tan importante?
- Analogía con el mundo real

### [Capítulo 2: El Planificador de Tareas](02-planificador-tareas.md)
- Problema: ¿Cómo ejecutar 100 tareas simultáneamente?
- Solución: Planificador con cola y prioridades
- Ejemplo paso a paso
- **Estado**: ✅ Completado

### [Capítulo 3: Gestor de Procesos](03-gestor-procesos.md)
- Diferencia entre tarea y proceso
- Crear y ejecutar procesos del SO
- Estados: Pendiente, Ejecutando, Completado, Fallo
- Códigos de salida y timestamps
- **Estado**: ✅ Completado

### [Capítulo 4: Gestor de Configuración](04-gestor-configuracion.md)
- Separación entre código y configuración
- Entornos (desarrollo vs producción)
- Validación de configuración
- Archivos YAML legibles
- **Estado**: ✅ Completado

### Capítulo 5: Flujo Completo
- Tokens, locks y mutexes (sin tecnicismos)
- Async/await explicado simple
- Por qué Rust es perfecto para esto

### Capítulo 4: El flujo completo
- Cómo fluye una solicitud de usuario
- De principio a fin
- Con diagrama animado

### Capítulo 5: Preguntas frecuentes
- ¿Qué pasa si hay 1000 tareas?
- ¿Qué pasa si una tarea falla?
- ¿Cómo escalamos?

### Capítulo 6: Buenas prácticas
- Cómo usar el planificador correctamente
- Antipatrones a evitar
- Consejos de rendimiento

---

## 🎯 Cómo usar este libro

### Si eres completamente nuevo:
1. Lee el Capítulo 1 (introducción)
2. Lee el Capítulo 2 (planificador)
3. Luego regresa cuando tengas dudas específicas

### Si ya sabes Rust:
1. Salta el Capítulo 3 (concurrencia)
2. Ve directo al Capítulo 4 (flujo completo)
3. Capítulo 6 para insights avanzados

### Si estás debugueando un problema:
- Capítulo 5 (FAQ) probablemente tiene la respuesta
- Capítulo 6 (mejores prácticas) para optimización

---

## 🚀 Conceptos clave que aprenderás

```
┌─────────────────────────────────────┐
│     Motor Central (Core Runtime)    │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │   Planificador de Tareas    │   │
│  │  (PlanificadorTareas)       │   │
│  │                             │   │
│  │  ┌─────────────────────┐   │   │
│  │  │ Cola de Prioridad   │   │   │
│  │  │ (BinaryHeap)        │   │   │
│  │  │                     │   │   │
│  │  │ [Alta]              │   │   │
│  │  │ [Normal] [Normal]   │   │   │
│  │  │ [Baja]              │   │   │
│  │  └─────────────────────┘   │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  Ejecuta concurrentemente usando:  │
│  - Tokio (async runtime)           │
│  - Mutex (concurrencia segura)     │
│  - BinaryHeap (ordenamiento)       │
│                                     │
└─────────────────────────────────────┘
```

---

## 📚 Estructura física

Los archivos están en: `crates/elap-core/src/scheduler/`

```
scheduler/
├── mod.rs           # Punto de entrada
├── tarea.rs         # Definición de tarea
├── cola.rs          # Implementación de cola
└── ejecutor.rs      # API pública
```

---

## 🔗 Documentos relacionados

- **[SCHEDULER.md](../../docs/03-Modules/SCHEDULER.md)** — Documentación técnica profesional
- **[ARCHITECTURE.md](../../docs/01-Architecture/ARCHITECTURE.md)** — Cómo el planificador encaja
- **[DECISIONS.md](../../docs/01-Architecture/DECISIONS.md)** — Por qué usamos Tokio

---

## 💡 Lo más importante

El Motor Central hace una cosa pero BIEN:
1. Recibe tareas
2. Las ordena por prioridad
3. Las ejecuta sin bloqueos
4. Rastrea estado

Todo lo demás construye encima.

---

**Siguiente**: Abre el [Capítulo 1: Introducción al Motor Central](01-introduccion.md)

**Última actualización**: 2026-08-04  
**Estado**: En construcción 🔨
