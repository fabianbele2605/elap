# Persistencia en BD — SQLite + PostgreSQL

**Autor**: ELAP Development Team  
**Fecha**: 2026-08-05  
**Versión**: 1.0  
**Fase**: 11

## Índice

1. [Descripción General](#descripción-general)
2. [SQLite (Default)](#sqlite-default)
3. [PostgreSQL (Avanzado)](#postgresql-avanzado)
4. [API de Repositorio](#api-de-repositorio)
5. [Ejemplos](#ejemplos)

---

## Descripción General

Sistema de persistencia con:
- ✅ **SQLite embebido** por defecto (sin dependencias)
- ✅ **PostgreSQL opcional** para escala
- ✅ **Auto-init** de tablas en startup
- ✅ **Repository pattern** para acceso a datos
- ✅ **Thread-safe** con connection pooling

### Flujo

```
┌─────────────────────────┐
│  App inicia             │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│  obtener_db()           │
│  └─ Detecta BD          │
│  └─ Crea si no existe   │
│  └─ Migrations auto     │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│  Database pool          │
│  (SQLitePool)           │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│  RepositorioAgente      │
│  (CRUD operations)      │
└─────────────────────────┘
```

---

## SQLite (Default)

### Ubicación

```
Linux:   ~/.local/share/elap/elap.db
macOS:   ~/Library/Application Support/elap/elap.db
Windows: C:\Users\[user]\AppData\Local\elap\elap.db
```

### Características

- **Archivo único**: Portable, easy backup
- **Embedded**: No requiere servidor separado
- **Límite**: ~280TB de datos
- **Conexiones**: Sincrónicas (pero usamos async en Rust)

### Inicialización

```rust
use elap_core::obtener_db;

#[tokio::main]
async fn main() -> Result<()> {
    // Auto-crea BD y tablas
    let db = obtener_db().await?;
    
    // Usar repositorio
    let agentes = RepositorioAgente::listar(&db).await?;
    
    Ok(())
}
```

### Tablas

```sql
-- Agentes
CREATE TABLE agentes (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    rol TEXT NOT NULL,
    objetivo TEXT NOT NULL,
    estado TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Historial de ejecuciones
CREATE TABLE execuciones (
    id TEXT PRIMARY KEY,
    agente_id TEXT NOT NULL,
    pasos_completados INTEGER NOT NULL,
    progreso REAL NOT NULL,
    resultado TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(agente_id) REFERENCES agentes(id)
);

-- Acciones realizadas
CREATE TABLE acciones (
    id TEXT PRIMARY KEY,
    agente_id TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(agente_id) REFERENCES agentes(id)
);
```

---

## PostgreSQL (Avanzado)

### Cuándo Usar

- Multi-usuario
- Aplicación distribuida
- >500MB de datos
- Necesitas replicación

### Instalación

```bash
# macOS
brew install postgresql@15

# Linux (Ubuntu/Debian)
sudo apt install postgresql postgresql-contrib

# Windows
# Descargar: https://www.postgresql.org/download/windows/

# Docker
docker run -d \
  --name elap-postgres \
  -e POSTGRES_USER=elap \
  -e POSTGRES_PASSWORD=elap_dev \
  -e POSTGRES_DB=elap_db \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine
```

### Conexión

```bash
# Env var
export DATABASE_URL=postgresql://elap:elap_dev@localhost/elap_db

# O en .env
DATABASE_URL=postgresql://user:pass@prod-db.aws.com/elap_db
```

### Compilar con PostgreSQL

```toml
# Cargo.toml
[features]
default = ["sqlite"]
sqlite = ["sqlx/sqlite"]
postgres = ["sqlx/postgres"]
```

```bash
cargo build --release --features postgres
```

---

## API de Repositorio

### RepositorioAgente

```rust
use elap_core::{Database, RepositorioAgente};

// Guardar agente
RepositorioAgente::guardar(
    &db,
    "agent-id".to_string(),
    "Nombre".to_string(),
    "Rol".to_string(),
    "Objetivo".to_string(),
    "Inactivo".to_string(),
).await?;

// Obtener agente
let agente = RepositorioAgente::obtener(&db, "agent-id").await?;

// Listar todos
let agentes = RepositorioAgente::listar(&db).await?;

// Registrar ejecución
RepositorioAgente::registrar_ejecucion(
    &db,
    "agent-id".to_string(),
    4,        // pasos completados
    1.0,      // progreso
    Some(r#"{"resultado": "ok"}"#.to_string()),
).await?;

// Obtener ejecuciones
let ejecuciones = RepositorioAgente::obtener_ejecuciones(
    &db,
    "agent-id"
).await?;

// Registrar acción
RepositorioAgente::registrar_accion(
    &db,
    "agent-id".to_string(),
    "Ejecutó paso X".to_string(),
).await?;

// Contar total
let total = RepositorioAgente::contar(&db).await?;
```

---

## Ejemplos

### Ejemplo 1: Guardar Agente en BD

```rust
use elap_core::{obtener_db, RepositorioAgente, AgentIntegrado};

#[tokio::main]
async fn main() -> Result<()> {
    let db = obtener_db().await?;
    
    let agente = AgentIntegrado::nuevo(
        "Vendedor".to_string(),
        "Sales".to_string(),
        "Procesar pedidos".to_string(),
    );
    
    // Guardar en BD
    RepositorioAgente::guardar(
        &db,
        agente.agente.id.clone(),
        agente.agente.nombre.clone(),
        agente.agente.rol.clone(),
        agente.plan.objetivo.clone(),
        format!("{:?}", agente.agente.estado),
    ).await?;
    
    println!("✅ Agente guardado en BD");
    
    Ok(())
}
```

### Ejemplo 2: Recuperar Historial

```rust
use elap_core::{obtener_db, RepositorioAgente};

#[tokio::main]
async fn main() -> Result<()> {
    let db = obtener_db().await?;
    
    let agente_id = "agent-123";
    
    // Obtener ejecuciones pasadas
    let ejecuciones = RepositorioAgente::obtener_ejecuciones(
        &db,
        agente_id
    ).await?;
    
    println!("Historial de ejecuciones:");
    for ejecucion in ejecuciones {
        println!(
            "  - {} pasos en {}",
            ejecucion.pasos_completados,
            ejecucion.created_at
        );
    }
    
    // Obtener acciones
    let acciones = RepositorioAgente::obtener_acciones(
        &db,
        agente_id
    ).await?;
    
    println!("Acciones realizadas:");
    for accion in acciones {
        println!("  - {}", accion.descripcion);
    }
    
    Ok(())
}
```

### Ejemplo 3: Migración SQLite → PostgreSQL

```bash
# Exportar desde SQLite
sqlite3 ~/.local/share/elap/elap.db .dump > backup.sql

# Importar en PostgreSQL
psql -U elap -d elap_db -f backup.sql

# Verificar
psql -U elap -d elap_db -c "SELECT COUNT(*) FROM agentes;"
```

---

## Mejores Prácticas

### ✅ Hacer

```rust
// Usar RepositorioAgente para acceso
let agente = RepositorioAgente::obtener(&db, id).await?;

// Usar transacciones para operaciones multi-paso
let mut tx = db.begin().await?;
// ... operaciones
tx.commit().await?;

// Crear índices para búsquedas frecuentes
// CREATE INDEX idx_agentes_rol ON agentes(rol);
```

### ❌ No Hacer

```rust
// ❌ SQL crudo sin validar entrada (SQL injection)
let query = format!("SELECT * FROM agentes WHERE id = {}", user_input);

// ❌ No pooling (conexiones exhaustas)
let db = sqlite::open(...)?;

// ❌ Queries sin async en tokio (bloquea runtime)
std::thread::sleep(Duration::from_secs(1));
```

---

## Performance

| Operación | SQLite | PostgreSQL |
|-----------|--------|-----------|
| INSERT | <1ms | <2ms |
| SELECT 1000 rows | ~5ms | ~10ms |
| UPDATE con índice | <1ms | <2ms |
| Concurrencia | Baja | Alta |

---

## Próximas Mejoras (Fase 12+)

- [ ] Connection pooling avanzado
- [ ] Query caching
- [ ] Full-text search
- [ ] Replicación PostgreSQL
- [ ] Backup automático
- [ ] Archival de historial antiguo

---

**Última actualización**: 2026-08-05
