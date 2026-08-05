# Módulo Manejo de Errores (Error Handling)

**Versión**: 0.1.0  
**Estado**: Implementado ✅  
**Ubicación**: `crates/elap-core/src/error.rs`  
**Responsable**: Motor Central (Rust)

---

## 1. Descripción general

El módulo `error` define tipos de error personalizados para ELAP y proporciona un mecanismo consistente de manejo de errores usando `Result<T, ElapError>`.

---

## 2. Responsabilidades

- ✅ Definir tipos de error específicos del dominio
- ✅ Implementar Display para mensajes legibles
- ✅ Implementar Error trait para compatibilidad
- ✅ Convertir de std::io::Error a ElapError
- ✅ Proporcionar alias ResultadoElap<T>

---

## 3. Componentes

### Enum ElapError

**Variantes**:

| Variante | Propósito |
|----------|-----------|
| `Config(String)` | Errores de configuración |
| `Io(std::io::Error)` | Errores de entrada/salida |
| `Validacion(String)` | Errores de validación |
| `Proceso(String)` | Errores de procesos |
| `Otro(String)` | Errores no categorizados |

**Ejemplo**:

```rust
let error = ElapError::Config("Puerto inválido".to_string());
println!("{}", error); // "Error de configuración: Puerto inválido"
```

### Type alias ResultadoElap<T>

```rust
pub type ResultadoElap<T> = Result<T, ElapError>;

// Uso
pub async fn iniciar(&self) -> ResultadoElap<()> {
    // ...
    Ok(())
}
```

---

## 4. Conversiones automáticas

**From<std::io::Error>**:

```rust
// Automático:
let io_err = std::io::Error::last_os_error();
let elap_err: ElapError = io_err.into();
// O con ? operator:
std::fs::read_to_string("file.txt")?; // convierte automáticamente
```

---

## 5. Patrones de uso

### Propagación con ?

```rust
pub async fn cargar_config(ruta: &str) -> ResultadoElap<Configuracion> {
    let contenido = std::fs::read_to_string(ruta)?; // Io error → ElapError
    let config: Configuracion = serde_yaml::from_str(&contenido)
        .map_err(|e| ElapError::Config(e.to_string()))?;
    Ok(config)
}
```

### Manejo explícito

```rust
match resultado {
    Ok(valor) => println!("Éxito: {}", valor),
    Err(ElapError::Config(msg)) => eprintln!("Config error: {}", msg),
    Err(ElapError::Io(io_err)) => eprintln!("IO error: {}", io_err),
    Err(e) => eprintln!("Error: {}", e),
}
```

---

## 6. Testing

**2 tests implementados**:

```
✅ test_error_display() - Display format
✅ test_error_from_io() - From<std::io::Error>
```

---

## 7. Integración con Motor Central

```rust
pub async fn iniciar(&self) -> ResultadoElap<()> {
    inicializar_logging(...)
        .map_err(|e| ElapError::Config(e.to_string()))?;
    
    self.config.validar()
        .map_err(|e| ElapError::Validacion(e.to_string()))?;
    
    Ok(())
}
```

---

**Última actualización**: 2026-08-05  
**Próximo módulo**: Task Scheduler mejorado con error handling
