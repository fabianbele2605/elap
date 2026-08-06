# Libro 04: Plugin Runtime — Capítulo 2 — Crear tu primer plugin

**Tema**: Implementar un plugin simple que siga el Plugin trait.

---

## 📋 Ejercicio: Plugin Saludador

Crearemos un plugin que saluda en idiomas diferentes.

---

## ✍️ Código

```rust
use elap_core::plugin::Plugin;

pub struct SaludadorPlugin {
    idioma: String,
}

impl SaludadorPlugin {
    pub fn nuevo(idioma: String) -> Self {
        Self { idioma }
    }
}

impl Plugin for SaludadorPlugin {
    fn nombre(&self) -> &str { "saludador" }
    fn version(&self) -> &str { "1.0.0" }
    fn descripcion(&self) -> &str { "Saluda en diferentes idiomas" }
    
    fn inicializar(&mut self) -> Result<(), String> {
        println!("Plugin saludador inicializado");
        Ok(())
    }
    
    fn ejecutar(&self, comando: &str, args: &[String]) 
        -> Result<String, String> {
        match comando {
            "saludar" => {
                let nombre = args.first()
                    .map(|s| s.as_str())
                    .unwrap_or("Mundo");
                
                let saludo = match self.idioma.as_str() {
                    "es" => format!("¡Hola, {}!", nombre),
                    "en" => format!("Hello, {}!", nombre),
                    "fr" => format!("Bonjour, {}!", nombre),
                    _ => format!("Hi, {}!", nombre),
                };
                
                Ok(saludo)
            }
            _ => Err("Comando desconocido".to_string()),
        }
    }
    
    fn finalizar(&mut self) -> Result<(), String> {
        println!("Plugin saludador finalizado");
        Ok(())
    }
    
    fn as_any(&self) -> &dyn std::any::Any {
        self
    }
}
```

---

## 🧪 Test

```rust
#[test]
fn test_plugin_saludador() {
    let mut plugin = SaludadorPlugin::nuevo("es".to_string());
    assert!(plugin.inicializar().is_ok());
    
    let resultado = plugin.ejecutar("saludar", 
        &["Alice".to_string()]);
    assert_eq!(resultado.unwrap(), "¡Hola, Alice!");
    
    assert!(plugin.finalizar().is_ok());
}
```

---

## 📦 Registrar en RegistroPlugins

```rust
let mut metadata = PluginMetadata::nuevo(
    "saludador".to_string(),
    "1.0.0".to_string(),
    "mi_empresa".to_string(),
    "Saluda en idiomas".to_string(),
    "./plugins/saludador.so".to_string(),
    "plugin_init".to_string(),
);
metadata.agregar_permiso("AccesoRed".to_string());

registro.registrar(metadata)?;
```

---

**Próximo**: Compilar como `.so` y cargar dinámicamente
