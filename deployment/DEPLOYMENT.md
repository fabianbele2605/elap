# ELAP Deployment Guide

**Fase 18 — Deployment (Docker + Kubernetes)**

---

## Docker Compose (Desarrollo Local)

```bash
cd deployment/docker

# Build images
docker-compose build

# Run all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f core

# Stop
docker-compose down
```

### Servicios incluidos:

- **core**: ELAP API (puerto 3000)
- **ai-runtime**: Python AI Runtime
- **postgres**: Base de datos
- **qdrant**: Vector DB
- **ollama**: LLM local (opcional)

---

## Kubernetes (Producción)

### 1. Build y push images

```bash
docker build -f deployment/docker/Dockerfile.core -t elap:core-latest .
docker build -f deployment/docker/Dockerfile.python -t elap:ai-runtime-latest .

# Push a registry
docker tag elap:core-latest <registry>/elap:core-latest
docker push <registry>/elap:core-latest
```

### 2. Deploy a K8s

```bash
kubectl apply -f deployment/kubernetes/statefulset-postgres.yaml
kubectl apply -f deployment/kubernetes/deployment-core.yaml
kubectl apply -f deployment/kubernetes/deployment-ai.yaml

# Check status
kubectl get pods
kubectl get svc

# View logs
kubectl logs -f deployment/elap-core
```

### 3. Verificar health

```bash
# Port forward
kubectl port-forward svc/elap-core 3000:3000

# Health check
curl http://localhost:3000/health
```

---

## Escalado

### Horizontal Pod Autoscaling

```bash
kubectl autoscale deployment elap-core \
  --min=2 --max=10 \
  --cpu-percent=80
```

---

## Monitoring

```bash
# Real-time metrics
kubectl top pods
kubectl top nodes

# Describe resources
kubectl describe pod <pod-name>
kubectl describe svc elap-core
```

---

## Troubleshooting

```bash
# Check pod status
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name> --previous

# Execute command in pod
kubectl exec -it <pod-name> -- bash

# Port forward for debugging
kubectl port-forward <pod-name> 3000:3000
```

---

**Próxima Fase**: Fase 19 — Advanced RAG (Reranking, Semantic Caching)

**Última actualización**: 2026-08-05
