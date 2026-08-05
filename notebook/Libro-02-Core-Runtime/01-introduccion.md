# Capítulo 1: Introducción al Motor Central

## El problema que resuelve

Imagina que eres un restaurante.

Tienes 50 clientes, cada uno pidiendo algo diferente **al mismo tiempo**.

¿Qué pasa?

### Sin un sistema

```
Cliente 1: "Quiero una hamburguesa"
Cocinero: "Espérate, estoy con el cliente 2"
Cliente 2: "Quiero una ensalada"
Cocinero: "Espérate, estoy con el cliente 3"
...
Cliente 50: "Mi comida se enfrió hace 30 minutos"
```

**Resultado**: Caos. Clientes enojados.

### Con un sistema (El Motor Central)

```
Cliente 1: "Quiero una hamburguesa"  ──┐
Cliente 2: "Quiero una ensalada"    ──┤
Cliente 3: "Quiero tacos"           ──┤
...                                    ├─→ [COLA ORGANIZADA]
Cliente 50: "Quiero pizza"          ──┤   ↓
                                       │   [COCINERO 1] procesa pedido 1
                                       │   [COCINERO 2] procesa pedido 2
                                       │   [COCINERO 3] procesa pedido 3
                                       │   (¡3 simultáneamente!)
                                       ↓
                                    [COMIDAS LISTAS]
```

**Resultado**: Eficiente. Clientes felices.

---

## ¿Qué es el Motor Central?

Es el "sistema de gestión de pedidos" de ELAP.

**Su trabajo**: Recibir solicitudes, ordenarlas, y asegurar que se procesen de forma **rápida, segura y eficiente**.

### Analogía técnica

```
USUARIO            MOTOR CENTRAL              AGENTE DE IA
                   ┌──────────────┐
"Dame un          │              │
 análisis"   ─→   │ Planificador  │  ─→  Procesar
                  │ de Tareas    │      solicitud
"Genera un        │              │
 reporte"    ─→   └──────────────┘  ─→  Generar
                        ↑                 reporte
                   (ordenado por
                    prioridad)
```

---

## Los 3 componentes básicos

### 1. La Tarea (Tarea)

Es una solicitud que alguien hace.

```rust
// Ejemplo: "Analizar datos de ventas"
let tarea = Tarea::nueva("analizar_ventas")
    .con_prioridad(PrioridadTarea::Alta);

// Propiedades:
// - ID único (para rastrear)
// - Nombre (qué es)
// - Prioridad (urgencia)
// - Estado (pendiente, ejecutando, completada)
// - Marca de tiempo (cuándo se creó)
```

### 2. La Cola (ColaTareas)

Es como el mostrador del restaurante.

```
[COLA CON PRIORIDAD]
┌─────────────────┐
│ [URGENTE] ←── procesar primero
│ • Alerta sistema│
│ • Respuesta VP │
├─────────────────┤
│ [NORMAL]        ├── procesar después
│ • Consulta IA   │
│ • Reporte      │
├─────────────────┤
│ [FONDO]        │
│ • Limpieza DB  │
│ • Backup      │
└─────────────────┘
```

**Clave**: Las tareas de **mayor prioridad salen primero**, como en un restaurante VIP.

### 3. El Ejecutor (PlanificadorTareas)

Es el "gerente del restaurante".

Coordina:
- ✅ Recibir nuevas tareas
- ✅ Ordenarlas en la cola
- ✅ Darles a los "cocineros" (workers)
- ✅ Rastrear que se completen
- ✅ Manejar fallos

---

## Un ejemplo real paso a paso

### Escena 1: El usuario solicita algo

```
Usuario: "Necesito un análisis de mis datos de clientes"
```

### Escena 2: El Motor Central recibe la solicitud

```rust
let planificador = PlanificadorTareas::nuevo(256); // Max 256 tareas simultáneas

let id_tarea = planificador.enviar("analizar_clientes").await;
// Resultado: ID único, ej: "a1b2c3d4"
```

**¿Qué pasó internamente?**

