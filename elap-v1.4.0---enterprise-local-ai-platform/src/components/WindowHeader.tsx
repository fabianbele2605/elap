import React, { useState } from 'react';
import { 
  Zap, 
  Minus, 
  Square, 
  X, 
  ChevronDown, 
  Activity, 
  FolderOpen, 
  Shield, 
  Terminal, 
  HelpCircle,
  RefreshCw,
  Cpu,
  Sliders,
  Bell
} from 'lucide-react';

interface WindowHeaderProps {
  projectName: string;
  onOpenSettings: () => void;
  onOpenNewAgent: () => void;
  activeTab: string;
  setActiveTab: (tab: any) => void;
}

export const WindowHeader: React.FC<WindowHeaderProps> = ({
  projectName,
  onOpenSettings,
  onOpenNewAgent,
  activeTab,
  setActiveTab
}) => {
  const [openMenu, setOpenMenu] = useState<string | null>(null);

  const toggleMenu = (menuName: string) => {
    setOpenMenu(openMenu === menuName ? null : menuName);
  };

  return (
    <header className="bg-[#0f1419] border-b border-[#1e293b] select-none z-30 flex flex-col shrink-0">
      {/* Top Title Bar & Window Chrome */}
      <div className="h-8 px-3 flex items-center justify-between text-xs text-slate-400 border-b border-[#1a2332]/60 bg-[#0b0f13]">
        {/* Left: MacOS Traffic Light Controls */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 group pr-2 border-r border-slate-800">
            <button 
              title="Close ELAP Window" 
              className="w-3 h-3 rounded-full bg-red-500/90 hover:bg-red-600 flex items-center justify-center text-[8px] text-red-950 font-bold opacity-80 group-hover:opacity-100 transition-opacity"
            >
              <X className="w-2 h-2 opacity-0 group-hover:opacity-100" />
            </button>
            <button 
              title="Minimize" 
              className="w-3 h-3 rounded-full bg-amber-500/90 hover:bg-amber-600 flex items-center justify-center text-[8px] text-amber-950 font-bold opacity-80 group-hover:opacity-100 transition-opacity"
            >
              <Minus className="w-2 h-2 opacity-0 group-hover:opacity-100" />
            </button>
            <button 
              title="Maximize" 
              className="w-3 h-3 rounded-full bg-emerald-500/90 hover:bg-emerald-600 flex items-center justify-center text-[8px] text-emerald-950 font-bold opacity-80 group-hover:opacity-100 transition-opacity"
            >
              <Square className="w-2 h-2 opacity-0 group-hover:opacity-100" />
            </button>
          </div>

          <div className="flex items-center gap-1.5 font-medium text-slate-300 pl-1">
            <Zap className="w-3.5 h-3.5 text-indigo-400 fill-indigo-400/20" />
            <span className="font-semibold text-slate-200">ELAP v1.4.0</span>
            <span className="text-slate-500">—</span>
            <span className="text-slate-400 font-mono text-[11px] bg-slate-800/80 px-1.5 py-0.5 rounded border border-slate-700/50">
              Enterprise Local AI Platform [{projectName}]
            </span>
          </div>
        </div>

        {/* Center: Active Context Indicator */}
        <div className="hidden md:flex items-center gap-2 text-[11px]">
          <span className="inline-flex items-center gap-1 text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded-full border border-emerald-800/50 font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            LOCAL INFERENCE ENGINE ONLINE
          </span>
        </div>

        {/* Right: Quick Action Controls */}
        <div className="flex items-center gap-2 text-slate-400">
          <button 
            onClick={onOpenSettings} 
            className="hover:text-slate-200 p-1 hover:bg-slate-800 rounded transition-colors flex items-center gap-1"
            title="System Settings"
          >
            <Sliders className="w-3.5 h-3.5" />
            <span className="hidden xl:inline text-[11px]">Config</span>
          </button>
          <div className="w-px h-3 bg-slate-800"></div>
          <span className="text-[10px] font-mono text-slate-500">v1.4.0-stable</span>
        </div>
      </div>

      {/* Menu Bar (File | Edit | View | Agents | Tools | Help) */}
      <div className="h-7 px-3 flex items-center gap-1 text-[12px] bg-[#0f172a] text-slate-300 font-sans border-b border-slate-800/80">
        {/* Menu Dropdown: File */}
        <div className="relative">
          <button 
            onClick={() => toggleMenu('file')}
            className={`px-2 py-0.5 rounded hover:bg-slate-800 transition-colors flex items-center gap-1 ${openMenu === 'file' ? 'bg-slate-800 text-white' : ''}`}
          >
            File <ChevronDown className="w-3 h-3 text-slate-500" />
          </button>
          {openMenu === 'file' && (
            <div className="absolute top-full left-0 mt-1 w-48 bg-[#1e293b] border border-slate-700 rounded-md shadow-2xl z-50 py-1 text-slate-200 text-xs">
              <button onClick={() => { onOpenNewAgent(); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white flex items-center justify-between">
                <span>New Agent...</span>
                <span className="text-[10px] opacity-60">⌘N</span>
              </button>
              <button onClick={() => { setActiveTab('history'); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white flex items-center justify-between">
                <span>Open History Logs</span>
                <span className="text-[10px] opacity-60">⌘H</span>
              </button>
              <div className="my-1 border-t border-slate-700/80"></div>
              <button onClick={() => { onOpenSettings(); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white flex items-center justify-between">
                <span>Preferences / Settings</span>
                <span className="text-[10px] opacity-60">⌘,</span>
              </button>
            </div>
          )}
        </div>

        {/* Menu Dropdown: Edit */}
        <div className="relative">
          <button 
            onClick={() => toggleMenu('edit')}
            className={`px-2 py-0.5 rounded hover:bg-slate-800 transition-colors flex items-center gap-1 ${openMenu === 'edit' ? 'bg-slate-800 text-white' : ''}`}
          >
            Edit <ChevronDown className="w-3 h-3 text-slate-500" />
          </button>
          {openMenu === 'edit' && (
            <div className="absolute top-full left-0 mt-1 w-44 bg-[#1e293b] border border-slate-700 rounded-md shadow-2xl z-50 py-1 text-slate-200 text-xs">
              <button className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white">Clear Active Session</button>
              <button className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white">Reset Model Context</button>
              <button className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white">Export Conversation JSON</button>
            </div>
          )}
        </div>

        {/* Menu Dropdown: View */}
        <div className="relative">
          <button 
            onClick={() => toggleMenu('view')}
            className={`px-2 py-0.5 rounded hover:bg-slate-800 transition-colors flex items-center gap-1 ${openMenu === 'view' ? 'bg-slate-800 text-white' : ''}`}
          >
            View <ChevronDown className="w-3 h-3 text-slate-500" />
          </button>
          {openMenu === 'view' && (
            <div className="absolute top-full left-0 mt-1 w-48 bg-[#1e293b] border border-slate-700 rounded-md shadow-2xl z-50 py-1 text-slate-200 text-xs">
              <button onClick={() => { setActiveTab('chat'); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white">💬 Chat View</button>
              <button onClick={() => { setActiveTab('dashboard'); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white">📊 Analytics Dashboard</button>
              <button onClick={() => { setActiveTab('tools'); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white">🛠️ Tool Chains</button>
              <button onClick={() => { setActiveTab('knowledge'); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white">📚 Knowledge Base</button>
            </div>
          )}
        </div>

        {/* Menu Dropdown: Agents */}
        <div className="relative">
          <button 
            onClick={() => toggleMenu('agents')}
            className={`px-2 py-0.5 rounded hover:bg-slate-800 transition-colors flex items-center gap-1 ${openMenu === 'agents' ? 'bg-slate-800 text-white' : ''}`}
          >
            Agents <ChevronDown className="w-3 h-3 text-slate-500" />
          </button>
          {openMenu === 'agents' && (
            <div className="absolute top-full left-0 mt-1 w-52 bg-[#1e293b] border border-slate-700 rounded-md shadow-2xl z-50 py-1 text-slate-200 text-xs">
              <button onClick={() => { onOpenNewAgent(); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white">➕ Create Agent</button>
              <button className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white">🔄 Reload Agent Profiles</button>
              <button className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white">🧠 Ollama Model Puller</button>
            </div>
          )}
        </div>

        {/* Menu Dropdown: Tools */}
        <div className="relative">
          <button 
            onClick={() => toggleMenu('tools')}
            className={`px-2 py-0.5 rounded hover:bg-slate-800 transition-colors flex items-center gap-1 ${openMenu === 'tools' ? 'bg-slate-800 text-white' : ''}`}
          >
            Tools <ChevronDown className="w-3 h-3 text-slate-500" />
          </button>
          {openMenu === 'tools' && (
            <div className="absolute top-full left-0 mt-1 w-48 bg-[#1e293b] border border-slate-700 rounded-md shadow-2xl z-50 py-1 text-slate-200 text-xs">
              <button onClick={() => { setActiveTab('tools'); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white">Tool Marketplace</button>
              <button onClick={() => { setActiveTab('tools'); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white">Visual Chain Builder</button>
            </div>
          )}
        </div>

        {/* Menu Dropdown: Help */}
        <div className="relative">
          <button 
            onClick={() => toggleMenu('help')}
            className={`px-2 py-0.5 rounded hover:bg-slate-800 transition-colors flex items-center gap-1 ${openMenu === 'help' ? 'bg-slate-800 text-white' : ''}`}
          >
            Help <ChevronDown className="w-3 h-3 text-slate-500" />
          </button>
          {openMenu === 'help' && (
            <div className="absolute top-full left-0 mt-1 w-48 bg-[#1e293b] border border-slate-700 rounded-md shadow-2xl z-50 py-1 text-slate-200 text-xs">
              <button className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white">ELAP Documentation</button>
              <button className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white">Ollama Connectivity Test</button>
              <button className="w-full text-left px-3 py-1.5 hover:bg-indigo-600 hover:text-white">About ELAP v1.4.0</button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
