# Dashboard CLI en Terminal — Monitoreo de Agentes

**Autor**: ELAP Development Team  
**Fecha**: 2026-08-05  
**Versión**: 1.0  
**Fase**: 12

## Descripción General

CLI interactivo para gestionar y monitorear agentes ELAP desde la terminal.

### Características

- ✅ **Listar agentes** con tabla formateada
- ✅ **Crear agentes** interactivamente
- ✅ **Monitoreo en vivo** vía WebSocket
- ✅ **Status en tiempo real** con barras de progreso
- ✅ **Ejecutar planes**
- ✅ **Colores y emojis** para mejor UX

---

## Instalación

```bash
# Desde source
cargo build -p elap-cli --release

# Binario en
./target/release/elap-cli
```

---

## Comandos

### `elap agents list`

Listar todos los agentes

```bash
$ elap agents list
📋 Listando agentes...

ID (primeros 8)  | Nombre
─────────────────┼────────────────────
a1b2c3d4         | Vendedor
e5f6g7h8         | Analizador
```

### `elap agents create`

Crear nuevo agente

```bash
$ elap agents create \
  --nombre "Bot Vendedor" \
  --rol "Sales" \
  --objetivo "Procesar pedidos"

🚀 Creando agente...

✓ Agente creado exitosamente
  ID: a1b2c3d4-e5f6-4g7h-i8j9...
  Nombre: Bot Vendedor
  Rol: Sales
  Objetivo: Procesar pedidos

→ Próximo: elap agent a1b2c3d4 watch
```

### `elap agent <id> info`

Información detallada del agente

```bash
$ elap agent a1b2c3d4 info

📊 Información del agente a1b2c3d4...

  ID: a1b2c3d4-e5f6-4g7h-i8j9...
  Nombre: Bot Vendedor
  Rol: Sales
  Objetivo: Procesar pedidos
  Estado: Completado
  Progreso: 100%
```

### `elap agent <id> watch` ⭐

Monitorear agente en vivo (WebSocket)

```bash
$ elap agent a1b2c3d4 watch

👁️  Monitoreando agente a1b2c3d4...
Presiona Ctrl+C para detener

• Estado: Ejecutando
▓ Progreso: 1/4 (25%)
→ Ejecutando: Leer archivo de ventas
▓ Progreso: 2/4 (50%)
→ Ejecutando: Validar estructura
▓ Progreso: 3/4 (75%)
→ Ejecutando: Procesar datos
▓ Progreso: 4/4 (100%)
💭 Plan completado. 4 pasos ejecutados.

✓ Completado
```

### `elap agent <id> execute`

Ejecutar plan del agente

```bash
$ elap agent a1b2c3d4 execute

⚡ Ejecutando agente a1b2c3d4...
✓ Ejecutando... 

✓ Completado

✓ Ejecución completada
  → 4 pasos completados
  → 100.0% completado
```

### `elap agent <id> status`

Estado actual del agente

```bash
$ elap agent a1b2c3d4 status

Estado: Completado
Progreso: 4/4 pasos
Porcentaje: 100%
Historial: 5 acciones
Aprendizaje: 1 reflexiones
```

### `elap agent <id> delete`

Eliminar agente

```bash
$ elap agent a1b2c3d4 delete

🗑️  Eliminando agente a1b2c3d4...
✓ Agente eliminado
```

---

## Configuración

### Variables de Entorno

```bash
# Server URL (default: http://localhost:3000)
export ELAP_SERVER="http://localhost:3000"

# JWT Token (para endpoints protegidos)
export ELAP_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Argumentos

```bash
# Token via argumento
elap --token "eyJhbGc..." agents list

# Server custom
elap --server "http://api.example.com" agents list
```

---

## Ejemplos de Flujo

### Flujo Completo

```bash
# 1. Crear agente
elap agents create \
  --nombre "Procesador" \
  --rol "Processor" \
  --objetivo "Procesar 100 archivos"

# 2. Obtener ID (ej: a1b2c3d4)

# 3. Monitorear en tiempo real
elap agent a1b2c3d4 watch

# 4. Ver status final
elap agent a1b2c3d4 status

# 5. Eliminar si quieres
elap agent a1b2c3d4 delete
```

### Con Token JWT

```bash
# Login primero (obtener token)
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"usuario": "admin", "contraseña": "admin123"}' \
  | jq '.token' -r > token.txt

# Usar token en CLI
elap --token "$(cat token.txt)" agents list
```

---

## UI/UX

### Colores

- 🔵 Cyan: IDs, URLs, datos técnicos
- ⚪ White: Nombres, estándares
- 🟡 Yellow: Estados, alertas
- 🟢 Green: Éxito, confirmaciones
- 🔴 Red: Errores
- 🟣 Magenta: Reflexiones/análisis

### Emojis

- 📋 Listados
- 🚀 Creación
- 👁️ Monitoreo
- ⚡ Ejecución
- 📊 Información
- ✓ Éxito
- ✗ Error
- → Pasos/acciones
- 💭 Reflexiones
- 🗑️ Eliminación

---

## Performance

| Operación | Latencia |
|-----------|----------|
| `agents list` | <100ms |
| `agent info` | <50ms |
| `agent watch` | <10ms/evento |
| WebSocket connect | <50ms |

---

## Próximas Mejoras (Fase 13+)

- [ ] Shell interactivo (REPL)
- [ ] Alias de comandos
- [ ] Historial de comandos
- [ ] Autocompletado
- [ ] Configuración persistent (~/.elaprc)
- [ ] Export de agentes (JSON/YAML)
- [ ] Filtros avanzados

---

**Última actualización**: 2026-08-05
