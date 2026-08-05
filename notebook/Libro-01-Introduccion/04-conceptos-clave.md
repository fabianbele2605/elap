# Libro 01: Introducción — Capítulo 4 — Conceptos clave

**Tema**: Las 4 ideas fundamentales de ELAP.

---

## 1️⃣ Agentes vs Tareas

**Tarea**: Una acción única y aislada.

```
Ejemplos:
- Leer archivo /home/usuario/documento.txt
- Llamar API GET https://api.ejemplo.com/datos
- Ejecutar SQL: SELECT * FROM usuarios
- Calcular promedio de números: [1, 2, 3, 4, 5]
```

**Agente**: Un proceso inteligente que puede hacer múltiples tareas.

```
Ejemplo: Tu asistente personal
┌─────────────────────────────────┐
│ Agente: "Analista de Ventas"    │
├─────────────────────────────────┤
│ Tarea 1: Leer datos de clientes │
│ Tarea 2: Analizar tendencias    │
│ Tarea 3: Generar reporte PDF    │
│ Tarea 4: Enviar email reporte   │
└─────────────────────────────────┘
```

**En ELAP**:
- Tareas = ejecutadas por Python AI Runtime
- Agentes = redes de tareas coordinadas por LangGraph
- Scheduler = Tokio async (programa tareas en Rust)

---

## 2️⃣ Permisos y Roles

**Rol**: Descripción de quién eres.

```
Ejemplo:
- Administrador: puede hacer todo
- Analista: puede leer datos, generar reportes
- Auditor: solo puede leer auditoría
```

**Permiso**: Lo que puedes hacer.

```
Ejemplo:
- LeerArchivos: acceso a read_file
- EscribirBaseDatos: acceso a sql_write
- EjecutarSistema: acceso a system_cmd
- AuditoriaCompleta: acceso a audit_logs
```

**Flujo en ELAP**:

```
Usuario quiere ejecutar herramienta
        ↓
¿Usuario tiene permiso?
        ↓
┌─ SÍ ──────────────────┐  ┌─ NO ───────────────────┐
│ ✅ Ejecutar          │  │ ❌ Error: Denegado      │
│ 📝 Registrar en log  │  │ 📝 Registrar intento    │
└──────────────────────┘  └─────────────────────────┘
```

**Roles predefinidos en ELAP**:

| Rol | Permisos | Caso de uso |
|-----|----------|------------|
| **admin** | Todos | DBA, DevOps |
| **analyst** | Leer datos, generar reportes | Business intelligence |
| **developer** | Código, plugins, tests | Desarrollo |
| **auditor** | Leer auditoría, reportes | Compliance |

---

## 3️⃣ Plugins y Herramientas

**Plugin**: Código que extiende ELAP.

```
Plugin = Tarea + Metadata + Sandbox

Estructura:
┌─ Plugin: "ConectarSQL" ────────────────┐
│                                        │
│ Metadata:                              │
│  - nombre: "conectar_sql"              │
│  - versión: "1.2.0"                    │
│  - permisos: [EscribirBD, LeerBD]      │
│                                        │
│ Código:                                │
│  fn ejecutar(conexión, query) {        │
│      db.execute(query)                 │
│  }                                     │
│                                        │
│ Sandbox:                               │
│  - Solo acceso a BD permitida          │
│  - Timeout: 30 segundos                │
│  - Memoria máxima: 512MB               │
│  - No acceso a archivos                │
└────────────────────────────────────────┘
```

**Herramienta**: Plugin + Ejecutable.

```
Herramientas en ELAP:

1. Archivo
   └─ leer_archivo(), escribir_archivo()

2. HTTP
   └─ get(), post(), put(), delete()

3. Base de Datos
   └─ conectar(), ejecutar_query()

4. SSH
   └─ ejecutar_remoto(), copiar_archivos()

5. Sistema
   └─ sistema_info(), ejecutar_comando()
```

---

## 4️⃣ Sandboxing

**Sin Sandbox** ❌

```
Usuario con malintención ejecuta:
  sistema_cmd("rm -rf /")
        ↓
❌ DESASTRE: ¡Se borra todo el disco!
```

**Con Sandbox en ELAP** ✅

```
Usuario intenta ejecutar:
  sistema_cmd("rm -rf /")
        ↓
Sandbox verifica:
  1. ¿Usuario tiene permiso? NO
  2. ¿Comando es permitido? NO
  3. ¿Path está en whitelist? NO
        ↓
✅ Se bloquea. Registra intento en auditoría.
```

**Mecanismos de sandbox en ELAP**:

```
1. Permission checks (RBAC)
   └─ ¿Rol tiene permiso?

2. Path whitelisting
   └─ Solo /data/, /reports/, /temp/

3. Command whitelisting
   └─ Solo comandos permitidos

4. Resource limits
   └─ Max 30 segundos
   └─ Max 512MB RAM
   └─ Max 10 archivos simultáneos

5. Process isolation
   └─ Ejecutar en contenedor (opcional)
```

---

## 📊 Tabla de relaciones

```
Usuario
  ├─ Tiene: Rol (1)
  ├─ Tiene: Permisos (muchos, via Rol)
  └─ Ejecuta: Tareas (muchas)

Rol
  ├─ Incluye: Permisos (muchos)
  └─ Pertenecen a: Usuarios (muchos)

Permiso
  ├─ Controla: Herramientas (muchas)
  └─ Pertenecen a: Roles (muchos)

Herramienta
  ├─ Requiere: Permisos (muchos)
  ├─ Es: Plugin
  └─ Ejecuta: Tarea
```

---

## 🎯 Ejemplo completo

```
Caso: Usuario "Ana" quiere analizar datos de ventas

┌─ 1. Usuario ─────────────────────────┐
│ Ana                                  │
│ Rol: analyst                         │
│ Permisos: [LeerDatos, GenerarReporte]
└──────────────────────────────────────┘
              ↓
┌─ 2. Intención ────────────────────────┐
│ "Analizar ventas últimos 30 días"    │
└──────────────────────────────────────┘
              ↓
┌─ 3. Tareas (Agente) ──────────────────┐
│ Tarea 1: Leer datos SQL              │
│   Requiere: Herramienta [sql_read]   │
│   Requiere permiso: [LeerDatos]      │
│   ✅ Ana tiene                        │
│                                      │
│ Tarea 2: Generar gráfico             │
│   Requiere: Herramienta [chart_gen]  │
│   Requiere permiso: [GenerarReporte] │
│   ✅ Ana tiene                        │
│                                      │
│ Tarea 3: Guardar PDF                 │
│   Requiere: Herramienta [file_write] │
│   Requiere permiso: [EscribirArchivo]│
│   ❌ Ana NO tiene                     │
│   → Tarea bloqueada                   │
└──────────────────────────────────────┘
              ↓
┌─ 4. Resultado ────────────────────────┐
│ Éxito parcial:                       │
│  ✅ Datos leídos                      │
│  ✅ Gráfico generado                  │
│  ❌ No guardar en PDF                 │
│  → Mostrar en pantalla en su lugar   │
└──────────────────────────────────────┘
```

---

## 🔜 Siguiente: Capítulo 5

**"Cómo Comenzar"**

Aprenderás:
- Requisitos de hardware
- Instalación paso a paso
- Primera ejecución
- Primeros comandos

---

**Capítulo siguiente**: [05-como-comenzar.md](05-como-comenzar.md)
