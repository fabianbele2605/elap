# Enterprise Local AI Platform (ELAP)
## Software Architecture & Engineering Handbook — Índice

**Versión:** 1.0
**Fecha:** Agosto 2026
**Clasificación:** Documentación interna de ingeniería — BBLABS

---

Este handbook está dividido en libros independientes, cada uno versionable y mantenible por separado. Este primer paquete entrega los cuatro documentos fundacionales; el resto se genera bajo demanda para no degradar la calidad por saturación de contexto.

### Paquete entregado (Fase 1 — Fundacionales)

| # | Documento | Archivo | Estado |
|---|-----------|---------|--------|
| 1 | Product Vision Document | `01-product-vision.md` | ✅ Entregado |
| 2 | Business Requirements Document | `02-business-requirements.md` | ✅ Entregado |
| 3 | Software Requirements Specification (SRS) | `03-srs.md` | ✅ Entregado |
| 4 | Software Architecture Document (SAD) | `04-software-architecture.md` | ✅ Entregado |

### Pendientes (se generan libro por libro, bajo pedido)

| # | Documento | Prioridad sugerida |
|---|-----------|---------------------|
| 5 | Engineering Standards Manual | Alta |
| 6 | Desktop Application Architecture | Alta |
| 7 | AI Runtime Architecture | Alta |
| 8 | Plugin SDK Specification | Media |
| 9 | Tool Engine Specification | Media |
| 10 | Agent Framework Specification | Media |
| 11 | Memory System Specification | Media |
| 12 | Workflow Engine Specification | Media |
| 13 | Installer Architecture | Baja |
| 14 | Deployment Guide | Baja |
| 15 | Security Architecture | Alta |
| 16 | Performance Optimization Guide | Baja |
| 17 | Testing Strategy | Media |
| 18 | CI/CD Guide | Media |
| 19 | Developer Handbook | Baja |
| 20 | Administrator Handbook | Baja |

**Cómo continuar:** dime "Continuar con el Libro 5" (o el que necesites) y lo genero como archivo independiente, manteniendo consistencia con lo ya definido aquí (RUST core + Python AI Runtime, IPC vía gRPC/sockets locales, Tauri como shell de escritorio).
