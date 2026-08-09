# 🏛️ Legal Knowledge System - ELAP

Sistema inteligente para obtener **leyes colombianas actualizadas** en tiempo real. Integrado con todos los agentes ELAP para respuestas basadas en legislación vigente.

> **NOTA:** Usando **SQLite** para desarrollo ágil. En producción cambiaremos a **Qdrant** para búsqueda semántica avanzada.

## 🎯 Arquitectura

```
┌─────────────────────────────────────────────────┐
│        HRAgent / BenefitsAgent / etc             │
├─────────────────────────────────────────────────┤
│  LegalSearchEngine (Búsqueda Inteligente)       │
├─────────────────────────────────────────────────┤
│  1. APIs Oficiales  2. SQLite Local   3. Web    │
│  (MinTrabajo, DIAN) (Cache 30 días)  (Backup)  │
└─────────────────────────────────────────────────┘
     ↓                    ↓                ↓
  .gov.co APIs      [SQLite DB]      [Web Search]
  High Trust        Medium Trust      Low Trust
```

## 📁 Archivos del Módulo

### 1. `official_apis.py` - Integraciones con canales oficiales
```python
# Ministerios y autoridades colombianas
- MintrabajoAPI: Código Sustantivo, resoluciones laborales
- DIANApi: Descuentos, retenciones, normas fiscales
- MinSalud: Afiliación EPS, derechos en salud
- SuperFinanciera: Pensiones, AFP, regulaciones
- BancoRepublica: UVR, datos económicos
```

### 2. `legal_search_engine.py` - Motor de búsqueda inteligente
```python
LegalSearchEngine.buscar_ley(query, tema)
# Prioridad:
# 1. APIs oficiales (confianza 99%)
# 2. Qdrant local si < 30 días (confianza 95%)
# 3. Web search a .gov.co (confianza 90%)
# 4. Fallback con recomendaciones
```

### 3. `update_scheduler.py` - Actualización automática
```python
# Ejecuta según schedule:
- 2:00 AM: Sincronización diaria de leyes
- Lunes 3:00 AM: Verificación de cambios
- 1º Mes 4:00 AM: Limpieza de caché viejo
```

## 🚀 Uso en Agentes

### HRAgent (Recursos Humanos)
```python
# Búsqueda automática de leyes laborales
legal_search = LegalSearchEngine()
ley = await legal_search.buscar_ley("licencia maternidad", tema="laboral")

# Incluir en prompt de Ollama
prompt = f"{system_prompt}\n\n🏛️ {ley['texto']}\n\nPregunta: {query}"
```

### BenefitsAgent (Prestaciones)
```python
# Buscar leyes de pensión/beneficios vigentes
ley = await legal_search.buscar_ley("cesantía", tema="pension")

# Respuestas siempre con legislación actualizada
```

## 📊 Temas Soportados

| Tema | Canales | Ejemplo Query |
|------|---------|--------------|
| `laboral` | MinTrabajo | "¿Derechos en maternidad?" |
| `salud` | MinSalud | "¿Cómo afiliar a EPS?" |
| `pension` | SuperFinanciera | "¿Cálculo de cesantía?" |
| `fiscal` | DIAN | "¿Descuentos en nómina?" |

## ⚙️ Configuración

### Iniciar el Scheduler (en startup)
```python
# En main.py o inicializador
from legal import leyes_scheduler

leyes_scheduler.start()
# Inicia actualizaciones automáticas
```

### Obtener Status
```python
status = leyes_scheduler.get_status()
# {
#   "running": True,
#   "jobs": [...],
#   "next_sync": "2026-08-10 02:00:00"
# }
```

## 📡 Canales Oficiales Disponibles

### Ministerio del Trabajo
- **URL:** https://www.mintrabajo.gov.co/
- **Contenido:** Código Sustantivo, resoluciones laborales
- **Actualización:** Semanal

### DIAN
- **URL:** https://www.dian.gov.co/
- **Contenido:** Retenciones, descuentos, UVT vigente
- **Actualización:** Diaria

### MinSalud
- **URL:** https://www.minsalud.gov.co/
- **Contenido:** Afiliación EPS, derechos en salud
- **Actualización:** Semanal

### SuperFinanciera
- **URL:** https://www.superfinanciera.gov.co/
- **Contenido:** Pensiones, AFP, normatividad
- **Actualización:** Mensual

### Banco de la República
- **URL:** https://datos.banrep.gov.co/
- **Contenido:** UVR, datos económicos
- **Actualización:** Diaria

## 🗄️ Almacenamiento en SQLite

```python
# Estructura de tabla en SQLite
CREATE TABLE leyes (
  id TEXT PRIMARY KEY,              -- Hash de la fuente
  texto TEXT,                       -- Contenido completo de la ley
  fuente TEXT,                      -- Ministerio o fuente oficial
  tema TEXT,                        -- laboral, salud, pension, fiscal
  fecha_actualizacion TEXT,         -- ISO datetime
  url TEXT,                         -- Link a fuente oficial
  numero_resolucion TEXT            -- Ej: CST-240
)
```

