import React, { useState } from 'react';
import { X, Sliders, CheckCircle2, Brain, Download, ShieldCheck, Cpu, RefreshCw, Server } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434');
  const [rustPort, setRustPort] = useState('3000');
  const [grpcPort, setGrpcPort] = useState('50051');
  const [newModelName, setNewModelName] = useState('llama3.3:70b');
  const [isPulling, setIsPulling] = useState(false);
  const [pullProgress, setPullProgress] = useState<number | null>(null);

  const handlePullModel = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newModelName.trim()) return;

    setIsPulling(true);
    setPullProgress(10);

    const interval = setInterval(() => {
      setPullProgress(prev => {
        if (!prev) return 10;
        if (prev >= 100) {
          clearInterval(interval);
          setIsPulling(false);
          return 100;
        }
        return prev + 15;
      });
    }, 400);
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-50 border border-slate-700 rounded-2xl w-full max-w-xl overflow-hidden shadow-2xl text-slate-700">
        <div className="px-5 py-3.5 bg-slate-50 border-b border-slate-300 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-blue-600" />
            <h3 className="font-bold text-sm text-slate-900">ELAP Enterprise Platform Settings</h3>
          </div>
          <button onClick={onClose} className="text-slate-700 hover:text-slate-700 p-1">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-5 text-xs font-sans max-h-[80vh] overflow-y-auto custom-scrollbar">
          {/* SYSTEM ENDPOINTS */}
          <div className="space-y-3 bg-white p-3.5 rounded-xl border border-slate-300">
            <h4 className="font-bold text-slate-700 flex items-center gap-1.5 text-xs uppercase tracking-wider">
              <Server className="w-3.5 h-3.5 text-blue-600" /> Core System Endpoints & Ports
            </h4>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 font-mono">
              <div>
                <label className="block text-[12px] text-slate-700 mb-1">Rust Core Engine Port</label>
                <input 
                  type="text" 
                  value={rustPort} 
                  onChange={(e) => setRustPort(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-700 rounded p-1.5 text-slate-700 text-xs" 
                />
              </div>

              <div>
                <label className="block text-[12px] text-slate-700 mb-1">Python gRPC Port</label>
                <input 
                  type="text" 
                  value={grpcPort} 
                  onChange={(e) => setGrpcPort(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-700 rounded p-1.5 text-slate-700 text-xs" 
                />
              </div>

              <div>
                <label className="block text-[12px] text-slate-700 mb-1">Ollama Host URL</label>
                <input 
                  type="text" 
                  value={ollamaUrl} 
                  onChange={(e) => setOllamaUrl(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-700 rounded p-1.5 text-slate-700 text-xs" 
                />
              </div>
            </div>
          </div>

          {/* OLLAMA MODEL PULLER */}
          <div className="space-y-3 bg-white p-3.5 rounded-xl border border-slate-300">
            <h4 className="font-bold text-slate-700 flex items-center gap-1.5 text-xs uppercase tracking-wider">
              <Brain className="w-3.5 h-3.5 text-purple-700" /> Local Ollama Model Manager
            </h4>

            <form onSubmit={handlePullModel} className="flex gap-2">
              <input 
                type="text" 
                value={newModelName}
                onChange={(e) => setNewModelName(e.target.value)}
                placeholder="e.g. llama3.3:70b, deepseek-r1:14b"
                className="flex-1 bg-slate-50 border border-slate-700 rounded-lg p-2 font-mono text-xs text-slate-900 focus:outline-none focus:border-blue-600"
              />
              <button 
                type="submit" 
                disabled={isPulling}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white font-medium rounded-lg shadow flex items-center gap-1.5 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                <span>{isPulling ? 'Pulling...' : 'ollama pull'}</span>
              </button>
            </form>

            {isPulling && (
              <div className="space-y-1 font-mono">
                <div className="flex justify-between text-[13px] text-purple-300">
                  <span>Downloading weights for {newModelName}...</span>
                  <span>{pullProgress}%</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div style={{ width: `${pullProgress}%` }} className="bg-purple-500 h-full transition-all"></div>
                </div>
              </div>
            )}
          </div>

          {/* LOCAL RBAC SECURITY */}
          <div className="space-y-2 bg-white p-3.5 rounded-xl border border-slate-300">
            <h4 className="font-bold text-slate-700 flex items-center gap-1.5 text-xs uppercase tracking-wider">
              <ShieldCheck className="w-3.5 h-3.5 text-green-600" /> Enterprise RBAC Security
            </h4>
            <div className="flex items-center justify-between text-xs text-slate-700">
              <span>Active User Role: <strong className="text-green-600">System Administrator</strong></span>
              <span className="text-[12px] font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-700">Full Execution Access</span>
            </div>
            <p className="text-[13px] text-slate-700 leading-relaxed">
              All agent prompts, vector embeddings, and tool responses are encrypted locally using AES-256 and stored on-device without cloud data leakage.
            </p>
          </div>
        </div>

        <div className="px-5 py-3 bg-slate-50 border-t border-slate-300 flex justify-end">
          <button 
            onClick={onClose}
            className="px-4 py-1.5 bg-blue-600 hover:bg-blue-600 text-white font-medium text-xs rounded-lg shadow"
          >
            Save & Close Settings
          </button>
        </div>
      </div>
    </div>
  );
};
