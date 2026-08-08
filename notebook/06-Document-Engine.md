# Libro 06: Document Engine - Generación Automática de Documentos Profesionales

**Capítulos:** 8  
**Nivel:** Intermedio  
**Duración de estudio:** 4-6 horas  
**Requisitos previos:** Libro 05 (Agents), conocimiento básico de Python y React

---

## 📚 Índice

1. Introducción al Problema
2. Arquitectura de Document Engine
3. Generadores de Documentos
4. Temas Corporativos
5. Integración con Agentes IA
6. REST API: Conectando Rust y Python
7. Interfaz de Usuario (Chat + Tab)
8. Caso Real: Andina Foods

---

## Capítulo 1: Introducción al Problema

### ¿Por qué automatizar documentos?

Imagina que eres una empresa con 100 empleados. Cada mes necesitas:
- Generar contratos laborales
- Crear reportes financieros
- Emitir facturas
- Producir políticas internas

**Sin automatización:**
- Tiempo: 2-3 horas por documento (plantilla + edición)
- Errores: Inconsistencias en formato, datos duplicados
- Costo: Personal administrativo permanente

**Con Document Engine (automatizado):**
- Tiempo: 30 segundos (usuario proporciona datos)
- Errores: Cero (formato consistente, contenido IA)
- Costo: Cero (ejecuta una vez, reutilizable)

### El flujo ideal

```
Usuario en chat:
"Necesito un contrato para Juan Pérez, gerente de ventas, $5M salario"
                    ↓
            Agente RRHH procesa
                    ↓
         Ollama genera contenido profesional
                    ↓
        DocumentEngine crea archivo Word
                    ↓
    Usuario descarga contrato en 1 segundo
```

### Desafíos técnicos resolvidos

1. **Contenido profesional:** ¿Cómo hacer que un LLM genere textos formales?
   - Solución: Prompts estructurados + Ollama (control total)

2. **Múltiples formatos:** ¿Word, PDF, Excel, PowerPoint?
   - Solución: Sistema modular de generadores

3. **Branding corporativo:** ¿Cómo aplicar temas personalizados?
   - Solución: Sistema de temas (YAML + templates)

4. **Integración:** ¿Cómo conectar Rust + Python + React?
   - Solución: REST API (simple, confiable, rápida)

---

## Capítulo 2: Arquitectura de Document Engine

### Diagrama de componentes

```
┌─────────────────────────────────────────────────────┐
│           DOCUMENT ENGINE (Python)                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │         DocumentEngine Core                 │   │
│  │  (Orquestador principal)                    │   │
│  └─────────────────────────────────────────────┘   │
│           ↓         ↓         ↓         ↓           │
│      Word       PDF      Excel    PowerPoint        │
│      Gen       Gen       Gen        Gen             │
│           ↓         ↓         ↓         ↓           │
│  ┌─────────────────────────────────────────────┐   │
│  │         Templates (Contract, Report, etc)  │   │
│  └─────────────────────────────────────────────┘   │
│           ↓                                         │
│  ┌─────────────────────────────────────────────┐   │
│  │  Temas (Andina Foods, Professional, etc)   │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
         ↑                              ↓
    Agentes IA                    Archivos generados
   (HR, Finance)           (/tmp/elap_documents/)
```

### Capas principales

**Capa 1: Núcleo (Core)**
- `DocumentEngine` class: Orquestador
- Métodos: `generate_word()`, `generate_pdf()`, etc.
- Responsabilidad: Decidir qué generador usar

**Capa 2: Generadores (Generators)**
- `WordGenerator`: Crea .docx con python-docx + docxtpl
- `PDFGenerator`: Convierte Word → PDF
- `ExcelGenerator`: Crea .xlsx con openpyxl
- `PowerPointGenerator`: Crea .pptx (future)

**Capa 3: Plantillas (Templates)**
- Archivos Word base (.docx)
- Variables Jinja2: `{{ variable_name }}`
- Ejemplo: `Empleado: {{ employee_name }}`

**Capa 4: Temas (Themes)**
- YAML con colores, fuentes, logos
- Ejemplos: "andina_foods", "professional"
- Aplicados en tiempo de compilación

### Flujo de datos

```
Datos de entrada
    ↓
DocumentEngine.generate_word(
    template="contract",
    data={
        "employee": "Juan Pérez",
        "salary": "5,000,000",
        ...
    },
    filename="contrato_Juan_Pérez.docx"
)
    ↓
[1] Cargar template base
[2] Aplicar tema (logo, colores)
[3] Renderizar variables Jinja2
[4] Generar archivo Word
    ↓
/tmp/elap_documents/contrato_Juan_Pérez.docx ✅
```

