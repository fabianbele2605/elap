# Capítulo 5 — Manejo de Errores

**Tema central**: Cómo los errores viajan por el sistema sin derribarlo.

**Objetivo pedagógico**: Entender por qué los errores explícitos son más seguros que panics.

---

## 🎯 La pregunta que responde este capítulo

> "¿Qué pasa si algo falla? ¿Se cae todo ELAP o podemos recuperarnos?"

**Respuesta**: El Motor Central maneja errores de forma explícita y controlada, permitiendo recuperación.

---

## 📖 Analogía: Viajero en el aeropuerto

Imagina un viajero (una función) que necesita:
1. Pasar por seguridad
2. Encontrar su gate
3. Subir al avión

**Opción A (mala - panic):**
```
Seguridad rechaza su pasaporte
    ↓
❌ CRASH - TODO EL AEROPUERTO SE CAE
```

**Opción B (buena - Result):**
```
Seguridad rechaza su pasaporte
    ↓
Función devuelve: Err(ErrorSeguridad("Pasaporte inválido"))
    ↓
Código superior maneja el error
    ↓
"Vaya a renovar su pasaporte, por favor"
    ↓
✅ El aeropuerto sigue funcionando
```

ELAP usa Opción B: **errores explícitos, no panics**.

---

## 🔧 ¿Qué es un Error?

Un error es algo que **puede salir mal, pero NO es un bug**:

```
❌ Bugs (puntos de quiebre):
   - División por cero (el código asume x != 0)
   - Array out of bounds (el código olvidó validar índice)
   - Null pointer (debería inicializarse)

✅ Errores (situaciones esperadas):
   - Archivo no encontrado
   - Permiso denegado
   - Configuración inválida
   - Conexión de red caída
```

**Regla de oro**: Si el usuario puede causar la situación, es un error. Si es un bug del código, es un panic.

---

## 🏗️ Estructura de Errores en ELAP

Todos los errores heredan de este enum:

```rust
pub enum ElapError {
    Config(String),       // Error de configuración
    Io(std::io::Error),   // Error de entrada/salida
    Validacion(String),   // Dato inválido
    Proceso(String),      // Error de proceso
    Otro(String),         // Otros
}
```

### Ejemplo en la vida real:

```rust
// Usuario intenta cargar config.yaml que no existe
match Configuracion::cargar("config.yaml") {
    Ok(config) => println!("Config cargada"),
    Err(ElapError::Io(e)) => eprintln!("Archivo no existe: {}", e),
    Err(ElapError::Config(msg)) => eprintln!("Config inválida: {}", msg),
    Err(e) => eprintln!("Error desconocido: {}", e),
}
```

---

## 🔄 El operador ? (pregunta)

Es la **forma elegante** de propagar errores hacia arriba:

```rust
// ❌ Forma verbosa (sin ?)
pub fn leer_archivo(ruta: &str) -> Result<String, Error> {
    match std::fs::read_to_string(ruta) {
        Ok(contenido) => Ok(contenido),
        Err(e) => Err(e.into()),
    }
}

// ✅ Forma elegante (con ?)
pub fn leer_archivo(ruta: &str) -> Result<String, Error> {
    let contenido = std::fs::read_to_string(ruta)?;
    Ok(contenido)
}
```

**¿Cómo funciona ?**

```
Línea 1: let config = Configuracion::cargar("config.yaml")?;
                                                            ↑
                                          Si devuelve Err, salta aquí
                                          Si devuelve Ok, continúa

Flujo si cargar() devuelve Err:
    ↓
Err(e) se propaga a la función superior
    ↓
La función superior decide qué hacer
```

---

## 📊 Flujo de errores: Motor Central iniciando

```
Motor::iniciar()
    ↓
1. Inicializar logging
    ├─ Si falla: Err(Config("No se pudo crear logs/"))
    └─ Si OK: continúa
    ↓
2. Validar configuración
    ├─ Si puerto=0: Err(Validacion("Puerto inválido"))
    ├─ Si clave vacía en prod: Err(Validacion("Clave no configurada"))
    └─ Si OK: continúa
    ↓
3. ✅ Ok(()) - Motor listo
```

**En código**:

