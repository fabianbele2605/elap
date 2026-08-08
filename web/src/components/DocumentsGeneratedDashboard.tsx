import React, { useState } from 'react';
import {
  Download,
  Eye,
  RotateCcw,
  FileText,
  Briefcase,
  Scale,
  TrendingUp,
  Search,
} from 'lucide-react';

interface GeneratedDoc {
  id: string;
  title: string;
  category: string;
  status: 'ready' | 'generating' | 'error';
  size: string;
  generatedAt: string;
  indexed: boolean;
}

interface DocumentsGeneratedDashboardProps {
  companyName: string;
  documents?: GeneratedDoc[];
  onDownload?: (docId: string) => void;
  onPreview?: (docId: string) => void;
  onRegenerate?: (docId: string) => void;
}

const DOCUMENT_CATEGORIES = [
  {
    name: 'RRHH',
    icon: Briefcase,
    color: 'blue',
    description: '5 documentos de Recursos Humanos',
  },
  {
    name: 'Finanzas',
    icon: TrendingUp,
    color: 'green',
    description: '3 documentos de Finanzas',
  },
  {
    name: 'Operaciones',
    icon: FileText,
    color: 'purple',
    description: '4 documentos de Operaciones',
  },
  {
    name: 'Legal',
    icon: Scale,
    color: 'red',
    description: '2 documentos Legales',
  },
  {
    name: 'Ventas',
    icon: TrendingUp,
    color: 'orange',
    description: '1 documento de Ventas',
  },
];

const DEFAULT_DOCUMENTS: GeneratedDoc[] = [
  {
    id: 'doc_001',
    title: 'Manual del Empleado',
    category: 'RRHH',
    status: 'ready',
    size: '2.4 MB',
    generatedAt: new Date().toLocaleString(),
    indexed: true,
  },
  {
    id: 'doc_002',
    title: 'Política de Vacaciones',
    category: 'RRHH',
    status: 'ready',
    size: '1.8 MB',
    generatedAt: new Date().toLocaleString(),
    indexed: true,
  },
  {
    id: 'doc_003',
    title: 'Código de Conducta',
    category: 'RRHH',
    status: 'ready',
    size: '2.1 MB',
    generatedAt: new Date().toLocaleString(),
    indexed: true,
  },
  {
    id: 'doc_004',
    title: 'Política de Ausencias',
    category: 'RRHH',
    status: 'ready',
    size: '1.5 MB',
    generatedAt: new Date().toLocaleString(),
    indexed: true,
  },
  {
    id: 'doc_005',
    title: 'Procedimiento de Contratación',
    category: 'RRHH',
    status: 'ready',
    size: '2.0 MB',
    generatedAt: new Date().toLocaleString(),
    indexed: true,
  },
  {
    id: 'doc_006',
    title: 'Presupuesto Anual',
    category: 'Finanzas',
    status: 'ready',
    size: '3.2 MB',
    generatedAt: new Date().toLocaleString(),
    indexed: true,
  },
  {
    id: 'doc_007',
    title: 'Política de Gastos',
    category: 'Finanzas',
    status: 'ready',
    size: '1.9 MB',
    generatedAt: new Date().toLocaleString(),
    indexed: true,
  },
  {
    id: 'doc_008',
    title: 'Reportes Financieros',
    category: 'Finanzas',
    status: 'ready',
    size: '2.7 MB',
    generatedAt: new Date().toLocaleString(),
    indexed: true,
  },
  {
    id: 'doc_009',
    title: 'Política de Calidad',
    category: 'Operaciones',
    status: 'ready',
    size: '2.3 MB',
    generatedAt: new Date().toLocaleString(),
    indexed: true,
  },
  {
    id: 'doc_010',
    title: 'Matriz de Procesos',
    category: 'Operaciones',
    status: 'ready',
    size: '2.5 MB',
    generatedAt: new Date().toLocaleString(),
    indexed: true,
  },
  {
    id: 'doc_011',
    title: 'Procedimientos Operacionales',
    category: 'Operaciones',
    status: 'ready',
    size: '3.1 MB',
    generatedAt: new Date().toLocaleString(),
    indexed: true,
  },
  {
    id: 'doc_012',
    title: 'Política de Compras',
    category: 'Operaciones',
    status: 'ready',
    size: '2.0 MB',
    generatedAt: new Date().toLocaleString(),
    indexed: true,
  },
  {
    id: 'doc_013',
    title: 'Términos y Condiciones',
    category: 'Legal',
    status: 'ready',
    size: '1.7 MB',
    generatedAt: new Date().toLocaleString(),
    indexed: true,
  },
  {
    id: 'doc_014',
    title: 'Política de Privacidad',
    category: 'Legal',
    status: 'ready',
    size: '1.9 MB',
    generatedAt: new Date().toLocaleString(),
    indexed: true,
  },
  {
    id: 'doc_015',
    title: 'Estrategia Comercial',
    category: 'Ventas',
    status: 'ready',
    size: '2.6 MB',
    generatedAt: new Date().toLocaleString(),
    indexed: true,
  },
];

