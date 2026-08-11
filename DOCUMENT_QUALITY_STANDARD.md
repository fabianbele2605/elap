# 📋 DOCUMENT QUALITY STANDARD v1.0 — ELAP

**Estándar de calidad profesional para generación automática de documentos.**

Basado en metodología Claude + best practices de office automation.

---

## CAPA 1 — Herramientas por formato

| Formato | Librería Principal | Validador | Conversión QA |
|---------|------------------|-----------|--------------|
| **PDF** | weasyprint | pdfplumber | pdfplumber text extraction |
| **Word** | python-docx | lxml (XSD) | LibreOffice headless |
| **Excel** | openpyxl | openpyxl + pandas | LibreOffice headless |
| **PPT** | python-pptx | lxml (XSD) | LibreOffice headless |

---

## CAPA 2 — Reglas obligatorias por formato

### **PDF**
- ✅ Portada profesional (primera página)
- ✅ Tabla de contenidos automática
- ✅ Números de página ("Página X de Y")
- ✅ Encabezados de sección consistentes
- ✅ Mínimo 1 gráfica si hay datos
- ✅ Texto seleccionable (no imagen)
- ❌ NO: placeholders "lorem ipsum", texto cortado, márgenes <0.5"

### **Word**
- ✅ Portada con metadata
- ✅ Tabla de contenidos automática (con estilos Heading)
- ✅ Números de página
- ✅ Saltos de página reales (page_break), no `\n`
- ✅ Listas con numeración real, no viñetas de texto
- ✅ Tablas con encabezados formateados
- ❌ NO: estilos inline, mezcla de fuentes, color sin contraste

### **Excel**
- ✅ Fórmulas reales, NUNCA hardcodes
- ✅ Validación de datos en celdas de input
- ✅ Formato condicional (color por valores)
- ✅ Comentarios en celdas con supuestos
- ✅ Convención de colores: azul=input, negro=fórmula, verde=link, amarillo=completar
- ✅ Múltiples hojas organizadas
- ❌ NO: resultados pegados como números, fórmulas que circulan, celdas vacías sin razón

### **TODOS LOS FORMATOS**
- ✅ Datos reales (del agente/base de datos)
- ✅ Colores corporativos consistentes
- ✅ Márgenes profesionales (0.75" - 1")
- ✅ Tipografía profesional (Arial, Calibri, Georgia - nunca Comic Sans)
- ✅ Contraste suficiente (WCAG AA mínimo)
- ❌ NO: texto placeholder, "TODO", "[insertar X]", "xxx", "lorem"

---

## CAPA 3 — Proceso de construcción

```
Agente (respuesta) 
    ↓
Parsing (extraer datos, métricas, tablas)
    ↓
Estructura (outline, secciones, TOC)
    ↓
Render (generar archivo con librerías)
    ↓
QA AUTOMÁTICO (validaciones)
    ↓
Reporte de calidad
    ↓
Entrega (archivo + reporte)
```

---

## CAPA 4 — QA AUTOMÁTICO (CRÍTICO)

Cada documento DEBE pasar estos checks antes de entregarse:

### **4.1 Validación de esquema**
- Word: validar contra XSD de Office Open XML
- Excel: validar contra XSD de Office Open XML
- PPT: validar contra XSD de Office Open XML
- PDF: validar PDF structure (text vs image)

### **4.2 Validación de contenido**
- ❌ Detectar "TODO", "[insertar", "xxx", "lorem", "undefined"
- ❌ Detectar valores NULL/None en tablas
- ❌ Detectar celdas vacías sin razón (Excel)
- ❌ Detectar fórmulas con errores (#DIV/0!, #REF!, #N/A)
- ❌ Detectar estilos inconsistentes

### **4.3 Validación visual**
- Convertir a PDF (LibreOffice)
- Extraer texto con pdfplumber
- Detectar texto cortado (líneas < 20 chars en párrafos largos)
- Detectar overlap (múltiples textos en misma posición)
- Detectar márgenes insuficientes

### **4.4 Validación de datos**
- Excel: recalcular todas las fórmulas
- Tablas: verificar que no haya celdas vacías críticas
- Validar que los números tengan sentido (no negativos donde no aplica)

### **4.5 Salida de QA**
Cada documento genera un **reporte QA** con:
```json
{
  "document_name": "HR_Analysis_2026-08-10.pdf",
  "timestamp": "2026-08-10T15:42:00Z",
  "format": "pdf",
  "agent": "HR Agent",
  "quality_score": 98,
  "checks": {
    "schema_validation": "✅ PASS",
    "content_validation": "✅ PASS (0 issues)",
    "visual_validation": "✅ PASS",
    "data_validation": "✅ PASS",
    "total_pages": 8,
    "total_charts": 2,
    "total_tables": 5
  },
  "warnings": [],
  "status": "READY_FOR_DELIVERY"
}
```

---

## CAPA 5 — Entrega

**Archivo + Reporte de QA**

Usuario recibe:
1. ✅ Documento (PDF/Word/Excel)
2. ✅ Reporte QA (JSON o texto)
3. ✅ URL de descarga

Si algún check falla:
- ⚠️ Reporte con detalles del problema
- 📌 Archivo NO se entrega (solo logs)
- 🔧 Sistema auto-intenta arreglarlo

---

## IMPLEMENTACIÓN CHECKLIST

- [ ] Módulo: `document_validators.py` (validaciones automáticas)
- [ ] Módulo: `document_qa_reporter.py` (reportes de QA)
- [ ] Integrar en: `document_generators.py` (PDF, Word, Excel)
- [ ] Tests: validadores para cada formato
- [ ] Documentación: guía de troubleshooting

---

## REFERENCIAS

- Metodología: Claude Document Quality Framework
- Stack: Python 3.11+, weasyprint, python-docx, openpyxl, pdfplumber
- Standard: WCAG 2.1 AA para accesibilidad

**Última actualización:** 2026-08-10  
**Versión:** 1.0 - Foundation
