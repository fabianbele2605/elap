# 📋 FASE 2: Herramientas Inteligentes de Documentos

**Duración:** 2-3 semanas  
**Objetivo:** Agentes lean, generen y procesen documentos reales  
**Entrada:** Fase 1 completa (MVP + Contexto empresarial)  
**Salida:** Agentes con capacidades de documentos + base para RAG (Fase 3)

---

## 🎯 Objetivos Principales

1. **Integrar LangGraph** — Orquestación real de agentes (no solo chat)
2. **Herramientas de lectura** — PDF, Excel, Word, imágenes, CSV
3. **Herramientas de generación** — Reportes PDF, Excel, gráficos
4. **Base vectorial local** — chromadb + embeddings para RAG
5. **Pipeline de documentos** — Agentes procesan documentación corporativa

---

## 📦 Stack a Integrar

### Backend (Python gRPC)
```
langraph              # Orquestación de agentes
langgraph-checkpoint  # Persistencia de estado
sentence-transformers # Embeddings locales
chromadb              # Base vectorial local
pypdf                 # Lectura de PDFs
pdfplumber            # Extracción avanzada de PDFs
python-docx           # Lectura/escritura Word
openpyxl              # Lectura/escritura Excel
xlsxwriter            # Generación Excel avanzada
reportlab             # Generación de PDFs profesionales
matplotlib            # Gráficos
plotly                # Gráficos interactivos
kaleido               # Exportación de gráficos
pandas                # Procesamiento de datos
pillow                # Procesamiento de imágenes
easyocr               # OCR local
```

### Frontend (React)
```
Componentes para:
- Upload de documentos
- Vista previa de archivos
- Generador de reportes
- Gráficos interactivos
- Visor de documentos
```

---

## 📅 Timeline (Semanas)

### **Semana 1: LangGraph + Arquitectura**
- [ ] Integrar LangGraph en Python gRPC
- [ ] Diseñar agentes como grafos (estados, transiciones)
- [ ] Persistencia de conversaciones (memory/state)
- [ ] Tests básicos de orquestación

**Entregable:** Agentes orquestados con estado persistente

### **Semana 2: Lectura de Documentos**
- [ ] Implementar herramientas de lectura:
  - [ ] PDF (pypdf + pdfplumber)
  - [ ] Excel (openpyxl)
  - [ ] Word (python-docx)
  - [ ] CSV (pandas)
  - [ ] Imágenes + OCR (easyocr)
- [ ] Agentes pueden consultar documentos
- [ ] Búsqueda en documentos

**Entregable:** Agentes leen y analizan documentos

### **Semana 3: Generación + RAG Base**
- [ ] Herramientas de generación:
  - [ ] Reportes PDF (reportlab)
  - [ ] Excel con gráficos (xlsxwriter + matplotlib)
  - [ ] Exportación de datos
- [ ] Embeddings + chromadb:
  - [ ] Indexar documentos
  - [ ] Búsqueda vectorial
  - [ ] Recuperación de contexto
- [ ] Testing end-to-end

**Entregable:** Agentes generan reportes automáticos + RAG funcional

---

## 🔧 Hitos Técnicos

### Hito 1: LangGraph Integration
```
Rust/Python gRPC
      ↓
 LangGraph Agent
      ├── Memory (conversaciones)
      ├── State (contexto)
      └── Tools (herramientas)
```

### Hito 2: Document Tools
```
Agent Input
    ↓
Tool Selection (read_pdf, read_excel, etc.)
    ↓
Document Processing
    ↓
Response Generation
```

### Hito 3: RAG Base
```
Upload Document
    ↓
Chunk + Embed (sentence-transformers)
    ↓
Index (chromadb)
    ↓
Query → Retrieval → Agent Response
```

---

## 📝 Requisitos de Implementación

### Python Backend
- [ ] Actualizar requirements.txt con nuevas librerías
- [ ] Crear módulo `tools/documents.py`
- [ ] Crear módulo `tools/generation.py`
- [ ] Crear módulo `memory/rag.py`
- [ ] Integrar con ejecutor de agentes

### Rust Backend
- [ ] Nuevo endpoint: `/agents/{id}/tools` (listar herramientas)
- [ ] Nuevo endpoint: `/documents/upload` (subir documentos)
- [ ] Nuevo endpoint: `/documents/{id}/search` (búsqueda RAG)
- [ ] Storage de documentos (local filesystem + metadata)

### Frontend
- [ ] Componente `DocumentUploader`
- [ ] Componente `DocumentViewer`
- [ ] Componente `ReportGenerator`
- [ ] Integración con `/documents` API

---

## ✅ Criterios de Aceptación

### Funcionalidad
- [ ] Agente RRHH lee documento de políticas y responde preguntas
- [ ] Agente CEO genera reporte de ventas en PDF/Excel
- [ ] Agente Finanzas extrae datos de Excel y genera gráficos
- [ ] Búsqueda vectorial en documentos corporativos

### Calidad
- [ ] 80%+ cobertura de tests (Python)
- [ ] Documentación de herramientas actualizada
- [ ] Performance: <2s para lectura, <5s para generación
- [ ] No hay memory leaks en procesamiento de documentos

### UX
- [ ] Upload de documentos funcional
- [ ] Vista previa de archivos
- [ ] Descarga de reportes generados
- [ ] Búsqueda intuitiva

---

## 🚀 Entrada a Fase 3

Al completar Fase 2 tendremos:
- ✅ LangGraph para orquestación
- ✅ Herramientas de documentos (read/write)
- ✅ RAG local funcional
- ✅ Agentes pueden procesar documentación

**Fase 3 (Knowledge Pack Generator)** usará todo esto para:
1. Usuario completa formulario de empresa
2. Sistema genera 15 documentos profesionales
3. Documentos se indexan en RAG
4. Agentes responden con contexto empresarial real

---

## 📊 Estimación de Esfuerzo

| Componente | Dev | Tests | Docs | Total |
|-----------|-----|-------|------|-------|
| LangGraph | 2d | 1d | 0.5d | 3.5d |
| Doc Tools | 3d | 2d | 1d | 6d |
| RAG | 2d | 1d | 0.5d | 3.5d |
| Frontend | 2d | 1d | 0.5d | 3.5d |
| **TOTAL** | **9d** | **5d** | **2.5d** | **16.5d** |

**Total:** 3-4 semanas (1 desarrollador)

---

## 📚 Documentación a Generar

- [ ] `docs/FASE_2_IMPLEMENTATION.md` — Guía técnica
- [ ] `docs/API_DOCUMENTS.md` — Endpoints de documentos
- [ ] `docs/TOOLS_REFERENCE.md` — Referencia de herramientas
- [ ] `docs/RAG_GUIDE.md` — Cómo usar RAG
- [ ] Ejemplo: Agente genera reporte de Andina Foods

---

**Generado:** 2026-08-07  
**Siguiente:** Fase 3 — Knowledge Pack Generator
