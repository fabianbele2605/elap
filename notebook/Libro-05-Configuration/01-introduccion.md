# Libro 05: Configuration Manager — Capítulo 1 — Introducción

**Tema central**: Cómo configurar ELAP sin tocar código.

**Objetivo pedagógico**: Entender por qué separar configuración del código y cómo validarla.

---

## 🎯 La pregunta que responde este capítulo

> "¿Cómo cambio la configuración de producción sin recompilar?"

**Respuesta**: Archivos de configuración validados + hot-reload

---

## 📖 Analogía: Receta de cocina vs Cocina real

Imagina que eres chef:

```
RECETA (Código)
├─ "Saltear 3 minutos"
├─ "Agregar 100g sal"
├─ "Temperatura 180°C"
└─ Nunca cambia (a menos que rehagamos el libro)

CONFIGURACIÓN (Archivo)
├─ config.toml → nivel de logging: "info"
├─ config.toml → puerto: 8080
├─ config.toml → BD: "produccion"
└─ Cambias sin tocar el código

COCINA REAL
├─ Lee la receta (código compilado)
├─ Consulta configuración (archivo externo)
├─ Valida: ¿sal entre 0-200g?
├─ Si no: error, no cocina
├─ Si sí: procede con ingredientes del config
```

**Configuración = Ingredientes variables**

---

## 🏗️ Estructura del Sistema de Configuración

```
┌─────────────────────────────────────┐
│    Configuration Manager            │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  ConfiguracionAvanzada        │  │
│  │  ├─ version, entorno          │  │
│  │  ├─ logging, base_datos       │  │
│  │  ├─ seguridad, plugins        │  │
│  │  └─ opciones (HashMap)        │  │
│  └───────────────────────────────┘  │
│                ↑                      │
│  ┌───────────────────────────────┐  │
│  │  CargadorConfiguracion        │  │
│  │  ├─ cargar_toml()             │  │
│  │  ├─ cargar_yaml()             │  │
│  │  ├─ cargar_json()             │  │
│  │  ├─ descubrir()               │  │
│  │  └─ cargar_con_override()     │  │
│  └───────────────────────────────┘  │
│                ↑                      │
│  ┌───────────────────────────────┐  │
│  │  ValidadorConfiguracion       │  │
│  │  ├─ validar()                 │  │
│  │  └─ errores + advertencias    │  │
│  └───────────────────────────────┘  │
│                ↑                      │
│  ┌───────────────────────────────┐  │
│  │  EsquemaConfiguracion         │  │
│  │  ├─ JSON Schema Draft-07      │  │
│  │  └─ validar_json()            │  │
│  └───────────────────────────────┘  │
│                ↑                      │
│  ┌───────────────────────────────┐  │
│  │  MonitorHotReload             │  │
│  │  ├─ agregar_archivo()         │  │
│  │  └─ hay_cambios()             │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## 🔑 Componentes principales

### 1. ConfiguracionAvanzada

Estructura con secciones:

```json
{
  "version": "1.0.0",
  "entorno": "desarrollo",
  "logging": {
    "nivel": "debug",
    "formato": "json",
    "guardar_archivo": true,
    "tamaño_maximo_mb": 100
  },
  "base_datos": {
    "tipo": "sqlite",
    "archivo": "./data/elap.db",
    "pool_maximo": 10,
    "timeout_segundos": 30
  },
  "seguridad": {
    "requiere_autenticacion": true,
    "rbac_habilitado": true,
    "cifrado_habilitado": true
  },
  "plugins": {
    "habilitados": true,
    "directorio": "./plugins",
    "maximo_plugins": 50
  }
}
```

**Presets**:
- `.defecto()` — Desarrollo con defaults
- `.produccion()` — Optimizado producción
- `.testing()` — Para tests (:memory:)

### 2. CargadorConfiguracion

**Cargar desde archivos**:

```
config.toml ──┐
config.yaml ──┼─→ CargadorConfiguracion ──→ ConfiguracionAvanzada
config.json ──┘
```

**Métodos principales**:
- `cargar_toml("config.toml")` — Cargar TOML
- `cargar_o_defecto()` — Con fallback
- `descubrir()` — Buscar *.toml, *.yaml, *.json
- `cargar_con_override("base.toml", "override.toml")` — Fusionar

**Ejemplo real**:
```
desarrollo:
  config/default.toml        (base común)
  config/desarrollo.toml     (override)

produccion:
  config/default.toml        (base común)
  config/produccion.toml     (override)