**Base de datos:** `leyes_colombianas.db` (SQLite)  
**Tamaño:** < 50 MB para todas las leyes colombianas  
**Índices:** fecha_actualizacion, tema (búsqueda rápida)

## 📈 Flujo de Búsqueda

```
Usuario: "¿Licencia por maternidad?"
         ↓
HRAgent: legal_search.buscar_ley(query, "laboral")
         ↓
1️⃣ APIs Oficiales?
   - Consulta MinTrabajo API
   - Si obtiene respuesta → Retorna con confianza 99%
         ↓
2️⃣ SQLite Local (<30 días)?
   - Busca en leyes_colombianas.db
   - Si encontrada y reciente → Retorna con confianza 95%
         ↓
3️⃣ Web Search?
   - Busca en google/bing filtrado .gov.co
   - Valida dominio oficial
   - Guarda en SQLite para futuro
   - Retorna con confianza 90%
         ↓
4️⃣ Fallback
   - Retorna canales recomendados
   - Sugiere contacto directo
```

## 🔄 Ciclo de Actualización

### Diariamente (2:00 AM)
```
MinTrabajo ─┐
MinSalud   ─┼─→ Sincronización Completa ─→ Qdrant
SuperFin   ─┤
DIAN       ─┘
```

### Semanalmente (Lunes 3:00 AM)
```
Verificar cambios → Detectar nuevas resoluciones → Notificar
```

### Mensualmente (1º Mes)
```
Limpiar Qdrant → Eliminar docs > 90 días → Optimizar base
```

## 🛠️ Troubleshooting

### ❌ "No se encontró información"
- Verificar que SQLite esté disponible: `ls -la leyes_colombianas.db`
- Revisar permisos de archivo: `chmod 644 leyes_colombianas.db`
- Ejecutar sincronización manual:
  ```python
  legal_search = LegalSearchEngine()
  await legal_search.sincronizar_todas_leyes()
  ```

### ❌ "Database locked"
```bash
# Eliminar base de datos y recriarla (pierde datos)
rm leyes_colombianas.db

# O esperar a que se libere
# (Verifica que no haya procesos escribiendo)
```

### ⚠️ "Información vieja"
- Force sync manual:
  ```python
  legal_search = LegalSearchEngine()
  await legal_search.sincronizar_todas_leyes()
  ```

### 📦 "Migrar a Qdrant en producción"
```python
# Cuando estés listo para producción:
# 1. Iniciar Qdrant
# 2. Cambiar LegalSearchEngine para usar Qdrant
# 3. Importar datos de SQLite a Qdrant
# Ver sección "Próximos Pasos"
```

## 📚 Ejemplos de Uso

### Ejemplo 1: Consulta de Maternidad (HRAgent)
```python
query = "¿Cuántos días de licencia por maternidad?"

legal_search = LegalSearchEngine()
ley = await legal_search.buscar_ley(query, tema="laboral")

# Resultado con ley actualizada
# Fuente: Código Sustantivo del Trabajo
# Fecha: 2026-08-09
# Artículo 240: Licencia de maternidad...
```

### Ejemplo 2: Consulta de Cesantía (BenefitsAgent)
```python
query = "¿Cómo calcular cesantía con 3 años?"

legal_search = LegalSearchEngine()
ley = await legal_search.buscar_ley(query, tema="pension")

# Retorna leyes vigentes sobre pensiones
# + fórmula de cálculo de cesantía
```

## 🔐 Seguridad

- ✅ Solo fuentes `.gov.co` (validadas)
- ✅ HTTPS en todas las conexiones
- ✅ Timeout en APIs (10 segundos max)
- ✅ Caché local sin datos sensibles
- ✅ Logs de todas las búsquedas

## 📊 Métricas

```python
# Ver status del sistema
status = leyes_scheduler.get_status()

# Salida:
# {
#   "running": True,
#   "jobs": [
#     {
#       "id": "sync_leyes_diarias",
#       "next_run": "2026-08-10 02:00:00"
#     }
#   ]
# }
```

## 🚀 Próximos Pasos

### Fase Actual (SQLite)
- [x] Búsqueda en APIs oficiales
- [x] Cache local en SQLite
- [x] Actualización automática
- [x] Integración en HRAgent/BenefitsAgent

### Fase 2 (Qdrant - Cuando todo funcione)
- [ ] Migrar SQLite → Qdrant
- [ ] Agregar embeddings reales (búsqueda semántica)
- [ ] Integrar Web Search API (Google Custom Search)
- [ ] Dashboard de auditoría de cambios legales
- [ ] Notificaciones por Slack/Email de cambios
- [ ] Versionado de leyes por fecha

### Fase 3 (Jurisprudencia)
- [ ] Agregar sentencias constitucionales
- [ ] Crear grafo de jurisprudencia
- [ ] Integrar referencias cruzadas

## 📝 Notas

- **Confianza 99%**: APIs oficiales directas
- **Confianza 95%**: Cache local < 30 días
- **Confianza 90%**: Web search a .gov.co
- **Confianza 0%**: Fallback sin ley

Todas las búsquedas retornan metadata sobre confianza y fuente.
