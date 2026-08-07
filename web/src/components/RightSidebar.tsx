import React, { useState } from 'react';
import { 
  Bot, 
  Wrench, 
  BookOpen, 
  Save, 
  Download, 
  Trash2, 
  Star, 
  Pin, 
  Sliders,
  ShieldCheck,
  Check, 
  Plus, 
  Info,
  RefreshCw,
  ExternalLink,
  ChevronRight,
  Database,
  FileText,
  Layers,
  Sparkles
} from 'lucide-react';
import { Agent, Tool, KnowledgeSource } from '../types';

interface RightSidebarProps {
  agent: Agent;
  tools: Tool[];
  knowledgeSources: KnowledgeSource[];
  onToggleTool: (toolId: string) => void;
  onClearChat: () => void;
  onExportChat: () => void;
  onUpdateAgentParams: (temp: number, topP: number, ctx: number) => void;
}

export const RightSidebar: React.FC<RightSidebarProps> = ({
  agent,
  tools,
  knowledgeSources,
  onToggleTool,
  onClearChat,
  onExportChat,
  onUpdateAgentParams
}) => {
  if (!agent) {
    return <div className="w-[280px] shrink-0 bg-slate-50 border-l border-slate-200" />;
  }

  const [isFavorite, setIsFavorite] = useState(true);
  const [isPinned, setIsPinned] = useState(true);
  const [temperature, setTemperature] = useState(agent.temperature || 0.7);
  const [topP, setTopP] = useState(agent.topP || 0.9);
  const [contextLength, setContextLength] = useState(agent.contextLength || 4096);

  const handleTempChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setTemperature(val);
    onUpdateAgentParams(val, topP, contextLength);
  };

  const handleTopPChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setTopP(val);
    onUpdateAgentParams(temperature, val, contextLength);
  };

  const handleContextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseInt(e.target.value);
    setContextLength(val);
    onUpdateAgentParams(temperature, topP, val);
  };

  return (
    <aside className="w-[280px] shrink-0 bg-white border-l border-slate-200 flex flex-col h-full text-slate-700 select-none overflow-y-auto custom-scrollbar">
      {/* DETALLES DEL AGENTE SECTION */}
      <div className="p-3 border-b border-slate-200/80 space-y-2">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-700 uppercase tracking-wider">
          <span className="flex items-center gap-1.5 text-blue-600">
            <Bot className="w-3.5 h-3.5" /> DETALLES DEL AGENTE
          </span>
          <span className="text-[12px] bg-slate-100 text-slate-700 font-mono px-1.5 py-0.5 rounded border border-slate-700">
            {agent.role}
          </span>
        </div>

        <div className="bg-slate-50 p-3 rounded-lg border border-slate-300 space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-md bg-blue-600/30 border border-blue-600/50 flex items-center justify-center text-blue-600 font-bold text-sm shadow">
              {agent.name.substring(0, 2).toUpperCase()}
            </div>
            <div>
              <h3 className="font-bold text-sm text-slate-900">{agent.name}</h3>
              <p className="text-[13px] font-mono text-blue-600">ID: {agent.id.substring(0, 14)}...</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-x-2 gap-y-1.5 text-[13px] pt-1 border-t border-slate-300/80 font-sans">
            <div>
              <span className="text-slate-700 block text-[12px]">Model:</span>
              <span className="font-mono text-slate-700 font-medium">{agent.model}</span>
            </div>
            <div>
              <span className="text-slate-700 block text-[12px]">Status:</span>
              <span className="text-green-600 font-medium flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-green-600400"></span> En línea
              </span>
            </div>
            <div>
              <span className="text-slate-700 block text-[12px]">Availability:</span>
              <span className="text-slate-700 font-mono">24/7 Local</span>
            </div>
            <div>
              <span className="text-slate-700 block text-[12px]">Skills Count:</span>
              <span className="text-slate-700 font-medium">{agent.skillsCount} Enabled</span>
            </div>
          </div>

          <p className="text-[13px] text-slate-700 italic bg-white/60 p-1.5 rounded border border-slate-300/80 leading-relaxed">
            "{agent.description}"
          </p>
        </div>
      </div>

      {/* TOOLS & CAPABILITIES SECTION */}
      <div className="p-3 border-b border-slate-200/80 space-y-2">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-700 uppercase tracking-wider">
          <span className="flex items-center gap-1.5 text-amber-700">
            <Wrench className="w-3.5 h-3.5" /> HERRAMIENTAS DISPONIBLES ({tools.length})
          </span>
        </div>

        <div className="space-y-1.5 text-[13px]">
          {tools.map(tool => {
            const isEnabled = agent.toolsEnabled?.includes(tool.id) || tool.isEnabled;
            return (
              <div 
                key={tool.id} 
                onClick={() => onToggleTool(tool.id)}
                className={`p-2 rounded-md border transition-all cursor-pointer flex items-center justify-between ${
                  isEnabled 
                    ? 'bg-slate-100 border-blue-600/50 text-slate-900' 
                    : 'bg-slate-50/60 border-slate-300/80 text-slate-700 hover:text-slate-700'
                }`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span className={`w-4 h-4 rounded flex items-center justify-center text-[12px] ${isEnabled ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700'}`}>
                    {isEnabled ? <Check className="w-3 h-3 stroke-[3]" /> : null}
                  </span>
                  <span className="font-medium truncate">{tool.name}</span>
                </div>
                <span className="text-[11px] font-mono opacity-60 bg-white px-1 py-0.5 rounded">
                  {tool.category}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* KNOWLEDGE SOURCES SECTION */}
      <div className="p-3 border-b border-slate-200/80 space-y-2">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-700 uppercase tracking-wider">
          <span className="flex items-center gap-1.5 text-purple-700">
            <BookOpen className="w-3.5 h-3.5" /> CONOCIMIENTO ADJUNTO
          </span>
        </div>

        <div className="space-y-1.5 text-[13px]">
          {knowledgeSources.map(source => (
            <div key={source.id} className="p-2 bg-slate-100 rounded-md border border-slate-300 flex items-start gap-2">
              {source.type === 'Database' && <Database className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />}
              {source.type === 'Document' && <FileText className="w-3.5 h-3.5 text-green-600 shrink-0 mt-0.5" />}
              {source.type === 'Vector DB' && <Layers className="w-3.5 h-3.5 text-purple-700 shrink-0 mt-0.5" />}
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-slate-700 truncate">{source.name}</span>
                  <span className="text-[11px] font-mono text-green-600 bg-green-600950/60 px-1 rounded border border-green-600/60">
                    {source.status}
                  </span>
                </div>
                <p className="text-[12px] text-slate-700 font-mono mt-0.5">
                  {source.vectorCount.toLocaleString()} vectors • {source.fileSize}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* HYPERPARAMETERS CONFIGURATION */}
      <div className="p-3 border-b border-slate-200/80 space-y-2.5">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-700 uppercase tracking-wider">
          <span className="flex items-center gap-1.5 text-blue-600">
            <Sliders className="w-3.5 h-3.5" /> HYPERPARAMETERS
          </span>
        </div>

        <div className="space-y-2.5 text-[13px] bg-slate-100 p-2.5 rounded-lg border border-slate-300">
          <div>
            <div className="flex items-center justify-between text-slate-700 mb-1">
              <span>Temperature</span>
              <span className="font-mono text-blue-600 font-bold">{temperature.toFixed(2)}</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="0.05" 
              value={temperature}
              onChange={handleTempChange}
              className="w-full accent-indigo-500 bg-slate-100 h-1 rounded cursor-pointer"
            />
          </div>

          <div>
            <div className="flex items-center justify-between text-slate-700 mb-1">
              <span>Top_P</span>
              <span className="font-mono text-blue-600 font-bold">{topP.toFixed(2)}</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="0.05" 
              value={topP}
              onChange={handleTopPChange}
              className="w-full accent-indigo-500 bg-slate-100 h-1 rounded cursor-pointer"
            />
          </div>

          <div>
            <div className="flex items-center justify-between text-slate-700 mb-1">
              <span>Context Length</span>
              <span className="font-mono text-blue-600 font-bold">{contextLength}</span>
            </div>
            <input 
              type="range" 
              min="1024" 
              max="32768" 
              step="1024" 
              value={contextLength}
              onChange={handleContextChange}
              className="w-full accent-indigo-500 bg-slate-100 h-1 rounded cursor-pointer"
            />
          </div>
        </div>
      </div>

      {/* CONVERSATION CONTROLS */}
      <div className="p-3 space-y-2 bg-white mt-auto">
        <div className="text-[12px] font-semibold text-slate-700 uppercase tracking-wider">
          Conversation Controls
        </div>

        <div className="grid grid-cols-2 gap-1.5 text-[13px]">
          <button 
            onClick={onExportChat}
            className="flex items-center justify-center gap-1.5 p-1.5 bg-slate-100 hover:bg-slate-100 text-slate-700 rounded border border-slate-700 transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-blue-600" /> Export
          </button>
          <button 
            onClick={onClearChat}
            className="flex items-center justify-center gap-1.5 p-1.5 bg-slate-100 hover:bg-red-950/60 hover:text-red-300 text-slate-700 rounded border border-slate-700 hover:border-red-800 transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5 text-red-400" /> Clear
          </button>
          <button 
            onClick={() => setIsFavorite(!isFavorite)}
            className={`flex items-center justify-center gap-1.5 p-1.5 rounded border transition-colors ${isFavorite ? 'bg-amber-100/40 text-amber-700 border-amber-800/80' : 'bg-slate-100 text-slate-700 border-slate-700'}`}
          >
            <Star className={`w-3.5 h-3.5 ${isFavorite ? 'fill-amber-400 text-amber-700' : ''}`} /> Favorite
          </button>
          <button 
            onClick={() => setIsPinned(!isPinned)}
            className={`flex items-center justify-center gap-1.5 p-1.5 rounded border transition-colors ${isPinned ? 'bg-slate-50/40 text-blue-600 border-blue-600-800/80' : 'bg-slate-100 text-slate-700 border-slate-700'}`}
          >
            <Pin className={`w-3.5 h-3.5 ${isPinned ? 'fill-blue-600 text-blue-600' : ''}`} /> Pin
          </button>
        </div>

        <div className="pt-2 border-t border-slate-300 flex items-center justify-between text-[12px] text-slate-700 font-mono">
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-3 h-3 text-green-600" /> Local RBAC: Admin
          </span>
          <span className="text-slate-700">Encrypted AES-256</span>
        </div>
      </div>
    </aside>
  );
};