```

### 3. ValidadorConfiguracion

Valida que la config es coherente:

```
Input: ConfiguracionAvanzada
  ↓
Validador: ¿Todos los campos requeridos?
           ¿Tipos correctos?
           ¿Valores en rango?
  ↓
Output: ResultadoValidacion {
  valido: bool,
  errores: Vec<String>,
  advertencias: Vec<String>
}
```

**Ejemplo error**:
- `pool_maximo = 0` ❌ "Pool máximo debe ser > 0"

### 4. EsquemaConfiguracion

Esquema JSON Draft-07 para validación formal:

```json
{
  "properties": {
    "entorno": {
      "enum": ["desarrollo", "testing", "produccion"]
    },
    "logging": {
      "nivel": {
        "enum": ["debug", "info", "warn", "error"]
      }
    }
  }
}
```

### 5. MonitorHotReload

Detecta cambios en archivos:

```
Monitor
  ├─ archivo: config.toml (timestamp: 1234567)
  └─ file modified
      └─ timestamp: 1234568
         hay_cambios() → true
```

---

## 💬 Conversación real: Cambiar configuración en producción

```
1. Operador: "Necesito aumentar buffer de logs de 100MB a 500MB"

2. Operador edita:
   config/produccion.toml:
   - tamaño_maximo_mb = 100
   + tamaño_maximo_mb = 500

3. Sistema detecta cambio:
   MonitorHotReload::hay_cambios() → true

4. Sistema recarga:
   - cargador.cargar_toml("config/produccion.toml")
   - validador.validar(&config)
   - si está OK: usa nuevo config
   - si hay error: mantiene anterior + alerta

5. Operador verifica:
   logs empiezan a rotar cada 500MB
   (sin reiniciar nada)

6. Sistema audita:
   AuditorRbac::registrar_acceso()
   "operador_123, acción_cambiar_config, recurso_logging"
```

---

## 🎓 Conceptos clave

### Separación de Preocupaciones

```
ANTES (acoplado):
  const LOGGING_LEVEL = "info";  // En el código
  
AHORA (desacoplado):
  config.toml:
    [logging]
    nivel = "info"
```

### Validación en capas

```
Capa 1: ¿Archivo existe?
Capa 2: ¿Es TOML/YAML/JSON válido?
Capa 3: ¿Todos los campos están?
Capa 4: ¿Los valores son correctos?
Capa 5: ¿Es internamente consistente?
```

### Fallback (graceful degradation)

```
Si config.toml no existe:
  → usar defecto()
  
Si config.toml inválido:
  → error + mantener anterior
```

---

## 📊 Flujo de carga típico

```
Usuario ejecuta ELAP
  ↓
1. CargadorConfiguracion::descubrir()
   Busca: config.toml, config.yaml, config.json
   
2. CargadorConfiguracion::cargar_toml("config.toml")
   Lee y parsea TOML
   
3. ValidadorConfiguracion::validar(&config)
   Comprueba coherencia
   
4. Si es válido:
   Motor inicia con esa config
   
5. MonitorHotReload::agregar_archivo("config.toml")
   Comienza a monitorear cambios

6. En loop principal:
   if monitor.hay_cambios() {
     recargar_config()
   }
```

---

## ✅ Ventajas

1. **Sin recompilación**: Cambia config, listo
2. **Validación automática**: No aceptas configs inválidas
3. **Presets por entorno**: Desarrollo ≠ producción automáticamente
4. **Hot-reload**: Cambios sin parar el sistema
5. **Auditoria**: Quién cambió qué y cuándo
6. **Fallback seguro**: Si falla, vuelve a anterior

---

## ⚠️ Errores comunes

```
❌ MALO: Hardcodear valores
  const PUERTO = 8080;
  
✅ BIEN: Usar configuración
  config.opciones.get("puerto")

❌ MALO: Confiar en entorno sin validar
  let entorno = env::var("ENTORNO")?;  // ¿Qué si es invalido?
  
✅ BIEN: Validar explícitamente
  let config = CargadorConfiguracion::desde_entorno(&entorno)?;
  validador.validar(&config)?;
```

---

## 🔜 Próximo: Capítulo 2

**"Crear tu archivo de configuración"**

Crearemos:
1. config/default.toml
2. config/desarrollo.toml
3. config/produccion.toml
4. Validarlos y ejecutar

---

**Capítulo siguiente**: 02-tu-primer-config.md (Coming soon)
