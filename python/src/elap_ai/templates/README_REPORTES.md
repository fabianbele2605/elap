# 📊 Sistema de Reportes Profesionales ELAP

**Versión**: 1.0  
**Fecha**: 2026-08-10  
**Estado**: ✅ Implementado y listo para integrar

---

## 🎯 Descripción General

Sistema automático de generación de **reportes HTML profesionales** con:

✅ **KPI Cards** - Métricas destacadas con colores según estado (positivo/warning/alert)  
✅ **Tablas Dinámicas** - Datos estructurados con badges de estado  
✅ **Diseño Responsivo** - Se adapta a móvil, tablet y escritorio  
✅ **Integración con Agentes** - Cada agente puede generar reportes especializados  
✅ **Preparado para PDF** - HTML optimizado para impresión/descarga PDF  
✅ **Temas Corporativos** - Branding Andina Foods (azul/blanco)

---

## 🏗️ Arquitectura

```
python/src/elap_ai/
├── templates/
│   ├── professional_report.html          # Plantilla base (referencia)
│   ├── report_generator.py               # 📦 Generador dinámico (CORE)
│   ├── agent_report_integrator.py        # Integrador con agentes
│   └── README_REPORTES.md                # Este archivo
│
└── rest_server.py                        # API REST con endpoints
    ├── POST /api/reports/{agent_id}      # Generar reporte
    └── GET /api/reports/download/{file}  # Descargar HTML
```

---

## 📝 Componentes

### 1. **ReportGenerator** (`report_generator.py`)

Clase principal para generar HTML dinámico.

```python
from elap_ai.templates.report_generator import ReportGenerator, ReportData, KPICard

# Crear datos de reporte
data = ReportData(
    title="📊 Reporte Financiero",
    subtitle="Q3 2026",
    agent_name="CFO Assistant",
    kpi_cards=[
        KPICard("Ingresos", "$21.2M", "↑ 12%", "positive", "💰"),
        KPICard("Utilidad", "$1.2M", "↑ 8%", "positive", "📈"),
    ],
    executive_summary="Análisis de desempeño financiero...",
    sections=[...],
    recommendations=["Rec 1", "Rec 2"],
    next_steps_short=["Paso 1"],
    next_steps_medium=["Paso 2"]
)

# Generar HTML
generator = ReportGenerator()
html = generator.generate_html(data)

# Guardar archivo
generator.save_html(html, "/path/to/report.html")
```

### 2. **ReportData** - Estructura de Datos

```python
@dataclass
class ReportData:
    title: str                    # Título principal del reporte
    subtitle: str                 # Subtítulo
    agent_name: str               # Nombre del agente generador
    kpi_cards: List[KPICard]      # Tarjetas KPI (máximo 4)
    executive_summary: str        # Resumen ejecutivo (texto)
    sections: List[Dict]          # Secciones dinámicas
    recommendations: List[str]    # Lista de recomendaciones
    next_steps_short: List[str]   # Corto plazo
    next_steps_medium: List[str]  # Mediano plazo
    generated_date: Optional[str] # Fecha (auto si no se proporciona)
    company: str = "Andina Foods S.A.S."
```

### 3. **KPICard** - Tarjeta de Métrica

```python
@dataclass
class KPICard:
    label: str      # "Ingresos", "Utilidad", etc.
    value: str      # "$21.2M", "5.9%", etc.
    change: str     # "↑ 12%", "↓ 3%", "→"
    status: str     # "positive", "warning", "alert"
    icon: str       # "💰", "📈", "📊"
```

---

## 🔌 API REST Endpoints

### POST `/api/reports/{agent_id}` - Generar Reporte

**Request:**
```bash
curl -X POST http://localhost:5000/api/reports/finance \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Reporte Financiero",
    "subtitle": "Q3 2026",
    "executive_summary": "Análisis...",
    "kpi_data": [
      {
        "label": "Ingresos",
        "value": "$21.2M",
        "change": "↑ 12%",
        "status": "positive",
        "icon": "💰"
      }
    ],
    "sections": [],
    "recommendations": ["Rec 1"],
    "next_steps_short": ["Paso 1"],
    "next_steps_medium": ["Paso 2"]
  }'
```

**Response:**
```json
{
  "status": "success",
  "report_id": "a1b2c3d4",
  "filename": "reporte_finance_a1b2c3d4.html",
  "filepath": "/tmp/elap_reports/reporte_finance_a1b2c3d4.html",
  "html": "<html>...",
  "url": "/api/reports/download/reporte_finance_a1b2c3d4.html"
}
```

### GET `/api/reports/download/{filename}` - Descargar

```bash
curl -X GET http://localhost:5000/api/reports/download/reporte_finance_a1b2c3d4.html \
  -O
```

---

## 🚀 Integración con Agentes

### Opción A: Generar desde el Agente

```python
# En finance_agent.py, cfo_assistant.py, etc.

from elap_ai.templates.report_generator import (
    ReportGenerator, ReportData, KPICard
)

async def process_query(self, prompt: str) -> dict:
    # Procesar la consulta...
    response_text = await self._generate_finance_response(prompt)
    
    # Crear datos del reporte
    report_data = ReportData(
        title="📊 Reporte Financiero",
        subtitle="Análisis detallado",
        agent_name=self.name,
        kpi_cards=[
            KPICard("Ingresos", "$21.2M", "↑ 12%", "positive", "💰"),
            # ...más cards
        ],
        executive_summary=response_text[:500],
        sections=[...],
        recommendations=[...],
        next_steps_short=[...],
        next_steps_medium=[...]
    )
    
    # Generar HTML
    generator = ReportGenerator()
    html = generator.generate_html(report_data)
    
    return {
        'message': response_text,
        'html_report': html,
        'intent': 'financial_analysis'
    }
```

