# Libro 04: Plugin Runtime — Capítulo 1 — Introducción

**Tema central**: Cómo permitir que terceros extiendan la plataforma sin romper nada.

**Objetivo pedagógico**: Entender por qué los plugins necesitan sandbox y cómo se controla su acceso.

---

## 🎯 La pregunta que responde este capítulo

> "¿Cómo le permito a un desarrollador tercero crear una extensión para mi sistema sin que pueda crashear toda la plataforma?"

**Respuesta**: Plugins = extensibilidad + sandbox = máxima seguridad

---

## 📖 Analogía: La tienda con empleados contratistas

Imagina una tienda departamental:

```
┌─────────────────────────────────────────┐
│        Tienda Central (ELAP)            │
│                                         │
│  - Caja registradora (datos sensibles)  │
│  - Bóveda (archivos del sistema)        │
│  - Almacén (recursos)                   │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  Departamento de Óptica (Plugin)│    │
│  │  ┌──────────────────────────┐   │    │
│  │  │ Empleado Contratista     │   │    │
│  │  │ (Plugin ejecutándose)    │   │    │
│  │  │                          │   │    │
│  │  │ ✗ No puede tocar caja    │   │    │
│  │  │ ✓ Puede vender lentes    │   │    │
│  │  │ ✗ No puede acceder red   │   │    │
│  │  │ ✓ Puede acceder archivos │   │    │
│  │  │   del departamento       │   │    │
│  │  └──────────────────────────┘   │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

**Plugins = empleados contratistas en sandbox**

---

## 🏗️ Estructura del Sistema de Plugins

```
┌─────────────────────────────────────────┐
│         Plugin Runtime                  │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │  Plugin Trait (contrato)          │  │
│  │  ├─ nombre()                      │  │
│  │  ├─ version()                     │  │
│  │  ├─ inicializar()                 │  │
│  │  ├─ ejecutar(comando, args)       │  │
│  │  └─ finalizar()                   │  │
│  └───────────────────────────────────┘  │
│           ↑                              │
│           │ Implementa                   │
│           │                              │
│  ┌───────────────────────────────────┐  │
│  │  Plugin Dinámico (.so/.dll)       │  │
│  │  "plugin_ventas v1.2.0"           │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │  Plugin Loader                    │  │
│  │  ├─ Descubrir plugins             │  │
│  │  ├─ Validar metadatos             │  │
│  │  ├─ Calcular hash SHA256          │  │
│  │  └─ Cargar por nombre             │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │  Plugin Registry                  │  │
│  │  ├─ HashMap<nombre, metadatos>    │  │
│  │  ├─ Registrar/desregistrar        │  │
│  │  ├─ Obtener, listar               │  │
│  │  └─ Buscar por autor/permiso      │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │  Plugin Sandbox                   │  │
│  │  ├─ Límite de memoria: 512 MB     │  │
│  │  ├─ Timeout: 30 segundos          │  │
│  │  ├─ Validación de permisos        │  │
│  │  └─ Políticas restrictiva/permisiva│  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 🔌 Componentes clave

### 1. Plugin Trait — El contrato

Todo plugin debe implementar 6 métodos:

```rust
pub trait Plugin: Send + Sync {
    fn nombre(&self) -> &str;           // "plugin_ventas"
    fn version(&self) -> &str;          // "1.2.0"
    fn descripcion(&self) -> &str;      // "Gestiona ventas"
    fn inicializar(&mut self) -> Result<(), String>;  // Setup
    fn ejecutar(&self, cmd: &str, args: &[String]) -> Result<String, String>;
    fn finalizar(&mut self) -> Result<(), String>;    // Cleanup
}
```

**¿Qué significa?**
- El plugin DEBE implementar estos métodos
- Sin ellos, no compila
- Es como un contrato laboral: "Si trabajas aquí, tienes que poder hacer X, Y, Z"

### 2. Plugin Metadata — La hoja de vida

```json
{
  "nombre": "plugin_ventas",
  "version": "1.2.0",
  "autor": "developer@empresa.com",
  "descripcion": "Gestiona ventas y reportes",
  "ruta_binario": "./plugins/plugin_ventas.so",
  "punto_entrada": "plugin_init",
  "permisos": ["AccesoArchivos", "AccesoRed"],
  "hash_verificacion": "a1b2c3d4..."
}
```

Información del plugin:
- Quién lo hizo
- Qué versión es
- Dónde está
- Qué permisos necesita
- Firma (hash)

### 3. Plugin Loader — El gerente de recursos

```
¿Existe el archivo?  ✓
¿Metadatos válidos?  ✓
¿Hash correcto?      ✓
→ Plugin listo para registrar
```

Tareas:
- Buscar plugins en el directorio
- Validar que tienen todo lo necesario
- Calcular hash SHA256 (verificación de integridad)
- Cargar por nombre

### 4. Plugin Registry — El registro central

HashMap thread-safe:

