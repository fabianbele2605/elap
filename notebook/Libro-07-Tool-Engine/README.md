# Libro 07: Tool Engine

**Fase 6 - Herramientas y Sandboxing**

Aprende cómo ELAP ejecuta herramientas (tools) de forma segura, con control de permisos, límites de recursos y auditoría completa.

---

## 📖 Capítulos

### 01 - Introducción ✅

**Tema**: ¿Por qué necesitas herramientas y cómo funcionan?

- 5 herramientas estándar (Archivo, HTTP, SQL, SSH, Sistema)
- Sandboxing: 5 niveles de seguridad
- Casos de uso reales
- Validación RBAC
- Arquitectura en 30 segundos

**Tiempo de lectura**: 10-15 minutos

---

## 🎯 Estructura del Libro

```
Libro 07: Tool Engine
├── Cap 1: Introducción
│   └─ ¿Qué es una herramienta?
│      RBAC, validación, casos de uso
│
├── Cap 2: Tu primera herramienta (próximo)
│   └─ Implementar un Tool
│      Registry, ejecución, resultados
│
├── Cap 3: Seguridad (próximo)
│   └─ Profundizar en sandboxing
│      Permiso, whitelisting, auditoría
│
└── Cap 4: Integración (próximo)
    └─ Tool Engine + Agentes
       Flujos complejos, pipelines
```

---

## 📚 Relación con otras fases

```
Fase 6: Tool Engine
├─ Necesita: Fase 1 (RBAC en core)
├─ Necesita: Fase 2 (IPC para UI)
├─ Completa: Sistema de seguridad
└─ Precede: Fase 7 (Model Manager)
```

---

## 🔗 Referencias

- **Documentación técnica**: [docs/03-Modules/TOOL_ENGINE.md](../../docs/03-Modules/TOOL_ENGINE.md)
- **Código fuente**: [crates/elap-core/src/tools/](../../crates/elap-core/src/tools/)
- **Tests**: 246 tests pasando ✅

---

**Autor**: ELAP Team  
**Versión**: 0.1.0  
**Última actualización**: 2026-08-05