export const DocumentsGeneratedDashboard: React.FC<DocumentsGeneratedDashboardProps> = ({
  companyName,
  documents = DEFAULT_DOCUMENTS,
  onDownload,
  onPreview,
  onRegenerate,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  // Filter documents
  const filteredDocs = documents.filter((doc) => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = !selectedCategory || doc.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Group by category
  const docsByCategory = DOCUMENT_CATEGORIES.map((cat) => ({
    ...cat,
    docs: documents.filter((doc) => doc.category === cat.name),
  }));

  const totalSize = documents
    .reduce((sum, doc) => {
      const sizeInMB = parseFloat(doc.size);
      return sum + sizeInMB;
    }, 0)
    .toFixed(1);

  return (
    <div className="h-screen overflow-y-auto bg-gradient-to-br from-slate-50 to-slate-100 p-4 md:p-8">
      <div className="max-w-6xl mx-auto pb-20">
        {/* Header */}
        <div className="mb-6 md:mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-2">
            📚 Knowledge Pack Generado
          </h1>
          <p className="text-slate-600 text-sm md:text-base">
            {companyName} — {documents.length} documentos listos para usar
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4 mb-6 md:mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-4xl font-bold text-blue-600">{documents.length}</div>
            <p className="text-slate-600 text-sm mt-2">Documentos Generados</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-4xl font-bold text-green-600">
              {documents.filter((d) => d.indexed).length}
            </div>
            <p className="text-slate-600 text-sm mt-2">Indexados en RAG</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-4xl font-bold text-purple-600">{totalSize} MB</div>
            <p className="text-slate-600 text-sm mt-2">Tamaño Total</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-4xl font-bold text-orange-600">5</div>
            <p className="text-slate-600 text-sm mt-2">Categorías</p>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="bg-white rounded-lg shadow p-4 md:p-6 mb-6 md:mb-8">
          <div className="flex flex-col gap-3 md:gap-4">
            <div className="flex-grow relative">
              <Search className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
              <input
                type="text"
                placeholder="Buscar documentos..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm md:text-base"
              />
            </div>

            {/* Category Filters */}
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => setSelectedCategory(null)}
                className={`px-3 md:px-4 py-2 rounded-lg font-medium transition-colors text-sm ${
                  selectedCategory === null
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                Todos
              </button>
              {DOCUMENT_CATEGORIES.map((cat) => (
                <button
                  key={cat.name}
                  onClick={() =>
                    setSelectedCategory(selectedCategory === cat.name ? null : cat.name)
                  }
                  className={`px-3 md:px-4 py-2 rounded-lg font-medium transition-colors text-xs md:text-sm ${
                    selectedCategory === cat.name
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  {cat.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Documents by Category */}
        <div className="space-y-8">
          {docsByCategory
            .filter((cat) => cat.docs.length > 0)
            .map((category) => (
              <div key={category.name} className="bg-white rounded-lg shadow overflow-hidden">
                {/* Category Header */}
                <div className="bg-gradient-to-r from-slate-50 to-slate-100 px-6 py-4 border-b border-slate-200">
                  <div className="flex items-center gap-3">
                    <category.icon className={`h-6 w-6 text-${category.color}-600`} />
                    <div>
                      <h2 className="text-lg font-bold text-slate-900">{category.name}</h2>
                      <p className="text-sm text-slate-600">{category.description}</p>
                    </div>
                    <span className="ml-auto bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                      {category.docs.length} documentos
                    </span>
                  </div>
                </div>

                {/* Documents Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4 p-4 md:p-6">
                  {category.docs.map((doc) => (
                    <div
                      key={doc.id}
                      className="border border-slate-200 rounded-lg p-3 md:p-4 hover:shadow-md transition-shadow flex flex-col"
                    >
                      {/* Status Badge */}
                      <div className="flex items-start justify-between mb-3 gap-2 flex-wrap">
                        <span
                          className={`text-xs font-medium px-2 py-1 rounded whitespace-nowrap ${
                            doc.status === 'ready'
                              ? 'bg-green-100 text-green-800'
                              : doc.status === 'generating'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {doc.status === 'ready' ? '✓ Listo' : 'Generando'}
                        </span>
                        {doc.indexed && (
                          <span className="text-xs font-medium px-2 py-1 rounded bg-purple-100 text-purple-800 whitespace-nowrap">
                            🧠 Indexado
                          </span>
                        )}
                      </div>

                      {/* Title */}
                      <h3 className="font-bold text-slate-900 mb-2 text-sm line-clamp-2">{doc.title}</h3>

                      {/* Metadata */}
                      <div className="text-xs text-slate-600 mb-4 space-y-1 flex-grow">
                        <p>📦 {doc.size}</p>
                        <p className="line-clamp-1">📅 {doc.generatedAt}</p>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex gap-2 mt-auto flex-wrap">
                        <button
                          onClick={() => onPreview && onPreview(doc.id)}
                          className="flex-1 min-w-[70px] flex items-center justify-center gap-1 px-2 md:px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded text-xs md:text-sm font-medium transition-colors"
                        >
                          <Eye className="h-4 w-4 flex-shrink-0" />
                          <span className="hidden md:inline">Ver</span>
                        </button>
                        <button
                          onClick={() => onDownload && onDownload(doc.id)}
                          className="flex-1 min-w-[70px] flex items-center justify-center gap-1 px-2 md:px-3 py-2 bg-green-50 hover:bg-green-100 text-green-700 rounded text-xs md:text-sm font-medium transition-colors"
                        >
                          <Download className="h-4 w-4 flex-shrink-0" />
                          <span className="hidden md:inline">Descargar</span>
                        </button>
                        <button
                          onClick={() => onRegenerate && onRegenerate(doc.id)}
                          className="flex items-center justify-center gap-1 px-2 md:px-3 py-2 bg-slate-50 hover:bg-slate-100 text-slate-700 rounded text-sm font-medium transition-colors"
                          title="Regenerar documento"
                        >
                          <RotateCcw className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
        </div>

        {/* Empty State */}
        {filteredDocs.length === 0 && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <FileText className="h-16 w-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-bold text-slate-900 mb-2">No hay documentos</h3>
            <p className="text-slate-600">
              Intenta cambiar los filtros o realiza una nueva generación
            </p>
          </div>
        )}

        {/* Footer Actions */}
        <div className="mt-6 md:mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4 md:p-6">
          <h3 className="font-bold text-slate-900 mb-3 text-base md:text-lg">🎯 Próximos pasos</h3>
          <ul className="text-sm text-slate-700 space-y-2 list-disc list-inside">
            <li>Descarga los documentos y personaliza según necesidades</li>
            <li>Comparte con tu equipo (los documentos están indexados en RAG)</li>
            <li>Los agentes de ELAP pueden consultar estos documentos automáticamente</li>
            <li>Regenera documentos individuales si necesitas actualizaciones</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
