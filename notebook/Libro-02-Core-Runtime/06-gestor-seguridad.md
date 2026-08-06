# Capítulo 6 — Gestor de Seguridad (RBAC)

**Tema central**: Cómo controlar qué puede hacer cada usuario sin levantar el sistema.

**Objetivo pedagógico**: Entender por qué las restricciones de acceso son críticas para un sistema empresarial.

---

## 🎯 La pregunta que responde este capítulo

> "¿Cómo prevenimos que el pasante borre accidentalmente toda la base de datos?"

**Respuesta**: Control de acceso basado en roles (RBAC) + auditoría de cada acción.

---

## 📖 Analogía: Centro de datos con niveles de seguridad

Imagina un edificio de oficinas:

```
┌─────────────────────────────────────┐
│   ELAP = Centro de Datos            │
├─────────────────────────────────────┤
│                                     │
│  Piso 1: INVITADO (solo lectura)   │
│  ├─ Puede: Leer archivos           │
│  └─ No puede: Modificar nada       │
│                                     │
│  Piso 2: USUARIO (operación normal) │
│  ├─ Puede: Leer y escribir archivos│
│  ├─ Puede: Ejecutar procesos       │
│  ├─ Puede: Ejecutar herramientas   │
│  └─ No puede: Cambiar configuración│
│                                     │
│  Piso 3: ADMIN (control total)     │
│  ├─ Puede: TODO                    │
│  └─ Responsabilidad: MÁXIMA        │
│                                     │
│  Piso 4: AGENTE (ejecución limitada)
│  ├─ Puede: Leer archivos           │
│  ├─ Puede: Ejecutar herramientas   │
│  └─ No puede: Escribir, cambiar cfg│
│                                     │
└─────────────────────────────────────┘
```

**¿Quién sube a cada piso?** Tu rol determina qué pisos puedes visitar.

---

## 🔧 ¿Qué es RBAC?

**RBAC = Role-Based Access Control**

En lugar de decir:
```
✅ "usuario_123 puede leer archivos"
✅ "usuario_456 puede leer archivos"
✅ "usuario_789 puede leer archivos"
```

Decimos:
```
✅ "El rol INVITADO puede leer archivos"
✅ Los usuarios se asignan a roles
✅ Todo usuario INVITADO hereda esos permisos automáticamente
```

**Ventaja**: Cambias un permiso y afecta a 1000 usuarios instantáneamente.

---

## 👥 Los 4 Roles en ELAP

### 1. ADMIN (Administrador)
- **¿Quién?**: Dueño de ELAP, Equipo DevOps
- **Permisos**: ✅ TODO
- **Peligro**: Si se compromete, el sistema es vulnerable
- **Regla**: Usa con contraseña fuerte, 2FA

### 2. USUARIO (Usuario normal)
- **¿Quién?**: Empleados que usan ELAP diariamente
- **Permisos**: 
  - ✅ Leer archivos
  - ✅ Escribir archivos
  - ✅ Ejecutar procesos
  - ✅ Ejecutar herramientas
  - ❌ Cambiar configuración
- **Protección**: No pueden romper configuraciones críticas

### 3. INVITADO (Visitante)
- **¿Quién?**: Clientes, consultores, auditores
- **Permisos**:
  - ✅ Leer archivos
  - ❌ TODO lo demás
- **Protección**: Máxima. Solo observan.

### 4. AGENTE (Agente de IA)
- **¿Quién?**: Procesos automatizados, bots, LLMs
- **Permisos**:
  - ✅ Leer archivos
  - ✅ Ejecutar herramientas
  - ❌ Escribir directamente, cambiar config
- **Protección**: El agente es una "caja de arena" controlada

---

## 🎫 Los 5 Permisos

Cada permiso responde: **"¿Qué quiero hacer?"**

```rust
LeerArchivos          → Abrir, consultar datos
EscribirArchivos      → Modificar, crear, eliminar datos
EjecutarProcesos      → Lanzar tareas del SO
EjecutarHerramientas  → Usar herramientas registradas
CambiarConfiguracion  → Editar settings críticos
```

**La tabla de verdad**:

| Rol | Leer | Escribir | Procesos | Herramientas | Config |
|-----|------|----------|----------|--------------|--------|
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ |
| Usuario | ✅ | ✅ | ✅ | ✅ | ❌ |
| Invitado | ✅ | ❌ | ❌ | ❌ | ❌ |
| Agente | ✅ | ❌ | ❌ | ✅ | ❌ |

---

## 🛡️ Cómo funciona en código

### Paso 1: Crear un GestorRbac

```rust
let rbac = GestorRbac::nuevo();  // Se inicializa con tabla anterior
```

### Paso 2: Validar permiso

```rust
// ¿Puede este rol ejecutar herramientas?
let resultado = rbac.validar_permiso(Rol::Usuario, Permiso::EjecutarHerramientas);

match resultado {
    Ok(()) => println!("✅ Permiso concedido"),
    Err(e) => println!("❌ {}", e),  // "Rol usuario no tiene permiso..."
}
```

### Paso 3: Usar el operador ?

