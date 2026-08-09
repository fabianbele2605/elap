# Fase 6: Plugin Runtime — Extensible Architecture

**Estado**: 🚀 Por iniciar (2026-08-09)  
**Duración**: 1 semana  
**Entrega**: 2026-08-15  

---

## 🎯 Visión

Un **sistema de plugins dinámicos empresarial** que permita:

```
Developer escribe plugin → ELAP lo carga → ejecuta en sandbox → monitorea salud
```

Sin necesidad de recompilar ELAP. Sin comprometer seguridad. Con recuperación automática.

---

## 📚 Contenido de esta carpeta

```
docs/06-Plugin-Runtime/
├── README.md           # Este archivo
├── PLAN.md            # Plan detallado (5 días)
└── MANIFEST_FORMAT.md # Especificación de manifests
```

---

## 🔧 Componentes a construir

### 1. Plugin Manifest Format

```toml
[metadata]
name = "web_scraper"
version = "1.0.0"
api_version = "1.5.0"
description = "Safe web content extraction"

[permissions]
required = ["network", "file_read"]
optional = ["gpu"]

[limits]
timeout_ms = 30000
memory_mb = 512
cpu_cores = 2
```

### 2. Permission Model

```
Plugin solicita: network + file_read
↓
Validador verifica
↓
Usuario aprueba/deniega
↓
Sandbox aisla según permisos
```

### 3. Advanced Sandbox

- **Memory**: Límite con cgroups en Linux
- **CPU**: Throttling con límite de cores
- **Filesystem**: Solo rutas permitidas
- **Network**: Solo hosts permitidos
- **Syscalls**: Filtering con seccomp (Linux)

### 4. Health Monitoring

```
Plugin en ejecución
  ↓
Monitorear: errores/latencia/uptime
  ↓
Calcular health_score (0.0 - 1.0)
  ↓
Si < 0.5: marcar unhealthy + deshabilitar
  ↓
Si > 0.8: re-habilitar
```

### 5. Plugin Lifecycle

```
Available (cargado)
    ↓
Active (ejecutando)
    ↓
Paused (timeout)
    ↓
Unhealthy (failures)
    ↓
Disabled (manual)
```

---

## 📊 Especificación técnica

### Plugin Trait

```rust
pub trait Plugin: Send + Sync {
    fn name(&self) -> &str;
    fn version(&self) -> &str;
    
    fn execute(
        &mut self,
        input: PluginInput,
    ) -> Result<PluginOutput, PluginError>;
}
```

### Plugin Loader

```rust
let plugin = PluginLoader::load("./plugins/my_plugin.so")?;
let result = plugin.execute(input)?;
```

### Permission Validator

```rust
let validator = PermissionValidator::new();
validator.check_permissions(
    &plugin.manifest,
    &user_policy
)?;
```

### Sandbox

```rust
let sandbox = PluginSandbox::new()
    .with_memory_limit(512)
    .with_timeout_ms(30000);

sandbox.execute(plugin, input)?;
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────┐
│     Plugin Runtime (PluginRuntime)      │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Registry                        │   │
│  │ - loaded_plugins: HashMap       │   │
│  │ - discover(&path)               │   │
│  │ - load(&id)                     │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Validator                       │   │
│  │ - permissions                   │   │
│  │ - manifest integrity            │   │
│  │ - dependencies                  │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Executor                        │   │
│  │ - load + sandbox + execute      │   │
│  │ - error recovery                │   │
│  │ - health monitoring             │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔒 Security Model

### Threat Model

| Amenaza | Mitigation |
|---------|-----------|
| Plugin crashea ELAP | Sandbox + timeout |
| Plugin consume toda RAM | Memory limits (cgroups) |
| Plugin hace network malicioso | Network whitelist |
| Plugin lee archivos sensibles | Filesystem whitelist |
| Plugin usa 100% CPU | CPU limits |
| Plugin tiene vulnerabilidad | Sandbox aísla impact |

### Permission Levels

```
admin > developer > user > guest
↓
Puede crear plugins
↓
Puede aprobar manifests
↓
Puede ejecutar plugins
↓
Solo ver logs
```

---

## 🚀 Uso esperado

### Para usuarios

```bash
# Descargar plugin del marketplace
elap plugin install web_scraper@1.0.0

# Revisar permisos
elap plugin show web_scraper
# Requires: network, file_read
# Memory: 512MB
# Timeout: 30s

# Aprobar
elap plugin approve web_scraper

# Ejecutar
curl http://localhost:3000/plugins/web_scraper/execute \
  -d '{"url": "https://example.com"}'
```

### Para desarrolladores

```rust
// my_plugin/src/lib.rs
use elap_plugin::*;

#[plugin]
pub struct MyScraper;

impl Plugin for MyScraper {
    fn name(&self) -> &str { "web_scraper" }
    fn version(&self) -> &str { "1.0.0" }
    
    fn execute(&mut self, input: PluginInput) -> Result<PluginOutput> {
        let url = input.get_string("url")?;
        // ... scrape safely ...
        Ok(PluginOutput::from_data(data))
    }
}
```

---

## 📈 Métricas de éxito

- ✅ 5+ plugins de ejemplo funcionales
- ✅ Sandbox aisla completamente
- ✅ Healthcheck detecta problemas en < 1s
- ✅ Latencia overhead < 50ms
- ✅ >85% test coverage
- ✅ Documentación completa

---

## 🔗 Referencias

- **PLAN.md**: Plan detallado (5 días)
- **MANIFEST_FORMAT.md**: Especificación de manifests (TBD)
- **Libros**: Libro 08 para NotebookLM (TBD)

---

**¿Listo para comenzar Fase 6?** ⚡