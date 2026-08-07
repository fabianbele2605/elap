import React, { useState } from 'react';
import { 
  Zap, 
  Search, 
  Plus, 
  Settings, 
  CheckCircle2, 
  Clock, 
  Bot, 
  Activity, 
  Brain, 
  Cpu, 
  SlidersHorizontal,
  Circle,
  TrendingUp,
  Sparkles
} from 'lucide-react';
import { Agent } from '../types';

interface LeftSidebarProps {
  agents: Agent[];
  selectedAgentId: string;
  onSelectAgent: (agentId: string) => void;
  onOpenNewAgentModal: () => void;
  onOpenSettingsModal: () => void;
  rustPortStatus: boolean;
  grpcPortStatus: boolean;
  ollamaPortStatus: boolean;
}

export const LeftSidebar: React.FC<LeftSidebarProps> = ({
  agents,
  selectedAgentId,
  onSelectAgent,
  onOpenNewAgentModal,
  onOpenSettingsModal,
  rustPortStatus,
  grpcPortStatus,
  ollamaPortStatus
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState<'all' | 'active' | 'recent'>('all');

  // Helper color map for agent badges
  const getAvatarBadgeClass = (colorName: string) => {
    switch (colorName) {
      case 'indigo':
        return 'bg-indigo-500/20 text-indigo-400 border-indigo-500/40';
      case 'emerald':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
      case 'amber':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      case 'purple':
        return 'bg-purple-500/20 text-purple-400 border-purple-500/40';
      case 'rose':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/40';
      default:
        return 'bg-blue-500/20 text-blue-400 border-blue-500/40';
    }
  };

  const getStatusDot = (status: string) => {
    switch (status) {
      case 'online':
        return <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" title="Online"></span>;
      case 'busy':
        return <span className="w-2 h-2 rounded-full bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.8)]" title="Busy"></span>;
      case 'idle':
        return <span className="w-2 h-2 rounded-full bg-slate-400" title="Idle"></span>;
      default:
        return <span className="w-2 h-2 rounded-full bg-red-400" title="Offline"></span>;
    }
  };

  const filteredAgents = agents.filter(agent => {
    const matchesQuery = agent.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         agent.role.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         agent.model.toLowerCase().includes(searchQuery.toLowerCase());
    
    if (!matchesQuery) return false;
    if (filter === 'active') return agent.status === 'online' || agent.status === 'busy';
    if (filter === 'recent') return agent.lastActive.includes('min') || agent.lastActive.includes('Just');
    return true;
  });

  return (
    <aside className="w-[220px] shrink-0 bg-[#0f1419] border-r border-[#1e293b] flex flex-col h-full text-slate-300 select-none">
      {/* Header & Logo */}
      <div className="p-3 border-b border-[#1e293b]/80 space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
              <Zap className="w-4 h-4 fill-white" />
            </div>
            <div>
              <h1 className="font-bold text-sm text-slate-100 tracking-tight leading-none flex items-center gap-1">
                ELAP <span className="text-[10px] text-indigo-400 font-mono bg-indigo-950/80 px-1 rounded border border-indigo-800">v1.4</span>
              </h1>
              <p className="text-[10px] text-slate-400">Agents Navigator</p>
            </div>
          </div>
        </div>

        {/* Search input */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search agents..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#182232] text-slate-200 placeholder-slate-500 text-[11px] rounded-md pl-8 pr-2 py-1.5 border border-slate-700/80 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center justify-between bg-[#151c27] p-0.5 rounded-md border border-slate-800 text-[11px]">
          <button 
            onClick={() => setFilter('all')}
            className={`flex-1 py-0.5 rounded text-center transition-all ${filter === 'all' ? 'bg-indigo-600 text-white font-medium shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
          >
            All
          </button>
          <button 
            onClick={() => setFilter('active')}
            className={`flex-1 py-0.5 rounded text-center transition-all ${filter === 'active' ? 'bg-indigo-600 text-white font-medium shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Active
          </button>
          <button 
            onClick={() => setFilter('recent')}
            className={`flex-1 py-0.5 rounded text-center transition-all ${filter === 'recent' ? 'bg-indigo-600 text-white font-medium shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Recent
          </button>
        </div>
      </div>

      {/* Agents Scrollable List */}
      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1.5 custom-scrollbar">
        <div className="px-1 py-0.5 flex items-center justify-between text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
          <span>Available Agents ({filteredAgents.length})</span>
          <Bot className="w-3 h-3 text-slate-400" />
        </div>

        {filteredAgents.map(agent => {
          const isSelected = agent.id === selectedAgentId;
          return (
            <div
              key={agent.id}
              onClick={() => onSelectAgent(agent.id)}
              className={`group relative p-2 rounded-lg cursor-pointer transition-all border ${
                isSelected 
                  ? 'bg-[#1e293b] border-indigo-500/80 shadow-md shadow-indigo-950/50 text-slate-100' 
                  : 'bg-[#131b26]/80 hover:bg-[#182333] border-slate-800/80 hover:border-slate-700 text-slate-300'
              }`}
            >
              {/* Selected indicator bar on left */}
              {isSelected && (
                <div className="absolute left-0 top-1.5 bottom-1.5 w-1 bg-indigo-500 rounded-r-full"></div>
              )}

              <div className="flex items-start justify-between mb-1 pl-1">
                <div className="flex items-center gap-1.5 min-w-0">
                  {getStatusDot(agent.status)}
                  <span className="font-semibold text-xs truncate text-slate-100 group-hover:text-indigo-300 transition-colors">
                    {agent.name}
                  </span>
                </div>
                <span className={`text-[9px] px-1.5 py-0.2 rounded border font-mono ${getAvatarBadgeClass(agent.avatarColor)}`}>
                  {agent.role}
                </span>
              </div>

              <div className="pl-3 space-y-1 text-[10px]">
                <div className="flex items-center justify-between text-slate-400">
                  <span className="font-mono text-[10px] bg-slate-900/90 px-1 py-0.5 rounded border border-slate-800 text-indigo-300/90">
                    {agent.model}
                  </span>
                  <span className="flex items-center gap-1 text-[9px] text-slate-400">
                    <Clock className="w-2.5 h-2.5" />
                    {agent.lastActive}
                  </span>
                </div>
              </div>
            </div>
          );
        })}

        {filteredAgents.length === 0 && (
          <div className="text-center py-6 px-2 text-slate-500 text-xs">
            <p>No agents match filter</p>
          </div>
        )}
      </div>

      {/* Bottom Controls & System Status */}
      <div className="p-2 border-t border-[#1e293b]/80 space-y-2 bg-[#0c1015]">
        {/* Buttons */}
        <div className="grid grid-cols-2 gap-1.5">
          <button 
            onClick={onOpenNewAgentModal}
            className="flex items-center justify-center gap-1 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-[11px] py-1.5 px-2 rounded-md shadow transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>NEW AGENT</span>
          </button>
          <button 
            onClick={onOpenSettingsModal}
            className="flex items-center justify-center gap-1 bg-[#1e293b] hover:bg-slate-700 text-slate-200 text-[11px] py-1.5 px-2 rounded-md border border-slate-700 transition-colors"
          >
            <Settings className="w-3.5 h-3.5" />
            <span>SETTINGS</span>
          </button>
        </div>

        {/* Connection Status Box */}
        <div className="bg-[#121924] p-2 rounded-md border border-slate-800/80 space-y-1 text-[10px] font-mono">
          <div className="text-[9px] text-slate-500 font-sans uppercase font-bold tracking-wider mb-1 flex items-center justify-between">
            <span>Core Connections</span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span>
          </div>

          <div className="flex items-center justify-between text-slate-300">
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Rust Core
            </span>
            <span className="text-slate-500">(3000)</span>
          </div>

          <div className="flex items-center justify-between text-slate-300">
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Python gRPC
            </span>
            <span className="text-slate-500">(50051)</span>
          </div>

          <div className="flex items-center justify-between text-slate-300">
            <span className="flex items-center gap-1">
              <Brain className="w-3 h-3 text-indigo-400" /> Ollama Local
            </span>
            <span className="text-slate-500">(11434)</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
