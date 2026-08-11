# 🎯 PLAN DE REFACTORING FRONTEND REACT/TAURI - ELAP

**Fecha**: 2026-08-10  
**Versión**: 1.0  
**Estado**: ✅ LISTO PARA IMPLEMENTACIÓN

---

## 📌 RESUMEN EJECUTIVO

El frontend actual tiene **3 problemas principales**:

1. ❌ **Chat sobrecargado** - Muestra tablas, métricas y análisis completo en el chat
2. ❌ **Reportes limitados** - Solo HTML, no PDF/Word/Excel
3. ❌ **Tabs estáticos** - Doc History, Knowledge, History no cargan datos reales

**Solución**: Refactorizar en 3 fases independientes (40 horas totales)

---

## 🎯 OBJETIVOS

### FASE 1: Chat Limpio (4 horas) ⚡
- ChatTab solo muestra **resumen de 3 líneas máximo**
- Botón "📄 REPORTE DETALLADO" abre modal con todo
- Reduce cognitive load del usuario

### FASE 2: Reportes Multi-Formato (16 horas) ⚡⚡
Generar desde backend:
- ✅ **HTML** - Diseño profesional mejorado
- ✅ **PDF** - Nativo con weasyprint
- ✅ **Word** - Editable con python-docx
- ✅ **Excel** - Tablas y gráficos con openpyxl

### FASE 3: Tabs Dinámicos (12 horas) ⚡⚡⚡
- Doc History → Reportes realmente generados
- Knowledge → Fuentes de conocimiento del backend
- History → Conversaciones reales
- Tools → Herramientas disponibles en el sistema

---

## 📋 CAMBIOS TÉCNICOS

### Backend (Python)

**Nuevos módulos**:
```
python/src/elap_ai/
├── report_generators/
│   ├── html_generator.py      (HTML moderno con CSS)
│   ├── pdf_generator.py       (PDF con weasyprint)
│   ├── docx_generator.py      (Word con python-docx)
│   └── excel_generator.py     (Excel con openpyxl)
└── reports_store.py           (Historial de reportes)
```

**Nuevos endpoints**:
```
POST   /api/reports/{agent_id}/generate-html    → ReportData → HTML
POST   /api/reports/{agent_id}/generate-pdf     → ReportData → PDF (blob)
POST   /api/reports/{agent_id}/generate-docx    → ReportData → DOCX (blob)
POST   /api/reports/{agent_id}/generate-excel   → ReportData → XLSX (blob)
GET    /api/reports/list                        → Array de reportes generados
GET    /api/reports/download/{id}               → Descargar reporte
```

### Frontend (React/TypeScript)

**Archivos nuevos**:
```
web/src/
├── components/
│   ├── MessageSummary.tsx                      (Resumen corto de mensaje)
│   ├── tabs/DocHistoryTab.tsx                  (Reportes generados)
│   └── modals/ReportExportModal.tsx            (Botones descarga)
└── hooks/
    └── useReportExport.ts                      (Generar PDF/Word/Excel)
```

**Archivos a modificar**:
```
web/src/
├── components/tabs/ChatTab.tsx                 (Solo resumen)
├── components/tabs/HistoryTab.tsx              (Datos reales)
├── components/tabs/KnowledgeTab.tsx            (Datos reales)
├── components/tabs/ToolsTab.tsx                (Datos reales)
├── components/modals/ReportModal.tsx           (Agregar botones descarga)
├── hooks/useReport.ts                          (Nueva función exportarReporte)
└── App.tsx                                     (Agregar DocHistoryTab)
```

---

## 🔧 DEPENDENCIAS A INSTALAR

**Backend**:
```bash
pip install weasyprint         # PDF generation
pip install python-docx        # Word generation
pip install openpyxl           # Excel generation
pip install jinja2             # Template rendering
```

**Frontend**: Sin nuevas dependencias (usa Chart.js que ya existe)

---

## 📊 COMPARATIVA ANTES/DESPUÉS

| Aspecto | Antes | Después |
|---------|-------|---------|
| Reporte solo HTML | ✅ | HTML/PDF/DOCX/XLSX |
| Chat limpio | ❌ | ✅ |
| Tabs con datos reales | ❌ | ✅ |
| Botones descargar PDF | ❌ | ✅ |
| Doc History dinámico | ❌ | ✅ |
| Líneas ChatTab | 600 | 350 |

---

## 🚀 TIMELINE

```
DÍA 1 (4 horas):  FASE 1 - Chat Limpio
DÍA 2-3 (16h):    FASE 2 - Reportes Multi-Formato
DÍA 4 (12h):      FASE 3 - Tabs Dinámicos
DÍA 5 (4h):       QA + Testing + Merge

Total: 40 horas / 1 developer / 1 semana
```

---

## ✅ CRITERIOS DE ÉXITO

- [ ] Chat muestra máximo 3 líneas + botón "Ver más"
- [ ] Puedo generar PDF desde ReportModal
- [ ] Puedo generar Word desde ReportModal
- [ ] Puedo generar Excel desde ReportModal
- [ ] Doc History muestra reportes realmente generados
- [ ] History carga conversaciones del backend
- [ ] Knowledge muestra fuentes reales
- [ ] Todos los agentes funcionan correctamente

---

## 📝 PRÓXIMOS PASOS

1. ✅ Entender este plan
2. ⏭️ **INICIAR FASE 1** - Chat Limpio (4 horas)
3. ⏭️ FASE 2 - Reportes Multi-Formato (16 horas)
4. ⏭️ FASE 3 - Tabs Dinámicos (12 horas)
5. ⏭️ QA + Merge

---

**¿Comenzamos con la FASE 1 (Chat Limpio)?** ✅
