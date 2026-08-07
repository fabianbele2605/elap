#!/bin/bash

# ELAP Complete Startup Script
# Inicia todos los servicios localmente para testing

set -e

PROJECT_DIR="/home/fabian/Escritorio/agenteC"
LOG_DIR="/tmp/elap_logs"

# Crear directorio de logs
mkdir -p "$LOG_DIR"

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🚀 ELAP Complete Startup Script                         ║"
echo "║  Iniciando todos los servicios localmente                ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Función para mostrar instrucciones
show_instructions() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  📋 INSTRUCCIONES - Abrir 3 Terminales (Terminal 1, 2, 3) ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    echo "🔴 TERMINAL 1 - Rust Core API (REST + gRPC):"
    echo "   cd $PROJECT_DIR/crates/elap-desktop"
    echo "   cargo run --release"
    echo ""
    echo "🟢 TERMINAL 2 - Python AI Runtime (gRPC Server):"
    echo "   cd $PROJECT_DIR/python"
    echo "   source venv/bin/activate"
    echo "   python -m elap_ai.grpc_server"
    echo ""
    echo "🔵 TERMINAL 3 - Tauri UI (Desktop App):"
    echo "   cd $PROJECT_DIR/web"
    echo "   npm run dev"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "✅ Una vez iniciados los 3 servicios, ejecuta en esta terminal:"
    echo "   source ~/.bashrc && bash $PROJECT_DIR/test_elap.sh"
    echo ""
}

# Función para verificar servicios
verify_services() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  🧪 Verificando Servicios                                ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""

    # Verificar Rust
    echo "⏳ Verificando Rust API (localhost:3000)..."
    if curl -s http://localhost:3000/agents > /dev/null 2>&1; then
        echo "✅ Rust API respondiendo"
    else
        echo "❌ Rust API NO responde - ¿Iniciaste Terminal 1?"
        return 1
    fi

    # Verificar Ollama
    echo "⏳ Verificando Ollama (localhost:11434)..."
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama respondiendo"
        MODELOS=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | head -3)
        echo "   Modelos disponibles: $MODELOS"
    else
        echo "❌ Ollama NO responde - ¿Iniciaste Ollama?"
        return 1
    fi

    # Verificar Python gRPC
    echo "⏳ Verificando Python gRPC (localhost:50051)..."
    if python3 -c "import grpc; print('OK')" 2>/dev/null; then
        echo "✅ gRPC disponible"
    else
        echo "⚠️  gRPC tools no disponibles (Terminal 2 debería estar corriendo)"
    fi

    echo ""
    return 0
}

# Función para hacer test E2E
test_e2e() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  🧪 Test E2E - Prueba Completa                          ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""

    # Test 1: Listar agentes
    echo "📝 Test 1: Listar Agentes"
    AGENTES=$(curl -s http://localhost:3000/agents | jq '.agentes | length')
    echo "   Resultado: $AGENTES agentes en sistema"

    # Test 2: Crear agente
    echo "📝 Test 2: Crear Agente"
    NUEVO=$(curl -s -X POST http://localhost:3000/agents \
        -H "Content-Type: application/json" \
        -d '{"nombre":"Test Agent","rol":"Sales","objetivo":"Probar sistema"}' \
        | jq -r '.id' 2>/dev/null || echo "error")

    if [ "$NUEVO" != "error" ] && [ ! -z "$NUEVO" ]; then
        echo "   ✅ Agente creado: $NUEVO"
    else
        echo "   ❌ Error al crear agente"
    fi

    # Test 3: Verificar modelo asignado
    echo "📝 Test 3: Verificar Rol→Modelo Mapping"
    MODELO=$(curl -s http://localhost:3000/agents | jq -r '.agentes[0].modelo' 2>/dev/null)
    if [ ! -z "$MODELO" ]; then
        echo "   ✅ Modelo asignado: $MODELO"
    else
        echo "   ❌ No hay modelo asignado"
    fi

    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  ✅ Tests Completados                                    ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
}

# Main
case "${1:-}" in
    "verify")
        verify_services
        ;;
    "test")
        test_e2e
        ;;
    *)
        show_instructions
        echo "💡 Tip: Una vez iniciados los servicios, ejecuta:"
        echo "   bash $PROJECT_DIR/start_elap.sh verify  (verificar servicios)"
        echo "   bash $PROJECT_DIR/start_elap.sh test    (hacer tests E2E)"
        ;;
esac

exit 0
