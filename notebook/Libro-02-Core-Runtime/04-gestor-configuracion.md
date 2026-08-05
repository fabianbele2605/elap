# Capítulo 4 — Gestor de Configuración

**Tema central**: Cómo ELAP se adapta a diferentes entornos (desarrollo, producción) sin cambiar código.

**Objetivo pedagógico**: Entender por qué la configuración debe estar separada del código.

---

## 🎯 La pregunta que responde este capítulo

> "Creé ELAP en mi laptop. ¿Cómo lo hago funcionar en producción sin reescribir código?"

**Respuesta**: El Gestor de Configuración permite cambiar comportamiento sin tocar el código.

---

## 📖 Analogía: Restaurante con múltiples sucursales

Imagina una cadena de restaurantes:

```
DESARROLLO (Mi laptop):
- Ubicación: Mi casa
- Personal: Yo solo
- Dinero: Presupuesto limitado
- Comidas: Experimentos

PRODUCCIÓN (Empresa real):
- Ubicación: Centro comercial
- Personal: 50 empleados
- Dinero: Inversión grande
- Comidas: Menú establecido
```

**El código es el mismo** (receta). **La configuración es diferente** (presupuesto, horarios, ingredientes).

ELAP es así: el Motor Central es la "receta", la configuración es los "parámetros del restaurante".

---

## 🔧 ¿Qué es Configuración?

Configuración es **información que cambia entre entornos pero NO es código**:

```
┌──────────────────────────┐
│  CONFIGURACIÓN DE ELAP   │
├──────────────────────────┤
│ Base de datos (URL)      │ ← Cambia por entorno
│ Puerto del servidor      │ ← Cambia por entorno
│ Nivel de logging         │ ← Cambia por entorno
│ Clave de cifrado         │ ← Cambia por entorno
│ Endpoint de Ollama       │ ← Cambia por entorno
│ Modo (dev/prod)          │ ← Cambia por entorno
└──────────────────────────┘
```

### NO es configuración

```
❌ Lógica de algoritmos
❌ Estructura de datos
❌ Flujos de proceso
❌ Validaciones de negocio
```

Esas van en código.

---

## 🏗️ Estructura de Configuración

ELAP divide configuración en 4 áreas:

```rust
┌─────────────────────────────────────┐
│       Configuracion General         │
├─────────────────────────────────────┤
│                                     │
│  ConfigBaseDatos                    │ ← Dónde guardar datos
│  ├─ tipo: "sqlite" o "postgresql"  │
│  ├─ url: "sqlite::memory:"         │
│  ├─ pool_size: 10                  │
│  └─ timeout: 30                    │
│                                     │
│  ConfigSeguridad                    │ ← Cómo proteger datos
│  ├─ clave_cifrado: "..."           │
│  ├─ rbac_habilitado: true          │
│  └─ auditoria_habilitada: true     │
│                                     │
│  ConfigIA                           │ ← Dónde está la IA
│  ├─ endpoint_ollama: "..."         │
│  ├─ modelo_defecto: "llama2"       │
│  └─ timeout_inferencia: 120        │
│                                     │
│  Configuración General              │ ← Metadatos
│  ├─ nombre_app: "ELAP"             │
│  ├─ puerto: 8000                   │
│  └─ modo: "production"             │
│                                     │
└─────────────────────────────────────┘
```

---

## 📝 Archivo de Configuración (YAML)

ELAP usa YAML porque es legible por humanos:

```yaml
# config.yaml

nombre_app: ELAP
version: "0.1.0"
modo: development           # ← Importante: development vs production
puerto: 8000
nivel_logging: info

base_datos:
  tipo: sqlite
  url: "sqlite::memory:"   # ← En desarrollo, DB en memoria (rápido)
  pool_size: 10
  timeout: 30

seguridad:
  clave_cifrado: "desarrollo-cambiar-en-produccion"
  rbac_habilitado: true
  ruta_permisos: "config/permisos.yaml"
  auditoria_habilitada: true

ia:
  endpoint_ollama: "http://localhost:11434"
  modelo_defecto: "llama2"
  timeout_inferencia: 120
  tamaño_contexto: 4096
```

### Comparación: desarrollo vs producción

```yaml
# DESARROLLO (config-dev.yaml)
modo: development
puerto: 8000
base_datos:
  tipo: sqlite
  url: "sqlite::memory:"     # ← Rápido, no requiere servidor

---

# PRODUCCIÓN (config-prod.yaml)
modo: production
puerto: 443                   # ← Puerto estándar HTTPS
base_datos:
  tipo: postgresql
  url: "postgres://user:SECURE_PASS@prod-db.com/elap"  # ← BD real
seguridad:
  clave_cifrado: "CLAVE-SECRETA-ALEATORIA-64-CHARS"   # ← Diferente
```

---

## 🚀 El API de Configuración

### 1. Crear configuración por defecto

```rust
let config = Configuracion::defecto();
// Automáticamente modo: "development"
```

### 2. Cargar desde archivo

```rust
let config = Configuracion::cargar("config/elap.yaml")?;
// Lee del archivo, parsea YAML
```

### 3. Validar configuración

```rust
config.validar()?;
// Verifica reglas de negocio
```

### 4. Guardar a archivo

```rust
config.guardar("config/elap.yaml")?;
// Escribe en YAML formato
```

### 5. Consultar modo

```rust
if config.es_produccion() {
    // Modo estricto
} else {
    // Modo permisivo
}
```

---

## 🔄 Flujo completo: Startup de ELAP

