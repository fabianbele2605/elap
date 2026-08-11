import React, { useState, useEffect } from 'react';
import {
  History,
  Search,
  Filter,
  Download,
  Star,
  Pin,
  Trash2,
  Bot,
  Clock,
  MessageSquare,
  Sparkles,
  ChevronRight,
  Check
} from 'lucide-react';
import { ConversationHistoryItem } from '../../types';
import { Conversation } from '../../hooks/useConversation';

interface HistoryTabProps {
  historyItems?: ConversationHistoryItem[];
  conversations?: Conversation[];
  onSelectSession?: (id: string) => void;
  onDeleteConversation?: (id: string) => void;
}

interface HistoryItem {
  id: string;
  agent_id: string;
  agent_name: string;
  timestamp: string;
  type: string;
  user_message: string;
  agent_response: string;
  status: string;
  icon: string;
}

export const HistoryTab: React.FC<HistoryTabProps> = ({
  historyItems = [],
  conversations = [],
  onSelectSession,
  onDeleteConversation
}) => {
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'pinned' | 'favorites'>('all');

  // Usar conversaciones reales del hook (prioritario) o fallback a historyItems
  const displayHistory = conversations.length > 0 ? conversations : historyItems;

  const filteredHistory = displayHistory.filter(item => {
    // Extraer propiedades comunes
    const title = 'title' in item ? item.title : item.agent_name;
    const agentName = 'agentName' in item ? item.agentName : item.agent_name;
    const preview = 'preview' in item ? item.preview : 'user_message' in item ? item.user_message : '';

    const matchesQuery = title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         agentName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         preview.toLowerCase().includes(searchQuery.toLowerCase());
    if (!matchesQuery) return false;

    // Si son conversaciones reales (del hook), no filtrar por pinned/favorites
    if (conversations.length > 0) return true;

    // Filtrar por propiedades solo si usamos historyItems
    if ('isPinned' in item && filterType === 'pinned') return item.isPinned;
    if ('isFavorite' in item && filterType === 'favorites') return item.isFavorite;
    return true;
  });

  return (
    <div className="flex-1 bg-white text-slate-700 p-4 lg:p-6 overflow-y-auto custom-scrollbar space-y-6">
      {/* HEADER */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <History className="w-5 h-5 text-blue-600" /> Historial de Conversaciones ({displayHistory.length})
          </h2>
          <p className="text-xs text-slate-700">
            Registro de todas las conversaciones con agentes, tokens consumidos y opciones de exportación.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs px-3 py-1.5 rounded-lg border border-slate-300 transition-colors">
            <Download className="w-4 h-4 text-blue-600" /> Exportar Historial
          </button>
        </div>
      </div>

      {/* SEARCH AND FILTERS BAR */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-slate-50 p-3 rounded-xl border border-slate-300">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-700" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Busca por título, agente, o palabras clave..."
            className="w-full bg-white border border-slate-700 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:border-blue-600"
          />
        </div>

        <div className="flex items-center gap-1 bg-white p-1 rounded-lg border border-slate-300 text-xs shrink-0">
          <button
            onClick={() => setFilterType('all')}
            className={`px-3 py-1 rounded-md transition-colors ${filterType === 'all' ? 'bg-blue-600 text-white font-medium' : 'text-slate-700 hover:text-slate-700'}`}
          >
            Todos
          </button>
          <button
            onClick={() => setFilterType('pinned')}
            className={`px-3 py-1 rounded-md transition-colors ${filterType === 'pinned' ? 'bg-blue-600 text-white font-medium' : 'text-slate-700 hover:text-slate-700'}`}
          >
            Fijados
          </button>
          <button
            onClick={() => setFilterType('favorites')}
            className={`px-3 py-1 rounded-md transition-colors ${filterType === 'favorites' ? 'bg-blue-600 text-white font-medium' : 'text-slate-700 hover:text-slate-700'}`}
          >
            Favoritos
          </button>
        </div>
      </div>

      {/* HISTORY TIMELINE LIST */}
      <div className="space-y-3">
        {loading ? (
          <div className="text-center py-12 text-slate-500">
            ⏳ Cargando historial...
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="text-center py-12 text-slate-700 text-sm">
            No se encontraron elementos en el historial.
          </div>
        ) : (
          filteredHistory.map(item => {
            const itemId = item.id;
            const itemTitle = 'title' in item ? item.title : item.agent_name;
            const itemAgent = 'agentName' in item ? item.agentName : item.agent_name;
            const itemPreview = 'preview' in item ? item.preview : ('user_message' in item ? item.user_message.substring(0, 100) : 'Sin vista previa');
            const itemTimestamp = item.updated_at || item.timestamp || new Date().toISOString();
            const isPinned = 'isPinned' in item ? item.isPinned : false;
            const isFavorite = 'isFavorite' in item ? item.isFavorite : false;
            const messageCount = 'messageCount' in item ? item.messageCount : (item.message_count || 0);
            const tokensUsed = 'tokensUsed' in item ? item.tokensUsed : '~150';
            const icon = 'icon' in item ? item.icon : '💬';

            return (
              <div
                key={itemId}
                onClick={() => onSelectSession?.(itemId)}
                className="p-4 bg-slate-50 hover:bg-slate-100 rounded-xl border border-slate-300 hover:border-blue-600/60 transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow"
              >
                <div className="space-y-1.5 min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{icon}</span>
                    <h3 className="font-bold text-sm text-slate-900 truncate">{itemTitle}</h3>
                    {isPinned && <Pin className="w-3.5 h-3.5 fill-blue-600 text-blue-600 shrink-0" />}
                    {isFavorite && <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-700 shrink-0" />}
                    <span className="text-[11px] font-mono bg-green-100 text-green-700 px-2 py-0.5 rounded ml-auto">
                      {item.status || 'completed'}
                    </span>
                  </div>

                  <p className="text-xs text-slate-700 line-clamp-1 italic">"{itemPreview}"</p>

                  <div className="flex items-center gap-4 text-[13px] font-mono text-slate-700 pt-1 flex-wrap">
                    <span className="flex items-center gap-1 text-slate-700">
                      <Bot className="w-3.5 h-3.5 text-blue-600" /> {itemAgent}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" /> {new Date(itemTimestamp).toLocaleTimeString('es-ES')}
                    </span>
                    <span className="flex items-center gap-1">
                      <MessageSquare className="w-3.5 h-3.5" /> {messageCount} msgs
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0 border-t sm:border-t-0 pt-2 sm:pt-0 border-slate-300">
                  <button
                    className="p-2 hover:bg-slate-100 rounded-lg text-slate-700 hover:text-blue-600 transition-colors"
                    title="Export session"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  {onDeleteConversation && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm(`¿Eliminar "${itemTitle}"?`)) {
                          onDeleteConversation(itemId);
                        }
                      }}
                      className="p-2 hover:bg-slate-100 rounded-lg text-slate-700 hover:text-red-600 transition-colors"
                      title="Eliminar"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                  <button className="p-2 hover:bg-slate-100 rounded-lg text-slate-700 hover:text-slate-900 transition-colors">
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
