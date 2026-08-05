# Libro 05: Configuration — Capítulo 2 — Tu primer archivo de configuración

**Tema**: Crear y validar archivos de configuración reales.

---

## 📋 Ejercicio

Crearemos `config/default.toml`, `config/desarrollo.toml` y `config/produccion.toml`.

---

## ✍️ archivo: config/default.toml (Base común)

```toml
version = "1.0.0"
entorno = "desarrollo"

[logging]
nivel = "info"
formato = "json"
guardar_archivo = true
ruta_archivo = "./logs/elap.log"
tamaño_maximo_mb = 100

[base_datos]
tipo = "sqlite"
archivo = "./data/elap.db"
pool_maximo = 10
timeout_segundos = 30

[seguridad]
requiere_autenticacion = true
rbac_habilitado = true
auditoria_habilitada = true
cifrado_habilitado = true
algoritmo_cifrado = "AES-256-GCM"

[plugins]
habilitados = true
directorio = "./plugins"
cargar_automaticamente = true
maximo_plugins = 50
```

---

## ✍️ archivo: config/desarrollo.toml (Override)

```toml
entorno = "desarrollo"

[logging]
nivel = "debug"
guardar_archivo = false
```

---

## ✍️ archivo: config/produccion.toml (Override)

```toml
entorno = "produccion"

[logging]
nivel = "warn"

[base_datos]
tipo = "postgresql"
url = "postgresql://user:pass@db.example.com:5432/elap"
pool_maximo = 50

[seguridad]
cifrado_habilitado = true
```

---

## 🔧 Código para cargar

```rust
use elap_core::CargadorConfiguracion;
use std::path::PathBuf;

fn main() {
    let loader = CargadorConfiguracion::nuevo(
        PathBuf::from("./config")
    );
    
    // Cargar base
    let config = loader.cargar_toml("default.toml")?;
    println!("✅ Config base cargada");
    
    // Aplicar override según entorno
    let entorno = std::env::var("ENTORNO")
        .unwrap_or_else(|_| "desarrollo".to_string());
    
    let config = loader.cargar_con_override(
        "default.toml",
        Some(&format!("config/{}.toml", entorno))
    )?;
    
    println!("✅ Config con override en: {}", entorno);
    println!("Logging level: {}", config.logging.nivel);
}
```

---

## ✅ Validación

```rust
use elap_core::ValidadorConfiguracion;

let config = loader.cargar_toml("default.toml")?;
let resultado = ValidadorConfiguracion::validar(&config);

assert!(resultado.valido);
println!("✅ Configuración válida");
```

---

**Próximo**: Hot-reload con MonitorHotReload
