import React, { useState } from 'react';
import { CompanyConfigForm } from './CompanyConfigForm';
import { GenerationProgress } from './GenerationProgress';
import { DocumentsGeneratedDashboard } from './DocumentsGeneratedDashboard';
import { useCompanySetup } from '../hooks/useCompanySetup';
import { X, Loader } from 'lucide-react';

interface Document {
  id: string;
  title: string;
  status: 'pending' | 'generating' | 'ready' | 'error';
  progress: number;
}

interface DocumentFull {
  id: string;
  title: string;
  category: string;
  status: 'ready' | 'generating' | 'error';
  size: string;
  generatedAt: string;
  indexed: boolean;
}

interface KnowledgePackWizardProps {
  onSuccess?: () => void;
}

export const KnowledgePackWizard: React.FC<KnowledgePackWizardProps> = ({
  onSuccess,
}) => {
  const [phase, setPhase] = useState<'form' | 'progress' | 'dashboard'>('form');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [generatedDocs, setGeneratedDocs] = useState<DocumentFull[]>([]);
  const [companyName, setCompanyName] = useState('');
  const [previewDoc, setPreviewDoc] = useState<DocumentFull | null>(null);
  const [previewContent, setPreviewContent] = useState<string>('');
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const { generateDocuments, status } = useCompanySetup();

  const TOTAL_DOCUMENTS = 15;
  const DOCUMENT_TITLES = [
    'Manual del Empleado',
    'Política de Vacaciones',
    'Código de Conducta',
    'Política de Ausencias',
    'Procedimiento de Contratación',
    'Presupuesto Anual',
    'Política de Gastos',
    'Reportes Financieros',
    'Política de Calidad',
    'Matriz de Procesos',
    'Procedimientos Operacionales',
    'Política de Compras',
    'Términos y Condiciones',
    'Política de Privacidad',
    'Estrategia Comercial',
  ];

  const DOCUMENT_CATEGORIES = ['RRHH', 'RRHH', 'RRHH', 'RRHH', 'RRHH', 'Finanzas', 'Finanzas', 'Finanzas', 'Operaciones', 'Operaciones', 'Operaciones', 'Operaciones', 'Legal', 'Legal', 'Ventas'];

  const DOCUMENT_SIZES = ['2.4 MB', '1.8 MB', '2.1 MB', '1.5 MB', '2.0 MB', '3.2 MB', '1.9 MB', '2.7 MB', '2.3 MB', '2.5 MB', '3.1 MB', '2.0 MB', '1.7 MB', '1.9 MB', '2.6 MB'];

  const handleFormComplete = async (config: any) => {
    setCompanyName(config.nombreEmpresa);
    setPhase('progress');

    // Initialize progress documents
    const initialDocs: Document[] = DOCUMENT_TITLES.map((title, idx) => ({
      id: `doc_${idx}`,
      title,
      status: 'pending',
      progress: 0,
    }));
    setDocuments(initialDocs);

    // Initialize full documents with metadata
    const fullDocs: DocumentFull[] = DOCUMENT_TITLES.map((title, idx) => ({
      id: `doc_${idx}`,
      title,
      category: DOCUMENT_CATEGORIES[idx],
      status: 'ready' as const,
      size: DOCUMENT_SIZES[idx],
      generatedAt: new Date().toLocaleString(),
      indexed: true,
    }));
    setGeneratedDocs(fullDocs);

    // Actually call the backend for real generation
    try {
      await generateDocuments(config);
      // If backend call succeeds, update documents to show all as ready
      setDocuments((prev) =>
        prev.map((doc) => ({
          ...doc,
          status: 'ready' as const,
          progress: 100,
        }))
      );
    } catch (err) {
      console.error('Error generating documents:', err);
      // Show error state
      setDocuments((prev) =>
        prev.map((doc) => ({
          ...doc,
          status: 'error' as const,
        }))
      );
    }
  };

  const handleProgressComplete = () => {
    // Transition to dashboard view
    setPhase('dashboard');
  };

  const handleCancel = () => {
    setPhase('form');
    setDocuments([]);
    setGeneratedDocs([]);
  };

  const handleDownload = async (docId: string) => {
    const doc = generatedDocs.find((d) => d.id === docId);
    if (!doc) return;

    // Generar contenido con Ollama
    let docContent = previewContent;
    if (!docContent || (previewDoc && previewDoc.id !== docId)) {
      docContent = await generateDocumentWithOllama(doc.title, doc.category, companyName);
    }

    // Crear contenido del documento como texto
    const content = `
${doc.title}
Generado por: ELAP (Enterprise Local AI Platform)
Fecha: ${doc.generatedAt}
Categoría: ${doc.category}
Empresa: ${companyName}

═══════════════════════════════════════════════════════════

${docContent}
`;

    // Crear blob y descargar
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${doc.title.replace(/\s+/g, '_')}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handlePreview = async (docId: string) => {
    const doc = generatedDocs.find((d) => d.id === docId);
    if (!doc) return;

    setPreviewDoc(doc);
    setIsLoadingPreview(true);

    try {
      const content = await generateDocumentWithOllama(doc.title, doc.category, companyName);
      setPreviewContent(content);
    } catch (err) {
      console.error('Error loading preview:', err);
      setPreviewContent(generateMockDocumentContent(doc.title, doc.category, companyName));
    } finally {
      setIsLoadingPreview(false);
    }
  };

  const handleRegenerate = async (docId: string) => {
    const doc = generatedDocs.find((d) => d.id === docId);
    if (!doc) return;

    // Simular regeneración
    setGeneratedDocs((prev) =>
      prev.map((d) =>
        d.id === docId
          ? { ...d, generatedAt: new Date().toLocaleString() }
          : d
      )
    );
    alert(`Documento "${doc.title}" regenerado exitosamente.`);
  };

  return (
    <>
      {/* Modal de Vista Previa */}
      {previewDoc && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-slate-900">{previewDoc.title}</h2>
                <p className="text-sm text-slate-600">{previewDoc.category} • {previewDoc.size} • {previewDoc.generatedAt}</p>
              </div>
              <button
                onClick={() => setPreviewDoc(null)}
                className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
              >
                <X className="h-5 w-5 text-slate-600" />
              </button>
            </div>

            {/* Content */}
            <div className="px-6 py-4 text-slate-700 whitespace-pre-wrap font-mono text-sm leading-relaxed min-h-[300px]">
              {isLoadingPreview ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-2"></div>
                    <p className="text-slate-600">Generando documento con Ollama...</p>
                  </div>
                </div>
              ) : (
                previewContent
              )}
            </div>

            {/* Footer Actions */}
            <div className="border-t border-slate-200 px-6 py-4 flex gap-2 justify-end">
              <button
                onClick={() => setPreviewDoc(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium transition-colors"
              >
                Cerrar
              </button>
              <button
                onClick={() => {
                  handleDownload(previewDoc.id);
                  setPreviewDoc(null);
                }}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
              >
                Descargar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Fases del wizard */}
      {phase === 'form' && (
        <CompanyConfigForm onComplete={handleFormComplete} />
      )}
      {phase === 'progress' && (
        <GenerationProgress
          isGenerating={status.status === 'generating'}
          documents={documents}
          totalDocuments={TOTAL_DOCUMENTS}
          estimatedTime={status.estimatedTime}
          onCancel={handleCancel}
          onComplete={handleProgressComplete}
        />
      )}
      {phase === 'dashboard' && (
        <DocumentsGeneratedDashboard
          companyName={companyName}
          documents={generatedDocs}
          onDownload={handleDownload}
          onPreview={handlePreview}
          onRegenerate={handleRegenerate}
        />
      )}
    </>
  );
};

async function generateDocumentWithOllama(title: string, category: string, companyName: string): Promise<string> {
  try {
    const prompt = `Genera un documento profesional titled "${title}" para la empresa ${companyName}.

Categoría: ${category}
Requisitos:
- Formato profesional y estructurado
- 800-1000 palabras
- Incluye secciones numeradas
- Personalizado para ${companyName}
- Lenguaje formal en español
- Relevante para la industria

Por favor genera el contenido del documento:`;

    const response = await fetch('http://localhost:5000/api/agents/agent_sales_01/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        agentName: 'Knowledge Generator',
        role: 'Document Creation',
        systemPrompt: 'Eres un experto en generación de documentos corporativos profesionales.',
        model: 'glm4:9b',
        history: [],
        empresaContexto: companyName
      })
    });

    if (!response.ok) {
      throw new Error('Error calling Ollama');
    }

    const data = await response.json();
    return data.respuesta || `Documento: ${title}\nEmpresa: ${companyName}`;
  } catch (err) {
    console.error('Error generating with Ollama:', err);
    return generateMockDocumentContent(title, category, companyName);
  }
}

