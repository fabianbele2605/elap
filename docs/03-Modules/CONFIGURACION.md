# Módulo Gestor de Configuración (Configuración)

**Versión**: 0.1.0  
**Estado**: Implementado ✅  
**Ubicación**: `crates/elap-core/src/config/`  
**Responsable**: Motor Central (Rust)

---

## 1. Descripción general

El módulo `config` permite cargar, guardar y validar la configuración de ELAP desde archivos YAML. Soporta múltiples entornos (desarrollo, producción) y valida automáticamente las reglas de negocio.

---

## 2. Responsabilidades

- ✅ Cargar configuración desde archivos YAML
- ✅ Guardar configuración a archivos YAML
- ✅ Validar configuración según reglas de negocio
- ✅ Soportar configuración por defecto (desarrollo)
- ✅ Distinguir entre desarrollo y producción
- ✅ Gestionar errores específicos de configuración

---

## 3. Componentes

### 3.1 Módulo `configuracion.rs`

Define las estructuras principales de configuración.

**Tipos principales**:

```rust
pub struct ConfigBaseDatos              // Configuración de DB
pub struct ConfigSeguridad              // Configuración de seguridad
pub struct ConfigIA                     // Configuración de IA
pub struct Configuracion                // Configuración general
```

**Estructura completa**:

```rust
pub struct Configuracion {
    pub nombre_app: String,             // "ELAP"
    pub version: String,                // "0.1.0"
    pub modo: String,                   // "development" o "production"
    pub puerto: u16,                    // 8000
    pub nivel_logging: String,          // "info"
    pub base_datos: ConfigBaseDatos,    // Config DB
    pub seguridad: ConfigSeguridad,     // Config seguridad
    pub ia: ConfigIA,                   // Config IA
}
```

**Métodos clave**:

```rust
Configuracion::defecto()                // Config de desarrollo
config.cargar(ruta)                     // Leer YAML
config.guardar(ruta)                    // Escribir YAML
config.validar()                        // Validar reglas
config.es_produccion()                  // Modo prod?
config.es_desarrollo()                  // Modo dev?
```

**Ejemplo**:

```rust
// Crear config por defecto
let config = Configuracion::defecto();

// Validar
config.validar()?;

// Guardar a archivo
config.guardar("config.yaml")?;

// Cargar de archivo
let config = Configuracion::cargar("config.yaml")?;
```

### 3.2 Módulo `error.rs`

Define errores específicos de configuración.

```rust
pub enum ErrorConfig {
    NoSeLeyoArchivo(String),       // Archivo no encontrado
    ErrorYaml(String),              // YAML inválido
    NoSeEscribioArchivo(String),   // No se pudo guardar
    CampoFaltante(String),          // Campo obligatorio
    ValorInvalido(String),          // Valor incorrecto
}
```

---

## 4. Patrón de uso

### Paso 1: Crear configuración por defecto

```rust
let config = Configuracion::defecto();
```

### Paso 2: Validar

```rust
config.validar()?;
```

### Paso 3: Guardar a archivo

```rust
config.guardar("config/elap.yaml")?;
```

### Paso 4: Cargar de archivo

```rust
let config = Configuracion::cargar("config/elap.yaml")?;
```

### Paso 5: Usar en el Motor

```rust
if config.es_produccion() {
    tracing::info!("Iniciando en PRODUCCIÓN");
    // Aplicar configuraciones estrictas
} else {
    tracing::info!("Iniciando en DESARROLLO");
}
```

---

## 5. Validación de configuración

Reglas de negocio implementadas:

| Regla | Condición |
|-------|-----------|
| Puerto válido | `puerto > 0` |
| Pool size válido | `pool_size > 0` |
| URL de BD | No puede estar vacía |
| Clave de producción | Si `modo == "production"`, no puede ser la clave de desarrollo |
| Timeout IA | `timeout_inferencia > 0` |

**Ejemplo de validación**:

```rust
let mut config = Configuracion::defecto();
config.modo = "production".to_string();

// Falla: clave aún tiene valor de desarrollo
assert!(config.validar().is_err());

// Arreglarlo
config.seguridad.clave_cifrado = "clave-secreta-produccion".to_string();

// Ahora pasa
assert!(config.validar().is_ok());
```

---

## 6. Formato YAML

Ejemplo de archivo `config.yaml`:

```yaml
nombre_app: ELAP
version: "0.1.0"
modo: production
puerto: 8000
nivel_logging: info

base_datos:
  tipo: postgresql
  url: "postgres://user:pass@localhost/elap"
  pool_size: 20
  timeout: 30

seguridad:
  clave_cifrado: "clave-super-secreta"
  rbac_habilitado: true
  ruta_permisos: "config/permisos.yaml"
  auditoria_habilitada: true

ia:
  endpoint_ollama: "http://localhost:11434"
  modelo_defecto: "mistral"
  timeout_inferencia: 180
  tamaño_contexto: 8192
```

---

## 7. Testing

**11 tests implementados**:

```
✅ test_configuracion_defecto()
✅ test_validar_puerto_cero()
✅ test_validar_pool_size_cero()
✅ test_validar_url_vacia()
✅ test_validar_clave_produccion()
✅ test_validar_correcto()
✅ test_es_produccion()
✅ test_es_desarrollo()
✅ test_guardar_y_cargar()
✅ test_cargar_archivo_inexistente()
✅ test_yaml_invalido()
```

**Ejecutar tests**:

```bash
cargo test config::
cargo test config:: -- --nocapture
```

---

## 8. Integración con Motor Central

```rust
async fn main() -> Result<()> {
    // 1. Cargar configuración
    let config = Configuracion::cargar("config/elap.yaml")
        .unwrap_or_else(|_| Configuracion::defecto());

    // 2. Validar
    config.validar()?;

    // 3. Usar en Motor
    let motor = MotorCentral::con_config(config).await;
    motor.iniciar().await?;

    Ok(())
}
```

---

## 9. Entornos

### Desarrollo

```yaml
modo: development
puerto: 8000
base_datos:
  tipo: sqlite
  url: "sqlite::memory:"
```

### Producción

```yaml
modo: production
puerto: 8000
base_datos:
  tipo: postgresql
  url: "postgres://prod_user:secure_pass@prod_db/elap_prod"
```

---

## 10. Decisiones de diseño

### ¿Por qué YAML en lugar de JSON?

- YAML es más legible para humanos
- Comentarios permitidos
- Menos verboso que JSON
- Estándar en aplicaciones Rust

### ¿Por qué validación explícita?

- `validar()` es un método separado
- Permite validación en tiempo de ejecución
- Las reglas son claras y testables
- Se puede llamar cuando sea necesario

### ¿Por qué defecto() en lugar de Default trait?

- `Default` devuelve config de producción por defecto (peligroso)
- `defecto()` es explícitamente para desarrollo
- Más seguro para el usuario

---

## 11. Roadmap futuro

| Fase | Mejora |
|------|--------|
| 1.1 | Variables de entorno |
| 1.2 | Recarga de config sin reinicio |
| 2.0 | Cifrado de la clave_cifrado en el archivo |
| 2.1 | Validación de JSON Schema |
| 3.0 | Config dinámico desde servidor remoto |

---

## 12. Referencias

- **Código**: `crates/elap-core/src/config/`
- **Tests**: mismos archivos, módulo `tests`
- **Dependencias**: `serde`, `serde_yaml`
- **Arquitectura**: [ARCHITECTURE.md](../01-Architecture/ARCHITECTURE.md)

---

**Última actualización**: 2026-08-04  
**Próximo módulo**: Logging (Fase 1, Paso 4)
