# Libro 06: Logging — Capítulo 2 — Configurar tu primer logger

**Tema**: Crear un logger funcional con múltiples outputs y filtros.

---

## 📋 Ejercicio

Crearemos un logger que:
- Escribe a consola
- Almacena en memoria (testing)
- Filtra por nivel
- Aplica rate-limiting

---

## ✍️ Código

```rust
use elap_core::{
    LoggerAvanzado, LogLevel, LogEntry, LogEvent,
    LogOutput, ConsoleOutput, MemoryOutput,
    FiltroNivel, RateLimiter,
};
use std::sync::Arc;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 1. Crear logger (solo INFO y superior)
    let logger = LoggerAvanzado::nuevo(LogLevel::Info);
    
    // 2. Agregar output consola
    logger.agregar_output(
        Arc::new(ConsoleOutput::nuevo())
    )?;
    
    // 3. Agregar output memoria (para testing)
    let memory_out = Arc::new(MemoryOutput::nuevo());
    logger.agregar_output(memory_out.clone())?;
    
    // 4. Crear rate-limiter
    let limiter = RateLimiter::nuevo(10); // 10 err/seg
    
    // 5. Registrar logs
    logger.info("app", "Aplicación iniciada")?;
    logger.warn("database", "Conexión lenta")?;
    
    // Simular errores repetidos con rate-limiting
    for i in 0..15 {
        if limiter.permitir("error_key") {
            logger.error("api", &format!("Error {}", i))?;
        }
    }
    
    // 6. Acceder a logs en memoria
    let eventos = memory_out.obtener_eventos()?;
    println!("\n📊 Eventos registrados: {}", eventos.len());
    
    for evento in eventos {
        println!("  [{:?}] {}", evento.entrada.nivel, evento.entrada.mensaje);
    }
    
    logger.flush()?;
    Ok(())
}
```

---

## 🧪 Output esperado

```
[2026-08-05T14:35:22Z] INFO | app | Aplicación iniciada
[2026-08-05T14:35:22Z] WARN | database | Conexión lenta
[2026-08-05T14:35:22Z] ERROR | api | Error 0
[2026-08-05T14:35:22Z] ERROR | api | Error 10

📊 Eventos registrados: 6
  [INFO] Aplicación iniciada
  [WARN] Conexión lenta
  [ERROR] Error 0
  [ERROR] Error 10
  ... (más eventos)
```

---

## 🔍 Filtrado avanzado

```rust
// Solo WARNING y ERROR
let logger = LoggerAvanzado::nuevo(LogLevel::Warn);

// Filtar módulos (solo 'database')
let filtro = FiltroModulo::nuevo(
    vec!["database".to_string()],
    false  // no invertir
);

// Agregar contexto a eventos
let entry = LogEntry::nuevo(
    LogLevel::Error,
    "Conexión perdida".to_string(),
    "database".to_string(),
);

let evento = LogEvent::nuevo(entry)
    .con_contexto("user_id".to_string(), "123".to_string())
    .con_ubicacion("main.rs".to_string(), 42);

logger.log(evento)?;
```

---

## ✅ Verificación

```bash
cargo test -p elap-core logging_v2
# test result: ok. 33 passed
```

---

**Próximo**: Integrar con rotación de logs y persistencia
