# Libro 01: Introducción — Capítulo 5 — Cómo comenzar

**Tema**: Lo que necesitas para ejecutar ELAP.

---

## 🖥️ Requisitos de hardware

### Mínimos (Desarrollo local)

```
CPU:       4 núcleos (Intel i5 / AMD Ryzen 5)
RAM:       8 GB
Almacenamiento: 20 GB (SSD recomendado)
Red:       Ethernet o WiFi 5GHz
SO:        Linux, macOS, Windows (WSL2)
```

**Rendimiento esperado**:
- Latencia: 1-3 segundos por pregunta
- Usuarios simultáneos: 2-3
- Modelos soportados: 7B parameters
- Token/segundo: 10-20

### Recomendado (Producción ligera)

```
CPU:       8 núcleos (Intel i7 / AMD Ryzen 7)
RAM:       32 GB
GPU:       NVIDIA A10 o equivalente (opcional)
Almacenamiento: 100 GB SSD
Red:       Gigabit Ethernet
Entorno:   Bare metal Linux
```

**Rendimiento esperado**:
- Latencia: 200-500ms
- Usuarios simultáneos: 10-20
- Modelos soportados: 7B, 13B parameters
- Token/segundo: 50-100

---

## 📦 Requisitos de software

### Instalados antes de ELAP

```bash
# 1. Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# 2. Python 3.10+
python3 --version  # debe ser 3.10+

# 3. Docker (opcional, para sandboxing)
sudo apt install docker.io

# 4. PostgreSQL 13+ (opcional, producción)
sudo apt install postgresql

# 5. Git
sudo apt install git
```

### Verificar instalación

```bash
$ rustc --version
rustc 1.80.0 (stable)

$ python3 --version
Python 3.10.12

$ cargo --version
cargo 1.80.0
```

---

## ⚙️ Instalación paso a paso

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/elap.git
cd elap
```

### Paso 2: Compilar Rust core

```bash
# Compilar en modo development
cargo build

# O en modo release (más rápido)
cargo build --release

# Ejecutar tests
cargo test
```

**Tiempo esperado**: 3-5 minutos (primera vez)

### Paso 3: Instalar dependencias Python

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar Ollama (para modelos locales)
curl https://ollama.ai/install.sh | sh
```

### Paso 4: Descargar modelo base

```bash
ollama pull llama2:7b

# Esto descarga ~5GB
# Esperar a que termine
```

### Paso 5: Verificar instalación

```bash
# Test Rust
cargo test --all

# Test Python
pytest tests/

# Ver versiones
elap --version
```

---

## 🚀 Primera ejecución

### Opción A: Línea de comandos

```bash
# Activar entorno Python
source venv/bin/activate

# Iniciar ELAP
./target/release/elap-cli

# Verás:
# ╔═══════════════════════════════════════╗
# ║  ELAP - Enterprise Local AI Platform  ║
# ║  v1.0.0                              ║
# ║  Desarrollado por Fabian Robles      ║
# ╚═══════════════════════════════════════╝
#
# Presiona Ctrl+C para salir
```

### Opción B: Interfaz de escritorio

```bash
# Ejecutar interfaz gráfica
cargo run --release -p elap-desktop

# Se abrirá ventana con:
# - Chat interactivo
# - Botones de controles
# - Vista de logs
```

---

## 🎮 Primeros comandos

### Si usas CLI

```bash
elap> obtener_estado_sistema

Respuesta:
{
  "cpu_porcentaje": 45.2,
  "memoria_gb": 4.5,
  "disco_gb": 50.2,
  "uptime_horas": 120
}
```

### Si usas Desktop UI

1. Abre la aplicación
2. Haz clic en el chat
3. Escribe: `¿Cuál es la capital de Francia?`
4. Presiona Enter o click en Enviar
5. Verás la respuesta en 1-2 segundos

---

## 📝 Configuración inicial

### Archivo: `.env.local`

```env
# Crear en raíz del proyecto
ELAP_LOG_LEVEL=INFO
ELAP_AI_MODEL=llama2:7b
ELAP_MAX_CONCURRENT_USERS=5
ELAP_AUDIT_ENABLED=true
ELAP_DATA_DIR=/home/usuario/.elap
```

### Archivo: `config/desarrollo.toml`

```toml
[core]
nombre_motor = "MotorCentral"
versión = "1.0.0"
timeout_segundos = 30

[ia]
modelo_por_defecto = "llama2:7b"
temperatura = 0.7
max_tokens = 512

[seguridad]
rbac_habilitado = true
auditoría_habilitada = true
```

---

## ✅ Checklist de iniciación

```
□ Rust compilable (cargo build)
□ Python tests pasando (pytest)
□ Ollama ejecutándose
□ Modelo descargado
□ .env.local configurado
□ Primera pregunta funciona
□ Logs visibles en stderr
□ Auditoría registrando eventos
```

---

## 🔍 Troubleshooting

### Error: "Modelo no encontrado"

```bash
$ ollama pull llama2:7b
# Reintenta descargar
```

### Error: "Puerto ocupado"

```bash
# Ver qué usa el puerto
lsof -i :8000

# Cambiar puerto en .env.local
ELAP_GRPC_PORT=8001
```

### Error: "Permiso denegado"

```bash
# ELAP intenta escribir donde no puede
# Solución: cambiar directorio de datos
mkdir -p ~/.elap
chmod 755 ~/.elap
export ELAP_DATA_DIR=~/.elap
```

### Error: "Out of memory"

```bash
# Usar modelo más pequeño
ollama pull llama2:3.8b
# O aumentar RAM del sistema
```

---

## 📊 Verificar funcionamiento

```bash
# Ver estado del core
curl http://localhost:8000/status
# Debe responder: {"estado": "ok"}

# Ver logs en tiempo real
tail -f /tmp/elap.log

# Test de herramientas
elap test-tools
# Debe listar: [archivo, http, sql, ssh, sistema]
```

---

## 🎯 Próximos pasos

Ahora que ELAP está corriendo:

1. **Leer** [Libro 02: Arquitectura del Core](../Libro-02-Core-Runtime/)
2. **Aprender** a crear plugins (Libro 03)
3. **Configurar** para producción (Libro 04)
4. **Implementar** flujos personalizados

---

## 🔜 Siguiente: Capítulo 6

**"Primeros Pasos Prácticos"**

Aprenderás:
- Tu primer plugin
- Tu primer agente
- Tu primer flujo
- Debugging básico

---

**Capítulo siguiente**: [06-primeros-pasos.md](06-primeros-pasos.md)
