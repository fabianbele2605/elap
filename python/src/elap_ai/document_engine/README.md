# Document Engine - ELAP Fase 4

Generador profesional de documentos para **ELAP** (Enterprise Local AI Platform).

## ✨ Características

- 📄 **Word (.docx)** - Con python-docx y docxtpl
- 📊 **Excel (.xlsx)** - Con openpyxl y fórmulas
- 📋 **PDF** - Con WeasyPrint o Borb
- 🎨 **PowerPoint (.pptx)** - Con python-pptx
- 📧 **HTML** - Para correos y web
- 🎭 **Temas corporativos** - Andina Foods, Default, Professional
- 🔄 **Plantillas** - docxtpl para personalización

## 🚀 Uso Rápido

### 1. Instalación

```bash
pip install python-docx docxtpl openpyxl weasyprint pptx pyyaml
```

### 2. Generación de Contrato

```python
from elap_ai.document_engine import DocumentEngine

engine = DocumentEngine(theme="andina_foods", language="es")

contract_data = {
    "empresa": "Andina Foods",
    "empleado": "Juan Pérez",
    "cargo": "Gerente de Ventas",
    "salario": 5000000,
    "fecha_inicio": "2026-09-01",
    "beneficios": ["Seguro médico", "Bonificación anual"],
    "ai_content": "Contenido generado por Ollama..."
}

# Generar en múltiples formatos
word_path = engine.generate_word("contract", contract_data)
pdf_path = engine.generate_pdf("contract", contract_data)
html = engine.generate_html("contract", contract_data)
```

### 3. Generación de Factura

```python
invoice_data = {
    "numero": "FAC-2026-001",
    "cliente": "Supermercados La Prosperidad",
    "fecha_emision": "2026-08-15",
    "items": [
        {
            "descripcion": "Pasta de tomate 500g",
            "precio_unitario": 45000,
            "cantidad": 5
        }
    ]
}

excel_path = engine.generate_excel("invoice", invoice_data)
pdf_path = engine.generate_pdf("invoice", invoice_data)
```

### 4. Generación de Reporte

```python
report_data = {
    "titulo": "Reporte Trimestral Q3 2026",
    "periodo": "Q3 2026",
    "metricas": {
        "Ventas Totales": "$2,450,000",
        "Crecimiento": "+15%"
    },
    "contenido_ia": "Análisis generado por IA...",
    "conclusiones": "Conclusiones..."
}

word_path = engine.generate_word("report", report_data)
excel_path = engine.generate_excel("report", report_data)
ppt_path = engine.generate_powerpoint("report", report_data)
```

## 📂 Estructura

```
document_engine/
├── core.py                      # DocumentEngine principal
├── schemas/__init__.py          # Tipos de datos (Contract, Invoice, Report)
├── generators/
│   ├── word_generator.py        # .docx con docxtpl
│   ├── pdf_generator.py         # PDF con WeasyPrint
│   ├── excel_generator.py       # .xlsx con openpyxl
│   ├── powerpoint_generator.py  # .pptx con python-pptx
│   └── html_generator.py        # HTML para web/correos
├── templates/
│   ├── word/                    # Plantillas .docx
│   ├── excel/                   # Plantillas .xlsx
│   ├── pdf/                     # Plantillas HTML/CSS
│   └── powerpoint/              # Plantillas .pptx
├── assets/
│   ├── themes.yaml              # Configuración de temas
│   ├── logos/                   # Logos corporativos
│   └── colors/                  # Paletas de colores
└── examples.py                  # Ejemplos de uso
```

## 🎨 Temas Disponibles

### Andina Foods
```yaml
primary_color: "#2D5016"  # Verde oscuro
secondary_color: "#8BC34A"  # Verde claro
accent_color: "#FF6B35"  # Naranja
```

### Default Corporate
```yaml
primary_color: "#003366"  # Azul corporativo
secondary_color: "#0099FF"  # Azul claro
accent_color: "#FF6600"  # Naranja
```

### Professional
```yaml
primary_color: "#1A1A1A"  # Negro
secondary_color: "#666666"  # Gris
accent_color: "#0066CC"  # Azul
```

## 🔌 API REST

### POST /documents/generate

Generar documento profesional vía REST API.

```bash
curl -X POST http://localhost:3000/documents/generate \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "contract",
    "format": "word",
    "theme": "andina_foods",
    "data": {
      "empresa": "Andina Foods",
      "empleado": "Juan Pérez",
      "cargo": "Gerente",
      "salario": 5000000,
      "fecha_inicio": "2026-09-01",
      "beneficios": ["Seguro", "Bonificación"],
      "ai_content": "..."
    }
  }'
```

Response:
```json
{
  "status": "completed",
  "document_id": "uuid-here",
  "filename": "contract_20260815_143022.docx",
  "format": "word",
  "download_url": "/documents/download/contract_20260815_143022.docx",
  "size_kb": 2450.5
}
```

## 🤖 Integración con Agentes

Los agentes generan JSON estructurado, Document Engine los convierte a documentos profesionales.

```python
# Agente RRHH genera JSON
agent_output = {
    "tipo": "contrato",
    "empleado": "Juan Pérez",
    "cargo": "Gerente",
    "salario": 5000000,
    "ai_generated_content": "..."
}

# Document Engine convierte a documento profesional
engine = DocumentEngine(theme="andina_foods")
path = engine.generate_word("contract", agent_output)
```

## 📋 Tipos de Documentos Soportados

- **contract** - Contratos laborales
- **invoice** - Facturas y recibos
- **report** - Reportes empresariales
- **hr_document** - Documentos RR.HH.
- **proposal** - Propuestas y presupuestos
- **certificate** - Certificados

## 🔐 Seguridad

- Validación de datos de entrada
- Sanitización de contenido
- Firmas digitales (con pyHanko)
- Watermarks opcionales
- Encriptación en tránsito

## 📊 Ejemplos Completos

Ver `examples.py` para ejemplos funcionales:

```bash
cd python/src/elap_ai/document_engine
python examples.py
```

## 🚀 Próximas Características

- [ ] Plantillas personalizadas por cliente
- [ ] Signatures digitales
- [ ] Watermarks automáticos
- [ ] Merging de documentos
- [ ] Conversión entre formatos
- [ ] Generación de índices automáticos
- [ ] Anexos dinámicos

## 📖 Documentación

Para más detalles, ver:
- `/docs/04-Fase4-DocumentEngine/` - Documentación técnica
- `/notebook/` - Guía didáctica

---

**Fase 4: Document Engine** - Generadores profesionales integrados con IA local.
