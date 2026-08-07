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
    <aside className="w-[280px] shrink-0 bg-[#0f1419] border-l border-[#1e293b] flex flex-col h-full text-slate-300 select-none overflow-y-auto custom-scrollbar">
      {/* AGENT DETAILS SECTION */}
      <div className="p-3 border-b border-[#1e293b]/80 space-y-2">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
          <span className="flex items-center gap-1.5 text-indigo-400">
            <Bot className="w-3.5 h-3.5" /> AGENT DETAILS
          </span>
          <span className="text-[10px] bg-slate-800 text-slate-300 font-mono px-1.5 py-0.5 rounded border border-slate-700">
            {agent.role}
          </span>
        </div>

        <div className="bg-[#131c28] p-3 rounded-lg border border-slate-800 space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-md bg-indigo-600/30 border border-indigo-500/50 flex items-center justify-center text-indigo-300 font-bold text-sm shadow">
              {agent.name.substring(0, 2).toUpperCase()}
            </div>
            <div>
              <h3 className="font-bold text-sm text-slate-100">{agent.name}</h3>
              <p className="text-[11px] font-mono text-indigo-400">ID: {agent.id.substring(0, 14)}...</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-x-2 gap-y-1.5 text-[11px] pt-1 border-t border-slate-800/80 font-sans">
            <div>
              <span className="text-slate-500 block text-[10px]">Model:</span>
              <span className="font-mono text-slate-200 font-medium">{agent.model}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px]">Status:</span>
              <span className="text-emerald-400 font-medium flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Online
              </span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px]">Availability:</span>
              <span className="text-slate-300 font-mono">24/7 Local</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px]">Skills Count:</span>
              <span className="text-slate-300 font-medium">{agent.skillsCount} Enabled</span>
            </div>
          </div>

          <p className="text-[11px] text-slate-400 italic bg-slate-900/60 p-1.5 rounded border border-slate-800/80 leading-relaxed">
            "{agent.description}"
          </p>
        </div>
      </div>

      {/* TOOLS & CAPABILITIES SECTION */}
      <div className="p-3 border-b border-[#1e293b]/80 space-y-2">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
          <span className="flex items-center gap-1.5 text-amber-400">
            <Wrench className="w-3.5 h-3.5" /> AVAILABLE TOOLS ({tools.length})
          </span>
        </div>

        <div className="space-y-1.5 text-[11px]">
          {tools.map(tool => {
            const isEnabled = agent.toolsEnabled?.includes(tool.id) || tool.isEnabled;
            return (
              <div 
                key={tool.id} 
                onClick={() => onToggleTool(tool.id)}
                className={`p-2 rounded-md border transition-all cursor-pointer flex items-center justify-between ${
                  isEnabled 
                    ? 'bg-[#152132] border-indigo-500/50 text-slate-100' 
                    : 'bg-[#101722]/60 border-slate-800/80 text-slate-500 hover:text-slate-400'
                }`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span className={`w-4 h-4 rounded flex items-center justify-center text-[10px] ${isEnabled ? 'bg-indigo-500 text-white' : 'bg-slate-800 text-slate-500'}`}>
                    {isEnabled ? <Check className="w-3 h-3 stroke-[3]" /> : null}
                  </span>
                  <span className="font-medium truncate">{tool.name}</span>
                </div>
                <span className="text-[9px] font-mono opacity-60 bg-slate-900 px-1 py-0.5 rounded">
                  {tool.category}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* KNOWLEDGE SOURCES SECTION */}
      <div className="p-3 border-b border-[#1e293b]/80 space-y-2">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
          <span className="flex items-center gap-1.5 text-purple-400">
            <BookOpen className="w-3.5 h-3.5" /> ATTACHED KNOWLEDGE
          </span>
        </div>

        <div className="space-y-1.5 text-[11px]">
          {knowledgeSources.map(source => (
            <div key={source.id} className="p-2 bg-[#121926] rounded-md border border-slate-800 flex items-start gap-2">
              {source.type === 'Database' && <Database className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />}
              {source.type === 'Document' && <FileText className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />}
              {source.type === 'Vector DB' && <Layers className="w-3.5 h-3.5 text-purple-400 shrink-0 mt-0.5" />}
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-slate-200 truncate">{source.name}</span>
                  <span className="text-[9px] font-mono text-emerald-400 bg-emerald-950/60 px-1 rounded border border-emerald-800/60">
                    {source.status}
                  </span>
                </div>
                <p className="text-[10px] text-slate-500 font-mono mt-0.5">
                  {source.vectorCount.toLocaleString()} vectors • {source.fileSize}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* HYPERPARAMETERS CONFIGURATION */}
      <div className="p-3 border-b border-[#1e293b]/80 space-y-2.5">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
          <span className="flex items-center gap-1.5 text-indigo-400">
            <Sliders className="w-3.5 h-3.5" /> HYPERPARAMETERS
          </span>
        </div>

        <div className="space-y-2.5 text-[11px] bg-[#121822] p-2.5 rounded-lg border border-slate-800">
          <div>
            <div className="flex items-center justify-between text-slate-300 mb-1">
              <span>Temperature</span>
              <span className="font-mono text-indigo-400 font-bold">{temperature.toFixed(2)}</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="0.05" 
              value={temperature}
              onChange={handleTempChange}
              className="w-full accent-indigo-500 bg-slate-800 h-1 rounded cursor-pointer"
            />
          </div>

          <div>
            <div className="flex items-center justify-between text-slate-300 mb-1">
              <span>Top_P</span>
              <span className="font-mono text-indigo-400 font-bold">{topP.toFixed(2)}</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="0.05" 
              value={topP}
              onChange={handleTopPChange}
              className="w-full accent-indigo-500 bg-slate-800 h-1 rounded cursor-pointer"
            />
          </div>

          <div>
            <div className="flex items-center justify-between text-slate-300 mb-1">
              <span>Context Length</span>
              <span className="font-mono text-indigo-400 font-bold">{contextLength}</span>
            </div>
            <input 
              type="range" 
              min="1024" 
              max="32768" 
              step="1024" 
              value={contextLength}
              onChange={handleContextChange}
              className="w-full accent-indigo-500 bg-slate-800 h-1 rounded cursor-pointer"
            />
          </div>
        </div>
      </div>

      {/* CONVERSATION CONTROLS */}
      <div className="p-3 space-y-2 bg-[#0d1218] mt-auto">
        <div className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
          Conversation Controls
        </div>

        <div className="grid grid-cols-2 gap-1.5 text-[11px]">
          <button 
            onClick={onExportChat}
            className="flex items-center justify-center gap-1.5 p-1.5 bg-[#1a2332] hover:bg-slate-700 text-slate-200 rounded border border-slate-700 transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-indigo-400" /> Export
          </button>
          <button 
            onClick={onClearChat}
            className="flex items-center justify-center gap-1.5 p-1.5 bg-[#1a2332] hover:bg-red-950/60 hover:text-red-300 text-slate-200 rounded border border-slate-700 hover:border-red-800 transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5 text-red-400" /> Clear
          </button>
          <button 
            onClick={() => setIsFavorite(!isFavorite)}
            className={`flex items-center justify-center gap-1.5 p-1.5 rounded border transition-colors ${isFavorite ? 'bg-amber-950/40 text-amber-300 border-amber-800/80' : 'bg-[#1a2332] text-slate-300 border-slate-700'}`}
          >
            <Star className={`w-3.5 h-3.5 ${isFavorite ? 'fill-amber-400 text-amber-400' : ''}`} /> Favorite
          </button>
          <button 
            onClick={() => setIsPinned(!isPinned)}
            className={`flex items-center justify-center gap-1.5 p-1.5 rounded border transition-colors ${isPinned ? 'bg-indigo-950/40 text-indigo-300 border-indigo-800/80' : 'bg-[#1a2332] text-slate-300 border-slate-700'}`}
          >
            <Pin className={`w-3.5 h-3.5 ${isPinned ? 'fill-indigo-400 text-indigo-400' : ''}`} /> Pin
          </button>
        </div>

        <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-500 font-mono">
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-3 h-3 text-emerald-400" /> Local RBAC: Admin
          </span>
          <span className="text-slate-400">Encrypted AES-256</span>
        </div>
      </div>
    </aside>
  );
};
