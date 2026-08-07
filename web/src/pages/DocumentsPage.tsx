import React, { useState } from 'react';
import { FileText, ArrowRight } from 'lucide-react';
import { DocumentUploader } from '../components/DocumentUploader';
import { DocumentSearcher } from '../components/DocumentSearcher';
import { ReportGenerator } from '../components/ReportGenerator';
import { AgentToolsList } from '../components/AgentToolsList';

export const DocumentsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'upload' | 'search' | 'report' | 'tools'>(
    'upload'
  );
  const [selectedAgent, setSelectedAgent] = useState('agent_rrhh');

  const tabs = [
    { id: 'upload', label: 'Subir Documentos', icon: '📄' },
    { id: 'search', label: 'Buscar', icon: '🔍' },
    { id: 'report', label: 'Generar Reporte', icon: '📊' },
    { id: 'tools', label: 'Herramientas', icon: '🔧' },
  ] as const;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3 mb-4">
            <FileText className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold text-slate-900">
                Centro de Documentos
              </h1>
              <p className="text-slate-600">
                Carga, busca y genera reportes con IA
              </p>
            </div>
          </div>

          {/* Agent Selector */}
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium text-slate-700">
              Agente:
            </label>
            <select
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
              className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="agent_rrhh">👥 Agente RRHH</option>
              <option value="agent_ceo">👔 Agente CEO</option>
              <option value="agent_finanzas">💰 Agente Finanzas</option>
              <option value="agent_ventas">📈 Agente Ventas</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex gap-1 -mb-px">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              {activeTab === 'upload' && (
                <div className="space-y-4">
                  <h2 className="text-xl font-bold text-slate-900">
                    Subir Documentos
                  </h2>
                  <p className="text-slate-600">
                    Carga documentos que el agente analizará y usará como
                    contexto en sus respuestas.
                  </p>
                  <DocumentUploader agentId={selectedAgent} />
                </div>
              )}

              {activeTab === 'search' && (
                <div className="space-y-4">
                  <h2 className="text-xl font-bold text-slate-900">
                    Buscar en Documentos
                  </h2>
                  <p className="text-slate-600">
                    Busca información específica en los documentos indexados.
                  </p>
                  <DocumentSearcher
                    agentId={selectedAgent}
                    collectionName="documentos_empresa"
                  />
                </div>
              )}

              {activeTab === 'report' && (
                <div className="space-y-4">
                  <h2 className="text-xl font-bold text-slate-900">
                    Generar Reporte
                  </h2>
                  <p className="text-slate-600">
                    Crea reportes profesionales en PDF o Excel con datos
                    enriquecidos.
                  </p>
                  <ReportGenerator agentId={selectedAgent} />
                </div>
              )}

              {activeTab === 'tools' && (
                <div className="space-y-4">
                  <h2 className="text-xl font-bold text-slate-900">
                    Herramientas del Agente
                  </h2>
                  <p className="text-slate-600">
                    Herramientas que el agente puede usar automáticamente para
                    procesar información.
                  </p>
                  <AgentToolsList agentId={selectedAgent} />
                </div>
              )}
            </div>
          </div>

          {/* Sidebar - Workflow */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-6">
              <h3 className="text-lg font-bold text-slate-900 mb-4">
                📋 Flujo de Trabajo
              </h3>

              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-bold text-blue-600">
                    1
                  </div>
                  <div>
                    <p className="font-medium text-slate-900">Subir Documentos</p>
                    <p className="text-xs text-slate-600">
                      Carga archivos PDF, Word o Excel
                    </p>
                  </div>
                </div>

                <div className="flex justify-center">
                  <ArrowRight className="h-5 w-5 text-slate-400 rotate-90" />
                </div>

                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-bold text-blue-600">
                    2
                  </div>
                  <div>
                    <p className="font-medium text-slate-900">
                      Sistema Indexa
                    </p>
                    <p className="text-xs text-slate-600">
                      RAG genera embeddings y los almacena
                    </p>
                  </div>
                </div>

                <div className="flex justify-center">
                  <ArrowRight className="h-5 w-5 text-slate-400 rotate-90" />
                </div>

                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-bold text-blue-600">
                    3
                  </div>
                  <div>
                    <p className="font-medium text-slate-900">Buscar Contexto</p>
                    <p className="text-xs text-slate-600">
                      Consulta preguntas sobre los documentos
                    </p>
                  </div>
                </div>

                <div className="flex justify-center">
                  <ArrowRight className="h-5 w-5 text-slate-400 rotate-90" />
                </div>

                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center text-sm font-bold text-green-600">
                    ✓
                  </div>
                  <div>
                    <p className="font-medium text-slate-900">
                      Respuesta Enriquecida
                    </p>
                    <p className="text-xs text-slate-600">
                      Agente responde con contexto de documentos
                    </p>
                  </div>
                </div>
              </div>

              {/* Stats */}
              <div className="mt-6 pt-6 border-t border-slate-200 space-y-3">
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-xs text-slate-600">Documentos Indexados</p>
                  <p className="text-2xl font-bold text-blue-600">12</p>
                </div>
                <div className="bg-green-50 p-3 rounded-lg">
                  <p className="text-xs text-slate-600">Búsquedas Hoy</p>
                  <p className="text-2xl font-bold text-green-600">37</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentsPage;