```
"plugin_ventas"    → PluginMetadata { ... }
"plugin_reportes"  → PluginMetadata { ... }
"plugin_soporte"   → PluginMetadata { ... }
```

Búsquedas rápidas:
- Listar todos los plugins
- Obtener uno por nombre
- Buscar por autor: "¿Quién hizo plugins?"
- Buscar por permiso: "¿Quién necesita acceso a red?"

### 5. Plugin Sandbox — El guardia de seguridad

```
Usuario: "Quiero ejecutar plugin_ventas"
Sandbox: "¿Tienes permiso AccesoRed?"
Usuario: "Sí"
Sandbox: "OK, pero:
  - Máximo 512 MB de memoria
  - Máximo 30 segundos de ejecución
  - Nada de procesos del SO
  Ahora adelante"
```

Configuraciones:

| Aspecto | Restrictiva | Defecto | Permisiva |
|---------|------------|---------|-----------|
| Memoria | 256 MB | 512 MB | 2048 MB |
| Timeout | 10s | 30s | 120s |
| Red | ✗ | ✗ | ✓ |
| Archivos | ✗ | ✗ | ✓ |
| Procesos | ✗ | ✗ | ✓ |

---

## 💬 Conversación real: Cargar y ejecutar plugin

```
1. Admin: "Descubre qué plugins tenemos"
   Loader: Escanea directorio /plugins
   Loader: Encuentra plugin_ventas.so
   
2. Admin: "Valida el plugin"
   Loader: Verifica metadatos
   Loader: Calcula hash
   Loader: OK ✅
   
3. Admin: "Regístrame ese plugin"
   Registry: Almacena en HashMap
   Registry: Ahora "plugin_ventas" está disponible
   
4. Usuario: "Ejecuta plugin_ventas con comando 'generar_reporte'"
   Sandbox: ¿Tienes permisos? (Consulta RBAC)
   RBAC: Sí, es Admin
   
5. Sandbox: ¿Permiso AccesoArchivos? Necesita para guardar reporte
   Metadata: Sí, tiene ese permiso
   
6. Sandbox: Ejecuta con límites
   - Máximo 512 MB RAM
   - Máximo 30 segundos
   
7. Plugin: Genera reporte exitosamente
   
8. Sandbox: Plugin terminó en 2.3 segundos, 45 MB RAM
   Auditor: Registra: usuario_admin, acción_ejecutar_plugin, recurso_plugin_ventas, resultado_éxito
   
9. Usuario: Recibe reporte ✓
```

**Todo ocurre de forma segura**

---

## 🔐 Seguridad en capas

```
┌────────────────────────────────┐
│   Capa 1: Validación           │
│   - Metadatos correctos?       │
│   - Hash correcto?             │
│   - Punto entrada válido?      │
└────────────────────────────────┘
            ↓
┌────────────────────────────────┐
│   Capa 2: RBAC                 │
│   - ¿Usuario tiene permiso?    │
│   - ¿Rol autorizado?           │
└────────────────────────────────┘
            ↓
┌────────────────────────────────┐
│   Capa 3: Permisos del plugin  │
│   - ¿Plugin tiene AccesoRed?   │
│   - ¿Plugin puede archivos?    │
└────────────────────────────────┘
            ↓
┌────────────────────────────────┐
│   Capa 4: Sandbox              │
│   - Límite 512 MB memoria      │
│   - Timeout 30 segundos        │
│   - Sin procesos del SO        │
└────────────────────────────────┘
            ↓
        Plugin ejecuta
        (de forma segura)
```

---

## 🎓 Lecciones clave

1. **Extensibilidad**: Los plugins permiten que terceros agreguen funcionalidad
2. **Seguridad en capas**: RBAC + permisos del plugin + sandbox
3. **Validación**: Metadatos, hashes, punto de entrada
4. **Aislamiento**: Cada plugin tiene límites claros
5. **Auditoría**: Se registra quién ejecutó qué

---

## 📚 Conexión con libros anteriores

```
Libro 01: Introducción
  ↓
Libro 02: Core Runtime (Motor, Scheduler, RBAC)
  ↓
Libro 03: Desktop (IPC, UI components)
  ↓
Libro 04: Plugin Runtime ← TÚ ESTÁS AQUÍ
  ├─ Plugin trait (interfaz)
  ├─ Plugin loader (carga)
  ├─ Plugin registry (gestión)
  └─ Plugin sandbox (seguridad)
  
Libro 05+: Tool Engine, Model Manager, etc.
```

El sistema de plugins es la base para extender ELAP de forma segura.

---

## 🔜 Próximo: Capítulo 2

**"Crear tu primer plugin"**

Construiremos un plugin de ejemplo:
1. Implementar Plugin trait
2. Definir metadatos
3. Compilar como .so
4. Registrarlo
5. Ejecutarlo en sandbox

---

**Capítulo siguiente**: 02-primer-plugin.md (Coming soon)
