import React, { useEffect } from 'react';
import { CheckCircle, AlertCircle, Loader } from 'lucide-react';

interface Document {
  id: string;
  title: string;
  status: 'pending' | 'generating' | 'ready' | 'error';
  progress: number;
}

interface GenerationProgressProps {
  isGenerating: boolean;
  documents: Document[];
  totalDocuments: number;
  estimatedTime?: string;
  onCancel?: () => void;
  onComplete?: () => void;
}

const DOCUMENT_LIST = [
  { id: 'manual_empleado', title: 'Manual del Empleado', category: 'RRHH' },
  { id: 'politica_vacaciones', title: 'Política de Vacaciones', category: 'RRHH' },
  { id: 'codigo_conducta', title: 'Código de Conducta', category: 'RRHH' },
  { id: 'politica_ausencias', title: 'Política de Ausencias', category: 'RRHH' },
  { id: 'procedimiento_contratacion', title: 'Procedimiento de Contratación', category: 'RRHH' },
  { id: 'presupuesto_anual', title: 'Presupuesto Anual', category: 'Finanzas' },
  { id: 'politica_gastos', title: 'Política de Gastos', category: 'Finanzas' },
  { id: 'reportes_financieros', title: 'Reportes Financieros', category: 'Finanzas' },
  { id: 'politica_calidad', title: 'Política de Calidad', category: 'Operaciones' },
  { id: 'matriz_procesos', title: 'Matriz de Procesos', category: 'Operaciones' },
  { id: 'procedimientos_operacionales', title: 'Procedimientos Operacionales', category: 'Operaciones' },
  { id: 'politica_compras', title: 'Política de Compras', category: 'Operaciones' },
  { id: 'terminos_condiciones', title: 'Términos y Condiciones', category: 'Legal' },
  { id: 'politica_privacidad', title: 'Política de Privacidad', category: 'Legal' },
  { id: 'estrategia_comercial', title: 'Estrategia Comercial', category: 'Ventas' },
];

export const GenerationProgress: React.FC<GenerationProgressProps> = ({
  isGenerating,
  documents: providedDocuments,
  totalDocuments,
  estimatedTime,
  onCancel,
  onComplete,
}) => {
  const documents = providedDocuments.length > 0 ? providedDocuments : DOCUMENT_LIST.map((doc) => ({
    ...doc,
    status: 'pending' as const,
    progress: 0,
  }));

  const completedCount = documents.filter((d) => d.status === 'ready').length;
  const errorCount = documents.filter((d) => d.status === 'error').length;
  const generatingCount = documents.filter((d) => d.status === 'generating').length;
  const pendingCount = documents.filter((d) => d.status === 'pending').length;

  const overallProgress = Math.round((completedCount / totalDocuments) * 100);

  useEffect(() => {
    if (!isGenerating && completedCount === totalDocuments && onComplete) {
      setTimeout(onComplete, 1500);
    }
  }, [isGenerating, completedCount, totalDocuments, onComplete]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Generando Knowledge Pack
          </h1>
          <p className="text-slate-600">
            Se están creando {totalDocuments} documentos personalizados para tu empresa...
          </p>
        </div>

        {/* Overall Progress */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-blue-600">{completedCount}</div>
              <div className="text-sm text-slate-600">Completados</div>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-yellow-600">{generatingCount}</div>
              <div className="text-sm text-slate-600">En progreso</div>
            </div>
            <div className="bg-slate-50 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-slate-600">{pendingCount}</div>
              <div className="text-sm text-slate-600">Pendientes</div>
            </div>
            <div className="bg-red-50 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-red-600">{errorCount}</div>
              <div className="text-sm text-slate-600">Errores</div>
            </div>
          </div>

          {/* Overall Progress Bar */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-slate-700">Progreso general</span>
              <span className="text-sm font-bold text-slate-900">{overallProgress}%</span>
            </div>
            <div className="w-full h-3 bg-slate-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500"
                style={{ width: `${overallProgress}%` }}
              />
            </div>
          </div>

          {estimatedTime && isGenerating && (
            <p className="text-sm text-slate-600 text-center">
              ⏱️ Tiempo estimado: {estimatedTime}
            </p>
          )}
        </div>

        {/* Documents List */}
        <div className="space-y-2">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Documentos</h2>

          {documents.map((doc) => (
            <div
              key={doc.id}
              className="bg-white rounded-lg p-4 flex items-center gap-4 shadow hover:shadow-md transition-shadow"
            >
              {/* Status Icon */}
              <div className="flex-shrink-0 w-6 h-6">
                {doc.status === 'ready' && (
                  <CheckCircle className="h-6 w-6 text-green-600" />
                )}
                {doc.status === 'generating' && (
                  <Loader className="h-6 w-6 text-blue-600 animate-spin" />
                )}
                {doc.status === 'error' && (
                  <AlertCircle className="h-6 w-6 text-red-600" />
                )}
                {doc.status === 'pending' && (
                  <div className="h-6 w-6 rounded-full border-2 border-slate-300" />
                )}
              </div>

              {/* Document Info */}
              <div className="flex-grow min-w-0">
                <p className="font-medium text-slate-900 truncate">{doc.title}</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex-grow h-1.5 bg-slate-200 rounded-full overflow-hidden max-w-xs">
                    <div
                      className="h-full bg-blue-600 transition-all duration-300"
                      style={{ width: `${doc.progress}%` }}
                    />
                  </div>
                  <span className="text-xs text-slate-600">{doc.progress}%</span>
                </div>
              </div>

              {/* Status Badge */}
              <div className="flex-shrink-0">
                <span
                  className={`text-xs font-medium px-2 py-1 rounded ${
                    doc.status === 'ready'
                      ? 'bg-green-100 text-green-800'
                      : doc.status === 'generating'
                        ? 'bg-blue-100 text-blue-800'
                        : doc.status === 'error'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-slate-100 text-slate-800'
                  }`}
                >
                  {doc.status === 'ready'
                    ? 'Listo'
                    : doc.status === 'generating'
                      ? 'Generando'
                      : doc.status === 'error'
                        ? 'Error'
                        : 'Pendiente'}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Action Buttons */}
        {!isGenerating && completedCount === totalDocuments && (
          <div className="mt-8 bg-green-50 border border-green-200 rounded-lg p-6 text-center">
            <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-3" />
            <h3 className="text-xl font-bold text-green-900 mb-2">
              ¡Documentos generados exitosamente!
            </h3>
            <p className="text-green-800 mb-4">
              Los {totalDocuments} documentos están listos para descargar y se han indexado en RAG.
            </p>
            <button
              onClick={onComplete}
              className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
            >
              Ir al Dashboard
            </button>
          </div>
        )}

        {isGenerating && (
          <div className="mt-8 flex gap-4 justify-center">
            {onCancel && (
              <button
                onClick={onCancel}
                className="px-6 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
              >
                Cancelar Generación
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
