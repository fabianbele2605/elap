import React, { useState } from 'react';
import { FileText, Download, Loader, AlertCircle, CheckCircle } from 'lucide-react';

interface Section {
  title: string;
  content: string;
}

interface ReportGeneratorProps {
  agentId: string;
}

export const ReportGenerator: React.FC<ReportGeneratorProps> = ({
  agentId,
}) => {
  const [title, setTitle] = useState('Reporte Profesional');
  const [format, setFormat] = useState<'pdf' | 'excel'>('pdf');
  const [sections, setSections] = useState<Section[]>([
    { title: 'Resumen Ejecutivo', content: 'Contenido del resumen' },
    { title: 'Datos Principales', content: 'Análisis de datos' },
  ]);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [generatedFile, setGeneratedFile] = useState<string>('');

  const handleAddSection = () => {
    setSections([
      ...sections,
      { title: `Sección ${sections.length + 1}`, content: '' },
    ]);
  };

  const handleRemoveSection = (index: number) => {
    setSections(sections.filter((_, i) => i !== index));
  };

  const handleSectionChange = (index: number, field: keyof Section, value: string) => {
    const updated = [...sections];
    updated[index][field] = value;
    setSections(updated);
  };

  const handleGenerate = async () => {
    if (!title.trim()) {
      setError('Ingresa un título para el reporte');
      return;
    }

    setGenerating(true);
    setError('');
    setGeneratedFile('');

    try {
      const response = await fetch('/documents/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: title.trim(),
          sections_json: JSON.stringify(sections),
          format,
          company_name: 'Andina Foods',
        }),
      });

      if (!response.ok) {
        throw new Error('Error al generar reporte');
      }

      const data = await response.json();

      if (data.status === 'completed') {
        setGeneratedFile(data.filename);
        // Simular descarga
        setTimeout(() => {
          const link = document.createElement('a');
          link.href = data.url;
          link.download = data.filename;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }, 500);
      } else {
        throw new Error(data.error || 'Error desconocido');
      }
    } catch (err) {
      setError('Error al generar el reporte. Intenta de nuevo.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-900 mb-2">
            Título del Reporte
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Ej: Reporte de Ventas Q3 2026"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-900 mb-2">
            Formato
          </label>
          <div className="flex gap-4">
            {(['pdf', 'excel'] as const).map((fmt) => (
              <label key={fmt} className="flex items-center gap-2">
                <input
                  type="radio"
                  name="format"
                  value={fmt}
                  checked={format === fmt}
                  onChange={(e) => setFormat(e.target.value as 'pdf' | 'excel')}
                  className="h-4 w-4"
                />
                <span className="text-sm text-slate-700">
                  {fmt === 'pdf' ? 'PDF' : 'Excel'}
                </span>
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-slate-900">Secciones</h3>
          <button
            onClick={handleAddSection}
            className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1 rounded transition-colors"
          >
            + Agregar sección
          </button>
        </div>

        <div className="space-y-3">
          {sections.map((section, index) => (
            <div key={index} className="space-y-2 p-3 bg-slate-50 rounded-lg">
              <div className="flex items-center justify-between">
                <input
                  type="text"
                  value={section.title}
                  onChange={(e) => handleSectionChange(index, 'title', e.target.value)}
                  placeholder="Título de sección"
                  className="flex-1 px-3 py-1 text-sm border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {sections.length > 1 && (
                  <button
                    onClick={() => handleRemoveSection(index)}
                    className="text-red-600 hover:text-red-700 text-sm ml-2"
                  >
                    Eliminar
                  </button>
                )}
              </div>
              <textarea
                value={section.content}
                onChange={(e) => handleSectionChange(index, 'content', e.target.value)}
                placeholder="Contenido de la sección"
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-24 resize-none"
              />
            </div>
          ))}
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {generatedFile && (
        <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700">
          <CheckCircle className="h-5 w-5 flex-shrink-0" />
          <p className="text-sm">
            Reporte generado: <span className="font-medium">{generatedFile}</span>
          </p>
        </div>
      )}

      <button
        onClick={handleGenerate}
        disabled={generating}
        className="w-full bg-green-600 hover:bg-green-700 disabled:bg-slate-400 text-white px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
      >
        {generating ? (
          <>
            <Loader className="h-5 w-5 animate-spin" />
            Generando reporte...
          </>
        ) : (
          <>
            <FileText className="h-5 w-5" />
            Generar {format === 'pdf' ? 'PDF' : 'Excel'}
          </>
        )}
      </button>
    </div>
  );
};
