import React, { useState } from 'react';
import { Search, Loader, AlertCircle } from 'lucide-react';

interface SearchResult {
  chunk: string;
  similarity: number;
}

interface DocumentSearcherProps {
  agentId: string;
  collectionName?: string;
}

export const DocumentSearcher: React.FC<DocumentSearcherProps> = ({
  agentId,
  collectionName = 'documentos_empresa',
}) => {
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!query.trim()) {
      setError('Ingresa una búsqueda');
      return;
    }

    setSearching(true);
    setError('');
    setResults([]);

    try {
      const response = await fetch('/documents/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          collection: collectionName,
          query: query.trim(),
          top_k: 5,
        }),
      });

      if (!response.ok) {
        throw new Error('Error en la búsqueda');
      }

      const data = await response.json();

      // Mapear respuesta a resultados
      if (data.chunks && Array.isArray(data.chunks)) {
        const searchResults: SearchResult[] = data.chunks.map(
          (chunk: string, index: number) => ({
            chunk,
            similarity: (1 - index * 0.1),
          })
        );
        setResults(searchResults);
      }
    } catch (err) {
      setError('Error al buscar. Intenta de nuevo.');
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="space-y-4">
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Busca en documentos: políticas, procedimientos, beneficios..."
            className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={searching}
          />
        </div>
        <button
          type="submit"
          disabled={searching}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
        >
          {searching ? (
            <>
              <Loader className="h-4 w-4 animate-spin" />
              Buscando...
            </>
          ) : (
            'Buscar'
          )}
        </button>
      </form>

      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-slate-900">
            {results.length} resultado{results.length !== 1 ? 's' : ''}
          </h3>
          <div className="space-y-2">
            {results.map((result, index) => (
              <div
                key={index}
                className="p-3 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <p className="text-xs font-medium text-blue-600">
                    Relevancia: {Math.round(result.similarity * 100)}%
                  </p>
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                    Resultado #{index + 1}
                  </span>
                </div>
                <p className="text-sm text-slate-700 line-clamp-3">
                  {result.chunk}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {searching && (
        <div className="flex justify-center py-8">
          <Loader className="h-8 w-8 text-blue-600 animate-spin" />
        </div>
      )}
    </div>
  );
};
