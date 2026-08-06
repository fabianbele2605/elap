# Libro 09: Capítulo 2 — Creando tu Primer Agente

## Objetivo del Capítulo

Al final sabrás crear un agente que:
- ✅ Lee un archivo
- ✅ Valida los datos
- ✅ Procesa la información
- ✅ Guarda resultados
- ✅ Reflexiona sobre lo hecho

---

## Ejercicio 1: Agente Simple - Procesar CSV

### Escenario

Tienes un archivo `ventas.csv` con 100 ventas. Necesitas:
1. Leerlo
2. Validar que tenga las columnas correctas
3. Contar cuántas ventas por región
4. Guardar el reporte

### Código Paso a Paso

```rust
use elap_core::{AgentIntegrado, json};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // === PASO 1: CREAR AGENTE ===
    let mut agente = AgentIntegrado::nuevo(
        "Analizador de Ventas".to_string(),        // Nombre
        "Sales Analyst".to_string(),               // Rol
        "Analizar ventas por región".to_string(),  // Objetivo
    );

    // === PASO 2: AGREGAR PASOS AL PLAN ===
    
    // Paso 1: Leer archivo
    agente.agregar_paso_herramienta(
        "Leer archivo de ventas".to_string(),
        "archivo".to_string(),
        json!({
            "operacion": "leer",
            "ruta": "/datos/ventas.csv"
        }),
    );

    // Paso 2: Validar estructura
    agente.agregar_paso_herramienta(
        "Validar columnas".to_string(),
        "sistema".to_string(),
        json!({
            "validar": true,
            "columnas_requeridas": ["ID", "Region", "Monto", "Fecha"]
        }),
    );

    // Paso 3: Procesar datos
    agente.agregar_paso_herramienta(
        "Contar ventas por región".to_string(),
        "sql".to_string(),
        json!({
            "query": "SELECT region, COUNT(*) as total FROM ventas GROUP BY region",
            "tipo": "lectura"
        }),
    );

    // Paso 4: Guardar reporte
    agente.agregar_paso_herramienta(
        "Guardar reporte final".to_string(),
        "archivo".to_string(),
        json!({
            "operacion": "escribir",
            "ruta": "/reportes/ventas_por_region.json"
        }),
    );

    // === PASO 3: EJECUTAR ===
    println!("🚀 Iniciando agente: {}", agente.agente.nombre);
    let resultado = agente.ejecutar()?;

    // === PASO 4: VER RESULTADOS ===
    println!("✅ Ejecución completada!");
    println!("Resultado: {:#?}", resultado);

    // Ver resumen
    let resumen = agente.resumen();
    println!("📊 Resumen:");
    println!("  - Agente: {}", resumen["agente"]["nombre"]);
    println!("  - Pasos: {}/{}", 
             resumen["pasos_completados"],
             resumen["pasos_totales"]
    );
    println!("  - Progreso: {:.0}%", resumen["progreso"].as_f64().unwrap_or(0.0) * 100.0);

    // Ver historial de acciones
    println!("📝 Acciones realizadas:");
    for accion in &agente.agente.historial_acciones {
        println!("  - {}", accion);
    }

    // Ver reflexiones
    println!("🧠 Reflexiones:");
    for reflexion in &agente.agente.reflexiones {
        println!("  - {}", reflexion);
    }

    Ok(())
}
```

### Salida Esperada

```
🚀 Iniciando agente: Analizador de Ventas
✅ Ejecución completada!
Resultado: {
  "agente_id": "a1b2c3d4-...",
  "plan_id": "e5f6g7h8-...",
  "pasos_completados": 4,
  "acciones": 4,
  "reflexiones": 1
}
📊 Resumen:
  - Agente: Analizador de Ventas
  - Pasos: 4/4
  - Progreso: 100%
📝 Acciones realizadas:
  - Agente integrado iniciando
  - Ejecutando: Leer archivo de ventas
  - Ejecutando: Validar columnas
  - Ejecutando: Contar ventas por región
  - Ejecutando: Guardar reporte final
🧠 Reflexiones:
  - Plan completado. 4 pasos ejecutados.
```

---

## Ejercicio 2: Agente con Contexto Dinámico

### Escenario

Un agente que registra variables mientras ejecuta:

