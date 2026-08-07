import React, { useState } from 'react';
import { 
  BookOpen, 
  Database, 
  FileText, 
  Layers, 
  Search, 
  Plus, 
  RefreshCw, 
  CheckCircle2, 
  HardDrive, 
  FileUp, 
  Sparkles,
  Sliders
} from 'lucide-react';
import { KnowledgeSource } from '../../types';

interface KnowledgeTabProps {
  knowledgeSources: KnowledgeSource[];
}

export const KnowledgeTab: React.FC<KnowledgeTabProps> = ({ knowledgeSources }) => {
  const [searchQuery, setSearchQuery] = useState('Q3 West Coast sales revenue');
  const [searchResults, setSearchResults] = useState<any[] | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearchKnowledge = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsSearching(true);

    try {
      const res = await fetch('/api/knowledge/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, topK: 3 })
      });
      const data = await res.json();
      setSearchResults(data.topMatches || []);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  const totalVectors = knowledgeSources.reduce((acc, curr) => acc + curr.vectorCount, 0);

  return (
    <div className="flex-1 bg-white text-slate-700 p-4 lg:p-6 overflow-y-auto custom-scrollbar space-y-6">
      {/* HEADER */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-purple-700" /> Local BookOpen RAG Base & Vector Index
          </h2>
          <p className="text-xs text-slate-700">
            Enterprise document embeddings and live database vector indexes for local AI agent grounding.
          </p>
        </div>

        <button className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-600 text-white font-medium text-xs px-3 py-1.5 rounded-lg shadow transition-colors">
          <FileUp className="w-4 h-4" /> Upload Document / Connect DB
        </button>
      </div>

      {/* RAG SUMMARY METRICS */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono">
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-300 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-purple-500/20 text-purple-700 flex items-center justify-center shrink-0">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{totalVectors.toLocaleString()}</div>
            <div className="text-xs text-slate-700">Total Embedded Vectors</div>
          </div>
        </div>

        <div className="bg-slate-50 p-4 rounded-xl border border-slate-300 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center shrink-0">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{knowledgeSources.length} Sources</div>
            <div className="text-xs text-slate-700">Active Knowledge Repositories</div>
          </div>
        </div>

        <div className="bg-slate-50 p-4 rounded-xl border border-slate-300 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-green-600500/20 text-green-600 flex items-center justify-center shrink-0">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">Cosine 0.94</div>
            <div className="text-xs text-slate-700">Avg Similarity Precision</div>
          </div>
        </div>
      </div>

      {/* RAG VECTOR SEARCH TESTER CONSOLE */}
      <div className="bg-slate-50 p-5 rounded-xl border border-slate-300 space-y-4">
        <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
          <Search className="w-4 h-4 text-blue-600" /> Test RAG Semantic Vector Retrieval
        </h3>

        <form onSubmit={handleSearchKnowledge} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-700" />
            <input 
              type="text" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Type natural language query to test top-k vector chunk retrieval..."
              className="w-full bg-white border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 font-mono"
            />
          </div>
          <button 
            type="submit" 
            disabled={isSearching}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-600 text-white font-medium text-xs rounded-lg shadow flex items-center gap-1.5 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isSearching ? 'Querying...' : 'Query Vectors'}</span>
          </button>
        </form>

        {/* Vector Match Results */}
        {searchResults && (
          <div className="space-y-2 pt-2 border-t border-slate-300 font-mono text-xs">
            <div className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Top-K Retrieved Chunks:</div>
            {searchResults.map((match, mIdx) => (
              <div key={mIdx} className="p-3 bg-slate-100 rounded-lg border border-slate-300 space-y-1">
                <div className="flex items-center justify-between text-blue-600 font-semibold text-[13px]">
                  <span>Chunk #{mIdx + 1} — Source: {match.sourceName}</span>
                  <span className="text-green-600 bg-green-600950/80 px-1.5 py-0.5 rounded border border-green-600 text-[12px]">
                    Relevance Score: {(match.relevanceScore * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-slate-700 text-[13px] leading-relaxed pt-1">{match.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* KNOWLEDGE SOURCES TABLE */}
      <div className="bg-slate-50 p-5 rounded-xl border border-slate-300 space-y-4">
        <h3 className="font-bold text-sm text-slate-900">Connected Knowledge Databases</h3>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left border-collapse font-sans">
            <thead>
              <tr className="border-b border-slate-300 text-slate-700 uppercase text-[12px] tracking-wider font-semibold">
                <th className="py-2 px-3">Name</th>
                <th className="py-2 px-3">Type</th>
                <th className="py-2 px-3">Status</th>
                <th className="py-2 px-3 font-mono">Vectors</th>
                <th className="py-2 px-3">Size</th>
                <th className="py-2 px-3">Last Updated</th>
                <th className="py-2 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {knowledgeSources.map(source => (
                <tr key={source.id} className="hover:bg-slate-100/40 transition-colors">
                  <td className="py-2.5 px-3 font-medium text-slate-900 flex items-center gap-2">
                    {source.type === 'Database' && <Database className="w-4 h-4 text-blue-400" />}
                    {source.type === 'Document' && <FileText className="w-4 h-4 text-green-600" />}
                    {source.type === 'Vector DB' && <Layers className="w-4 h-4 text-purple-700" />}
                    <span>{source.name}</span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-700 font-mono text-[13px]">{source.type}</td>
                  <td className="py-2.5 px-3">
                    <span className="inline-flex items-center gap-1 text-[12px] font-mono bg-green-600950/80 text-green-600 px-2 py-0.5 rounded border border-green-600">
                      <span className="w-1.5 h-1.5 rounded-full bg-green-600400"></span> {source.status}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-mono text-slate-700">{source.vectorCount.toLocaleString()}</td>
                  <td className="py-2.5 px-3 font-mono text-slate-700">{source.fileSize}</td>
                  <td className="py-2.5 px-3 text-slate-700 text-[13px]">{source.lastUpdated}</td>
                  <td className="py-2.5 px-3 text-right">
                    <button className="text-xs text-blue-600 hover:text-blue-600 font-medium">Re-index</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
