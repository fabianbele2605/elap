import React, { useState, useEffect } from 'react';
import { Wrench, Loader, AlertCircle } from 'lucide-react';

interface Tool {
  name: string;
  description: string;
  parameters?: string[];
}

interface AgentToolsListProps {
  agentId: string;
}

export const AgentToolsList: React.FC<AgentToolsListProps> = ({ agentId }) => {
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTools = async () => {
      try {
        setLoading(true);
        setError('');

        const response = await fetch(`/agents/${agentId}/tools`);

        if (!response.ok) {
          throw new Error('Error al obtener herramientas');
        }

        const data = await response.json();

        if (data.tools && Array.isArray(data.tools)) {
          setTools(data.tools);
        }
      } catch (err) {
        setError('No se pudieron cargar las herramientas');
      } finally {
        setLoading(false);
      }
    };

    if (agentId) {
      fetchTools();
    }
  }, [agentId]);

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <Loader className="h-8 w-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
        <AlertCircle className="h-5 w-5 flex-shrink-0" />
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  if (tools.length === 0) {
    return (
      <div className="text-center py-8">
        <Wrench className="h-12 w-12 text-slate-300 mx-auto mb-4" />
        <p className="text-slate-600">No hay herramientas disponibles</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium text-slate-900 flex items-center gap-2">
        <Wrench className="h-4 w-4" />
        Herramientas disponibles ({tools.length})
      </h3>

      <div className="grid gap-3 md:grid-cols-2">
        {tools.map((tool, index) => (
          <div
            key={index}
            className="p-3 border border-slate-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <h4 className="font-medium text-slate-900 text-sm mb-1">
              {tool.name}
            </h4>
            <p className="text-xs text-slate-600 mb-2">{tool.description}</p>
            {tool.parameters && tool.parameters.length > 0 && (
              <div className="space-y-1">
                <p className="text-xs font-medium text-slate-700">
                  Parámetros:
                </p>
                <div className="flex flex-wrap gap-1">
                  {tool.parameters.map((param) => (
                    <span
                      key={param}
                      className="inline-block bg-slate-100 text-slate-700 text-xs px-2 py-0.5 rounded"
                    >
                      {param}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
