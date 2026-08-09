# Fase 6: Plugin Runtime — Plan de Implementación

**Versión**: 1.0  
**Inicio**: 2026-08-09  
**Duración estimada**: 1 semana  
**Entrega**: 2026-08-15  

---

## 📋 Resumen ejecutivo

Completar el **framework de plugins dinámicos** para ELAP que permita:
- ✅ Cargar plugins en runtime (sin recompilar)
- ✅ Validar seguridad antes de ejecutar
- ✅ Aislar ejecución (sandboxing)
- ✅ Gestionar permisos granulares (RBAC)
- ✅ Monitorear salud y performance

---

## 🎯 Entregables

### 1️⃣ Plugin Loader Mejorado (~200 LOC)

**Archivo**: `crates/elap-core/src/plugin/loader.rs` (mejorado)

**Features actuales**:
- ✅ Cargar librerías dinámicas (.so, .dylib, .dll)
- ✅ Resolver símbolos (`plugin_new`, `plugin_execute`)
- ✅ Validar integridad (SHA256)

**Features a agregar**:
- ✅ Plugin version negotiation
- ✅ Dependency resolution
- ✅ Hot reload (actualizar plugins sin reiniciar)
- ✅ Rollback automático si falla

### 2️⃣ Plugin Manifest Format (~100 LOC)

**Archivo**: `crates/elap-core/src/plugin/manifest.rs` (nuevo)

```toml
# plugin_manifest.toml
[metadata]
name = "web_scraper"
version = "1.0.0"
description = "Scrape web content safely"
author = "ELAP Team"

[requirements]
min_api_version = "1.5.0"
dependencies = ["crypto", "http"]

[permissions]
required = ["network", "file_read", "memory:1GB"]
optional = ["gpu"]

[safety]
timeout_ms = 30000
max_memory_mb = 512
max_file_size_mb = 100
```

### 3️⃣ Permission Model Avanzado (~300 LOC)

**Archivo**: `crates/elap-core/src/plugin/permissions.rs` (nuevo)

```rust
pub enum PluginPermission {
    // Network
    Network { hosts: Vec<String> },
    
    // File system
    FileRead { paths: Vec<PathBuf> },
    FileWrite { paths: Vec<PathBuf> },
    
    // Memory
    Memory { max_mb: usize },
    
    // CPU
    Cpu { max_cores: usize },
    
    // Custom
    Custom { name: String, value: String },
}

pub struct PluginPolicy {
    pub required: Vec<PluginPermission>,
    pub optional: Vec<PluginPermission>,
    pub dangerous_allowed: bool,
}
```

### 4️⃣ Advanced Sandbox (~400 LOC)

**Archivo**: `crates/elap-core/src/plugin/sandbox.rs` (mejorado)

**Capacidades**:
- ✅ Límites de memoria (cgroups en Linux)
- ✅ Límites de CPU
- ✅ Filesystem isolation
- ✅ Network filtering
- ✅ Syscall filtering (seccomp en Linux)

### 5️⃣ Plugin Lifecycle Management (~250 LOC)

**Archivo**: `crates/elap-core/src/plugin/lifecycle.rs` (nuevo)

```rust
pub enum PluginState {
    Available,      // Cargado, listo para usar
    Active,         // Ejecutándose
    Paused,         // Pausado (no responde)
    Unhealthy,      // Fallos recientes
    Disabled,       // Usuario lo deshabilitó
}

pub struct PluginInstance {
    pub metadata: PluginMetadata,
    pub state: PluginState,
    pub health_score: f32,  // 0.0 - 1.0
    pub last_error: Option<ElapError>,
    pub uptime_ms: u64,
}
```

### 6️⃣ Plugin Registry Mejorado (~200 LOC)

**Archivo**: `crates/elap-core/src/plugin/registry.rs` (mejorado)

**Features**:
- ✅ Descubrimiento automático
- ✅ Búsqueda por nombre/tipo/capacidad
- ✅ Versionado
- ✅ Caché de plugins

