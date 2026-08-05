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

### [Capítulo 5: Manejo de Errores](05-manejo-errores.md)
- Errores vs Panics
- El operador ? para propagación
- Tipos de error específicos (Config, Io, Validacion, Proceso)
- Patrones de manejo seguro
- **Estado**: ✅ Completado

### Capítulo 6: Flujo Completo
- Tokens, locks y mutexes (sin tecnicismos)
- Async/await explicado simple
- Por qué Rust es perfecto para esto

### Capítulo 7: Preguntas frecuentes
- ¿Qué pasa si hay 1000 tareas?
- ¿Qué pasa si una tarea falla?
- ¿Cómo escalamos?

### Capítulo 8: Buenas prácticas
- Cómo usar el motor correctamente
- Antipatrones a evitar
- Consejos de rendimiento

---

## 🎯 Cómo usar este libro

### Si eres completamente nuevo:
1. Lee el Capítulo 1 (introducción)
2. Lee el Capítulo 2 (planificador)
3. Lee el Capítulo 3 (procesos)
4. Lee el Capítulo 4 (configuración)
5. Lee el Capítulo 5 (errores)
6. Luego regresa cuando tengas dudas específicas

### Si ya sabes Rust:
1. Salta Capítulo 1-2 si son obvios
2. Lee Capítulo 3-5 para entender ELAP específicamente
3. Capítulo 7 (FAQ) probablemente responde tus preguntas
4. Capítulo 8 para insights avanzados

### Si estás debugueando un problema:
- Capítulo 5 (Manejo de Errores) para entender propagación
- Capítulo 7 (FAQ) probablemente tiene la respuesta
- Capítulo 8 (mejores prácticas) para optimización

---

## 🚀 Conceptos clave que aprenderás

```
┌──────────────────────────────────────────────┐
│      Motor Central (Core Runtime)            │
├──────────────────────────────────────────────┤
│                                              │
│ ┌─────────────┐   ┌─────────────────┐       │
│ │Planificador │   │ Gestor Procesos │       │
│ │de Tareas    │   │                 │       │
│ │             │   │  std::process   │       │
│ │  BinaryHeap │   │  Command        │       │
│ │  (Prioridad)│   │  Timestamps     │       │
│ └─────────────┘   └─────────────────┘       │
│         ↓                   ↓                │
│ ┌────────────────────────────────────┐      │
│ │   Configuración (YAML)             │      │
│ │   - Puertos                        │      │
│ │   - Niveles de logging             │      │
│ │   - Modos (dev/prod)               │      │
│ └────────────────────────────────────┘      │
│         ↓                                   │
│ ┌────────────────────────────────────┐      │
│ │   Manejo de Errores (Result)       │      │
│ │   - Config, Io, Validacion         │      │
│ │   - Operador ?                     │      │
│ │   - Propagación segura             │      │
│ └────────────────────────────────────┘      │
│                                              │
└──────────────────────────────────────────────┘
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

## 📊 Progreso del libro

| Capítulo | Tema | Estado |
|----------|------|--------|
| 1 | Introducción al Motor | ✅ Completado |
| 2 | Planificador de Tareas | ✅ Completado |
| 3 | Gestor de Procesos | ✅ Completado |
| 4 | Gestor de Configuración | ✅ Completado |
| 5 | Manejo de Errores | ✅ Completado |
| 6 | Flujo Completo | 🔜 En construcción |
| 7 | FAQ | 🔜 Pendiente |
| 8 | Buenas Prácticas | 🔜 Pendiente |

---

**Para comenzar**: Abre el [Capítulo 1: Introducción al Motor Central](01-introduccion.md)

**Última actualización**: 2026-08-05  
**Estado**: 5/8 capítulos completados ✅