```
PASO 1: Buscar archivo de config
─────────────────────────────────
¿Existe config/elap.yaml?
  → SÍ: cargar
  → NO: usar defecto()

        ↓

PASO 2: Validar configuración
──────────────────────────────
config.validar()?;

Verifica:
✓ Puerto > 0
✓ Pool size > 0
✓ URL de BD no vacía
✓ En producción, clave cifrado es segura
✓ Timeout > 0

Si falla: PANIC (no iniciamos con config inválida)

        ↓

PASO 3: Imprimir información
──────────────────────────────
println!("ELAP {}", config.version);
println!("Modo: {}", config.modo);
println!("BD: {}", config.base_datos.tipo);

        ↓

PASO 4: Usar configuración en Motor
────────────────────────────────────
let motor = MotorCentral::con_config(config);
motor.iniciar().await?;
```

---

## 🛡️ Validación de Configuración

El Gestor valida automáticamente:

```rust
config.validar()?;
```

**Reglas de negocio**:

```
Puerto válido:
  puerto > 0
  ✓ puerto: 8000 (OK)
  ✗ puerto: 0 (ERROR)

URL de BD:
  url no puede estar vacía
  ✓ url: "sqlite::memory:" (OK)
  ✗ url: "" (ERROR)

Clave de producción:
  Si modo == "production":
    clave_cifrado != "desarrollo-cambiar-en-produccion"
  ✓ modo: "development" + clave: "desarrollo..." (OK)
  ✗ modo: "production" + clave: "desarrollo..." (ERROR)
```

---

## 📊 Ejemplo real: Migrar de desarrollo a producción

### Paso 1: Crear config.yaml en desarrollo

```bash
# En mi laptop
let config = Configuracion::defecto();
config.guardar("config/elap.yaml")?;
```

Genera `config/elap.yaml`:
```yaml
modo: development
puerto: 8000
base_datos:
  tipo: sqlite
  url: "sqlite::memory:"
```

### Paso 2: Copiar a producción y modificar

```bash
# En servidor producción
# Copiar archivo config/elap.yaml

# Editar para producción:
modo: production
puerto: 443
base_datos:
  tipo: postgresql
  url: "postgres://elap_user:secret@prod-db/elap_db"
seguridad:
  clave_cifrado: "CLAVE-ALEATORIA-DE-PRODUCCION"
```

### Paso 3: Compilar y ejecutar (mismo código)

```bash
cargo build --release
./target/release/elap-cli start

# Output:
# ELAP v0.1.0
# Modo: production
# BD: postgresql
# Iniciando Motor Central...
```

**El código es EXACTAMENTE IGUAL** en desarrollo y producción. Solo cambia el archivo de configuración.

---

## 💡 Preguntas frecuentes

### P: ¿Dónde guardo la clave de cifrado segura?

R: **NO la guardes en el repositorio Git**. Opciones:

**Opción 1: Variable de entorno**
```bash
export ELAP_CLAVE_CIFRADO="clave-secreta"
# En código:
let clave = std::env::var("ELAP_CLAVE_CIFRADO")?;
```

**Opción 2: Archivo .env local (en .gitignore)**
```bash
echo "ELAP_CLAVE_CIFRADO=clave-secreta" > .env.local
```

**Opción 3: Secrets manager (AWS, HashiCorp Vault)**
```rust
let clave = vault_client.get_secret("elap/cipher_key")?;
```

### P: ¿Puedo tener múltiples archivos de config?

R: **Sí**. Ejemplo:

```bash
cargo run -- --config config/dev.yaml
cargo run -- --config config/prod.yaml
```

Luego en código:
```rust
let ruta_config = args.config.unwrap_or("config/elap.yaml");
let config = Configuracion::cargar(&ruta_config)?;
```

### P: ¿Qué pasa si tengo un archivo YAML corrupto?

R: `cargar()` devuelve error. En main:

```rust
match Configuracion::cargar("config.yaml") {
    Ok(config) => { /* usar */ }
    Err(e) => {
        eprintln!("Error al cargar config: {}", e);
        std::process::exit(1);  // No continuar
    }
}
```

### P: ¿Puedo cambiar la config sin reiniciar ELAP?

R: **En v0.1 no**. Fase 1.2 agregará recarga dinámica.

Solución temporal: reiniciar el proceso.

---

## 🎓 Lecciones clave

1. **Separación**: Configuración ≠ Código. Permite cambiar comportamiento sin recompilar.

2. **Validación temprana**: `config.validar()` en startup. Mejor fallar rápido.

3. **Entornos claros**: `modo: "development"` vs `modo: "production"` hace evidente dónde estás.

4. **YAML legible**: El admin ve la configuración claramente, sin necesidad de saber Rust.

5. **Defecto sensato**: `Configuracion::defecto()` permite ejecutar sin archivo (útil en desarrollo).

---

## 📚 Conexión con capítulos anteriores

```
Cap 1: Introducción al Motor
          ↓
Cap 2: Planificador (ordena tareas)
          ↓
Cap 3: Gestor de Procesos (ejecuta tareas)
          ↓
Cap 4: Gestor de Configuración (configura Motor)
          ↓ (próximo)
Cap 5: Flujo Completo (todo junto)
```

**¿Cómo se conectan?**

```
Motor Central
├─ Lee Configuracion (Cap 4)
├─ Usa Planificador (Cap 2)
└─ Usa Gestor de Procesos (Cap 3)
```

---

## 🔜 Próximo: Flujo Completo (Capítulo 5)

Ahora que conoces:
- Motor Central
- Planificador de Tareas
- Gestor de Procesos
- Gestor de Configuración

El siguiente capítulo muestra **cómo todo funciona junto**: una solicitud de usuario desde el inicio hasta el final.

---

**Capítulo siguiente**: 05-flujo-completo.md (Coming soon)
