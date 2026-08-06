# Módulo Logging Avanzado (v2)

**Versión**: 0.2.0  
**Estado**: Implementado ✅  
**Ubicación**: `crates/elap-core/src/logging_v2/`

---

## 1. Descripción general

Sistema de logging estructurado con múltiples outputs, rotación de archivos, filtrado y rate-limiting.

Características:
- Eventos de log tipados (LogLevel, LogEntry, LogEvent)
- Múltiples outputs (Consola, Memoria, extensible)
- Rotación automática por tamaño
- Filtrado por nivel y módulo
- Rate-limiting para eventos duplicados
- Timestamps UTC automáticos

---

## 2. Componentes

### Events
- `LogLevel` enum: Debug, Info, Warn, Error
- `LogEntry` struct: nivel, mensaje, módulo, timestamp
- `LogEvent` struct: ID, entrada, contexto, ubicación

### Outputs
- `LogOutput` trait para implementar nuevos outputs
- `ConsoleOutput` — Imprime a stdout
- `MemoryOutput` — Almacena en Vec (testing)

### Logger
- `LoggerAvanzado` — Orquesta múltiples outputs
- Métodos: debug(), info(), warn(), error()
- Filtrado automático por nivel

### Rotation
- `GestorRotacion` — Maneja rotación de archivos
- `EstrategiaRotacion` enum: PorTamaño, Diario, Híbrido
- Limpieza automática de archivos antiguos

### Filters
- `FilterLog` trait para filtros personalizados
- `FiltroNivel` — Filtra por nivel mínimo
- `FiltroModulo` — Filtra por módulo específico
- `RateLimiter` — Limita eventos por segundo

---

## 3. Testing

**Total: 33 tests**

- events: 8 tests
- outputs: 5 tests
- logger: 10 tests
- rotation: 5 tests
- filters: 5 tests

---

## 4. Arquitectura

```
┌──────────────────────────────┐
│   LoggerAvanzado             │
│ (Orquestador)                │
└──────────────────────────────┘
           ↓
┌──────────────────────────────┐
│  LogEvent (tipado)           │
│  ├─ LogEntry + contexto      │
│  └─ ID + ubicación           │
└──────────────────────────────┘
           ↓ (Múltiples)
┌──────────────────────────────┐
│  LogOutput implementations   │
│  ├─ ConsoleOutput            │
│  ├─ MemoryOutput             │
│  └─ FileOutput (futuro)      │
└──────────────────────────────┘
           ↓ (Opcional)
┌──────────────────────────────┐
│  Filtros & Rate-limiting     │
│  ├─ FiltroNivel              │
│  ├─ FiltroModulo             │
│  └─ RateLimiter              │
└──────────────────────────────┘
           ↓ (Opcional)
┌──────────────────────────────┐
│  GestorRotacion              │
│  └─ Rotación + limpieza      │
└──────────────────────────────┘
```

---

## 5. Uso típico

```rust
// 1. Crear logger
let logger = LoggerAvanzado::nuevo(LogLevel::Info);

// 2. Agregar outputs
logger.agregar_output(Arc::new(ConsoleOutput::nuevo()))?;
logger.agregar_output(Arc::new(MemoryOutput::nuevo()))?;

// 3. Registrar logs
logger.info("app", "Aplicación iniciada")?;
logger.warn("database", "Conexión lenta")?;

// 4. Fluir eventos con contexto
let entry = LogEntry::nuevo(LogLevel::Error, "Error crítico".to_string(), "api".to_string());
let evento = LogEvent::nuevo(entry)
    .con_contexto("user_id".to_string(), "123".to_string())
    .con_ubicacion("main.rs".to_string(), 42);
logger.log(evento)?;

// 5. Rotar logs
let gestor = GestorRotacion::nuevo(
    PathBuf::from("./app.log"),
    EstrategiaRotacion::PorTamaño(100)
);
if gestor.necesita_rotacion() {
    gestor.rotar()?;
}

// 6. Rate-limiting
let limiter = RateLimiter::nuevo(100); // 100 eventos/segundo
if limiter.permitir("error_key") {
    logger.error("app", "Error procesado")?;
}
```

---

## 6. LogLevels

| Nivel | Uso | Orden |
|-------|-----|-------|
| DEBUG | Información detallada | 0 (menor) |
| INFO | Información general | 1 |
| WARN | Advertencias | 2 |
| ERROR | Errores | 3 (mayor) |

---

## 7. Limitaciones y futuro

**Actual**:
- FileOutput no implementado (struct, no escriba a disco)
- Filtros básicos solamente
- Sin integración async

**Futuro**:
- FileOutput completo
- Filtros regex
- Async/await support
- Integración con OpenTelemetry

---

**Última actualización**: 2026-08-05  
**Total tests**: 33 ✅