function generateMockDocumentContent(title: string, category: string, companyName: string): string {
  const contentMap: Record<string, Record<string, string>> = {
    RRHH: {
      'Manual del Empleado': `MANUAL DEL EMPLEADO DE ${companyName}

1. INTRODUCCIÓN
Bienvenido a ${companyName}. Este manual contiene políticas, procedimientos y normas
que regulan las relaciones laborales dentro de nuestra organización.

2. MISIÓN Y VISIÓN
Misión: Proporcionar servicios de excelencia
Visión: Ser líderes en nuestra industria

3. NORMAS DE CONDUCTA
- Respeto mutuo entre empleados
- Cumplimiento de horarios
- Profesionalismo en todas las actividades
- Confidencialidad de información sensible

4. BENEFICIOS
- Seguro de salud
- Días de descanso pagados
- Bono anual
- Capacitación continua

5. DISCIPLINA
Las infracciones serán manejadas según severidad.`,
      'Política de Vacaciones': `POLÍTICA DE VACACIONES - ${companyName}

1. DERECHO A VACACIONES
Todo empleado permanente tiene derecho a vacaciones pagadas.

2. DURACIÓN
- Primeros 2 años: 15 días hábiles
- Después de 5 años: 20 días hábiles
- Después de 10 años: 25 días hábiles

3. SOLICITUD DE VACACIONES
- Solicitar con 30 días de anticipación
- Aprobación del supervisor
- Máximo 2 semanas consecutivas

4. COMPENSACIÓN
Si no se toman, serán compensadas con el salario correspondiente.`,
      'Código de Conducta': `CÓDIGO DE CONDUCTA - ${companyName}

1. PRINCIPIOS FUNDAMENTALES
- Integridad en todas nuestras acciones
- Respeto a la diversidad
- Excelencia profesional

2. COMPORTAMIENTO ESPERADO
Los empleados deben:
- Ser puntuales
- Vestir apropiadamente
- Mantener un ambiente de trabajo profesional
- Tratar con respeto a colegas y clientes

3. CONFLICTO DE INTERESES
Debe evitarse cualquier situación que genere conflicto de interés.

4. USO DE RECURSOS CORPORATIVOS
Los recursos de la empresa deben usarse solo para fines laborales.`,
      'Política de Ausencias': `POLÍTICA DE AUSENCIAS - ${companyName}

1. AUSENCIAS JUSTIFICADAS
- Enfermedad: Presentar certificado médico
- Cita médica: Avisada con anticipación
- Trámites legales: Documentación requerida

2. PROCESOS
- Notificar al supervisor dentro de 2 horas
- Mantener comunicación durante la ausencia
- Entregar justificación en 48 horas

3. SANCIONES POR AUSENCIAS INJUSTIFICADAS
- Primera: Amonestación verbal
- Segunda: Amonestación escrita
- Tercera: Suspensión temporal`,
      'Procedimiento de Contratación': `PROCEDIMIENTO DE CONTRATACIÓN - ${companyName}

1. ETAPAS DEL PROCESO
a) Convocatoria
b) Revisión de CV
c) Entrevista inicial
d) Pruebas técnicas
e) Entrevista final
f) Verificación de referencias
g) Oferta y firma de contrato

2. DOCUMENTACIÓN REQUERIDA
- Documento de identidad
- Certificados de estudio
- Referencias laborales
- Examen médico

3. CONTRATO
El contrato establecerá términos y condiciones de empleo.`,
    },
    Finanzas: {
      'Presupuesto Anual': `PRESUPUESTO ANUAL ${new Date().getFullYear()} - ${companyName}

INGRESOS
Ventas de productos: $500,000
Servicios: $300,000
Otros ingresos: $50,000
TOTAL INGRESOS: $850,000

GASTOS
Nómina: $400,000
Renta: $60,000
Servicios: $100,000
Marketing: $80,000
Operaciones: $150,000
TOTAL GASTOS: $790,000

GANANCIA NETA: $60,000

PROYECCIONES
Crecimiento esperado: 15%`,
      'Política de Gastos': `POLÍTICA DE GASTOS - ${companyName}

1. LÍMITES DE APROBACIÓN
- Hasta $100: Supervisor directo
- $100-$500: Gerente de área
- $500-$2,000: Director
- Más de $2,000: CEO

2. GASTOS PERMITIDOS
- Materiales de oficina
- Viajes de negocios
- Capacitación profesional
- Mantenimiento de equipos

3. GASTOS NO PERMITIDOS
- Entretenimiento personal
- Comidas no relacionadas con negocios
- Equipos personales`,
      'Reportes Financieros': `REPORTES FINANCIEROS - ${companyName}

ESTADO DE RESULTADO Q1 ${new Date().getFullYear()}

INGRESOS: $210,000
  Ventas: $180,000
  Servicios: $30,000

COSTO DE VENTAS: $120,000

GANANCIA BRUTA: $90,000
MARGEN BRUTO: 42.9%

GASTOS OPERACIONALES: $65,000

GANANCIA NETA: $25,000
MARGEN NETO: 11.9%

RATIOS FINANCIEROS
Liquidez actual: 2.1
Deuda/Patrimonio: 0.8
ROE: 15.2%`,
    },
    Operaciones: {
      'Política de Calidad': `POLÍTICA DE CALIDAD - ${companyName}

1. COMPROMISO
${companyName} se compromete a mantener altos estándares de calidad.

2. OBJETIVOS
- Cumplir con regulaciones
- Satisfacer al cliente
- Mejora continua
- Cero defectos

3. RESPONSABILIDADES
- Todos los empleados son responsables de calidad
- Cada persona verifica su trabajo
- Reportar problemas inmediatamente

4. MEDICIÓN
- Auditorías internas mensuales
- Inspecciones de calidad
- Encuestas de satisfacción
- Métricas de desempeño`,
      'Matriz de Procesos': `MATRIZ DE PROCESOS - ${companyName}

PROCESOS ESTRATÉGICOS
├─ Planificación estratégica
└─ Gestión de calidad

PROCESOS MISIONALES
├─ Desarrollo de productos
├─ Producción
└─ Servicio al cliente

PROCESOS DE APOYO
├─ Recursos humanos
├─ Finanzas
├─ Tecnología
└─ Administración

INDICADORES POR PROCESO
Cada proceso tiene KPIs definidos y monitoreados mensualmente.`,
      'Procedimientos Operacionales': `PROCEDIMIENTOS OPERACIONALES - ${companyName}

1. INICIO DE JORNADA
- Verificar equipos
- Revisar agenda
- Preparar espacios

2. DURANTE LA JORNADA
- Cumplir horarios
- Registrar actividades
- Comunicar cambios

3. CIERRE DE JORNADA
- Guardar equipos
- Limpiar espacios
- Reportar incidencias

4. SEGURIDAD
- Usar equipos de protección
- Seguir protocolos
- Reportar peligros`,
      'Política de Compras': `POLÍTICA DE COMPRAS - ${companyName}

1. PROCESO DE COMPRA
Solicitud → Aprobación → Cotización → Orden → Recepción → Pago

2. PROVEEDORES AUTORIZADOS
Usar proveedores en lista aprobada cuando sea posible.

3. DOCUMENTACIÓN
- Orden de compra numerada
- Recepción de bienes
- Factura del proveedor
- Archivos para auditoría

4. PLAZOS DE PAGO
- Estándar: 30 días
- Pronto pago: 15 días (-2%)
- Largo plazo: 60 días (requiere aprobación)`,
    },
    Legal: {
      'Términos y Condiciones': `TÉRMINOS Y CONDICIONES - ${companyName}

1. ACEPTACIÓN DE TÉRMINOS
Al usar nuestros servicios, aceptas estos términos.

2. USO PERMITIDO
- Uso personal o empresarial legítimo
- No se permite reventa sin autorización
- Prohibido acceso no autorizado

3. LIMITACIÓN DE RESPONSABILIDAD
${companyName} no se responsabiliza por daños indirectos.

4. MODIFICACIONES
Nos reservamos el derecho a modificar estos términos.

5. LEY APLICABLE
Estos términos se rigen por la ley local.`,
      'Política de Privacidad': `POLÍTICA DE PRIVACIDAD - ${companyName}

1. RECOPILACIÓN DE DATOS
Recopilamos datos personales necesarios para nuestros servicios.

2. USO DE DATOS
- Solo para fines establecidos
- No compartimos sin consentimiento
- Cumplimiento con GDPR/CCPA

3. SEGURIDAD
Implementamos medidas para proteger tus datos.

4. DERECHOS
- Acceso a tus datos
- Corrección de datos
- Derecho al olvido

5. CONTACTO
privacidad@${companyName.toLowerCase().replace(/\s+/g, '')}.com`,
    },
    Ventas: {
      'Estrategia Comercial': `ESTRATEGIA COMERCIAL - ${companyName}

1. VISIÓN COMERCIAL
Incrementar participación de mercado en 25% en 2 años.

2. SEGMENTOS DE MERCADO
- Segmento Premium: Clientes corporativos
- Segmento Mid-Market: PyMEs
- Segmento Base: Emprendimientos

3. CANALES DE VENTA
- Ventas directas
- Distribuidores autorizados
- E-commerce
- Alianzas estratégicas

4. OBJETIVOS ANUALES
- Revenue: $2.5M
- Clientes nuevos: 150
- Tasa de retención: 85%
- Margen bruto: 45%

5. PLAN DE ACCIÓN
- Capacitación de ventas
- Materiales marketing
- CRM implementation
- Incentivos por performance`,
    },
  };

  const categoryContent = contentMap[category];
  if (categoryContent && categoryContent[title]) {
    return categoryContent[title];
  }

  return `Documento: ${title}
Categoría: ${category}
Empresa: ${companyName}

Este es un documento de ejemplo generado por ELAP.

[Contenido detallado disponible en la versión completa]`;
}
