# 🚀 ELAP Production Deployment Guide

**Versión**: 1.4.0  
**Fecha**: 2026-08-06  
**Status**: ✅ Production Ready

---

## 📋 Requisitos

- Docker ≥ 20.10
- docker-compose ≥ 1.29
- 4GB RAM mínimo
- 10GB espacio disco (con modelos)

---

## 🚀 Quick Start

### 1. **Clonar y Configurar**

```bash
git clone https://github.com/bblabs/elap.git
cd elap

# Copiar configuración
cp .env.example .env

# (Opcional) Editar .env con valores específicos
nano .env
```

### 2. **Iniciar con Docker Compose**

```bash
# Opción A: Todo automático (build + start)
./deployment/scripts/deploy.sh start

# Opción B: Paso a paso
./deployment/scripts/deploy.sh build
./deployment/scripts/deploy.sh up
```

### 3. **Verificar Servicios**

```bash
# Ver estado
./deployment/scripts/deploy.sh status

# Ver logs
./deployment/scripts/deploy.sh logs
```

---

## 📊 Servicios

### **ELAP Core (Rust)**
- **Puerto**: 3000 (REST API)
- **Puerto**: 50051 (gRPC)
- **Health**: `curl http://localhost:3000/agents`

### **AI Runtime (Python)**
- **Puerto**: 50051 (gRPC)
- **Conecta a**: Ollama en 11434

### **PostgreSQL**
- **Puerto**: 5432
- **Usuario**: `elap`
- **Password**: `elap` (cambiar en .env)
- **Base de datos**: `elap`

### **Qdrant (Vector DB)**
- **Puerto**: 6333
- **Para**: RAG embeddings

### **Ollama (LLM)**
- **Puerto**: 11434
- **Modelos**: glm4:9b, qwen2.5-coder:7b, qwen3:8b

---

## 🔧 Comandos Útiles

```bash
# Iniciar
./deployment/scripts/deploy.sh start

# Detener
./deployment/scripts/deploy.sh stop

# Reiniciar
./deployment/scripts/deploy.sh restart

# Ver logs
./deployment/scripts/deploy.sh logs

# Ver logs del Core
./deployment/scripts/deploy.sh logs-core

# Ver logs del AI Runtime
./deployment/scripts/deploy.sh logs-ai

# Ver estado
./deployment/scripts/deploy.sh status

# Limpiar todo
./deployment/scripts/deploy.sh clean
```

---

## 🐳 Docker Compose Estructura

```yaml
Services:
├── postgres (PostgreSQL 16)
├── qdrant (Vector DB)
├── ollama (Local LLM)
├── core (Rust REST + gRPC)
└── ai-runtime (Python gRPC)

Volumes:
├── postgres_data (base de datos)
├── qdrant_data (embeddings)
└── ollama_data (modelos LLM)

Network:
└── elap-network (bridge)
```

---

## 🔐 Producción (Mejoras Futuras)

### Seguridad
- [ ] HTTPS/TLS
- [ ] Reverse proxy (Nginx)
- [ ] Rate limiting
- [ ] JWT authentication

### Performance
- [ ] Load balancer
- [ ] Redis cache
- [ ] Auto-scaling

### Monitoring
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] ELK stack (Elasticsearch)

---

## 🐛 Troubleshooting

### "Connection refused to postgres"
```bash
# Esperar a que postgres esté listo
docker-compose -f deployment/docker/docker-compose.yml logs postgres

# Reiniciar
./deployment/scripts/deploy.sh restart
```

### "Ollama models not found"
```bash
# Entrar a Ollama y descargar modelos
docker exec elap-ollama ollama pull glm4:9b
docker exec elap-ollama ollama pull qwen2.5-coder:7b
```

### "AI Runtime no conecta"
```bash
# Ver logs
./deployment/scripts/deploy.sh logs-ai

# Verificar que Ollama está corriendo
curl http://localhost:11434/api/tags
```

---

## 📊 Endpoints Principales

### **REST API (Core)**
- `GET /agents` - Listar agentes
- `POST /agents` - Crear agente
- `POST /agents/{id}/execute` - Ejecutar agente
- `GET /agents/{id}/execute/stream` - Streaming (WebSocket)

### **Health Checks**
- Rust: `curl http://localhost:3000/agents`
- Python: `docker-compose logs ai-runtime`
- Ollama: `curl http://localhost:11434/api/tags`
- Postgres: `curl http://localhost:5432` (no response = ok)
- Qdrant: `curl http://localhost:6333/health`

---

## 📈 Monitoreo

### Ver logs en tiempo real
```bash
./deployment/scripts/deploy.sh logs
```

### Ver logs de un servicio específico
```bash
docker-compose -f deployment/docker/docker-compose.yml logs -f core
docker-compose -f deployment/docker/docker-compose.yml logs -f ai-runtime
```

### Estadísticas de Docker
```bash
docker stats
```

---

## 🛠️ Kubernetes (Futuro)

Para deploy en K8s, ver:
- `deployment/kubernetes/deployment-core.yaml`
- `deployment/kubernetes/deployment-ai.yaml`
- `deployment/kubernetes/statefulset-postgres.yaml`

```bash
# Aplicar manifests
kubectl apply -f deployment/kubernetes/
```

---

## 📝 Notas

- **Volúmenes persistentes**: Los datos se guardan en `postgres_data`, `qdrant_data`, `ollama_data`
- **Networks**: Los servicios se comunican por `elap-network` (no exponen puertos internamente)
- **Health checks**: Cada servicio tiene health checks para reinicio automático
- **Restart policy**: `unless-stopped` (reinicia automáticamente si falla)

---

## 🚀 Próximos Pasos

1. **Configurar dominio y HTTPS** (Let's Encrypt)
2. **Agregar monitoring** (Prometheus + Grafana)
3. **Backup automático** de base de datos
4. **Load testing** con herramientas como `ab` o `k6`

---

**Versión**: 1.4.0 Production Ready  
**Última actualización**: 2026-08-06
