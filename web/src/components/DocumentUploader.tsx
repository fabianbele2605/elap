import React, { useState } from 'react';
import { Upload, File, CheckCircle, AlertCircle } from 'lucide-react';

interface DocumentUploaderProps {
  agentId: string;
  onUploadSuccess?: (filename: string) => void;
}

export const DocumentUploader: React.FC<DocumentUploaderProps> = ({
  agentId,
  onUploadSuccess,
}) => {
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file: File) => {
    // Validar tipo de archivo
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/csv',
      'image/png',
      'image/jpeg',
    ];

    if (!allowedTypes.includes(file.type)) {
      setError('Formato no soportado. Usa PDF, Word, Excel, CSV o imágenes.');
      return;
    }

    setUploading(true);
    setError('');

    try {
      // Simular upload (en producción, sería un multipart/form-data POST)
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const filename = file.name;
      setUploadedFiles([...uploadedFiles, filename]);
      if (onUploadSuccess) {
        onUploadSuccess(filename);
      }
    } catch (err) {
      setError('Error al subir el archivo. Intenta de nuevo.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-600 bg-blue-50'
            : 'border-slate-300 hover:border-blue-400'
        }`}
      >
        <Upload className="mx-auto h-12 w-12 text-slate-400 mb-4" />
        <div className="space-y-2">
          <p className="text-lg font-medium text-slate-900">
            Arrastra documentos aquí
          </p>
          <p className="text-sm text-slate-600">
            o haz clic para seleccionar archivos
          </p>
          <p className="text-xs text-slate-500 mt-2">
            Formatos soportados: PDF, Word, Excel, CSV, PNG, JPG
          </p>
        </div>
        <input
          type="file"
          onChange={handleFileInput}
          disabled={uploading}
          className="hidden"
          id="file-input"
          accept=".pdf,.docx,.xlsx,.csv,.png,.jpg,.jpeg"
        />
        <label
          htmlFor="file-input"
          className="mt-4 inline-block bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg cursor-pointer transition-colors"
        >
          {uploading ? 'Subiendo...' : 'Seleccionar archivo'}
        </label>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-slate-900">
            Documentos subidos
          </h3>
          <div className="space-y-2">
            {uploadedFiles.map((filename) => (
              <div
                key={filename}
                className="flex items-center gap-2 p-2 bg-green-50 border border-green-200 rounded-lg"
              >
                <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-900 truncate">
                    {filename}
                  </p>
                  <p className="text-xs text-green-600">Indexado en RAG</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
