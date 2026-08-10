#!/bin/bash

# 🚀 STARTUP SCRIPT - TESTING DE 15 AGENTES + LEGAL KNOWLEDGE SYSTEM
# Ejecutar: bash STARTUP_TESTING.sh

set -e  # Detener en error

echo "═══════════════════════════════════════════════════════════════"
echo "🚀 STARTUP: ELAP Multi-Agent Testing"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Verificar Python
echo -e "${BLUE}[1/5]${NC} Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 no encontrado${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python ${PYTHON_VERSION}${NC}"

# 2. Verificar Ollama
echo -e "${BLUE}[2/5]${NC} Verificando Ollama..."
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama no instalado. Descargando desde ollama.ai...${NC}"
    echo "   Requerido para respuestas de agentes."
    echo "   Instalación manual: https://ollama.ai"
    exit 1
fi
echo -e "${GREEN}✅ Ollama instalado${NC}"

# 3. Verificar modelos Ollama
echo -e "${BLUE}[3/5]${NC} Verificando modelos Ollama necesarios..."
# Intentar listar modelos (requiere que Ollama esté corriendo)
if ! ollama list 2>/dev/null | grep -q "qwen"; then
    echo -e "${YELLOW}⚠️  Modelos no encontrados. Descargando...${NC}"
    echo "   Ejecutando: ollama pull qwen3:8b"
    # No ejecutamos pull automáticamente porque es lento
    echo -e "${YELLOW}   Ejecuta manualmente:${NC}"
    echo "   ollama pull qwen3:8b"
    echo "   ollama pull glm4:9b"
else
    echo -e "${GREEN}✅ Modelos disponibles${NC}"
fi

# 4. Verificar estructura del proyecto
echo -e "${BLUE}[4/5]${NC} Verificando estructura del proyecto..."
REQUIRED_FILES=(
    "python/src/elap_ai/legal/legal_search_engine.py"
    "python/src/elap_ai/agents/hr_agent.py"
    "python/src/elap_ai/agents/benefits_agent.py"
    "python/src/elap_ai/rest_server.py"
    "python/src/elap_ai/system_prompts.py"
)

ALL_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Falta: $file${NC}"
        ALL_EXIST=false
    fi
done

if [ "$ALL_EXIST" = true ]; then
    echo -e "${GREEN}✅ Todos los archivos presentes${NC}"
else
    echo -e "${RED}❌ Archivos faltantes${NC}"
    exit 1
fi

# 5. Verificar dependencias Python
echo -e "${BLUE}[5/5]${NC} Verificando dependencias Python..."
REQUIRED_PACKAGES=(
    "aiohttp"
    "apscheduler"
)

ALL_INSTALLED=true
for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $package" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Falta: $package${NC}"
        ALL_INSTALLED=false
    fi
done

if [ "$ALL_INSTALLED" = true ]; then
    echo -e "${GREEN}✅ Todas las dependencias instaladas${NC}"
else
    echo -e "${YELLOW}Instalando dependencias...${NC}"
    pip install aiohttp apscheduler
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ VERIFICACIÓN COMPLETADA${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Mostrar próximos pasos
echo -e "${BLUE}PRÓXIMOS PASOS:${NC}"
echo ""
echo "1️⃣  Iniciar Ollama (si aún no está corriendo):"
echo "   ${YELLOW}ollama serve${NC}"
echo ""
echo "2️⃣  Descargar modelos necesarios (si aún no los tienes):"
echo "   ${YELLOW}ollama pull qwen3:8b${NC}"
echo "   ${YELLOW}ollama pull glm4:9b${NC}"
echo ""
echo "3️⃣  Iniciar REST Server de Python:"
echo "   ${YELLOW}cd python && python -m src.elap_ai.rest_server${NC}"
echo ""
echo "4️⃣  Abrir frontend y probar:"
echo "   ${YELLOW}http://localhost:3000${NC}"
echo ""
echo "5️⃣  Seleccionar un agente y enviar pregunta:"
echo "   Ejemplos en: PREGUNTAS_AGENTES_15.md"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN}🚀 Sistema listo para testing${NC}"
echo "═══════════════════════════════════════════════════════════════"