```
1. Se crea una Tarea nueva
   - ID: a1b2c3d4
   - Nombre: "analizar_clientes"
   - Prioridad: Normal (por defecto)
   - Estado: Pendiente
   - Creada en: 2026-08-04 10:30:45

2. Se agrega a la Cola
   - Busca su lugar por prioridad
   - Espera su turno

3. El planificador devuelve el ID
   - Ahora podemos rastrearla
```

### Escena 3: El trabajo se procesa

```rust
// El planificador obtiene la siguiente tarea
if let Some(tarea) = planificador.proxima_tarea().await {
    println!("Procesando: {}", tarea.nombre);
    // Tarea.estado = Ejecutando
    
    // Hacer el trabajo (llamar al agente de IA)
    let resultado = procesar_con_agente(&tarea).await;
    
    if resultado.es_ok() {
        planificador.completar_tarea(tarea.id).await;
        // Tarea.estado = Completada
    } else {
        planificador.fallar_tarea(tarea.id).await;
        // Tarea.estado = Falló
    }
}
```

### Escena 4: El usuario obtiene el resultado

```
Motor Central: "La tarea a1b2c3d4 está completada"
Usuario: "Aquí está tu análisis..."
```

---

## ¿Por qué es importante?

### Sin Motor Central

```
1 usuario = 1 solicitud = 1 espera = Lento
```

### Con Motor Central

```
50 usuarios = 50 solicitudes SIMULTÁNEAMENTE = Rápido
```

### Números

- **Máximo tareas simultáneas**: 256
- **Velocidad de procesamiento**: Milisegundos
- **Confiabilidad**: 0 pérdida de tareas

---

## Analogía final: El teatro

Imagina un teatro donde:

- **Usuarios** = Público esperando entrar
- **Tareas** = Butacas disponibles
- **Cola** = Fila de espera (ordenada por categoría VIP, normal, general)
- **Motor Central** = Gerente del teatro

```
40 personas esperan entrar
├─ 5 VIPs (prioridad alta) ─→ Entran primero
├─ 20 normales (normal)    ─→ Después
└─ 15 general (baja)       ─→ Al final

Resultado: Todos entran, sin caos, en orden.
```

---

## Lo que aprenderás en los próximos capítulos

| Capítulo | Qué aprenderás |
|----------|----------------|
| 2 | Cómo funciona exactamente el planificador |
| 3 | Por qué usamos Tokio (async/await) |
| 4 | Cómo fluye una solicitud de principio a fin |
| 5 | Respuestas a tus preguntas |
| 6 | Cómo usarlo correctamente |

---

## Conceptos clave para recordar

1. **Tarea** = Una solicitud que necesita procesamiento
2. **Cola** = Lugar donde esperan las tareas (ordenadas por prioridad)
3. **Planificador** = Quien coordina todo
4. **Concurrencia** = Hacer múltiples cosas al mismo tiempo (no secuencialmente)
5. **Prioridad** = Las cosas urgentes se hacen primero

---

## Preguntas que podrías tener ahora

### P: ¿Y si hay 1000 tareas?

**R**: El planificador las maneja. Pero solo ejecuta 256 simultáneamente. Las demás esperen su turno en la cola. Es como un cine: puedes tener 10000 personas comprando entrada, pero solo 500 entran al mismo tiempo.

### P: ¿Qué pasa si una tarea falla?

**R**: Se marca como "falló" y se registra. El planificador no se bloquea. Es como en un restaurante: si un pedido se quema, el cocinero avisa, anota el problema, y sigue con el siguiente pedido.

### P: ¿Puedo hacer que una tarea sea prioritaria?

**R**: ¡Sí! Exactamente para eso existe `enviar_alta_prioridad()`. Es como decir "necesito esto YA", y se salta la fila.

---

## Siguiente capítulo

[Capítulo 2: El Planificador de Tareas - Cómo funciona internamente](02-planificador.md)

---

**Nota**: Este capítulo es intro. No te preocupes si no entiendes todo de Rust aún. El próximo capítulo lo explica con diagramas.

**Última actualización**: 2026-08-04
