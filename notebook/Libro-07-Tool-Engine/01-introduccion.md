# Libro 07: Tool Engine — Capítulo 1 — Introducción

**Tema**: Por qué necesitas herramientas y cómo funcionan.

---

## 🎯 ¿Qué es una herramienta?

Una **herramienta** (tool) es una función especializada que hace una cosa bien.

**Analógía**: Un martillo

```
┌─ MARTILLO ────────────────┐
│ Propósito: Clavar clavos  │
│ Entrada: {clavo, tablas}  │
│ Salida: Clavo clavado     │
│ Restricción: No lo uses   │
│            en vidrio      │
└───────────────────────────┘
```

En ELAP:

```
┌─ HERRAMIENTA: leer_archivo ──────────┐
│ Propósito: Leer contenido             │
│ Entrada: {ruta: "/data/file.txt"}    │
│ Salida: {"contenido": "...", ...}    │
│ Restricción: Solo /data/, /reports/  │
└──────────────────────────────────────┘
```

---

## 🔧 Las 5 herramientas de ELAP

### 1. FileTool — Leer y escribir archivos

```
Operaciones:
├─ leer: Obtener contenido
├─ escribir: Crear/modificar
└─ listar: Ver directorio

Ejemplo:
{
  "herramienta": "archivo",
  "operacion": "leer",
  "ruta": "/data/usuarios.json"
}

Respuesta:
{
  "contenido": "[{id:1, nombre:Juan}, ...]",
  "bytes": 4096,
  "timestamp": "2026-08-05T14:30:00Z"
}
```

### 2. HttpTool — Hablar con APIs externas

```
Operaciones:
├─ GET: Obtener datos
├─ POST: Enviar datos
├─ PUT: Actualizar
└─ DELETE: Eliminar

Ejemplo:
{
  "herramienta": "http",
  "metodo": "GET",
  "url": "https://api.ejemplo.com/productos"
}

Respuesta:
{
  "estado": 200,
  "cuerpo": "[{id:1, nombre:Producto A}, ...]",
  "headers": {"content-type": "application/json"}
}
```

### 3. SqlTool — Consultar bases de datos

```
Operaciones:
├─ select: Leer datos
├─ insert: Agregar datos
└─ update: Modificar datos

Ejemplo:
{
  "herramienta": "sql",
  "operacion": "select",
  "query": "SELECT * FROM pedidos WHERE estado='pendiente'"
}

Respuesta:
{
  "filas": [
    {id:1, cliente:"Juan", total:500},
    {id:2, cliente:"Ana", total:750}
  ],
  "total_filas": 2
}
```

### 4. SshTool — Ejecutar en servidores remotos

```
Operaciones:
├─ ejecutar: Correr comando
└─ copiar: Transferir archivo

Ejemplo:
{
  "herramienta": "ssh",
  "operacion": "ejecutar",
  "host": "servidor_produccion",
  "comando": "df -h"
}

Respuesta:
{
  "salida": "Filesystem  Size  Used Avail Use% Mounted on...",
  "estado": 0
}
```

### 5. SystemTool — Información del servidor

```
Operaciones:
├─ info: SO y hardware
├─ recursos: CPU, memoria, disco
└─ variables: Variables de entorno

Ejemplo:
{
  "herramienta": "sistema",
  "operacion": "recursos"
}

Respuesta:
{
  "cpu_porcentaje": 45.2,
  "memoria_usada_gb": 4.5,
  "disco_usado_gb": 250,
  "uptime_segundos": 86400
}
```

---

## 🔐 ¿Por qué sandboxing?

Sin sandboxing (PELIGROSO):

```
Usuario: "Ejecuta: rm -rf /"
Sistema: "OK" ← ¡¡Desastre!!
```

Con sandboxing (SEGURO):

```
Usuario: "Ejecuta: rm -rf /"
Sistema: "Validando..."
  ✓ ¿Tienes permiso? SÍ
  ✓ ¿Comando permitido? NO ← Bloqueado
Resultado: Error "Comando bloqueado"
```

**Niveles de seguridad**:

```
1. RBAC (Role-Based Access Control)
   └─ ¿Qué rol eres? (admin, analyst, auditor)

2. Permission Checking
   └─ ¿Tienes el permiso específico?

3. Path Whitelisting
   └─ ¿Ruta en lista permitida? (/data, /reports, /tmp)

4. Command Blacklisting
   └─ ¿Comando no está bloqueado? (no rm -rf, dd, mkfs)

5. Resource Limits
   └─ ¿No excedes 512MB de parámetros?
   └─ ¿Ejecutaste en <30 segundos?
```

---