```rust
use elap_core::{AgentIntegrado, ContextoAgente, json};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut agente = AgentIntegrado::nuevo(
        "Procesador Inteligente".to_string(),
        "DataProcessor".to_string(),
        "Procesar y enriquecer datos".to_string(),
    );

    // === AGREGAR RESTRICCIÓN AL CONTEXTO ===
    agente.contexto.agregar_restriccion(
        "Sin acceso a BD de producción".to_string()
    );

    // === AGREGAR PASOS ===
    agente.agregar_paso_herramienta(
        "Leer 1000 registros".to_string(),
        "archivo".to_string(),
        json!({"ruta": "/datos/bulk.csv"}),
    );

    agente.agregar_paso_herramienta(
        "Enriquecer con geolocalización".to_string(),
        "http".to_string(),
        json!({
            "url": "https://api.geolocation.com/batch",
            "batch_size": 100
        }),
    );

    agente.agregar_paso_herramienta(
        "Guardar datos enriquecidos".to_string(),
        "archivo".to_string(),
        json!({"ruta": "/datos/enriched.parquet"}),
    );

    // === EJECUTAR Y MONITOREAR ===
    println!("Ejecutando agente...");
    let resultado = agente.ejecutar()?;

    // === LEER VARIABLES DEL CONTEXTO ===
    if let Some(registros_leidos) = agente.contexto.get_variable("paso_1_resultado") {
        println!("📊 Registros leídos: {:?}", registros_leidos);
    }

    println!("✅ Contexto final: {:?}", agente.contexto.variables);

    Ok(())
}
```

---

## Ejercicio 3: Múltiples Agentes Independientes

### Escenario

Ejecutar 3 agentes diferentes sin que interfieran:

```rust
use elap_core::AgentIntegrado;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // === AGENTE 1: Recopilador de Datos ===
    let mut agente1 = AgentIntegrado::nuevo(
        "Recopilador".to_string(),
        "DataCollector".to_string(),
        "Recopilar datos de 5 fuentes".to_string(),
    );

    agente1.agregar_paso_herramienta(
        "Fuente API 1".to_string(),
        "http".to_string(),
        serde_json::json!({"url": "https://api1.com"}),
    );

    agente1.agregar_paso_herramienta(
        "Fuente API 2".to_string(),
        "http".to_string(),
        serde_json::json!({"url": "https://api2.com"}),
    );

    // === AGENTE 2: Validador ===
    let mut agente2 = AgentIntegrado::nuevo(
        "Validador".to_string(),
        "DataValidator".to_string(),
        "Validar calidad de datos".to_string(),
    );

    agente2.agregar_paso_herramienta(
        "Verificar valores nulos".to_string(),
        "sql".to_string(),
        serde_json::json!({"query": "SELECT COUNT(*) FROM datos WHERE col IS NULL"}),
    );

    // === AGENTE 3: Reportero ===
    let mut agente3 = AgentIntegrado::nuevo(
        "Reportero".to_string(),
        "Reporter".to_string(),
        "Generar reportes finales".to_string(),
    );

    agente3.agregar_paso_herramienta(
        "Compilar reporte HTML".to_string(),
        "sistema".to_string(),
        serde_json::json!({"generar_html": true}),
    );

    // === EJECUTAR SECUENCIALMENTE ===
    println!("🟦 Ejecutando Agente 1: Recopilador");
    agente1.ejecutar()?;
    println!("✅ Agente 1 completado\n");

    println!("🟩 Ejecutando Agente 2: Validador");
    agente2.ejecutar()?;
    println!("✅ Agente 2 completado\n");

    println!("🟨 Ejecutando Agente 3: Reportero");
    agente3.ejecutar()?;
    println!("✅ Agente 3 completado\n");

    // === MOSTRAR RESÚMENES ===
    println!("=== RESUMEN FINAL ===\n");
    
    println!("Agente 1:");
    println!("{:#?}", agente1.resumen());
    
    println!("\nAgente 2:");
    println!("{:#?}", agente2.resumen());
    
    println!("\nAgente 3:");
    println!("{:#?}", agente3.resumen());

    Ok(())
}
```

---

## Ejercicio 4: Con Sistema de Memoria

### Escenario

Un agente que aprende de sus errores:

