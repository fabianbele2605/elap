import React from 'react';
import { 
  BarChart2, 
  Bot, 
  MessageSquare, 
  Wrench, 
  Zap, 
  Activity, 
  Cpu, 
  HardDrive, 
  TrendingUp, 
  Clock, 
  CheckCircle2, 
  Brain, 
  Server, 
  Layers, 
  ShieldCheckCheck,
  RefreshCw
} from 'lucide-react';
import { Agent, HardwareMetrics } from '../../types';

interface DashboardTabProps {
  agents: Agent[];
  hardware: HardwareMetrics;
}

export const DashboardTab: React.FC<DashboardTabProps> = ({ agents, hardware }) => {
  const activeCount = agents.filter(a => a.status === 'online' || a.status === 'busy').length;

  return (
    <div className="flex-1 bg-white text-slate-700 p-4 lg:p-6 overflow-y-auto custom-scrollbar space-y-6">
      {/* HEADER BAR */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-blue-600" /> Executive Analytics & System Dashboard
          </h2>
          <p className="text-xs text-slate-700">
            Real-time local LLM inference telemetry, agent execution counts, and hardware VRAM utilization.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono bg-green-600950/60 text-green-600 border border-green-600/80 px-2.5 py-1 rounded-md flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-green-600400 animate-pulse"></span>
            ALL 3 CORE SERVICES HEALTHY
          </span>
        </div>
      </div>

      {/* 4 METRIC CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Active Agentes */}
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-300 hover:border-blue-600/50 transition-colors shadow-lg">
          <div className="flex items-center justify-between text-slate-700 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Agentes Active</span>
            <div className="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-600 flex items-center justify-center">
              <Bot className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono">
            {activeCount} <span className="text-xs text-slate-700 font-normal">/ {agents.length} Total</span>
          </div>
          <div className="mt-2 text-[13px] text-green-600 flex items-center gap-1 font-mono">
            <TrendingUp className="w-3 h-3" /> +2 agents initialized today
          </div>
        </div>

        {/* Card 2: Conversations Today */}
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-300 hover:border-blue-600/50 transition-colors shadow-lg">
          <div className="flex items-center justify-between text-slate-700 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Conversations Today</span>
            <div className="w-8 h-8 rounded-lg bg-green-600500/20 text-green-600 flex items-center justify-center">
              <MessageSquare className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono">
            42 <span className="text-xs text-slate-700 font-normal">Sessions</span>
          </div>
          <div className="mt-2 text-[13px] text-green-600 flex items-center gap-1 font-mono">
            <TrendingUp className="w-3 h-3" /> +18.4% volume vs yesterday
          </div>
        </div>

        {/* Card 3: Tools Executed */}
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-300 hover:border-blue-600/50 transition-colors shadow-lg">
          <div className="flex items-center justify-between text-slate-700 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Tools Executed</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-700 flex items-center justify-center">
              <Wrench className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono">
            1,840 <span className="text-xs text-slate-700 font-normal">Calls</span>
          </div>
          <div className="mt-2 text-[13px] text-amber-700 flex items-center gap-1 font-mono">
            <Activity className="w-3 h-3" /> 0.02% error rate (3 retries)
          </div>
        </div>

        {/* Card 4: Avg Response Latency */}
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-300 hover:border-blue-600/50 transition-colors shadow-lg">
          <div className="flex items-center justify-between text-slate-700 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Avg Response Time</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/20 text-purple-700 flex items-center justify-center">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono">
            245 <span className="text-xs text-slate-700 font-normal">ms / token</span>
          </div>
          <div className="mt-2 text-[13px] text-blue-600 flex items-center gap-1 font-mono">
            <Zap className="w-3 h-3" /> Ollama Q4_K_M quant active
          </div>
        </div>
      </div>

      {/* GRAPH ROW 1: Token Usage Over Time & Agent Activity Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Token Usage Chart Visual */}
        <div className="lg:col-span-2 bg-slate-50 p-5 rounded-xl border border-slate-300 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-sm text-slate-900">Token Throughput Over Time (Last 24 Hours)</h3>
              <p className="text-xs text-slate-700">Total generated tokens processed across local agents.</p>
            </div>
            <span className="text-xs font-mono bg-slate-100 px-2 py-1 rounded text-blue-600 border border-slate-700">
              Peak: 48,200 tok/hr
            </span>
          </div>

          {/* Simulated Bar Graph */}
          <div className="h-48 flex items-end justify-between gap-2 pt-6 pb-2 px-2 border-b border-slate-300 font-mono text-[12px] text-slate-700">
            {[20, 35, 42, 18, 55, 78, 92, 65, 84, 98, 70, 88, 60, 72, 90, 82].map((val, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1 h-full justify-end group">
                <div 
                  style={{ height: `${val}%` }} 
                  className="w-full bg-gradient-to-t from-indigo-700 to-indigo-400 rounded-t group-hover:from-indigo-500 group-hover:to-purple-400 transition-all relative"
                >
                  <span className="absolute -top-6 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 bg-white text-indigo-600 px-1 rounded border border-blue-600-700 text-[11px] pointer-events-none">
                    {val * 420}
                  </span>
                </div>
                <span className="text-[11px] text-slate-700">{i * 2}:00</span>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between text-xs text-slate-700 font-mono pt-1">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-blue-600"></span> Prompt Tokens: 124,800</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-purple-500"></span> Completion Tokens: 382,400</span>
            <span className="text-slate-700 font-bold">Total: 507,200</span>
          </div>
        </div>

        {/* Agent Activity Distribution */}
        <div className="bg-slate-50 p-5 rounded-xl border border-slate-300 space-y-4">
          <h3 className="font-bold text-sm text-slate-900">Agent Activity Breakdown</h3>

          <div className="space-y-3 font-mono text-xs">
            <div>
              <div className="flex justify-between text-slate-700 mb-1">
                <span className="text-blue-600">🔵 Sales Agent</span>
                <span>38%</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div className="bg-blue-600 h-full w-[38%]"></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-slate-700 mb-1">
                <span className="text-green-600">🟢 IT Support Agent</span>
                <span>26%</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div className="bg-green-600500 h-full w-[26%]"></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-slate-700 mb-1">
                <span className="text-amber-700">🟠 Analytics Agent</span>
                <span>18%</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div className="bg-amber-500 h-full w-[18%]"></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-slate-700 mb-1">
                <span className="text-purple-700">🟣 Research Agent</span>
                <span>12%</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div className="bg-purple-500 h-full w-[12%]"></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-slate-700 mb-1">
                <span className="text-rose-700">🔴 Financial Agent</span>
                <span>6%</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div className="bg-rose-500 h-full w-[6%]"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* HARDWARE VRAM & SYSTEM HEALTH */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-50 p-5 rounded-xl border border-slate-300 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
              <Brain className="w-4 h-4 text-blue-600" /> Local Ollama Model Memory Allocation
            </h3>
            <span className="text-xs font-mono text-green-600 bg-green-600950 px-2 py-0.5 rounded border border-green-600">
              Loaded: glm4:9b
            </span>
          </div>

          <div className="p-3 bg-white rounded-lg border border-slate-300 space-y-2 font-mono text-xs">
            <div className="flex justify-between text-slate-700">
              <span>VRAM Used:</span>
              <span className="text-blue-600 font-bold">{hardware.vramUsedGb} GB / {hardware.vramTotalGb} GB</span>
            </div>
            <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden p-0.5">
              <div className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full w-[30%]"></div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[13px] pt-2 border-t border-slate-300 text-slate-700">
              <div>Layers in VRAM: <strong className="text-slate-700">32/32 (100% GPU)</strong></div>
              <div>Context Buffer: <strong className="text-slate-700">4,096 tokens</strong></div>
            </div>
          </div>
        </div>

        <div className="bg-slate-50 p-5 rounded-xl border border-slate-300 space-y-3">
          <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
            <Server className="w-4 h-4 text-green-600" /> Enterprise Microservices Architecture
          </h3>

          <div className="space-y-2 font-mono text-xs">
            <div className="p-2 bg-white rounded border border-slate-300 flex items-center justify-between">
              <span className="flex items-center gap-2 text-slate-700">
                <CheckCircle2 className="w-3.5 h-3.5 text-green-600" /> Rust Core Execution Engine (Port 3000)
              </span>
              <span className="text-green-600">2ms latency</span>
            </div>

            <div className="p-2 bg-white rounded border border-slate-300 flex items-center justify-between">
              <span className="flex items-center gap-2 text-slate-700">
                <CheckCircle2 className="w-3.5 h-3.5 text-green-600" /> Python gRPC Worker (Port 50051)
              </span>
              <span className="text-green-600">4ms latency</span>
            </div>

            <div className="p-2 bg-white rounded border border-slate-300 flex items-center justify-between">
              <span className="flex items-center gap-2 text-slate-700">
                <CheckCircle2 className="w-3.5 h-3.5 text-green-600" /> Ollama Local LLM Server (Port 11434)
              </span>
              <span className="text-blue-600">14ms latency</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
