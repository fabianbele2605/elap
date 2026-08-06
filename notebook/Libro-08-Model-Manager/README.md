# Libro 08: Model Manager

**Fase 7 - Gestión de modelos de IA locales**

Aprende cómo ELAP ejecuta modelos de IA (LLMs) en tu máquina usando Ollama, con caché automático y memoria conversacional.

---

## 📖 Capítulos

### 01 - Introducción ✅

**Tema**: El cerebro de ELAP

- ¿Qué es un modelo?
- Ollama: modelos en tu máquina
- 3 tipos de modelos (Generativo, Embedding, Chat)
- Modelos recomendados
- Flujos comunes
- Optimizaciones automáticas
- Arquitectura de Model Manager
- Primeros pasos

**Tiempo**: 10-12 minutos

---

## 🏗️ Estructura

```
Libro 08: Model Manager
├── Cap 1: Introducción ✅
│   └─ Conceptos fundamentales
│
├── Cap 2: Tu primer modelo (próximo)
│   └─ Instalación y uso
│
├── Cap 3: Embeddings avanzados (próximo)
│   └─ Búsqueda de similitud
│
└── Cap 4: Agentes + Modelos (próximo)
    └─ Integración con Tool Engine
```

---

## 🔗 Relación con otras fases

```
Fase 6: Tool Engine
  ↓ Herramientas (File, HTTP, SQL)
Fase 7: Model Manager ← AQUÍ
  ↓ Modelos (LLM local)
Fase 8: Agent Framework
  ↓ Agentes que usan Tools + Modelos
Fase 9: Web API
```

---

## 📚 Documentación

- **Técnica**: [docs/03-Modules/MODELMANAGER.md](../../docs/03-Modules/MODELMANAGER.md)
- **Código**: [crates/elap-core/src/models/](../../crates/elap-core/src/models/)
- **Tests**: 33 tests pasando ✅

---

## 🎯 Lo que aprenderás

- [ ] Instalar Ollama
- [ ] Descargar modelos
- [ ] Crear ModelManager
- [ ] Generar texto
- [ ] Usar embeddings
- [ ] Conversar con memoria
- [ ] Optimizar con caché

---

**Autor**: ELAP Team  
**Versión**: 0.1.0  
**Última actualización**: 2026-08-05