```rust
use elap_core::{AgentIntegrado, SistemaMemoria};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let sistema = SistemaMemoria::nuevo(20, 5);  // 20 eventos recientes, 5 patrones

    let mut agente = AgentIntegrado::nuevo(
        "Aprendiz".to_string(),
        "LearningBot".to_string(),
        "Procesar datos y aprender patrones".to_string(),
    );

    // Registrar inicio
    sistema.registrar_evento(serde_json::json!({
        "tipo": "inicio",
        "agente": agente.agente.nombre,
        "timestamp": chrono::Utc::now().to_rfc3339(),
    }));

    // === AGREGAR PASOS ===
    agente.agregar_paso_herramienta(
        "Leer archivo sin validar".to_string(),
        "archivo".to_string(),
        serde_json::json!({"ruta": "/datos.csv"}),
    );

    agente.agregar_paso_herramienta(
        "Procesar directamente".to_string(),
        "sistema".to_string(),
        serde_json::json!({"procesar": true}),
    );

    // === EJECUTAR ===
    println!("🤖 Agente ejecutando con memoria...");
    let resultado = agente.ejecutar()?;

    // Simular que encontró un error
    sistema.registrar_evento(serde_json::json!({
        "tipo": "error",
        "paso": 2,
        "mensaje": "CSV sin encabezado - falló validación",
        "timestamp": chrono::Utc::now().to_rfc3339(),
    }));

    // === GUARDAR PATRÓN APRENDIDO ===
    sistema.largo_plazo.guardar_patron(
        "CSV sin encabezado causa fallo".to_string(),
        serde_json::json!({
            "tipo_archivo": "csv",
            "tiene_encabezado": false,
            "tamaño": "1.2 MB",
        }),
        "SIEMPRE: Validar encabezado ANTES de procesar datos".to_string(),
    );

    // === VER LO APRENDIDO ===
    println!("\n📚 Lo que aprendió el sistema:");
    for patron in sistema.largo_plazo.obtener_patrones() {
        println!("  📌 Patrón: {}", patron.descripcion);
        println!("     Lección: {}", patron.leccion);
        println!("     Visto: {} veces", patron.ocurrencias);
    }

    // === EVENTOS RECIENTES ===
    println!("\n⏰ Últimos eventos:");
    let ultimos = sistema.corto_plazo.obtener_ultimos(3);
    for evento in ultimos {
        println!("  - {}", evento);
    }

    Ok(())
}
```

---

## Ejercicio 5: Monitoreo en Vivo

### Escenario

Seguir la ejecución de un agente en tiempo real:

```rust
use elap_core::AgentIntegrado;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut agente = AgentIntegrado::nuevo(
        "Procesador en Vivo".to_string(),
        "LiveProcessor".to_string(),
        "Procesar con actualizaciones en tiempo real".to_string(),
    );

    // Agregar 10 pasos para ver el progreso
    for i in 1..=10 {
        agente.agregar_paso_herramienta(
            format!("Paso {}", i),
            "sistema".to_string(),
            serde_json::json!({"numero": i}),
        );
    }

    // === BARRA DE PROGRESO MANUAL ===
    println!("📊 Ejecutando agente con 10 pasos:\n");

    // Simular ejecución monitoreando
    let resultado = agente.ejecutar()?;

    // Mostrar progreso
    let resumen = agente.resumen();
    let progreso = resumen["progreso"].as_f64().unwrap_or(0.0);
    let pasos = resumen["pasos_completados"].as_u64().unwrap_or(0);
    let total = resumen["pasos_totales"].as_u64().unwrap_or(1);

    // Barra visual
    let barra_len = (progreso * 20.0) as usize;
    let barra = "█".repeat(barra_len) + &"░".repeat(20 - barra_len);
    
    println!("[{}] {}/{} pasos ({:.0}%)", barra, pasos, total, progreso * 100.0);

    // Estado final
    println!("\n✨ Estado final del agente:");
    println!("   ID: {}", agente.agente.id);
    println!("   Nombre: {}", agente.agente.nombre);
    println!("   Rol: {}", agente.agente.rol);
    println!("   Estado: {:?}", agente.agente.estado);
    println!("   Acciones: {}", agente.agente.historial_acciones.len());
    println!("   Reflexiones: {}", agente.agente.reflexiones.len());

    Ok(())
}
```

---

## Quiz: ¿Lo Entendiste?

**Pregunta 1**: ¿Cuál es la diferencia entre paso y plan?
- A) Un paso es una tarea, un plan es una lista de tareas ✅
- B) No hay diferencia
- C) Un plan es una tarea, un paso es una lista

**Pregunta 2**: ¿Cuántos agentes puedo ejecutar en paralelo?
- A) Solamente uno
- B) Los que quieras - cada uno es independiente ✅
- C) Máximo 10

**Pregunta 3**: ¿Para qué sirve ContextoAgente?
- A) Solo para mostrar logs
- B) Para guardar variables que cambian durante ejecución ✅
- C) Para definir el nombre del agente

---

**Próximo Capítulo**: Agentes Avanzados con Modelos de IA
