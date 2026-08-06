# Módulo Seguridad (RBAC y Auditoría)

**Versión**: 0.1.0  
**Estado**: Implementado ✅  
**Ubicación**: `crates/elap-core/src/security/`  
**Responsable**: Motor Central (Rust)

---

## 1. Descripción general

El módulo `security` implementa control de acceso basado en roles (RBAC) y un sistema de auditoría para registrar todas las acciones de usuarios en ELAP.

**Componentes principales**:
- `Rol`: Enum con 4 roles (Admin, Usuario, Invitado, Agente)
- `Permiso`: Enum con 5 permisos (LeerArchivos, EscribirArchivos, EjecutarProcesos, EjecutarHerramientas, CambiarConfiguracion)
- `GestorRbac`: Valida permisos según rol del usuario
- `RegistroAuditoria`: Registro inmutable de una acción
- `AuditorRbac`: Almacena y gestiona registros de acceso

---

## 2. Responsabilidades

- ✅ Definir roles y permisos del sistema
- ✅ Validar permisos antes de operaciones sensibles
- ✅ Registrar intentos exitosos y denegados
- ✅ Auditoría con timestamp de cada acción
- ✅ Integración con MotorCentral para acceso global

---

## 3. Componentes

### 3.1 Enum Rol

```rust
pub enum Rol {
    Admin,      // Acceso total
    Usuario,    // Acceso normal
    Invitado,   // Solo lectura
    Agente,     // Ejecución de herramientas
}
```

**Ubicación**: `security/rol.rs`  
**Tests**: 5 tests de Display y comparación

### 3.2 Enum Permiso

```rust
pub enum Permiso {
    LeerArchivos,
    EscribirArchivos,
    EjecutarProcesos,
    EjecutarHerramientas,
    CambiarConfiguracion,
}
```

**Ubicación**: `security/permisos.rs`  
**Tests**: 6 tests de Display y comparación

### 3.3 Struct GestorRbac

Valida si un rol tiene permiso para una acción.

**Métodos**:

| Método | Firma | Retorna |
|--------|-------|---------|
| `nuevo()` | `() -> Self` | GestorRbac inicializado |
| `validar_permiso()` | `(rol: Rol, permiso: Permiso) -> ResultadoElap<()>` | Ok si tiene permiso |
| `permisos_del_rol()` | `(rol: Rol) -> ResultadoElap<Vec<Permiso>>` | Lista de permisos |

**Ejemplo**:

```rust
let rbac = GestorRbac::nuevo();
rbac.validar_permiso(Rol::Admin, Permiso::CambiarConfiguracion)?;
// Ok - Admin tiene todos los permisos
```

**Ubicación**: `security/rbac.rs`  
**Tests**: 8 tests (roles, permisos, validación)

### 3.4 Struct RegistroAuditoria

Registro inmutable de una acción auditada.

**Campos**:

```rust
pub struct RegistroAuditoria {
    pub usuario_id: String,    // Quién
    pub accion: String,        // Qué (ej: "ejecutar_herramienta")
    pub recurso: String,       // Sobre qué
    pub resultado: String,     // "exitoso" o "denegado"
    pub timestamp: u64,        // Cuándo (Unix timestamp)
}
```

**Métodos**:

| Método | Firma | Retorna |
|--------|-------|---------|
| `nuevo()` | `(usuario_id, accion, recurso, resultado) -> Self` | RegistroAuditoria |

**Ejemplo**:

```rust
let registro = RegistroAuditoria::nuevo(
    "usuario_123".to_string(),
    "cambiar_config".to_string(),
    "config.yaml".to_string(),
    "denegado".to_string(),
);
println!("{}", registro.timestamp); // Unix seconds
```

**Ubicación**: `security/auditor.rs`  
**Tests**: 3 tests (creación, timestamp, resultado)

### 3.5 Struct AuditorRbac

Gestor de registros auditados con almacenamiento thread-safe.

**Métodos**:

| Método | Firma | Retorna |
|--------|-------|---------|
| `nuevo()` | `() -> Self` | AuditorRbac inicializado |
| `registrar_acceso()` | `(&self, usuario_id: &str, accion: &str, recurso: &str)` | () |
| `registrar_intento_fallido()` | `(&self, usuario_id: &str, accion: &str, recurso: &str)` | () |
| `obtener_registros()` | `(&self) -> Vec<RegistroAuditoria>` | Clone de registros |

**Ejemplo**:

```rust
let auditor = AuditorRbac::nuevo();
auditor.registrar_acceso("admin", "leer_archivo", "datos.txt");
auditor.registrar_intento_fallido("usuario", "cambiar_config", "config.yaml");

let registros = auditor.obtener_registros();
for reg in registros {
    println!("{} - {} - {}", reg.usuario_id, reg.accion, reg.resultado);
}
```

**Ubicación**: `security/auditor.rs`  
**Tests**: 4 tests (creación, registro, múltiples registros)

---

## 4. Integración con MotorCentral

**MotorCentral** inicializa automáticamente ambos gestores:

```rust
pub struct MotorCentral {
    config: Configuracion,
    gestor_rbac: GestorRbac,      // ← Inicializado en new()
    auditor: AuditorRbac,         // ← Inicializado en new()
}
```

**Acceso**:

```rust
let motor = MotorCentral::nuevo(config);
motor.rbac().validar_permiso(Rol::Admin, Permiso::LeerArchivos)?;
motor.auditor().registrar_acceso("admin", "inicio", "motor");
```

---

## 5. Patrón de uso recomendado

```rust
pub async fn ejecutar_herramienta(
    motor: &MotorCentral,
    usuario_id: &str,
    herramienta: &str,
) -> ResultadoElap<String> {
    // 1. Validar permiso
    motor.rbac()
        .validar_permiso(Rol::Usuario, Permiso::EjecutarHerramientas)
        .map_err(|_| {
            motor.auditor().registrar_intento_fallido(
                usuario_id,
                "ejecutar_herramienta",
                herramienta,
            );
            ElapError::Validacion("Permiso denegado".to_string())
        })?;

    // 2. Auditar acceso exitoso
    motor.auditor().registrar_acceso(
        usuario_id,
        "ejecutar_herramienta",
        herramienta,
    );

    // 3. Ejecutar operación
    Ok(format!("Ejecutada: {}", herramienta))
}
```

---

## 6. Testing

**Total: 26 tests**
- 5 tests de Rol
- 6 tests de Permiso
- 8 tests de GestorRbac
- 3 tests de RegistroAuditoria
- 4 tests de AuditorRbac

**Cobertura**: >85%

```bash
cargo test -p elap-core security::
```

---

## 7. Limitaciones y futuro

**Actual (Paso 6)**:
- RBAC basado en roles estáticos
- Sin permisos personalizados por usuario
- Sin expiración de tokens
- Sin bases de datos de auditoría (solo en memoria)

**Fase 2**:
- Persistencia de auditoría en SQLite
- Permisos dinámicos por usuario
- Sistema de tokens con expiración
- API REST para consultas de auditoría

---

**Última actualización**: 2026-08-05  
**Próximo módulo**: Integración con Plugin System (Fase 1-Paso 7)
