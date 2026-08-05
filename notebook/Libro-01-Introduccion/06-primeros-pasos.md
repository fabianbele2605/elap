# Libro 01: Introducción — Capítulo 6 — Primeros pasos prácticos

**Tema**: Tu primer plugin, agente y flujo en 10 minutos.

---

## 📌 Resumen: 4 cosas que harás

```
1. Crear tu primer plugin (5 minutos)
2. Registrarlo en ELAP (1 minuto)
3. Ejecutar un agente que lo use (2 minutos)
4. Debuggear si falla (2 minutos)
```

---

## 🔧 Paso 1: Crear tu primer plugin

### Crear archivo: `plugins/saludador.rs`

```rust
use elap_core::plugin::Plugin;
use serde_json::{json, Value};

pub struct PluginSaludador;

impl Plugin for PluginSaludador {
    fn nombre(&self) -> &str {
        "saludador"
    }

    fn descripcion(&self) -> &str {
        "Plugin que saluda usuarios por su nombre"
    }

    fn ejecutar(&self, parametros: &Value) -> Result<Value, String> {
        // Extraer nombre del parámetro
        let nombre = parametros
            .get("nombre")
            .and_then(|v| v.as_str())
            .ok_or_else(|| "Parámetro 'nombre' requerido".to_string())?;

        // Generar saludo
        let saludo = format!("¡Hola, {}! ¿Cómo estás?", nombre);

        // Retornar resultado
        Ok(json!({
            "mensaje": saludo,
            "timestamp": chrono::Utc::now().to_rfc3339(),
        }))
    }

    fn validar(&self) -> Result<(), String> {
        Ok(())
    }
}
```

### Compilar el plugin

```bash
# En la raíz del proyecto
cargo build --release

# Ver que compila sin errores
# ✅ Finished release target(s)
```

---

## 🎯 Paso 2: Registrar el plugin

### Opción A: Vía CLI

```bash
elap plugin register ./plugins/saludador.rs

# Respuesta:
# ✅ Plugin 'saludador' registrado
# Ubicación: /home/usuario/.elap/plugins/saludador
```

### Opción B: Vía código (si desarrollas integración)

```rust
use elap_core::plugin::RegistroPlugins;

let registro = RegistroPlugins::nuevo();
let plugin = PluginSaludador;

registro.registrar(
    plugin.nombre(),
    plugin.descripcion(),
)?;

println!("✅ Plugin registrado");
```

---

## 🤖 Paso 3: Crear y ejecutar tu primer agente

### Crear archivo: `ejemplos/agente_saludador.py`

```python
from elap_ai.agent_runtime import AgentRuntime
from elap_ai.tools import ToolRegistry
import json

# 1. Inicializar agente
agente = AgentRuntime(nombre="SaludadorMaestro", rol="asistente")

# 2. Obtener registro de herramientas
registro = ToolRegistry()

# 3. Crear tarea: "Saluda a todos en la sala de reuniones"
tarea = {
    "descripcion": "Saluda a Ana, Bob y Carlos",
    "herramienta": "saludador",
    "parametros": [
        {"nombre": "Ana"},
        {"nombre": "Bob"},
        {"nombre": "Carlos"},
    ]
}

# 4. Ejecutar agente
try:
    resultado = agente.ejecutar(tarea)
    print("✅ Agente completó tarea")
    print(json.dumps(resultado, indent=2))
except Exception as e:
    print(f"❌ Error: {e}")
```

### Ejecutar el agente

```bash
cd ejemplos
python agente_saludador.py

# Salida esperada:
# ✅ Agente completó tarea
# {
#   "saludos": [
#     {"nombre": "Ana", "mensaje": "¡Hola, Ana! ¿Cómo estás?"},
#     {"nombre": "Bob", "mensaje": "¡Hola, Bob! ¿Cómo estás?"},
#     {"nombre": "Carlos", "mensaje": "¡Hola, Carlos! ¿Cómo estás?"}
#   ],
#   "duracion_ms": 145
# }
```

---

## 🔗 Paso 4: Crear tu primer flujo

### ¿Qué es un flujo?

```
Flujo = Secuencia de tareas conectadas

     Entrada
        ↓
   [Tarea 1]
        ↓
   [Tarea 2]
        ↓
   [Tarea 3]
        ↓
     Salida
```