### Opción B: Usar AgentReportIntegrator

```python
from elap_ai.templates.agent_report_integrator import AgentReportIntegrator

async def generate_reports():
    async with AgentReportIntegrator() as integrator:
        # Reporte Financiero
        report = await integrator.create_finance_report(
            ingresos="$21,200 MM",
            utilidad="$1,260 MM",
            margen="5.9%",
            clientes="1,450",
            resumen="Andina Foods consolidó...",
            analisis="Eficiencia operativa excepcional...",
            recomendaciones=[
                "Optimizar rotación de inventarios",
                "Expandir a Caribe",
                "Digitalizar procesos"
            ]
        )
        
        print(f"✅ Reporte generado: {report['filename']}")
```

---

## 🎨 Estilos y Personalización

### Colores Corporativos

```css
Azul Principal:    #1e3c72, #2a5298
Fondo Claro:       #f5f7fa, #f8f9fa
Texto:             #333, #2c3e50
Verde (Positivo):  #27ae60
Naranja (Warning): #f39c12
Rojo (Alert):      #e74c3c
```

### Clases CSS Disponibles

```html
<!-- KPI Card -->
<div class="kpi-card positive">
  <div class="kpi-label">📊 Métrica</div>
  <div class="kpi-value">$1.2M</div>
  <div class="kpi-change">↑ 12%</div>
</div>

<!-- Badge -->
<span class="badge success">✓ Positivo</span>
<span class="badge warning">⚠ Revisar</span>
<span class="badge alert">✗ Crítico</span>

<!-- Highlight -->
<span class="highlight">texto importante</span>
```

---

## 📊 Ejemplos de Reportes Especializados

### 1. Reporte Financiero (CFO, Finance Agent)

```python
_create_finance_report(data)
# Métricas: Ingresos, Utilidad, Margen, ROE, Liquidez, Rotación
```

### 2. Reporte RRHH (HR Agent)

```python
_create_hr_report(data)
# Métricas: Empleados, Rotación, Antigüedad, Capacitaciones
```

### 3. Reporte Ventas (Sales Agent)

```python
_create_sales_report(data)
# Métricas: Ingresos, Clientes Nuevos, Tasa Cierre, Ticket Promedio
```

### 4. Reporte Ejecutivo (CEO Assistant)

```python
_create_executive_report(data)
# Métricas: Ingresos Anuales, Utilidad Operacional, ROE, Crecimiento
```

### 5. Reporte Procura (Compras Agent)

```python
_create_procurement_report(data)
# Métricas: Ahorro, Proveedores, Tiempo Entrega, Cumplimiento
```

---

## 🔄 Flujo Completo

```
┌─────────────────┐
│  User Query     │
│  (Frontend)     │
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│  Agent Ejecuta   │
│  (Python)        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Genera Datos     │
│ Estructurados    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ReportGenerator  │ ◄─── Crea HTML dinámico
│ .generate_html() │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ REST API         │
│ /api/reports/    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Archivo HTML     │
│ /tmp/elap_...    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Frontend descarga│
│ y muestra        │
└──────────────────┘
```

---

## 📦 Instalación de Dependencias

```bash
# Ninguna dependencia externa requerida
# El generador usa solo HTML/CSS puro + Python stdlib

# Las únicas dependencias son las que ya existen:
# - aiohttp (REST server)
# - httpx (cliente HTTP)
```

---

## ✅ Checklist de Integración

Cuando integres en un agente:

- [ ] Importar `ReportGenerator`, `ReportData`, `KPICard`
- [ ] Crear `ReportData` con datos del agente
- [ ] Llamar `generator.generate_html(data)`
- [ ] Retornar HTML en respuesta o guardarlo
- [ ] Probar endpoint REST `/api/reports/{agent_id}`
- [ ] Validar HTML en navegador
- [ ] Probar descarga PDF (Ctrl+P en navegador)

---

## 🔧 Troubleshooting

### Error: "Report not found"
✓ Verificar que el directorio `/tmp/elap_reports/` existe  
✓ Verificar permisos de escritura en `/tmp/`

### Error: "Invalid JSON"
✓ Validar formato del request JSON  
✓ Asegurar que `kpi_data` es una lista válida

### HTML no muestra correctamente
✓ Limpiar caché del navegador (Ctrl+Shift+Del)  
✓ Verificar que el HTML está bien formado (DevTools)

### Muy lento al generar
✓ Reducir cantidad de `sections` o `rows` en tablas  
✓ Usar strings cortos en datos

---

## 📚 Próximas Fases

**Fase 2 (Planificado):**
- Integración con Chart.js para gráficos interactivos
- Exportación a PDF con pdfkit o weasyprint
- Edición interactiva de reportes en frontend
- Plantillas personalizables por cliente

**Fase 3:**
- Reportes programados (ej: cada lunes a las 8 AM)
- Distribución por email
- Versioning de reportes históricos
- Comparativas período-a-período

---

## 📞 Contacto y Soporte

Para dudas o problemas:
- Revisar código en `report_generator.py`
- Consultar ejemplos en `agent_report_integrator.py`
- Ver reporte de referencia en `/notebooks/reporte_ejemplo.html`

**Última actualización**: 2026-08-10  
**Autor**: ELAP Intelligence System