```rust
pub fn ejecutar_herramienta(usuario_rol: Rol, herramienta: &str) -> ResultadoElap<()> {
    // Si no tiene permiso, retorna error inmediatamente
    self.rbac.validar_permiso(usuario_rol, Permiso::EjecutarHerramientas)?;
    
    // Si llegamos aquí, tenía permiso
    println!("Ejecutando: {}", herramienta);
    Ok(())
}
```

---

## 📋 Sistema de Auditoría

### ¿Qué es auditoría?

**Auditoría = Registro de quién hizo qué y cuándo**

Cada vez que alguien intenta una acción, registramos:
- **Quién**: usuario_id
- **Qué**: acción (ej: "cambiar_config")
- **Dónde**: recurso (ej: "config.yaml")
- **Resultado**: "exitoso" o "denegado"
- **Cuándo**: timestamp Unix

### Ejemplo en la vida real:

```
10:30:45 admin    cambiar_config    config.yaml    exitoso
10:31:12 usuario  cambiar_config    config.yaml    denegado
10:31:15 usuario  ejecutar_herramienta sql.py     exitoso
10:32:03 invitado ejecutar_herramienta sql.py     denegado
```

### Cómo se usa:

```rust
let auditor = AuditorRbac::nuevo();

// Acción exitosa
auditor.registrar_acceso("admin", "cambiar_config", "config.yaml");

// Intento denegado
auditor.registrar_intento_fallido("usuario", "cambiar_config", "config.yaml");

// Consultamos el historial
let registros = auditor.obtener_registros();
for reg in registros {
    println!("{} - {} - {}", reg.usuario_id, reg.accion, reg.resultado);
}
```

---

## 🔍 Caso de uso: Usuario intenta cambiar configuración

```
Usuario (rol: Usuario) intenta: CambiarConfiguracion

┌─────────────────────────────────────┐
│ Motor Central                       │
│                                     │
│ motor.rbac().validar_permiso(       │
│   Rol::Usuario,                     │
│   Permiso::CambiarConfiguracion     │
│ )?                                  │
│      ↓                              │
│ Tabla RBAC:                         │
│   Usuario → [Leer, Escribir, ...]   │
│   NO contiene: CambiarConfiguracion │
│      ↓                              │
│ Err(Validacion("Permiso denegado")) │
│      ↓                              │
│ motor.auditor()                     │
│   .registrar_intento_fallido(...)   │
│      ↓                              │
│ Log: usuario - cambiar_config      │
│      config.yaml - denegado        │
└─────────────────────────────────────┘
```

**Resultado**: Usuario rechazado + evento auditado = seguridad + visibilidad

---

## 💡 Preguntas frecuentes

### P: ¿Qué pasa si un usuario necesita un permiso que no tiene?

**R**: Se lo pide a un ADMIN. El ADMIN puede:
1. Darle un rol más alto (temporal)
2. O crear un rol personalizado (Fase 2)

### P: ¿Se guardan los registros de auditoría?

**R**: Actualmente en memoria (se pierden al reiniciar). Fase 2 agregará SQLite.

### P: ¿Puedo tener múltiples roles?

**R**: Actualmente no (un usuario = un rol). Fase 2 lo permitirá.

### P: ¿Qué pasa si alguien roba la contraseña del ADMIN?

**R**:
1. El atacante tiene TODO acceso
2. **Todos** sus intentos quedan auditados
3. Se puede revocar la contraseña inmediatamente
4. Auditoría + alertas son la defensa

### P: ¿Cuánta performance cuesta validar permisos?

**R**: Muy poco. HashMap lookup = O(1). Casi instantáneo.

---

## 🎓 Lecciones clave

1. **RBAC es prevención**: Evita errores accidentales (no ataca maliciosos)
2. **Auditoría es detective**: Registra TODOS los intentos para investigar
3. **Capas de defensa**: RBAC + auditoría + alertas = seguridad real
4. **Principio de menor privilegio**: Cada rol tiene SOLO lo que necesita
5. **Confianza = transparencia**: Todo está registrado, nada es oculto

---

## 📚 Conexión con capítulos anteriores

```
Cap 1: Introducción
Cap 2: Planificador       → Ejecuta tareas
Cap 3: Procesos           → Del SO
Cap 4: Configuración      → Parámetros
Cap 5: Errores            → Recuperación
Cap 6: Seguridad ← AQUÍ   → Quién puede hacer qué
         ↓
         Todos se integran en MotorCentral
```

**Integración real**:
```rust
pub async fn iniciar(&self) -> ResultadoElap<()> {
    inicializar_logging()?;      // Cap 4
    self.config.validar()?;       // Cap 5
    
    // Si llegamos aquí sin errores, el sistema está seguro
    // ✅ Logging configurado
    // ✅ Config validada
    // ✅ RBAC listo
    // ✅ Auditoría lista
    Ok(())
}
```

---

## 🔜 Próximo: Fase 1 Paso 7

El siguiente paso es **Gestor de Plugins** - permitir que código de terceros se ejecute **dentro de la jaula de RBAC**.

Los plugins verán:
```
"¿Puedo escribir archivos?"
↓ RBAC consulta
"¿Qué rol tiene el plugin?"
↓
Sí o no, basado en rol
```

---

**Capítulo siguiente**: 07-gestor-plugins.md (Coming soon)