## 💡 Casos de uso reales

### Caso 1: Dashboard de ventas

```
Agente: "Quiero analizar ventas del mes"

Flujo:
1. SqlTool: SELECT * FROM ventas WHERE mes=agosto
2. FileTool: Guardar en /reports/ventas_agosto.json
3. HttpTool: POST a https://dashboard.ejemplo.com/reportes
4. SystemTool: Verificar espacio en disco

Resultado: ✅ Reporte enviado al dashboard
```

### Caso 2: Backup automático

```
Agente: "Hacer backup de BD"

Flujo:
1. SystemTool: recursos → 50% disco libre ✓
2. SqlTool: SELECT * FROM usuarios → 100K registros
3. FileTool: escribir /backups/usuarios_20260805.json
4. SshTool: copiar a servidor_backup

Resultado: ✅ Backup completado
```

### Caso 3: Monitoreo de sistema

```
Agente: "Revisar salud del sistema"

Flujo:
1. SystemTool: info → Linux, 8 cores
2. SystemTool: recursos → CPU 85% ⚠️
3. SshTool: ejecutar "ps aux | top -b"
4. FileTool: escribir /reports/alerta_cpu.txt

Resultado: ⚠️ Alerta: CPU alta, revisar procesos
```

---

## 📊 Cómo fluyen los datos

```
Usuario → Agente → Herramientas → Resultado

Ejemplo: "¿Cuántos usuarios activos hay?"

Paso 1: Usuario
  "¿Cuántos usuarios activos?"

Paso 2: Agente (LangGraph)
  Entiende que necesita datos
  Planifica: Usar SqlTool

Paso 3: Herramienta
  SqlTool ejecuta: 
  SELECT COUNT(*) FROM usuarios WHERE estado='activo'
  
Paso 4: Resultado
  {"count": 1523, "timestamp": "2026-08-05T14:30:00Z"}

Paso 5: Agente interpreta
  "Hay 1,523 usuarios activos"

Paso 6: Usuario ve respuesta
  "Hay 1,523 usuarios activos"
```

---

## ⚡ Validación en 5 pasos

```
Usuario quiere ejecutar una herramienta
         ↓
1️⃣ RBAC: ¿Tienes rol que permite esto?
         ↓
2️⃣ Permiso: ¿Tu rol tiene el permiso específico?
         ↓
3️⃣ Parámetros: ¿No envías >512MB de datos?
         ↓
4️⃣ Ruta: ¿Path está en whitelist?
         ↓
5️⃣ Comando: ¿Comando no está bloqueado?
         ↓
✅ SÍ a todo → Ejecutar herramienta
❌ NO en cualquiera → Bloquear + registrar en auditoría
```

---

## 🎓 Conceptos clave

| Concepto | Significado | Ejemplo |
|----------|-------------|---------|
| **Tool** | Función especializada | FileTool, HttpTool |
| **Trait** | Interfaz que todo tool debe cumplir | `fn ejecutar()` |
| **Registry** | Registro de herramientas disponibles | "¿Qué tools hay?" |
| **Sandbox** | Límites de seguridad | Timeout 30s, memoria 512MB |
| **RBAC** | Control de permisos por rol | admin vs analyst |
| **Ejecutor** | Motor que corre la herramienta | EjecutorHerramientas |

---

## 🚀 Arquitectura en 30 segundos

```
┌─────────────────────────────────────────────┐
│ EjecutorHerramientas                        │
│  1. Validar permisos (RBAC)                │
│  2. Validar sandbox (límites)              │
│  3. Ejecutar tool.ejecutar(params)         │
│  4. Medir tiempo                           │
│  5. Retornar resultado                     │
└─────────────────────────────────────────────┘
           ↑                        ↓
┌──────────────────┐        ┌──────────────────┐
│  ContextoUser    │        │ ResultadoEjecución
│  - usuario       │        │ - exitoso        │
│  - permisos      │        │ - datos          │
│  - sandbox       │        │ - error          │
└──────────────────┘        │ - duracion_ms    │
                            └──────────────────┘
           ↑
       ┌───────────┐
       │ 5 Tools   │
       ├───────────┤
       │ • Archivo │
       │ • HTTP    │
       │ • SQL     │
       │ • SSH     │
       │ • Sistema │
       └───────────┘
```

---

## 🎯 Próximo: Capítulo 2

**"Tu primera herramienta"**

Aprenderás:
- Implementar tu propio Tool
- Integrar con el registry
- Ejecutar desde Python
- Ver resultados en tiempo real

---

**Siguiente capítulo**: [02-tu-primera-herramienta.md](02-tu-primera-herramienta.md)