---

## Capítulo 3: Generadores de Documentos

### Word Generator (python-docx + docxtpl)

**¿Por qué Word?**
- Estándar corporativo
- Fácil de editar después
- Compatible con mail merge
- Soporta imágenes, tablas, estilos

**Proceso:**

```python
# Paso 1: Crear documento base
doc = Document('templates/contract_template.docx')

# Paso 2: Reemplazar variables
template_content = {
    'employee_name': 'Juan Pérez',
    'salary': '5,000,000',
    'benefits': 'Seguro médico, Bonificación',
    'responsibilities': ['Gestionar equipo', 'Alcanzar metas']
}

# Paso 3: Usar docxtpl para Jinja2
jinja_doc = DocxTemplate('template.docx')
jinja_doc.render(template_content)

# Paso 4: Guardar
jinja_doc.save('contrato_Juan_Pérez.docx')
```

**Ventajas:**
- ✅ Plantillas visuales (WYSIWYG)
- ✅ Soporte Jinja2
- ✅ Preserva formato original
- ✅ Genera .docx válidos

### PDF Generator

**Conversión Word → PDF:**

```python
from docx2pdf import convert

convert('contrato_Juan_Pérez.docx', 'contrato_Juan_Pérez.pdf')
```

**Alternativa:** LibreOffice headless (más robusto)
```bash
libreoffice --headless --convert-to pdf contrato.docx
```

### Excel Generator

Para reportes y datos tabulares:

```python
import openpyxl
from openpyxl.styles import Font, PatternFill

wb = openpyxl.Workbook()
ws = wb.active
ws['A1'] = 'Reporte Financiero'
ws['A1'].font = Font(bold=True, size=14)
ws.append(['Mes', 'Ingresos', 'Gastos', 'Utilidad'])
ws.append(['Enero', 100000, 50000, 50000])
wb.save('reporte.xlsx')
```

### PowerPoint Generator

**En desarrollo:**
```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()
slide_layout = prs.slide_layouts[5]  # Blank layout
slide = prs.slides.add_slide(slide_layout)
# Agregar texto, imágenes, etc.
prs.save('presentacion.pptx')
```

---

## Capítulo 4: Temas Corporativos

### ¿Qué es un tema?

Un **tema** es un conjunto de:
- Logo corporativo
- Colores (primario, secundario, acentos)
- Fuentes (encabezados, cuerpo)
- Estilos de tabla
- Espaciado

### Estructura YAML

```yaml
# themes.yaml
andina_foods:
  name: "Andina Foods"
  logo: "assets/logos/andina_foods.png"
  colors:
    primary: "#FF6B35"      # Naranja
    secondary: "#004E89"    # Azul marino
    accent: "#F77F00"       # Naranja oscuro
  fonts:
    heading: "Arial"
    body: "Calibri"
  metadata:
    company_name: "Distribuidora Andina Foods S.A.S."
    company_mission: "Conectar productores con comercio..."

professional:
  name: "Professional"
  logo: "assets/logos/professional.png"
  colors:
    primary: "#1F4788"
    secondary: "#4A90E2"
    accent: "#7B68EE"
```

### Aplicar tema a documento

```python
def generate_word(self, template_name, data, filename):
    # Cargar tema
    theme = self.load_theme(self.theme)
    
    # Aplicar a documento base
    doc = Document('templates/{}.docx'.format(template_name))
    
    # Reemplazar logo
    for para in doc.paragraphs:
        for run in para.runs:
            if run.text == '{{LOGO}}':
                run.text = ''  # Será reemplazado visualmente
    
    # Renderizar variables
    template = DocxTemplate('templates/{}.docx'.format(template_name))
    template.render({**data, **theme['metadata']})
    
    template.save(filename)
    return filename
```

---

## Capítulo 5: Integración con Agentes IA

### HRAgent: Contratos Laborales

**Arquitectura:**

```python
class HRAgent(Agent):
    def process_query(self, query: str) -> Dict:
        # [1] Detectar intent
        if self._tiene_datos_contrato(query):
            # [2] Extraer datos
            datos = self._extraer_datos(query)
            
            # [3] Generar contenido con Ollama
            contenido = await self._generar_contenido_ollama(datos)
            
            # [4] Crear documento
            resultado = await self.generate_contract(
                empresa=datos['empresa'],
                empleado=datos['empleado'],
                # ...
                ai_content=contenido
            )
            
            # [5] Retornar con link de descarga
            return {
                "intent": "contract_generated",
                "message": f"...[DESCARGAR CONTRATO]({download_url})...",
                "generated_file": resultado['path']
            }
```

