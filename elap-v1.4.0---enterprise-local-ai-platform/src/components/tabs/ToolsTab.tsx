import React, { useState } from 'react';
import { 
  Wrench, 
  Play, 
  Plus, 
  Terminal, 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  Sliders, 
  Layers, 
  Globe, 
  Database, 
  BarChart2, 
  FileText, 
  FileSearch, 
  Code, 
  Sparkles,
  Check
} from 'lucide-react';
import { Tool } from '../../types';

interface ToolsTabProps {
  tools: Tool[];
  onToggleTool: (toolId: string) => void;
}

export const ToolsTab: React.FC<ToolsTabProps> = ({ tools, onToggleTool }) => {
  const [selectedToolId, setSelectedToolId] = useState<string>(tools[0]?.id || '');
  const [testInput, setTestInput] = useState<string>('SELECT region, SUM(amount) FROM q3_deals GROUP BY region;');
  const [executionOutput, setExecutionOutput] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionTime, setExecutionTime] = useState<number | null>(null);

  const selectedTool = tools.find(t => t.id === selectedToolId) || tools[0];

  const handleTestExecute = async () => {
    setIsExecuting(true);
    setExecutionOutput(null);

    const startTime = Date.now();
    try {
      const res = await fetch('/api/tools/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          toolId: selectedTool.id,
          toolName: selectedTool.name,
          input: testInput
        })
      });
      const data = await res.json();
      setExecutionTime(Date.now() - startTime);
      setExecutionOutput(data.output || 'Tool executed successfully with 0 exit code.');
    } catch (err) {
      setExecutionOutput(`Execution Error: ${err}`);
      setExecutionTime(Date.now() - startTime);
    } finally {
      setIsExecuting(false);
    }
  };

  const getToolIcon = (iconName: string) => {
    switch (iconName) {
      case 'Globe': return <Globe className="w-4 h-4 text-blue-400" />;
      case 'BarChart2': return <BarChart2 className="w-4 h-4 text-amber-400" />;
      case 'FileText': return <FileText className="w-4 h-4 text-emerald-400" />;
      case 'Database': return <Database className="w-4 h-4 text-indigo-400" />;
      case 'Terminal': return <Terminal className="w-4 h-4 text-purple-400" />;
      case 'FileSearch': return <FileSearch className="w-4 h-4 text-rose-400" />;
      default: return <Wrench className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="flex-1 bg-[#0b0f15] text-slate-200 p-4 lg:p-6 overflow-y-auto custom-scrollbar space-y-6">
      {/* HEADER */}
      <div className="flex items-center justify-between border-b border-[#1e293b] pb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Wrench className="w-5 h-5 text-amber-400" /> Tool Marketplace & Visual Chain Execution
          </h2>
          <p className="text-xs text-slate-400">
            Registered local microservices and Python tool bindings accessible by AI agents.
          </p>
        </div>

        <button className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs px-3 py-1.5 rounded-lg shadow transition-colors">
          <Plus className="w-4 h-4" /> Register Custom Tool
        </button>
      </div>

      {/* VISUAL CHAIN BUILDER PREVIEW */}
      <div className="bg-[#121924] p-5 rounded-xl border border-slate-800 space-y-3">
        <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-400" /> Multi-Tool Agent Execution Chain
        </h3>
        
        <div className="p-4 bg-[#0c1118] rounded-xl border border-slate-800/80 flex flex-col md:flex-row items-center justify-between gap-3 text-xs font-mono">
          <div className="p-3 bg-[#151e2b] rounded-lg border border-slate-700 text-center w-full md:w-auto">
            <div className="text-slate-400 text-[10px] uppercase">Step 1: Data Retrieval</div>
            <div className="font-bold text-slate-200 mt-0.5">Sales Database Query</div>
            <div className="text-[10px] text-emerald-400 mt-1">18ms latency</div>
          </div>

          <ArrowRight className="w-4 h-4 text-slate-500 shrink-0 hidden md:block" />

          <div className="p-3 bg-[#151e2b] rounded-lg border border-indigo-500/50 text-center w-full md:w-auto">
            <div className="text-indigo-400 text-[10px] uppercase">Step 2: Local LLM Processing</div>
            <div className="font-bold text-indigo-200 mt-0.5">glm4:9b (Ollama)</div>
            <div className="text-[10px] text-indigo-300 mt-1">Context: 4,096 tok</div>
          </div>

          <ArrowRight className="w-4 h-4 text-slate-500 shrink-0 hidden md:block" />

          <div className="p-3 bg-[#151e2b] rounded-lg border border-slate-700 text-center w-full md:w-auto">
            <div className="text-slate-400 text-[10px] uppercase">Step 3: Analytics Engine</div>
            <div className="font-bold text-slate-200 mt-0.5">Data Analysis Engine</div>
            <div className="text-[10px] text-amber-400 mt-1">35ms latency</div>
          </div>

          <ArrowRight className="w-4 h-4 text-slate-500 shrink-0 hidden md:block" />

          <div className="p-3 bg-[#151e2b] rounded-lg border border-slate-700 text-center w-full md:w-auto">
            <div className="text-slate-400 text-[10px] uppercase">Step 4: Output Synthesis</div>
            <div className="font-bold text-slate-200 mt-0.5">Executive Report Gen</div>
            <div className="text-[10px] text-emerald-400 mt-1">90ms latency</div>
          </div>
        </div>
      </div>

      {/* TWO COLUMNS: TOOLS MARKETPLACE & DIRECT TESTER */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Tool List (5 cols) */}
        <div className="lg:col-span-5 bg-[#121924] p-4 rounded-xl border border-slate-800 space-y-3">
          <h3 className="font-bold text-sm text-slate-100 uppercase tracking-wider text-xs">
            Registered Enterprise Tools ({tools.length})
          </h3>

          <div className="space-y-2">
            {tools.map(tool => {
              const isSelected = tool.id === selectedTool.id;
              return (
                <div
                  key={tool.id}
                  onClick={() => setSelectedToolId(tool.id)}
                  className={`p-3 rounded-lg border transition-all cursor-pointer flex items-start justify-between ${
                    isSelected
                      ? 'bg-[#1a2536] border-indigo-500 text-slate-100 shadow'
                      : 'bg-[#0f1622] border-slate-800/80 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <div className="flex items-start gap-2.5 min-w-0">
                    <div className="p-2 rounded bg-slate-900 border border-slate-800 shrink-0">
                      {getToolIcon(tool.iconName)}
                    </div>
                    <div>
                      <h4 className="font-bold text-xs text-slate-100 flex items-center gap-1.5">
                        {tool.name}
                        <span className="text-[9px] font-mono text-slate-500 bg-slate-900 px-1 rounded">
                          v{tool.version}
                        </span>
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-2">{tool.description}</p>
                      <div className="flex items-center gap-3 text-[10px] text-slate-500 font-mono mt-2">
                        <span>Calls: {tool.executionCount}</span>
                        <span>Avg: {tool.avgLatencyMs}ms</span>
                      </div>
                    </div>
                  </div>

                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleTool(tool.id);
                    }}
                    className={`px-2 py-1 rounded text-[10px] font-mono border transition-colors ${
                      tool.isEnabled
                        ? 'bg-emerald-950/80 text-emerald-400 border-emerald-800'
                        : 'bg-slate-900 text-slate-500 border-slate-800'
                    }`}
                  >
                    {tool.isEnabled ? 'Enabled' : 'Disabled'}
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Direct Tool Execution Tester (7 cols) */}
        <div className="lg:col-span-7 bg-[#121924] p-5 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
                <Terminal className="w-4 h-4 text-purple-400" /> Interactive Execution Console ({selectedTool.name})
              </h3>
              <p className="text-xs text-slate-400">Test parameters and verify JSON responses before binding to agents.</p>
            </div>
            <span className="text-xs font-mono text-indigo-400 bg-indigo-950 px-2 py-0.5 rounded border border-indigo-800">
              {selectedTool.category}
            </span>
          </div>

          {/* Parameters Schema */}
          <div className="space-y-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Accepted Parameters:</span>
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              {selectedTool.parameters.map((param, pIdx) => (
                <div key={pIdx} className="p-2 bg-[#0d131c] rounded border border-slate-800">
                  <div className="text-indigo-300 font-bold">{param.name} ({param.type})</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">{param.description}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Input Box */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 block">Execution Payload / Query:</label>
            <textarea
              value={testInput}
              onChange={(e) => setTestInput(e.target.value)}
              rows={3}
              className="w-full bg-[#0d131c] border border-slate-700 rounded-lg p-2.5 text-xs font-mono text-slate-100 focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Execute Button */}
          <button
            onClick={handleTestExecute}
            disabled={isExecuting}
            className={`w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs rounded-lg shadow flex items-center justify-center gap-2 transition-colors ${
              isExecuting ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <Play className={`w-3.5 h-3.5 ${isExecuting ? 'animate-spin' : ''}`} />
            <span>{isExecuting ? 'Executing Tool Local Worker...' : 'Execute Tool Test'}</span>
          </button>

          {/* Execution Output Window */}
          {executionOutput && (
            <div className="p-3 bg-[#070b10] rounded-lg border border-slate-800 space-y-1.5 font-mono text-xs">
              <div className="flex items-center justify-between text-[11px] text-emerald-400 border-b border-slate-800 pb-1">
                <span className="flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Execution Completed
                </span>
                <span>Latency: {executionTime}ms</span>
              </div>
              <pre className="text-slate-300 whitespace-pre-wrap text-[11px] leading-relaxed pt-1">
                {executionOutput}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
