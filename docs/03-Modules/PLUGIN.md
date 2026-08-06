# Módulo Plugin Runtime

**Versión**: 0.1.0  
**Estado**: Implementado ✅  
**Ubicación**: `crates/elap-core/src/plugin/`  
**Responsable**: Framework de plugins Rust

---

## 1. Descripción general

Sistema extensible para cargar y ejecutar plugins de terceros de forma segura.

Incluye:
- Trait base para plugins (Plugin trait)
- Metadatos de plugin con validación
- Cargador dinámico de plugins (.so, .dll, .dylib)
- Registro central de plugins (RegistroPlugins)
- Sandbox para ejecución aislada con límites de recursos

---

## 2. Responsabilidades

- ✅ Definir interfaz estándar para plugins (Plugin trait)
- ✅ Validar metadatos de plugins
- ✅ Cargar plugins desde archivos binarios
- ✅ Registrar y gestionar plugins disponibles
- ✅ Ejecutar plugins en sandbox aislado
- ✅ Controlar permisos y acceso a recursos

---

## 3. Componentes

### 3.1 Plugin Trait

**Archivo**: `src/plugin/plugin_trait.rs`

Interfaz que todo plugin debe implementar:

```rust
pub trait Plugin: Send + Sync {
    fn nombre(&self) -> &str;
    fn version(&self) -> &str;
    fn descripcion(&self) -> &str;
    fn inicializar(&mut self) -> Result<(), String>;
    fn ejecutar(&self, comando: &str, args: &[String]) -> Result<String, String>;
    fn finalizar(&mut self) -> Result<(), String>;
    fn as_any(&self) -> &dyn Any;
}
```

**Métodos clave**:
- `nombre()` — Identificador único
- `version()` — Versión semántica
- `inicializar()` — Setup del plugin
- `ejecutar()` — Ejecutar comando
- `finalizar()` — Cleanup

### 3.2 Plugin Metadata

**Archivo**: `src/plugin/metadata.rs`

Estructura de metadatos:

```rust
pub struct PluginMetadata {
    pub nombre: String,
    pub version: String,
    pub autor: String,
    pub descripcion: String,
    pub ruta_binario: String,
    pub punto_entrada: String,
    pub permisos: Vec<String>,
    pub hash_verificacion: Option<String>,
}
```

**Métodos**:
- `nuevo()` — Crear metadatos
- `agregar_permiso()` — Agregar permiso requerido

### 3.3 Plugin Loader

**Archivo**: `src/plugin/loader.rs`

Cargador dinámico de plugins:

```rust
pub struct PluginLoader {
    directorio_plugins: PathBuf,
}
```

**Métodos**:
- `nuevo()` — Crear loader
- `validar_binario()` — Verificar existencia
- `validar_metadata()` — Validar metadatos
- `cargar()` — Cargar plugin con validación
- `descubrir()` — Escanear directorio de plugins
- `cargar_por_nombre()` — Buscar plugin por nombre
- `calcular_hash()` — SHA256 para verificación

### 3.4 Plugin Registry

**Archivo**: `src/plugin/registry.rs`

Registro central thread-safe:

```rust
pub struct RegistroPlugins {
    plugins: Arc<Mutex<HashMap<String, PluginMetadata>>>,
}
```

**Métodos**:
- `registrar()` — Registrar plugin
- `desregistrar()` — Remover plugin
- `obtener()` — Obtener por nombre
- `listar()` — Listar todos
- `contar()` — Cantidad de plugins
- `existe()` — Verificar existencia
- `buscar_por_autor()` — Búsqueda
- `buscar_por_permiso()` — Búsqueda

### 3.5 Plugin Sandbox

**Archivo**: `src/plugin/sandbox.rs`

Aislamiento y control de recursos:

```rust
pub struct PluginSandbox {
    config: ConfiguracionSandbox,
    politica: PoliticaEjecucion,
}

pub struct ConfiguracionSandbox {
    pub limite_memoria_mb: u32,
    pub timeout_segundos: u64,
    pub permitir_red: bool,
    pub permitir_archivos: bool,
    pub permitir_procesos: bool,
}

pub struct PoliticaEjecucion {
    pub requiere_firma: bool,
    pub requiere_permisos: bool,
    pub auditar_acciones: bool,
}
```

**Métodos**:
- `nuevo()` — Crear sandbox
- `defecto()` — Configuración por defecto
- `validar_plugin()` — Validar plugin
- `tiene_permiso()` — Verificar permiso específico
- `puede_acceder_red()` — Control de red
- `puede_acceder_archivos()` — Control de archivos
- `puede_acceder_procesos()` — Control de procesos

**Presets**:
- `ConfiguracionSandbox::restrictiva()` — Máxima seguridad
- `ConfiguracionSandbox::permisiva()` — Para plugins confiables

---

## 4. Testing

**Total: 35 tests** (110 en elap-core)

**Breakdown**:
- plugin_trait: 3 tests (implícitos en metadata)
- metadata: 3 tests
- loader: 9 tests (6 + 3 nuevos)
- registry: 13 tests (10 + 3 nuevos)
- sandbox: 12 tests

**Ejecución**:
```bash
cargo test -p elap-core plugin
cargo test -p elap-core plugin::registry
cargo test -p elap-core plugin::sandbox
cargo test -p elap-core plugin::loader
```

---

## 5. Flujo de uso típico

```
1. PluginLoader descubre plugins en directorio
   ↓
2. Lee metadatos y valida
   ↓
3. Calcula hash SHA256 para verificación
   ↓
4. RegistroPlugins almacena plugin disponible
   ↓
5. Usuario solicita ejecutar plugin
   ↓
6. PluginSandbox valida permisos
   ↓
7. Ejecuta en sandbox con límites de recurso
   ↓
8. AuditorRbac registra acción
```

---

## 6. Seguridad

### Validación
- Metadatos validados (nombre, versión, punto entrada)
- Binarios verificados (existencia, hash SHA256)
- Permisos declarados explícitamente

### Aislamiento
- Sandbox con límites de memoria y timeout
- Políticas configurables (restrictiva/permisiva)
- Integración con RBAC para validación de permisos
- Auditoría de todas las acciones

### Permisos
- `AccesoRed` — Permitir conexiones de red
- `AccesoArchivos` — Permitir lectura/escritura de archivos
- `AccesoProcesos` — Permitir crear/terminar procesos

---

## 7. Limitaciones y futuro

**Actual (Paso 6)**:
- Sandbox es configuracional pero no aplicado en runtime (para Fase 4)
- Sin carga dinámica real de símbolos (para Fase 3 Paso 2)
- Sin límites de CPU/memoria verdaderos (para Fase 4)

**Fase 3 Pasos siguientes**:
- Paso 7: Integración con MotorCentral
- Paso 8+: Ejecutor real de plugins

**Fase 4+**:
- Límites de recursos en runtime
- Carga dinámica de símbolos
- Sandboxing en procesos aislados

---

## 8. API Pública

Exportados desde `crate::plugin`:

```rust
pub use plugin_trait::Plugin;
pub use metadata::PluginMetadata;
pub use loader::PluginLoader;
pub use registry::RegistroPlugins;
pub use sandbox::{PluginSandbox, ConfiguracionSandbox, PoliticaEjecucion};
```

---

**Última actualización**: 2026-08-05  
**Próximo**: Fase 3 Paso 7 (Integración)
