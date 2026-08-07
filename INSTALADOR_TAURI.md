# 🚀 ELAP v1.5.0 — Guía de Instalación (Desktop App)

**Versión:** 1.5.0 (Tauri 2.0)  
**Estado:** Listo para distribuir  
**Formatos:** Windows (.exe), Linux (.deb), macOS (.dmg)

---

## 📋 Requisitos del Sistema

### Mínimo
- **OS:** Windows 10+, Ubuntu 20.04+, macOS 11+
- **RAM:** 8 GB
- **Disco:** 20 GB disponibles (incluye modelos Ollama)
- **GPU:** Opcional (CPU funciona, GPU recomendada para rendimiento)

### Recomendado
- **OS:** Windows 11, Ubuntu 22.04, macOS 13+
- **RAM:** 16 GB
- **Disco:** SSD con 30 GB libres
- **GPU:** NVIDIA CUDA 12+ o Apple Silicon

---

## ⚙️ Pre-instalación

### 1. Instalar Ollama (Obligatorio)

**Windows:**
```bash
# Descargar: https://ollama.ai/download
# Instalar y ejecutar
ollama serve
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

**macOS:**
```bash
# Descargar: https://ollama.ai/download
# O via Homebrew:
brew install ollama
ollama serve
```

Verificar que Ollama esté corriendo:
```bash
curl http://localhost:11434/api/tags
```

### 2. Descargar Modelos (opcional — se descargan en primera ejecución)

```bash
ollama pull qwen3:8b
ollama pull glm4:9b
ollama pull qwen2.5-coder:7b
```

Cada modelo es **4-6 GB**, total ~15 GB.

---

## 📥 Instalación de ELAP

### Windows

1. **Descargar:** `ELAP-v1.5.0-windows.exe` desde [releases](https://github.com/fabianbele2605/ELAP/releases)
2. **Ejecutar:** Doble clic en el instalador
3. **Seguir asistente** de instalación
4. **Iniciar:** ELAP se abrirá automáticamente

Atajo de escritorio: Se crea automáticamente

### Linux (Ubuntu/Debian)

```bash
# Descargar
wget https://github.com/fabianbele2605/ELAP/releases/download/v1.5.0/elap-v1.5.0.deb

# Instalar
sudo dpkg -i elap-v1.5.0.deb

# Ejecutar
elap

# O desde menú de aplicaciones
```

### macOS

1. **Descargar:** `ELAP-v1.5.0.dmg`
2. **Montar:** Doble clic en el archivo
3. **Instalar:** Arrastrar ELAP.app a Applications
4. **Ejecutar:** Abrir desde Applications o Spotlight (⌘+Space)

---

## 🔧 Configuración Inicial

### Primera ejecución

1. **Bienvenida:** Se abrirá la app
2. **Configuración de empresa:**
   - Nombre de la empresa
   - Sector
   - Ubicación
   - Logo (opcional)
3. **Seleccionar agentes** a instalar:
   - Sistema (obligatorio): System Supervisor, Task Router, Memory Manager
   - Dirección: CEO, CFO, CMO
   - Administración: RRHH, Contabilidad, Finanzas, Compras
   - Comercial: Ventas, CRM, Atención
   - Documentación: Gestor Documental, PDF Assistant

### Configuración de Ollama

Si Ollama no está en `localhost:11434`:

1. **Settings** → **Conexiones**
2. **Ollama URL:** `http://[IP]:[PUERTO]`
3. **Guardar**

La app validará la conexión automáticamente.

---

## ✅ Verificación de Instalación

### Checklist

- [ ] Ollama corriendo en `localhost:11434`
- [ ] App abre sin errores
- [ ] Agentes listados en sidebar
- [ ] Chat responde (espera 30-50s en CPU)
- [ ] Generador de reportes funciona

### Solución de problemas

| Problema | Solución |
|----------|----------|
| **App no inicia** | Reiniciar PC, verificar permisos |
| **Ollama no conecta** | Verificar URL en Settings, reiniciar Ollama |
| **Chat no responde** | Esperar (modelos lentos en CPU), verificar Ollama |
| **Modelos no descargan** | Espacio disco, conexión internet |

---

## 🚀 Uso Rápido

### Crear agente

1. Sidebar izquierdo → **INSTALL AGENTS**
2. Seleccionar agentes
3. Clic **Instalar Agentes**
4. Esperar carga (1-2 min)

### Chatear con agente

1. Seleccionar agente del sidebar
2. Escribir pregunta
3. Esperar respuesta

### Configurar empresa

1. **Settings** → **Configuración de Empresa**
2. Ingresar datos
3. Guardar

---

## 📊 Performance esperado

| Métrica | CPU | GPU |
|---------|-----|-----|
| **Latencia primer token** | 30-50s | 2-5s |
| **Throughput** | ~5 tokens/s | ~50 tokens/s |
| **Uso de RAM** | 8-12 GB | 4-6 GB |

**Nota:** La primera respuesta es más lenta (carga de modelo en memoria).

---

## 🔄 Actualizaciones

### Verificar actualizaciones

**Settings** → **Acerca de** → **Buscar actualizaciones**

### Actualizar manualmente

1. Descargar nueva versión desde [releases](https://github.com/fabianbele2605/ELAP/releases)
2. Instalar (sobreescribe sin perder datos)
3. Reiniciar app

**Datos conservados:** Agentes, conversaciones, configuración

---

## 📚 Documentación

- **[Guía de usuarios](docs/USER_GUIDE.md)** — Cómo usar la app
- **[API Reference](docs/API.md)** — Para desarrolladores
- **[FAQ](docs/FAQ.md)** — Preguntas frecuentes
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** — Solución de problemas

---

## 🤝 Soporte

- **Email:** fabian.beleno@bblabs.io
- **GitHub Issues:** [Reportar bug](https://github.com/fabianbele2605/ELAP/issues)
- **Documentación:** [wiki.elap.local](docs/)

---

## 📦 Contenido de la instalación

```
ELAP/
├── app/                  # Aplicación Tauri
├── models/               # Modelos descargados (10-15 GB)
├── data/                 # Agentes, configuración, datos
├── logs/                 # Logs de operación
└── docs/                 # Documentación
```

**Tamaño total:** 20-30 GB (incluyendo modelos)

---

**Versión:** 1.5.0  
**Fecha:** 2026-08-07  
**Licencia:** Comercial
