import React, { useState } from 'react';
import { CheckCircle2, Circle, Download, AlertCircle } from 'lucide-react';
import { AGENT_TEMPLATES, CATEGORIES } from '../../config/agents';

interface InstallAgentsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onInstall: (agentIds: string[]) => Promise<void>;
}

export const InstallAgentsModal: React.FC<InstallAgentsModalProps> = ({
  isOpen,
  onClose,
  onInstall
}) => {
  const [selectedAgents, setSelectedAgents] = useState<Set<string>>(
    new Set(['system_supervisor', 'task_router', 'memory_manager'])
  );
  const [isInstalling, setIsInstalling] = useState(false);

  const toggleAgent = (agentId: string) => {
    const newSelected = new Set(selectedAgents);
    if (newSelected.has(agentId)) {
      newSelected.delete(agentId);
    } else {
      newSelected.add(agentId);
    }
    setSelectedAgents(newSelected);
  };

  const handleInstall = async () => {
    setIsInstalling(true);
    try {
      await onInstall(Array.from(selectedAgents));
      onClose();
    } catch (err) {
      console.error('Error installing agents:', err);
    } finally {
      setIsInstalling(false);
    }
  };

  if (!isOpen) return null;

  const groupedAgents = Object.entries(CATEGORIES).reduce((acc, [key, label]) => {
    acc[key] = AGENT_TEMPLATES.filter(a => a.categoria === key);
    return acc;
  }, {} as Record<string, typeof AGENT_TEMPLATES>);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-auto">
        <div className="sticky top-0 bg-white border-b border-slate-200 p-4">
          <h2 className="text-lg font-bold text-slate-900">Instalar Agentes ELAP</h2>
          <p className="text-sm text-slate-600 mt-1">Selecciona los agentes que necesita tu organización</p>
        </div>

        <div className="p-6 space-y-6">
          {Object.entries(groupedAgents).map(([category, agents]) => (
            <div key={category}>
              <h3 className="text-sm font-bold text-slate-700 mb-3 flex items-center gap-2">
                {CATEGORIES[category as keyof typeof CATEGORIES]}
                <span className="text-xs bg-slate-200 text-slate-700 px-2 py-0.5 rounded">
                  {agents.filter(a => selectedAgents.has(a.id)).length}/{agents.length}
                </span>
              </h3>
              <div className="space-y-2 ml-2">
                {agents.map(agent => (
                  <label key={agent.id} className="flex items-start gap-3 p-3 hover:bg-slate-50 rounded cursor-pointer transition-colors">
                    <div className="mt-0.5">
                      {selectedAgents.has(agent.id) ? (
                        <CheckCircle2 className="w-5 h-5 text-blue-600" />
                      ) : (
                        <Circle className="w-5 h-5 text-slate-400" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <input
                        type="checkbox"
                        checked={selectedAgents.has(agent.id)}
                        onChange={() => toggleAgent(agent.id)}
                        className="hidden"
                      />
                      <p className="font-medium text-slate-900 text-sm">{agent.nombre}</p>
                      <p className="text-xs text-slate-600 mt-0.5">{agent.descripcion}</p>
                      <p className="text-xs text-slate-500 mt-1">
                        Modelo: <span className="font-mono bg-slate-100 px-1.5 py-0.5 rounded">{agent.modelo}</span>
                      </p>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="sticky bottom-0 bg-slate-50 border-t border-slate-200 p-4 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-slate-700">
            <AlertCircle className="w-4 h-4 text-amber-600" />
            <span>{selectedAgents.size} agentes seleccionados</span>
          </div>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              disabled={isInstalling}
              className="px-4 py-2 text-slate-700 hover:bg-slate-100 rounded font-medium text-sm transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={handleInstall}
              disabled={isInstalling || selectedAgents.size === 0}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white rounded font-medium text-sm flex items-center gap-2 transition-colors"
            >
              <Download className="w-4 h-4" />
              {isInstalling ? 'Instalando...' : 'Instalar Agentes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
