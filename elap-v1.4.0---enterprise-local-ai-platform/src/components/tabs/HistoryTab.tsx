import React, { useState } from 'react';
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

interface HistoryTabProps {
  historyItems: ConversationHistoryItem[];
  onSelectSession: (id: string) => void;
}

export const HistoryTab: React.FC<HistoryTabProps> = ({ historyItems, onSelectSession }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'pinned' | 'favorites'>('all');

  const filteredHistory = historyItems.filter(item => {
    const matchesQuery = item.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         item.agentName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.preview.toLowerCase().includes(searchQuery.toLowerCase());
    if (!matchesQuery) return false;
    if (filterType === 'pinned') return item.isPinned;
    if (filterType === 'favorites') return item.isFavorite;
    return true;
  });

  return (
    <div className="flex-1 bg-[#0b0f15] text-slate-200 p-4 lg:p-6 overflow-y-auto custom-scrollbar space-y-6">
      {/* HEADER */}
      <div className="flex items-center justify-between border-b border-[#1e293b] pb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <History className="w-5 h-5 text-indigo-400" /> Session History & Query Logs
          </h2>
          <p className="text-xs text-slate-400">
            Audit trail of multi-agent conversations, token consumed per session, and exported logs.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1.5 bg-[#1a2433] hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-lg border border-slate-700 transition-colors">
            <Download className="w-4 h-4 text-indigo-400" /> Export All History (JSON)
          </button>
        </div>
      </div>

      {/* SEARCH AND FILTERS BAR */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#121924] p-3 rounded-xl border border-slate-800">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input 
            type="text" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search past conversations by title, agent name, or message keywords..."
            className="w-full bg-[#0c1118] border border-slate-700 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center gap-1 bg-[#0c1118] p-1 rounded-lg border border-slate-800 text-xs shrink-0">
          <button 
            onClick={() => setFilterType('all')}
            className={`px-3 py-1 rounded-md transition-colors ${filterType === 'all' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'}`}
          >
            All Logs
          </button>
          <button 
            onClick={() => setFilterType('pinned')}
            className={`px-3 py-1 rounded-md transition-colors ${filterType === 'pinned' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Pinned
          </button>
          <button 
            onClick={() => setFilterType('favorites')}
            className={`px-3 py-1 rounded-md transition-colors ${filterType === 'favorites' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Favorites
          </button>
        </div>
      </div>

      {/* HISTORY TIMELINE LIST */}
      <div className="space-y-3">
        {filteredHistory.map(item => (
          <div 
            key={item.id}
            onClick={() => onSelectSession(item.id)}
            className="p-4 bg-[#121924] hover:bg-[#162130] rounded-xl border border-slate-800 hover:border-indigo-500/60 transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow"
          >
            <div className="space-y-1.5 min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-sm text-slate-100 truncate">{item.title}</h3>
                {item.isPinned && <Pin className="w-3.5 h-3.5 fill-indigo-400 text-indigo-400 shrink-0" />}
                {item.isFavorite && <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400 shrink-0" />}
              </div>

              <p className="text-xs text-slate-400 line-clamp-1 italic">"{item.preview}"</p>

              <div className="flex items-center gap-4 text-[11px] font-mono text-slate-500 pt-1">
                <span className="flex items-center gap-1 text-slate-300">
                  <Bot className="w-3.5 h-3.5 text-indigo-400" /> {item.agentName}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" /> {item.timestamp}
                </span>
                <span className="flex items-center gap-1">
                  <MessageSquare className="w-3.5 h-3.5" /> {item.messageCount} msgs
                </span>
                <span className="flex items-center gap-1 text-indigo-300">
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" /> {item.tokensUsed} tokens
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0 border-t sm:border-t-0 pt-2 sm:pt-0 border-slate-800">
              <button className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-indigo-300 transition-colors" title="Export session">
                <Download className="w-4 h-4" />
              </button>
              <button className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-100 transition-colors">
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}

        {filteredHistory.length === 0 && (
          <div className="text-center py-12 text-slate-500 text-sm">
            No history logs found matching criteria.
          </div>
        )}
      </div>
    </div>
  );
};