```rust
pub async fn iniciar(&self) -> ResultadoElap<()> {
    // 1. Logging
    inicializar_logging(&self.config.ruta_logs, ...)
        .map_err(|e| ElapError::Config(e.to_string()))?;
    
    // 2. Validación
    self.config.validar()
        .map_err(|e| ElapError::Validacion(e.to_string()))?;
    
    // Si todo OK:
    Ok(())
}
```

Si falla en paso 1 → devuelve Err(Config(...))  
Si falla en paso 2 → devuelve Err(Validacion(...))  
Si todo bien → devuelve Ok(())

---

## 🛡️ Patrones de seguridad

### Nunca .unwrap() en código de biblioteca

```rust
// ❌ NUNCA - puede crashear
pub fn procesar(x: Option<i32>) -> i32 {
    x.unwrap() + 1  // Si x es None, ¡CRASH!
}

// ✅ SIEMPRE - retorna error
pub fn procesar(x: Option<i32>) -> Result<i32, ElapError> {
    x.ok_or_else(|| ElapError::Validacion("x es requerido".to_string()))
        .map(|val| val + 1)
}
```

### El ? operator evita .unwrap()

```rust
// Con ?:
let valor = opcion?;  // Si None, propaga el error arriba
// Con .unwrap():
let valor = opcion.unwrap(); // Si None, ¡CRASH!
```

---

## 💡 Preguntas frecuentes

### P: ¿Cuándo uso Result vs Option?

```
Option<T>   → valor puede existir o no (Some/None)
Result<T,E> → operación puede tener éxito o error específico

// Opción
fn buscar_usuario(id: u32) -> Option<User> {
    // Si existe → Some(user)
    // Si no existe → None
}

// Result
fn cargar_config(ruta: &str) -> Result<Config, ElapError> {
    // Si existe → Ok(config)
    // Si falla → Err(ElapError::Io(...))
}
```

### P: ¿Cómo sé qué error devolver?

**Regla**: Devuelve el error **más específico posible**:

```rust
// ❌ Demasiado vago
Err(ElapError::Otro("Algo salió mal"))

// ✅ Específico
Err(ElapError::Config("Puerto debe ser > 0"))
```

### P: ¿Qué pasa si me olvido de manejar un error?

```rust
// ❌ Error de compilación
let config = Configuracion::cargar("config.yaml");
// ^^^ Result<Config, Error> - no manejada

// ✅ Opciones
// 1. Propagar con ?
let config = Configuracion::cargar("config.yaml")?;

// 2. Manejar explícitamente
let config = match Configuracion::cargar("config.yaml") {
    Ok(c) => c,
    Err(e) => {
        eprintln!("Error: {}", e);
        return Err(e);
    }
};

// 3. Usar unwrap_or (no recomendado en biblioteca)
let config = Configuracion::cargar("config.yaml")
    .unwrap_or_else(|_| Configuracion::defecto());
```

---

## 🎓 Lecciones clave

1. **Errores ≠ Panics**: Los errores son esperables, los panics no.

2. **El ? operator es oro**: Propaga errores sin boilerplate.

3. **Sé específico**: `ElapError::Config(...)` es mejor que `ElapError::Otro(...)`.

4. **Nunca .unwrap() en bibliotecas**: Fuerza al código superior a manejar el error.

5. **Los tipos son documentación**: Mirando `ResultadoElap<()>` sabes que puede fallar.

---

## 📚 Conexión con capítulos anteriores

```
Cap 1: Introducción al Motor
Cap 2: Planificador (ordena tareas)
Cap 3: Procesos (ejecuta tareas)
Cap 4: Configuración (parámetros)
Cap 5: Manejo de Errores (recuperación) ← AQUÍ
         ↓
         Todos los anteriores devuelven Result
```

**¿Cómo se conecta?**

```
Planificador devuelve: Result<Tarea, Error>
Procesos devuelven: Result<(), Error>
Configuración devuelve: Result<Config, Error>
Motor devuelve: Result<(), Error>
```

Si algo falla en cualquier capa, el error sube hasta el CLI o Desktop que lo muestra al usuario.

---

## 🔜 Próximo: Fase 1 Paso 6

Ahora que entiendes manejo de errores, el siguiente paso es **Gestor de Seguridad (RBAC)**.

Los errores que verás: `ElapError::Validacion("Permiso denegado")`.

---

**Capítulo siguiente**: 06-gestor-seguridad.md (Coming soon)
