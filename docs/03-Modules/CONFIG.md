# Módulo Configuration Manager

**Versión**: 0.1.0  
**Estado**: Implementado ✅  
**Ubicación**: `crates/elap-core/src/configuration/`  
**Responsable**: Sistema de configuración Rust

---

## 1. Descripción general

Sistema de configuración persistente, versionado y validado.

Características:
- Soporte TOML/YAML/JSON
- Validación por esquema JSON
- Hot-reload con detección de cambios
- Configuraciones presets (desarrollo, testing, producción)
- Fusión de configuraciones (base + override)

---

## 2. Responsabilidades

- ✅ Cargar configuración desde múltiples formatos
- ✅ Validar configuración contra esquema
- ✅ Detectar cambios en archivos
- ✅ Fusionar configuraciones
- ✅ Proporcionar presets por entorno
- ✅ Serializar/deserializar configuración

---

## 3. Componentes

### 3.1 Config Struct

**Archivo**: `src/configuration/config_struct.rs`

Estructuras principales:

**ConfiguracionAvanzada**
```rust
pub struct ConfiguracionAvanzada {
    pub version: String,
    pub entorno: String,
    pub opciones: HashMap<String, ConfigOption>,
    pub logging: ConfigLogging,
    pub base_datos: ConfigBaseDatos,
    pub seguridad: ConfigSeguridad,
    pub plugins: ConfigPlugins,
}
```

**ConfigOption** (enum)
- Booleano(bool)
- Entero(i64)
- Decimal(f64)
- Texto(String)
- Arreglo(Vec<ConfigOption>)
- Objeto(HashMap<String, ConfigOption>)

**Subsecciones**:
- `ConfigLogging` — Configuración de logging
- `ConfigBaseDatos` — Configuración de BD
- `ConfigSeguridad` — Configuración de seguridad
- `ConfigPlugins` — Configuración de plugins

**Métodos**:
- `defecto()` — Modo desarrollo
- `produccion()` — Optimizado para producción
- `testing()` — Configuración para tests
- `validar()` — Validar consistencia

### 3.2 Cargador

**Archivo**: `src/configuration/loader.rs`

```rust
pub struct CargadorConfiguracion {
    ruta_base: PathBuf,
}
```

**Métodos**:
- `cargar_toml()` — Cargar TOML
- `cargar_yaml()` — Cargar YAML
- `cargar_json()` — Cargar JSON
- `cargar_o_defecto()` — Cargar con fallback
- `guardar_toml()` — Guardar a TOML
- `descubrir()` — Buscar archivos de config
- `cargar_con_override()` — Base + override
- `desde_entorno()` — Cargar según ENTORNO
- `crear_directorio()` — Crear carpeta

### 3.3 Validador

**Archivo**: `src/configuration/validator.rs`

```rust
pub struct ValidadorConfiguracion;

pub struct ResultadoValidacion {
    pub valido: bool,
    pub errores: Vec<String>,
    pub advertencias: Vec<String>,
}
```

**Validaciones**:
- Campos requeridos
- Tipos de datos
- Enumeraciones
- Límites numéricos
- Consistencia entre secciones

### 3.4 Esquema JSON

**Archivo**: `src/configuration/schema.rs`

```rust
pub struct EsquemaConfiguracion;
```

**Métodos**:
- `obtener()` — Esquema JSON completo
- `obtener_string()` — Esquema como string
- `validar_json()` — Validar contra esquema

**Formato**:
- JSON Schema Draft-07
- Validación de propiedades
- Tipos con restricciones
- Enumeraciones

### 3.5 Hot-reload

**Archivo**: `src/configuration/hotreload.rs`

```rust
pub struct MonitorHotReload {
    archivos: Vec<ArchivoMonitoreado>,
    intervalo_check_ms: u64,
}

pub struct ArchivoMonitoreado {
    pub ruta: PathBuf,
    pub ultima_modificacion: u64,
}
```

**Métodos**:
- `nuevo()` — Crear monitor
- `agregar_archivo()` — Monitorear archivo
- `hay_cambios()` — Detectar cambios
- `archivos_modificados()` — Lista de cambios
- `limpiar()` — Reiniciar monitoreo

---

## 4. Testing

**Total: 49 tests**

**Breakdown**:
- config_struct: 16 tests
- loader: 12 tests
- validator: 8 tests
- schema: 6 tests
- hotreload: 7 tests

**Ejecución**:
```bash
cargo test -p elap-core configuration
cargo test -p elap-core configuration::config_struct
cargo test -p elap-core configuration::loader
```

---

## 5. Flujo de uso típico

```
1. Inicializar cargador
   loader = CargadorConfiguracion::nuevo("./config")

2. Descubrir archivos
   archivos = loader.descubrir()

3. Cargar configuración
   config = loader.cargar_toml("config.toml")

4. Validar
   validador = ValidadorConfiguracion
   resultado = validador.validar(&config)

5. Agregar esquema
   schema = EsquemaConfiguracion::obtener()
   validar_json = EsquemaConfiguracion::validar_json()

6. Monitorear cambios
   monitor = MonitorHotReload::nuevo(1000)
   monitor.agregar_archivo(ruta)
   if monitor.hay_cambios() { recargar() }
```

---

## 6. Formatos soportados

### TOML
```toml
version = "1.0.0"
entorno = "desarrollo"

[logging]
nivel = "info"
formato = "json"

[base_datos]
tipo = "sqlite"
archivo = "./data/elap.db"
```

### YAML
```yaml
version: "1.0.0"
entorno: desarrollo
logging:
  nivel: info
  formato: json
base_datos:
  tipo: sqlite
  archivo: ./data/elap.db
```

### JSON
```json
{
  "version": "1.0.0",
  "entorno": "desarrollo",
  "logging": {
    "nivel": "info",
    "formato": "json"
  }
}
```

---

## 7. Presets de entorno

| Entorno | Base datos | Logging | Seguridad |
|---------|-----------|---------|-----------|
| **desarrollo** | SQLite en memoria | DEBUG | Completo |
| **testing** | :memory: | DEBUG | Completo |
| **produccion** | PostgreSQL | WARN | Máximo cifrado |

---

## 8. Validación

Reglas aplicadas:
- `version` requerido (formato X.Y.Z)
- `entorno` requerido (desarrollo, testing, produccion)
- `logging.nivel` en [debug, info, warn, error]
- `base_datos.pool_maximo` > 0
- `base_datos.tipo` en [sqlite, postgresql, mysql]
- `plugins.maximo_plugins` > 0
- SQLite requiere `archivo`
- BD remota requiere `url`

---

## 9. Limitaciones y futuro

**Actual (Paso 5)**:
- Hot-reload solo detecta cambios, no recarga automática
- Esquema JSON es validación manual
- Sin integración de variables de entorno

**Fase 4 Pasos siguientes**:
- Paso 6: Integración con MotorCentral
- Paso 7: Variables de entorno

**Fase 5+**:
- Recarga automática en runtime
- Notificaciones de cambios
- Migración de versiones

---

## 10. API Pública

Exportados desde `crate::configuration`:

```rust
pub use config_struct::ConfiguracionAvanzada;
pub use loader::CargadorConfiguracion;
pub use validator::{ValidadorConfiguracion, ResultadoValidacion};
pub use schema::EsquemaConfiguracion;
pub use hotreload::{MonitorHotReload, ArchivoMonitoreado};
```

---

**Última actualización**: 2026-08-05  
**Próximo**: Fase 4 Paso 6 (Integración)