### Ejemplo: Flujo de análisis

```python
# ejemplos/flujo_analisis.py
from elap_ai.agent_runtime import AgentRuntime, FlowBuilder
import json

# 1. Crear builder de flujo
builder = FlowBuilder(nombre="AnálisisVentas")

# 2. Definir pasos
paso_1 = {
    "nombre": "leer_datos",
    "herramienta": "sql_read",
    "parámetros": {"query": "SELECT * FROM ventas"}
}

paso_2 = {
    "nombre": "procesar",
    "herramienta": "analisis",
    "parámetros_desde": "paso_1"  # Usar salida anterior
}

paso_3 = {
    "nombre": "generar_reporte",
    "herramienta": "reporte_pdf",
    "parámetros_desde": "paso_2"
}

# 3. Agregar pasos al flujo
builder.agregar_paso(paso_1)
builder.agregar_paso(paso_2)
builder.agregar_paso(paso_3)

# 4. Construir y ejecutar
flujo = builder.construir()
resultado = flujo.ejecutar()

print(json.dumps(resultado, indent=2))
```

### Ejecutar el flujo

```bash
python ejemplos/flujo_analisis.py

# Salida esperada:
# {
#   "status": "éxito",
#   "pasos": 3,
#   "duracion_total_ms": 4320,
#   "salida_final": "reporte.pdf"
# }
```

---

## 🐛 Paso 5: Debugging básico

### Si algo falla

```bash
# 1. Ver logs detallados
export ELAP_LOG_LEVEL=DEBUG
python agente_saludador.py

# 2. Ver trazabilidad
elap debug <id_tarea>

# 3. Ver auditoría de lo que pasó
elap audit show --tarea <id_tarea>
```

### Errores comunes y soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| `Plugin not found` | Plugin no registrado | `elap plugin list` |
| `Permission denied` | RBAC bloqueó tarea | Verificar rol en auditoría |
| `Timeout` | Tarea tardó >30s | Aumentar timeout en config |
| `Memory error` | Resultado muy grande | Limitar resultado con `limit: 1000` |

---

## 📚 Estructura de proyecto recomendada

```
tu-proyecto/
├── ejemplos/
│   ├── agente_saludador.py
│   └── flujo_analisis.py
├── plugins/
│   └── saludador.rs
├── tests/
│   └── test_saludador.py
├── config/
│   └── desarrollo.toml
└── README.md
```

---

## ✅ Verificación: ¿Lo hiciste bien?

```bash
# Responde SÍ a todo esto:

□ ¿Compiló sin errores?
  elap plugin list | grep saludador

□ ¿Se ejecutó el agente?
  ¿Viste "✅ Agente completó tarea"?

□ ¿Recibiste salidos esperados?
  ¿Viste "¡Hola, Ana!..." etc?

□ ¿El flujo funcionó?
  ¿Se creó reporte.pdf?

□ ¿Entiendes los logs?
  ¿Sabes dónde mirar si algo falla?
```

Si respondiste SÍ a todo → **¡Felicidades! 🎉**

---

## 🚀 Próximos pasos

Ahora que sabes lo básico:

1. **Explora** los documentos técnicos en `/docs`
2. **Crea** tus propios plugins (Libro 03)
3. **Configura** ELAP para tu caso (Libro 04)
4. **Monitorea** con logging avanzado (Libro 05)
5. **Optimiza** con el Tool Engine (Libro 06)

---

## 📖 Recursos

- **CLAUDE.md**: Estándares de código
- **ARCHITECTURE.md**: Diseño del sistema
- **DECISIONS.md**: Por qué cada decisión

---

## 🎓 Resumen del Libro 01

```
Cap 1: Qué es ELAP
   └─ Visión, casos de uso, ROI

Cap 2: Arquitectura general
   └─ 5 capas, comunicación, seguridad

Cap 3: Flujo de datos
   └─ Cómo viaja un dato de entrada a salida

Cap 4: Conceptos clave
   └─ Agentes, roles, plugins, sandbox

Cap 5: Cómo comenzar
   └─ Requisitos, instalación, config

Cap 6: Primeros pasos ← ESTÁS AQUÍ
   └─ Tu primer plugin, agente, flujo
```

---

**Libro siguiente**: [Libro 02 - Core Runtime](../Libro-02-Core-Runtime/)
