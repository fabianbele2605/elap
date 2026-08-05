# Libro 06: Logging Avanzado — Capítulo 1 — Introducción

**Tema central**: Cómo entender qué ocurrió en tu sistema sin perder información.

**Objetivo pedagógico**: Logging no es solo `println!()` — es eventos estructurados que cuentan historias.

---

## 🎯 La pregunta que responde este capítulo

> "¿Qué pasó en mi sistema hace 3 horas?"

**Respuesta**: Logs estructurados, rotados, filtrados y retornable en cualquier momento.

---

## 📖 Analogía: Diario personal vs Notas de Detective

```
DIARIO PERSONAL (Logging básico)
├─ "Hoy fue un día raro"
├─ "Algo salió mal"
└─ Sin contexto

NOTAS DE DETECTIVE (Logging avanzado)
├─ Fecha: 2026-08-05 14:35:22
├─ Evento: Usuario login
├─ Contexto: user_id=123, ip=192.168.1.1
├─ Ubicación: auth.rs:45
├─ Severidad: INFO
└─ Puedo reconstruir TODO

Logging avanzado = Reconstrucción forense
```

---

## 🏗️ Componentes principales

### 1. LogLevel (Severidad)

```
DEBUG  (0) — "Esto ayuda en debugging"
  ↓
INFO   (1) — "Algo importante pasó"
  ↓
WARN   (2) — "Cuidado, algo raro"
  ↓
ERROR  (3) — "¡PROBLEMA!"
```

**Ejemplo**:
```rust
logger.debug("parser", "token encontrado");    // Silencioso en prod
logger.info("auth", "usuario login");          // Registrado
logger.warn("db", "conexión lenta");           // Registrado
logger.error("api", "fallo crítico");          // Registrado siempre
```

### 2. LogEvent (Evento tipado)

```json
{
  "id": "uuid-123",
  "entrada": {
    "nivel": "ERROR",
    "mensaje": "Conexión perdida",
    "modulo": "database",
    "timestamp": 1691174122
  },
  "contexto": {
    "user_id": "123",
    "connection_id": "abc"
  },
  "ubicacion": {
    "archivo": "main.rs",
    "linea": 45
  }
}
```

**Ventaja**: JSON → Parseable → Searchable → Analizable

### 3. LogOutput (Múltiples destinos)

```
Logger
  ├─→ Console (terminal)
  ├─→ Archivo (persistencia)
  └─→ Memoria (testing)
```

**Puedes agregar más**:
```rust
logger.agregar_output(Arc::new(InfluxDB::nuevo()))?;
logger.agregar_output(Arc::new(S3Uploader::nuevo()))?;
```

### 4. GestorRotacion (No llenar disco)

```
app.log (100 MB)
  ↓ (Lleno)
Rotar
  ├─ app.log.20260805_143522 (100 MB)
  └─ app.log (nuevo, vacío)
```

**Limpieza automática**:
```rust
gestor.limpiar_antiguos(30)?;  // Elimina logs > 30 días
```

### 5. Filtros (Reducir ruido)

```
[FiltroNivel]
Input:  DEBUG, INFO, WARN, ERROR
Output: WARN, ERROR (solo los serios)

[FiltroModulo]
Input:  Todos los módulos
Output: Solo "database" (si lo filtras)

[RateLimiter]
Input:  Error cada 10ms (mismo error)
Output: Error cada segundo (no 100 veces)
```

---

## 💬 Conversación real: Debugging con logs

```
1. Usuario: "La API está lenta entre 14:00-15:00"

2. Analista revisa logs:
   SELECT * FROM logs 
   WHERE timestamp BETWEEN '14:00' AND '15:00'
   AND modulo = 'api'
   ORDER BY timestamp

3. Descubre patrón:
   14:05:12 INFO api "request_id=abc, latency=50ms"
   14:05:13 INFO api "request_id=def, latency=300ms"  ← Salto
   14:05:14 INFO api "request_id=ghi, latency=2000ms" ← Mucho más

4. Revisa contexto:
   LOG evento 14:05:13
   → contexto.database_pool_size = 10
   → contexto.active_connections = 10
   (Todas ocupadas!)

5. Solución: Aumentar pool a 20

6. Verifica:
   SELECT COUNT(*) FROM logs
   WHERE timestamp > '14:30'
   AND latency < 200ms
   (Mejora confirmada)
```

---

## 📊 Casos de uso

### 1. Debugging de Bugs
```
ERROR app "NullPointerException"
  contexto: {
    "line": 42,
    "file": "auth.rs",
    "user_id": 123
  }
→ Voy a auth.rs:42 y veo el problema
```

### 2. Auditoría de Seguridad
```
INFO security "user_login"
  contexto: {
    "user_id": 123,
    "ip": "192.168.1.1",
    "timestamp": "2026-08-05T14:35:22Z"
  }
→ Registro completo de quién accedió cuándo
```

### 3. Performance Analysis
```
WARN database "slow_query"
  contexto: {
    "duration_ms": 5000,
    "query": "SELECT * FROM users WHERE..."
  }
→ Identifico queries lentas
```

### 4. Testing
```
logger.debug("test", "setup_ok");
logger.info("test", "running_test_1");
logger.error("test", "assertion_failed");
```

---

## 🔄 Flujo completo

```
1. Código ejecuta
   ↓
2. Evento ocurre
   ↓
3. LogEvent se crea
   logger.info("module", "mensaje")?
   ↓
4. Filtros se aplican
   ¿Nivel >= nivel_minimo? ✓
   ¿Modulo permitido? ✓
   ¿Rate limit ok? ✓
   ↓
5. Múltiples outputs
   Console → imprime
   Archivo → escribe
   Memoria → almacena (test)
   ↓
6. Rotación (si necesita)
   ¿Archivo > 100 MB? → Rotar
   ¿Más de 30 días? → Eliminar
   ↓
7. Análisis posterior
   grep/awk/jq/SQL
   "¿Qué pasó?"
   → Puedo responder
```

---

## ✅ Ventajas

1. **Auditoría**: Registro completo de acciones
2. **Debugging**: Contexto para cada evento
3. **Performance**: Identifico cuellos de botella
4. **Compliance**: Cumple requisitos de seguridad
5. **Alertas**: Triggers en eventos importantes
6. **Rotación**: Sin llenar disco automáticamente

---

## ⚠️ Errores comunes

```
❌ MALO:
  println!("Error!");  // ¿Cuándo? ¿Dónde? ¿Por qué?
  eprintln!("Falló");  // Perdido en terminal

✅ BIEN:
  logger.error("api", "validación falló")?;
  evento.con_contexto("user_id".to_string(), user_id);
  evento.con_ubicacion("auth.rs".to_string(), 42);

❌ MALO:
  logger.debug("cada microsegundo", "tick")?;  // SPAM

✅ BIEN:
  if limiter.permitir("debug_key") {
    logger.debug("main", "tick")?;
  }
```

---

## 📚 Próximo: Capítulo 2

**"Configurar tu primer logger"**

Crearemos:
1. Logger con Console + Memory outputs
2. Filtro por nivel
3. Rate-limiter para errores
4. Rotación de archivos

---

**Capítulo siguiente**: 02-configurar-logger.md (Coming soon)
