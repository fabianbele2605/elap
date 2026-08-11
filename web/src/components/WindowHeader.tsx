import { API_BASE_URL } from '../../config/api';
import React, { useState, useEffect } from 'react';
import {
  Zap,
  Minus,
  Square,
  X,
  ChevronDown,
  Activity,
  FolderOpen,
  ShieldCheck,
  Terminal,
  HelpCircle,
  RefreshCw,
  Cpu,
  Sliders,
  Bell
} from 'lucide-react';

interface MenuItem {
  label: string;
  action?: string;
  shortcut?: string;
  icon?: string;
  divider?: boolean;
}

interface MenuCategory {
  label: string;
  items: MenuItem[];
}

interface MenuConfig {
  [key: string]: MenuCategory;
}

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
  const [menuConfig, setMenuConfig] = useState<MenuConfig | null>(null);
  const [loading, setLoading] = useState(true);

  // Cargar configuración del menú desde API
  useEffect(() => {
    const loadMenuConfig = async () => {
      try {
        setLoading(true);
        const response = await fetch('${API_BASE_URL}/api/menu-config');
        if (response.ok) {
          const config = await response.json();
          setMenuConfig(config);
          console.log('✅ Configuración del menú cargada desde API');
        } else {
          console.log('⚠️ API no disponible, usando menú por defecto');
          setMenuConfig(null);
        }
      } catch (error) {
        console.log('⚠️ No se pudo conectar a API:', error);
        setMenuConfig(null);
      } finally {
        setLoading(false);
      }
    };

    loadMenuConfig();
  }, []);

  const toggleMenu = (menuName: string) => {
    setOpenMenu(openMenu === menuName ? null : menuName);
  };

  const handleMenuAction = (action?: string) => {
    if (!action) return;

    if (action.startsWith('setActiveTab:')) {
      const tab = action.split(':')[1];
      setActiveTab(tab);
      setOpenMenu(null);
    } else if (action === 'openNewAgent') {
      onOpenNewAgent();
      setOpenMenu(null);
    } else if (action === 'openSettings') {
      onOpenSettings();
      setOpenMenu(null);
    }
  };

  return (
    <header className="bg-white border-b border-slate-200 select-none z-30 flex flex-col shrink-0">
      {/* Top Title Bar & Window Chrome */}
      <div className="h-8 px-3 flex flex-row items-center justify-between text-xs text-slate-600 border-b border-slate-100 bg-white gap-1">
        {/* Left: MacOS Traffic Light Controls */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 group pr-2 border-r border-slate-300">
            <button 
              title="Close ELAP Window" 
              className="w-3 h-3 rounded-full bg-red-500/90 hover:bg-red-600 flex items-center justify-center text-[10px] text-red-950 font-bold opacity-80 group-hover:opacity-100 transition-opacity"
            >
              <X className="w-2 h-2 opacity-0 group-hover:opacity-100" />
            </button>
            <button 
              title="Minimize" 
              className="w-3 h-3 rounded-full bg-amber-500/90 hover:bg-amber-600 flex items-center justify-center text-[10px] text-amber-950 font-bold opacity-80 group-hover:opacity-100 transition-opacity"
            >
              <Minus className="w-2 h-2 opacity-0 group-hover:opacity-100" />
            </button>
            <button 
              title="Maximize" 
              className="w-3 h-3 rounded-full bg-green-600500/90 hover:bg-green-600600 flex items-center justify-center text-[10px] text-emerald-700 font-bold opacity-80 group-hover:opacity-100 transition-opacity"
            >
              <Square className="w-2 h-2 opacity-0 group-hover:opacity-100" />
            </button>
          </div>

          <div className="flex items-center gap-1.5 font-medium text-slate-700 pl-1">
            <Zap className="w-3.5 h-3.5 text-blue-600 fill-blue-600/20" />
            <span className="font-semibold text-slate-700">ELAP v1.5.0</span>
            <span className="text-slate-700">—</span>
            <span className="text-slate-700 font-mono text-[13px] bg-slate-100/80 px-1.5 py-0.5 rounded border border-slate-700/50">
              Enterprise Local AI Platform [{projectName}]
            </span>
          </div>
        </div>

        {/* Center: Active Context Indicator */}
        <div className="hidden md:flex items-center gap-2 text-[13px]">
          <span className="inline-flex items-center gap-1 text-green-600 bg-green-600950/40 px-2 py-0.5 rounded-full border border-green-600/50 font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-green-600400 animate-pulse"></span>
            LOCAL INFERENCE ENGINE ONLINE
          </span>
        </div>

        {/* Right: Quick Action Controls */}
        <div className="flex items-center gap-2 text-slate-700">
          <button 
            onClick={onOpenSettings} 
            className="hover:text-slate-700 p-1 hover:bg-slate-100 rounded transition-colors flex items-center gap-1"
            title="System Settings"
          >
            <Sliders className="w-3.5 h-3.5" />
            <span className="hidden xl:inline text-[13px]">Config</span>
          </button>
          <div className="w-px h-3 bg-slate-100"></div>
          <span className="text-[12px] font-mono text-slate-700">v1.5.0-stable</span>
        </div>
      </div>

      {/* Menu Bar (File | Editar | Ver | Agentes | Tools | Ayuda) */}
      <div className="h-7 px-2 sm:px-3 flex flex-nowrap items-center gap-0.5 sm:gap-1 text-[11px] sm:text-[12px] bg-white text-slate-700 font-sans border-b border-slate-200 overflow-x-auto">
        {/* Menu Dropdown: File */}
        <div className="relative">
          <button
            onClick={() => toggleMenu('file')}
            className={`px-2 py-0.5 rounded hover:bg-slate-100 transition-colors flex items-center gap-1 ${openMenu === 'file' ? 'bg-slate-100 text-slate-900' : ''}`}
          >
            File <ChevronDown className="w-3 h-3 text-slate-700" />
          </button>
          {openMenu === 'file' && (
            <div className="absolute top-full left-0 mt-1 w-48 bg-white border border-slate-200 rounded-md shadow-lg z-50 py-1 text-slate-700 text-xs">
              <button onClick={() => { onOpenNewAgent(); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-blue-50 hover:text-blue-700 flex items-center justify-between">
                <span>Nuevo Agente...</span>
                <span className="text-[12px] opacity-60">⌘N</span>
              </button>
              <button onClick={() => { setActiveTab('history'); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-blue-50 hover:text-blue-700 flex items-center justify-between">
                <span>Abrir Registros</span>
                <span className="text-[12px] opacity-60">⌘H</span>
              </button>
              <div className="my-1 border-t border-slate-700/80"></div>
              <button onClick={() => { onOpenSettings(); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-blue-50 hover:text-blue-700 flex items-center justify-between">
                <span>Preferencias / Settings</span>
                <span className="text-[12px] opacity-60">⌘,</span>
              </button>
            </div>
          )}
        </div>

        {/* Menu Dropdown: Editar */}
        <div className="relative">
          <button 
            onClick={() => toggleMenu('edit')}
            className={`px-2 py-0.5 rounded hover:bg-slate-100 transition-colors flex items-center gap-1 ${openMenu === 'edit' ? 'bg-slate-100 text-white' : ''}`}
          >
            Editar <ChevronDown className="w-3 h-3 text-slate-700" />
          </button>
          {openMenu === 'edit' && (
            <div className="absolute top-full left-0 mt-1 w-44 bg-slate-100 border border-slate-700 rounded-md shadow-2xl z-50 py-1 text-slate-700 text-xs">
              <button className="w-full text-left px-3 py-1.5 hover:bg-blue-50 hover:text-blue-700">Limpiar Sesión Activa</button>
              <button className="w-full text-left px-3 py-1.5 hover:bg-blue-50 hover:text-blue-700">Reset Model Context</button>
              <button className="w-full text-left px-3 py-1.5 hover:bg-blue-50 hover:text-blue-700">Exportar Conversación</button>
            </div>
          )}
        </div>

        {/* Menu Dropdown: Ver (Dinámico desde API) */}
        <div className="relative">
          <button
            onClick={() => toggleMenu('view')}
            className={`px-2 py-0.5 rounded hover:bg-slate-100 transition-colors flex items-center gap-1 ${openMenu === 'view' ? 'bg-slate-100 text-white' : ''}`}
          >
            {menuConfig?.view?.label || 'Ver'} <ChevronDown className="w-3 h-3 text-slate-700" />
          </button>
          {openMenu === 'view' && (
            <div className="absolute top-full left-0 mt-1 w-48 bg-white border border-slate-200 rounded-md shadow-lg z-50 py-1 text-slate-700 text-xs">
              {menuConfig?.view?.items ? (
                menuConfig.view.items.map((item, idx) =>
                  item.divider ? (
                    <div key={idx} className="my-1 border-t border-slate-200"></div>
                  ) : (
                    <button
                      key={idx}
                      onClick={() => handleMenuAction(item.action)}
                      className="w-full text-left px-3 py-1.5 hover:bg-blue-50 hover:text-blue-700"
                    >
                      {item.label}
                    </button>
                  )
                )
              ) : (
                <div className="px-3 py-2 text-slate-500">Cargando...</div>
              )}
            </div>
          )}
        </div>

        {/* Menu Dropdown: Agentes */}
        <div className="relative">
          <button 
            onClick={() => toggleMenu('agents')}
            className={`px-2 py-0.5 rounded hover:bg-slate-100 transition-colors flex items-center gap-1 ${openMenu === 'agents' ? 'bg-slate-100 text-white' : ''}`}
          >
            Agentes <ChevronDown className="w-3 h-3 text-slate-700" />
          </button>
          {openMenu === 'agents' && (
            <div className="absolute top-full left-0 mt-1 w-52 bg-slate-100 border border-slate-700 rounded-md shadow-2xl z-50 py-1 text-slate-700 text-xs">
              <button onClick={() => { onOpenNewAgent(); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-blue-50 hover:text-blue-700">Crear Agente</button>
              <button className="w-full text-left px-3 py-1.5 hover:bg-blue-50 hover:text-blue-700">Reload Profiles</button>
              <button className="w-full text-left px-3 py-1.5 hover:bg-blue-50 hover:text-blue-700">Model Manager</button>
            </div>
          )}
        </div>

        {/* Menu Dropdown: Tools */}
        <div className="relative">
          <button 
            onClick={() => toggleMenu('tools')}
            className={`px-2 py-0.5 rounded hover:bg-slate-100 transition-colors flex items-center gap-1 ${openMenu === 'tools' ? 'bg-slate-100 text-white' : ''}`}
          >
            Tools <ChevronDown className="w-3 h-3 text-slate-700" />
          </button>
          {openMenu === 'tools' && (
            <div className="absolute top-full left-0 mt-1 w-48 bg-white border border-slate-200 rounded-md shadow-lg z-50 py-1 text-slate-700 text-xs">
              <button onClick={() => { setActiveTab('tools'); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-blue-50 hover:text-blue-700">Mercado de Wrench</button>
              <button onClick={() => { setActiveTab('tools'); setOpenMenu(null); }} className="w-full text-left px-3 py-1.5 hover:bg-blue-50 hover:text-blue-700">Visual Chain Builder</button>
            </div>
          )}
        </div>

        {/* Menu Dropdown: Ayuda */}
        <div className="relative">
          <button 
            onClick={() => toggleMenu('help')}
            className={`px-2 py-0.5 rounded hover:bg-slate-100 transition-colors flex items-center gap-1 ${openMenu === 'help' ? 'bg-slate-100 text-white' : ''}`}
          >
            Ayuda <ChevronDown className="w-3 h-3 text-slate-700" />
          </button>
          {openMenu === 'help' && (
            <div className="absolute top-full left-0 mt-1 w-48 bg-white border border-slate-200 rounded-md shadow-lg z-50 py-1 text-slate-700 text-xs">
              <button className="w-full text-left px-3 py-1.5 hover:bg-blue-50 hover:text-blue-700">ELAP Documentation</button>
              <button className="w-full text-left px-3 py-1.5 hover:bg-blue-50 hover:text-blue-700">Ollama Connectivity Test</button>
              <button className="w-full text-left px-3 py-1.5 hover:bg-blue-50 hover:text-blue-700">About ELAP v1.5.0</button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
