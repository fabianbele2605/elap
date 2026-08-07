#!/bin/bash

# ELAP Production Deployment Script
# Uso: ./deploy.sh [start|stop|restart|logs|build]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCKER_COMPOSE_FILE="$PROJECT_DIR/deployment/docker/docker-compose.yml"

echo "🚀 ELAP Deployment Script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Función para mostrar ayuda
show_help() {
  cat <<EOF
Uso: ./deploy.sh [COMANDO]

Comandos:
  start     - Iniciar todos los servicios (build + up)
  stop      - Detener todos los servicios
  restart   - Reiniciar todos los servicios
  build     - Compilar imágenes Docker
  up        - Iniciar servicios (sin compilar)
  down      - Detener y remover contenedores
  logs      - Mostrar logs en vivo
  logs-core - Logs solo del core
  logs-ai   - Logs solo del AI runtime
  status    - Estado de los servicios
  clean     - Limpiar volúmenes y datos

Ejemplos:
  ./deploy.sh start
  ./deploy.sh logs
  ./deploy.sh restart
EOF
}

# Validar que Docker está instalado
if ! command -v docker &> /dev/null; then
  echo "❌ Error: Docker no está instalado"
  exit 1
fi

if ! command -v docker-compose &> /dev/null; then
  echo "❌ Error: docker-compose no está instalado"
  exit 1
fi

# Ejecutar comando
case "${1:-start}" in
  start)
    echo "📦 Compilando imágenes..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    echo "✅ Imágenes compiladas"
    echo ""
    echo "🔥 Iniciando servicios..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    echo "✅ Servicios iniciados"
    echo ""
    echo "⏳ Esperando que los servicios estén healthy..."
    sleep 5
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    echo ""
    echo "🎉 ELAP está corriendo:"
    echo "   • REST API:     http://localhost:3000"
    echo "   • PostgreSQL:   localhost:5432"
    echo "   • Qdrant:       http://localhost:6333"
    echo "   • Ollama:       http://localhost:11434"
    ;;

  stop)
    echo "🛑 Deteniendo servicios..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" stop
    echo "✅ Servicios detenidos"
    ;;

  restart)
    echo "🔄 Reiniciando servicios..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" restart
    echo "✅ Servicios reiniciados"
    sleep 2
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    ;;

  build)
    echo "📦 Compilando imágenes Docker..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    echo "✅ Imágenes compiladas"
    ;;

  up)
    echo "🔥 Iniciando servicios (sin compilar)..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    ;;

  down)
    echo "🛑 Deteniendo y removiendo contenedores..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    echo "✅ Contenedores removidos"
    ;;

  logs)
    echo "📋 Mostrando logs en vivo (Ctrl+C para salir)..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f
    ;;

  logs-core)
    echo "📋 Logs del Core (Ctrl+C para salir)..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f core
    ;;

  logs-ai)
    echo "📋 Logs del AI Runtime (Ctrl+C para salir)..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f ai-runtime
    ;;

  status)
    echo "📊 Estado de los servicios:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    ;;

  clean)
    echo "🧹 Limpiando volúmenes y datos..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down -v
    echo "✅ Datos limpiados"
    ;;

  *)
    show_help
    exit 1
    ;;
esac

exit 0
