import React, { useState, useEffect } from 'react';
import { Trash2, Download, RefreshCw, Search } from 'lucide-react';

interface Document {
  filename: string;
  size: number;
  createdAt: string;
  type: 'contract' | 'invoice' | 'report' | 'other';
  employee?: string;
}

interface DocumentsTabProps {
  isLoading?: boolean;
}

export default function DocumentsTab({ isLoading = false }: DocumentsTabProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [filteredDocs, setFilteredDocs] = useState<Document[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'contract' | 'invoice' | 'report'>('all');
  const [loading, setLoading] = useState(true);

  // Cargar documentos al iniciar
  useEffect(() => {
    loadDocuments();
  }, []);

  // Filtrar documentos cuando cambian search o filter
  useEffect(() => {
    let filtered = documents;

    // Filtro por tipo
    if (filterType !== 'all') {
      filtered = filtered.filter(doc => doc.type === filterType);
    }

    // Filtro por búsqueda
    if (searchTerm) {
      filtered = filtered.filter(doc =>
        doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (doc.employee && doc.employee.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    setFilteredDocs(filtered);
  }, [documents, searchTerm, filterType]);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      // Llamar a la API real en puerto 5000 (Python)
      const response = await fetch('http://localhost:5000/api/documents');
      if (response.ok) {
        const data = await response.json();
        // Transformar datos si es necesario
        const formattedData = data.map((doc: any) => ({
          filename: doc.filename,
          size: doc.size || 0,
          createdAt: doc.createdAt || new Date().toISOString(),
          type: doc.type || 'other',
          employee: doc.employee
        }));
        setDocuments(formattedData);
        console.log(`✅ Cargados ${formattedData.length} documentos desde API`);
      } else {
        console.log('API respondió con error, usando mock data');
        setDocuments(getMockDocuments());
      }
    } catch (error) {
      console.log('⚠️ No se pudo conectar a API, usando mock data:', error);
      setDocuments(getMockDocuments());
    } finally {
      setLoading(false);
    }
  };

  const getMockDocuments = (): Document[] => {
    return [
      {
        filename: 'contrato_Juan_Pérez.docx',
        size: 45230,
        createdAt: '2026-08-08T10:05:00Z',
        type: 'contract',
        employee: 'Juan Pérez',
      },
      {
        filename: 'contrato_María_García.docx',
        size: 45100,
        createdAt: '2026-08-08T10:10:00Z',
        type: 'contract',
        employee: 'María García',
      },
      {
        filename: 'contrato_Carlos_López.docx',
        size: 44950,
        createdAt: '2026-08-08T10:15:00Z',
        type: 'contract',
        employee: 'Carlos López',
      },
      {
        filename: 'contrato_Ana_Rodríguez.docx',
        size: 45050,
        createdAt: '2026-08-08T10:20:00Z',
        type: 'contract',
        employee: 'Ana Rodríguez',
      },
      {
        filename: 'contrato_Pedro_Martínez.docx',
        size: 45300,
        createdAt: '2026-08-08T10:25:00Z',
        type: 'contract',
        employee: 'Pedro Martínez',
      },
      {
        filename: 'contrato_Laura_Rodríguez.docx',
        size: 45180,
        createdAt: '2026-08-08T10:30:00Z',
        type: 'contract',
        employee: 'Laura Rodríguez',
      },
    ];
  };

  const handleDelete = async (filename: string) => {
    if (confirm(`¿Eliminar ${filename}?`)) {
      try {
        // Llamar a API real en puerto 5000
        const response = await fetch(`http://localhost:5000/api/documents/${filename}`, {
          method: 'DELETE'
        });
        if (response.ok) {
          setDocuments(documents.filter(doc => doc.filename !== filename));
          console.log(`✅ Eliminado: ${filename}`);
        } else {
          alert('Error: No se pudo eliminar el documento');
        }
      } catch (error) {
        alert('Error eliminando documento (¿API no disponible?)');
        console.error(error);
      }
    }
  };

  const handleDownload = (filename: string) => {
    window.location.href = `/documents/download/${filename}`;
  };

  const handleRegenerate = (filename: string) => {
    alert(`Regenerar: ${filename}\n(Próximamente)`);
  };

  const getTypeIcon = (type: Document['type']) => {
    switch (type) {
      case 'contract':
        return '📄';
      case 'invoice':
        return '🧾';
      case 'report':
        return '📊';
      default:
        return '📎';
    }
  };

  const getTypeLabel = (type: Document['type']) => {
    switch (type) {
      case 'contract':
        return 'Contrato';
      case 'invoice':
        return 'Factura';
      case 'report':
        return 'Reporte';
      default:
        return 'Documento';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="flex flex-col h-full gap-4 p-3 sm:p-4 lg:p-6">
      {/* HEADER */}
      <div>
        <h2 className="text-lg sm:text-xl font-bold text-slate-900 mb-4">📁 Documentos Generados</h2>

        {/* BÚSQUEDA Y FILTROS */}
        <div className="flex gap-2 flex-col sm:flex-row sm:flex-wrap">
          {/* Buscador */}
          <div className="flex-1 min-w-[200px] relative">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Buscar por nombre o empleado..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Filtro por tipo */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as any)}
            className="px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">📋 Todos</option>
            <option value="contract">📄 Contratos</option>
            <option value="invoice">🧾 Facturas</option>
            <option value="report">📊 Reportes</option>
          </select>

          {/* Botón recargar */}
          <button
            onClick={loadDocuments}
            disabled={loading}
            className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
          >
            <RefreshCw className="w-4 h-4 inline mr-1" />
            Recargar
          </button>
        </div>
      </div>

      {/* CONTENIDO */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-slate-500">⏳ Cargando documentos...</div>
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-slate-500 mb-2">No hay documentos</p>
              <p className="text-xs text-slate-400">
                {searchTerm || filterType !== 'all' ? 'Intenta cambiar los filtros' : 'Genera tu primer documento en el chat'}
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            {/* VISTA DESKTOP: TABLA */}
            <div className="hidden md:block space-y-2">
              {/* HEADER DE TABLA */}
              <div className="grid grid-cols-12 gap-2 px-3 py-2 bg-slate-100 rounded-lg font-semibold text-xs text-slate-700">
                <div className="col-span-5">Nombre</div>
                <div className="col-span-2">Tipo</div>
                <div className="col-span-2">Tamaño</div>
                <div className="col-span-3">Acciones</div>
              </div>

              {/* FILAS */}
              {filteredDocs.map((doc, idx) => (
                <div
                  key={idx}
                  className="grid grid-cols-12 gap-2 items-center px-3 py-2 bg-white border border-slate-200 rounded-lg hover:shadow-sm transition-shadow"
                >
                  {/* Nombre */}
                  <div className="col-span-5 flex items-start">
                    <span className="text-lg mr-2">{getTypeIcon(doc.type)}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 truncate">{doc.filename}</p>
                      {doc.employee && (
                        <p className="text-xs text-slate-500 truncate">{doc.employee}</p>
                      )}
                    </div>
                  </div>

                  {/* Tipo */}
                  <div className="col-span-2">
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                      {getTypeLabel(doc.type)}
                    </span>
                  </div>

                  {/* Tamaño */}
                  <div className="col-span-2">
                    <p className="text-xs text-slate-500">{formatFileSize(doc.size)}</p>
                    <p className="text-xs text-slate-400">{formatDate(doc.createdAt)}</p>
                  </div>

                  {/* Acciones */}
                  <div className="col-span-3 flex gap-1">
                    <button
                      onClick={() => handleDownload(doc.filename)}
                      title="Descargar"
                      className="p-1.5 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleRegenerate(doc.filename)}
                      title="Regenerar"
                      className="p-1.5 text-green-600 hover:bg-green-50 rounded transition-colors"
                    >
                      <RefreshCw className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(doc.filename)}
                      title="Eliminar"
                      className="p-1.5 text-red-600 hover:bg-red-50 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* VISTA MÓVIL: TARJETAS */}
            <div className="md:hidden space-y-3">
              {filteredDocs.map((doc, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-white border border-slate-200 rounded-lg hover:shadow-sm transition-shadow"
                >
                  <div className="flex items-start gap-3 mb-3">
                    <span className="text-2xl">{getTypeIcon(doc.type)}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 truncate">{doc.filename}</p>
                      {doc.employee && (
                        <p className="text-xs text-slate-500 truncate">{doc.employee}</p>
                      )}
                      <span className="inline-block text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded mt-1">
                        {getTypeLabel(doc.type)}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-500 mb-3 pb-3 border-b border-slate-100">
                    <div>
                      <p>{formatFileSize(doc.size)}</p>
                      <p>{formatDate(doc.createdAt)}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleDownload(doc.filename)}
                      title="Descargar"
                      className="flex-1 p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors text-xs font-medium"
                    >
                      <Download className="w-4 h-4 mx-auto" />
                    </button>
                    <button
                      onClick={() => handleRegenerate(doc.filename)}
                      title="Regenerar"
                      className="flex-1 p-2 text-green-600 hover:bg-green-50 rounded transition-colors text-xs font-medium"
                    >
                      <RefreshCw className="w-4 h-4 mx-auto" />
                    </button>
                    <button
                      onClick={() => handleDelete(doc.filename)}
                      title="Eliminar"
                      className="flex-1 p-2 text-red-600 hover:bg-red-50 rounded transition-colors text-xs font-medium"
                    >
                      <Trash2 className="w-4 h-4 mx-auto" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* FOOTER CON ESTADÍSTICAS */}
      <div className="border-t border-slate-200 pt-3 text-xs text-slate-600">
        <p>
          Mostrando <strong>{filteredDocs.length}</strong> de <strong>{documents.length}</strong> documentos
          {filteredDocs.length > 0 && (
            <span className="ml-2">
              • Tamaño total: <strong>{formatFileSize(filteredDocs.reduce((sum, doc) => sum + doc.size, 0))}</strong>
            </span>
          )}
        </p>
      </div>
    </div>
  );
}