**Ejemplo real:**

Usuario escribe:
```
Empresa: Andina Foods
Empleado: Juan Pérez
Cargo: Gerente de Ventas
Salario: 5.000.000
Fecha inicio: 01/09/2026
Beneficios: Seguro médico, Bonificación, Plan de pensión
Responsabilidades: Gestionar equipo, Alcanzar metas
```

El agente:
1. ✅ Detecta los 4 keywords (Empresa, Empleado, Cargo, Salario)
2. ✅ Extrae datos con regex
3. ✅ Llama Ollama:
   ```
   "Escribe un párrafo profesional para un contrato laboral de Juan Pérez,
    Gerente de Ventas en Andina Foods..."
   ```
4. ✅ Ollama responde:
   ```
   "En virtud del presente Contrato Laboral, Distribuidora Andina Foods S.A.S.,
    en adelante 'la Empresa', contrata a Juan Pérez en calidad de Gerente de Ventas..."
   ```
5. ✅ DocumentEngine genera Word con:
   - Logo Andina Foods
   - Datos personalizados
   - Contenido Ollama
   - Formato profesional

### FinanceAgent: Facturas y Reportes

Similar a HRAgent pero para documentos financieros:

```python
class FinanceAgent(Agent):
    async def generate_invoice(self, numero, cliente, items, ...):
        # Calcula subtotales, impuesto, total
        # Crea documento con formato de factura
        # Retorna link de descarga
```

**Ventaja:** El agente sabe **cómo** generar documentos, el DocumentEngine sabe **qué** generar.

---

## Capítulo 6: REST API - Conectando Rust y Python

### Problema: ¿Cómo comunican Rust y Python?

Opciones:
1. **gRPC:** Tipado, rápido, pero complejo
2. **REST HTTP:** Simple, accesible, suficiente
3. **Socket directo:** Acoplamiento fuerte ❌

Elegimos **REST HTTP**.

### Arquitectura

```
Usuario en React (Frontend)
         ↓
    Envía prompt
         ↓
Rust Backend (Puerto 3000)
         ↓ HTTP POST
Python REST API (Puerto 5000)
         ↓
    HRAgent procesa
         ↓
   DocumentEngine genera
         ↓
   Retorna JSON
         ↓
Rust sirve documento
         ↓
React descarga archivo
```

### Endpoint: POST /api/agents/{agent_id}/execute

**Request (desde Rust):**
```json
{
  "prompt": "Empresa: Andina...\nEmpleado: Juan...",
  "agent_id": "hr",
  "model": "glm4:9b"
}
```

**Response (desde Python):**
```json
{
  "agente_id": "hr",
  "estado": "completado",
  "respuesta": "✅ CONTRATO GENERADO...\n[DESCARGAR CONTRATO](http://...)",
  "generated_file": "/tmp/elap_documents/contrato_Juan_Pérez.docx",
  "tokens": {"prompt": 50, "completion": 100}
}
```

### Código Python (aiohttp)

```python
async def ejecutar_agente(request):
    data = await request.json()
    prompt = data.get('prompt')
    agent_id = data.get('agent_id')
    
    # Ejecutar agente
    if agent_id == 'hr':
        agent = hr_agent
    else:
        agent = finance_agent
    
    result = await agent.process_query(prompt)
    
    return web.json_response({
        'agente_id': agent_id,
        'estado': 'completado',
        'respuesta': result['message'],
        # ...
    })
```

### Código Rust (reqwest)

```rust
async fn ejecutar_agente(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Json(payload): Json<serde_json::Value>,
) -> Result<Json<EjecucionResponse>, StatusCode> {
    let client = reqwest::Client::new();
    let python_api_url = format!("http://127.0.0.1:5000/api/agents/{}/execute", id);
    
    let response = client
        .post(&python_api_url)
        .json(&payload)
        .send()
        .await?;
    
    let api_response = response.json::<EjecucionResponse>().await?;
    
    Ok(Json(api_response))
}
```

---

## Capítulo 7: Interfaz de Usuario

### Chat: Descargar desde mensaje

**Problema:** ¿Cómo mostrar un botón descargable en el chat?

**Solución:** Markdown links

