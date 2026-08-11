# 🐳 ELAP Docker Setup - PostgreSQL Production

## 📋 Requisitos previos

```bash
# Instalar Docker
sudo apt install docker.io docker-compose -y

# Iniciar servicio
sudo systemctl start docker
sudo usermod -aG docker $USER
```

---

## 🚀 Iniciando Docker

### **Paso 1: Levantar servicios**

```bash
cd /home/fabian/Escritorio/agenteC

# Levantar todos los contenedores
docker-compose up -d

# Verificar estado
docker-compose ps
```

### **Paso 2: Esperar a que PostgreSQL esté listo**

```bash
# Ver logs de PostgreSQL
docker-compose logs postgres

# Cuando veas: "database system is ready to accept connections"
# ✅ Estás listo
```

### **Paso 3: Verificar BD**

```bash
# Entrar a psql
docker exec -it elap_postgres psql -U elap_user -d elap_db

# Dentro de psql:
\dt                    # Ver tablas
SELECT COUNT(*) FROM conversations;
\q                     # Salir
```

---

## 🔄 Migración de SQLite a PostgreSQL

### **Exportar datos de SQLite (si hay)**

```bash
# Si tienes datos en SQLite, puedes exportarlos:
sqlite3 /tmp/elap_conversations.db ".dump" > /tmp/backup.sql
```

---

## 🔧 Actualizar REST Server para PostgreSQL

### **Opción A: Usar PostgreSQL (RECOMENDADO)**

```python
# En rest_server.py, reemplazar:
from .conversation_manager import ConversationManager

# Por:
from .conversation_manager_postgres import ConversationManagerPostgres

conversation_manager = ConversationManagerPostgres(
    host="localhost",
    port=5432,
    database="elap_db",
    user="elap_user",
    password="elap_secure_pass_2026"
)
```

### **Opción B: Mantener SQLite (desarrollo)**

```python
conversation_manager = ConversationManager(
    db_path="/tmp/elap_conversations.db"
)
```

---

## 🧹 Limpieza

### **Detener contenedores**

```bash
docker-compose down
```

### **Eliminar volúmenes (⚠️ pierde datos)**

```bash
docker-compose down -v
```

### **Ver logs en vivo**

```bash
docker-compose logs -f postgres
docker-compose logs -f qdrant
docker-compose logs -f redis
```

---

## 📊 Arquitectura final

```
┌─────────────────────────────────────┐
│     React Frontend (localhost:3000)  │
└──────────────────┬──────────────────┘
                   │
┌──────────────────▼──────────────────┐
│    Python REST API (localhost:5000)  │
│    └─ 15 Agentes AI                  │
└──────────────────┬──────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
   ┌────▼────┐ ┌──▼──┐ ┌─────▼────┐
   │PostgreSQL│ │Qdrant│ │  Redis   │
   │:5432    │ │:6333 │ │ :6379    │
   └─────────┘ └──────┘ └──────────┘
```

---

## ✅ Checklist

- [ ] Docker instalado
- [ ] docker-compose up -d
- [ ] PostgreSQL inicializado
- [ ] Tablas creadas en BD
- [ ] REST server usando PostgreSQL
- [ ] Frontend enviando conversación_id
- [ ] Historial mostrando datos reales

---

## 🆘 Troubleshooting

### **Error: "Connection refused"**

```bash
# PostgreSQL no está listo, espera más:
docker-compose logs postgres
```

### **Error: "permission denied"**

```bash
# Agregar usuario a grupo docker:
sudo usermod -aG docker $USER
newgrp docker
```

### **BD vacía después de iniciar**

```bash
# Reiniciar y asegurar init-db.sql se ejecute:
docker-compose down -v
docker-compose up -d
```

---

## 📝 Conexión desde Python

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="elap_db",
    user="elap_user",
    password="elap_secure_pass_2026"
)
cursor = conn.cursor()
cursor.execute("SELECT * FROM conversations")
print(cursor.fetchall())
```

---

**Última actualización:** 2026-08-10  
**Versión:** 1.0 - Production Ready