### 7️⃣ Health Monitoring (~200 LOC)

**Archivo**: `crates/elap-core/src/plugin/health.rs` (nuevo)

```rust
pub struct PluginHealthMonitor {
    pub errors_last_minute: u32,
    pub avg_execution_time_ms: f32,
    pub success_rate: f32,  // 0.0 - 1.0
    pub last_execution: Option<SystemTime>,
}

pub enum HealthStatus {
    Healthy,         // success_rate > 90%
    Degraded,        // success_rate 70-90%
    Unhealthy,       // success_rate < 70%
}
```

### 8️⃣ Plugin Discovery Service (~150 LOC)

**Archivo**: `crates/elap-core/src/plugin/discovery.rs` (nuevo)

```rust
pub struct PluginMarketplace {
    pub local_plugins: Vec<PluginMetadata>,
    pub remote_plugins: Vec<RemotePlugin>,  // De registry online
}

pub async fn discover_plugins(path: &str) -> Result<Vec<PluginMetadata>>;
pub async fn fetch_plugin_from_registry(id: &str) -> Result<Plugin>;
```

### 9️⃣ Tests (~400+ LOC)

- ✅ Plugin loading/unloading
- ✅ Permission validation
- ✅ Sandbox isolation
- ✅ Lifecycle transitions
- ✅ Health monitoring
- ✅ Error recovery

---

## 🔄 Arquitectura

```
┌─────────────────────────────────────────────────┐
│         Plugin Runtime Framework                │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ Plugin Discovery & Registry             │   │
│  │ - Scan directories                      │   │
│  │ - Parse manifests                       │   │
│  │ - Cache metadata                        │   │
│  └─────────────────────────────────────────┘   │
│                    ↓                            │
│  ┌─────────────────────────────────────────┐   │
│  │ Permission Validator                    │   │
│  │ - Check manifest permissions            │   │
│  │ - User approval                         │   │
│  │ - Granular rules                        │   │
│  └─────────────────────────────────────────┘   │
│                    ↓                            │
│  ┌─────────────────────────────────────────┐   │
│  │ Plugin Loader                           │   │
│  │ - Load .so/.dylib/.dll                  │   │
│  │ - Resolve symbols                       │   │
│  │ - Version negotiation                   │   │
│  └─────────────────────────────────────────┘   │
│                    ↓                            │
│  ┌─────────────────────────────────────────┐   │
│  │ Sandbox & Isolation                     │   │
│  │ - Memory limits (cgroups)               │   │
│  │ - CPU limits                            │   │
│  │ - Filesystem isolation                  │   │
│  │ - Network filtering                     │   │
│  └─────────────────────────────────────────┘   │
│                    ↓                            │
│  ┌─────────────────────────────────────────┐   │
│  │ Plugin Execution & Monitoring           │   │
│  │ - Execute in sandbox                    │   │
│  │ - Monitor health                        │   │
│  │ - Collect metrics                       │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🎬 Orden de implementación

| Día | Tarea | LOC | Status |
|-----|-------|-----|--------|
| 1 | Plan + Manifest format | 100 | ⏳ |
| 2 | Permissions + Health monitoring | 500 | ⏳ |
| 3 | Advanced sandbox + Lifecycle | 650 | ⏳ |
| 4 | Plugin discovery + Tests | 400 | ⏳ |
| 5 | Integration + Documentation | 300 | ⏳ |

---

## ✅ Checklist de finalización

- [ ] Plugin manifest format (.toml)
- [ ] Permission model completo
- [ ] Advanced sandbox (memory/CPU/FS)
- [ ] Health monitoring
- [ ] Plugin lifecycle states
- [ ] Plugin discovery service
- [ ] Tests (>80% cobertura)
- [ ] Documentation (Manifest guide)
- [ ] Libro 08 para NotebookLM
- [ ] CHANGELOG.md actualizado
- [ ] Integración con REST API

---

**Próxima fase**: Fase 7 - Testing & Quality (después 2026-08-15)