```
[DESCARGAR CONTRATO](http://localhost:3000/documents/download/contrato_Juan.docx)
```

**React renderiza:**
```jsx
<a href={url} download className="bg-blue-600 text-white rounded px-4 py-2">
  DESCARGAR CONTRATO
</a>
```

**Código en ChatTab.tsx:**
```typescript
const linkMatch = paragraph.match(/\[(.*?)\]\((.*?)\)/);
if (linkMatch) {
  const [, linkText, linkUrl] = linkMatch;
  return (
    <a href={linkUrl} download className="bg-blue-600 hover:bg-blue-700 text-white rounded">
      {linkText}
    </a>
  );
}
```

### Tab "Documentos": Organizar y gestionar

**Funcionalidades:**
- Listado de documentos generados
- Búsqueda por nombre/empleado
- Filtro por tipo (contratos, facturas, reportes)
- Acciones:
  - ⬇️ Descargar
  - 🔄 Regenerar (próximamente)
  - 🗑️ Eliminar

**Componente:**
```typescript
export default function DocumentsTab() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  
  useEffect(() => {
    // Cargar documentos
    const filtered = documents.filter(doc =>
      (filterType === 'all' || doc.type === filterType) &&
      doc.filename.includes(searchTerm)
    );
    setFilteredDocs(filtered);
  }, [documents, searchTerm, filterType]);
  
  return (
    <div>
      {/* Búsqueda y filtros */}
      {/* Tabla de documentos */}
      {/* Estadísticas */}
    </div>
  );
}
```

---

## Capítulo 8: Caso Real - Distribuidora Andina Foods

### Contexto de la empresa

**Andina Foods S.A.S.**
- Sector: FMCG (Comercio mayorista)
- Ubicación: Barranquilla, Colombia
- Empleados: 187
- Clientes activos: 1.450

**Estructura:**
- Gerente General: Carlos Andrés Meléndez Ruiz
- Gerente Comercial: Jorge Luis Herrera Barros
- Gerente de RRHH: Andrés Felipe Cárdenas Molina
- Gerente de Operaciones: Marcela Isabel Torres Pacheco

**Financieros (2025):**
- Ingresos: $21.200 MM
- Utilidad neta: $1.260 MM
- Margen neto: 5,9%

### Caso de uso: Contratación

**Escenario:**
Andina Foods necesita contratar 5 nuevos gerentes. Actualmente:
- Tiempo por contrato: 2-3 horas (redacción manual)
- Total: 10-15 horas de trabajo administrativo
- Riesgo: Inconsistencias en formato

**Con Document Engine:**

```
Gerente de RRHH abre ELAP
     ↓
Va a tab "Chat" y escribe:
"Empresa: Distribuidora Andina Foods S.A.S.
 Empleado: Juan Pérez
 Cargo: Gerente de Ventas
 Salario: 5.000.000
 ..."
     ↓
Sistema:
- Agente RH detecta datos
- Ollama genera contenido profesional
- DocumentEngine crea contrato Word
- Contrato descargable en 30 segundos
     ↓
Repite para 4 empleados más
Total: 2-3 minutos en lugar de 10-15 horas
```

### Resultados esperados

✅ **Tiempo:** De 15 horas → 3 minutos (reducción 99%)  
✅ **Calidad:** Formato consistente, contenido profesional  
✅ **Costo:** Sin recurso administrativo  
✅ **Reusabilidad:** Plantilla reutilizable para futuras contrataciones

---

## Conclusiones

**Document Engine resuelve:**
1. ✅ Automatización de documentos
2. ✅ Integración IA (Ollama) + Python + Rust + React
3. ✅ Branding corporativo personalizado
4. ✅ Múltiples formatos (Word, PDF, Excel)
5. ✅ Interfaz intuitiva (Chat + Tab)

**Tecnologías clave:**
- Python: DocumentEngine, Agentes, REST API
- Rust: Backend, HTTP server, descarga de archivos
- React: UI, Markdown parsing, gestión de documentos
- Ollama: Generación de contenido IA
- Plantillas: docxtpl (Jinja2 + Word)

**Próximos pasos:**
1. Persistencia real (API `/api/documents`)
2. Regenerar documentos (con nuevos datos)
3. Templates adicionales (acuerdos, políticas, certificados)
4. Audit log (quién generó qué, cuándo)
5. Integración con sistemas reales (SAP, HRIS)

---

**Fin del Libro 06**

*Para más información, ver documentación técnica en `/docs/04-Document-Engine/`*
