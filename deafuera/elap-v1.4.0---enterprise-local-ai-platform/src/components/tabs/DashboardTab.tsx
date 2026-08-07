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
  ShieldCheck,
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
    <div className="flex-1 bg-[#0b0f15] text-slate-200 p-4 lg:p-6 overflow-y-auto custom-scrollbar space-y-6">
      {/* HEADER BAR */}
      <div className="flex items-center justify-between border-b border-[#1e293b] pb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-indigo-400" /> Executive Analytics & System Dashboard
          </h2>
          <p className="text-xs text-slate-400">
            Real-time local LLM inference telemetry, agent execution counts, and hardware VRAM utilization.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono bg-emerald-950/60 text-emerald-400 border border-emerald-800/80 px-2.5 py-1 rounded-md flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            ALL 3 CORE SERVICES HEALTHY
          </span>
        </div>
      </div>

      {/* 4 METRIC CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Active Agents */}
        <div className="bg-[#121924] p-4 rounded-xl border border-slate-800 hover:border-indigo-500/50 transition-colors shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Agents Active</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <Bot className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-100 font-mono">
            {activeCount} <span className="text-xs text-slate-500 font-normal">/ {agents.length} Total</span>
          </div>
          <div className="mt-2 text-[11px] text-emerald-400 flex items-center gap-1 font-mono">
            <TrendingUp className="w-3 h-3" /> +2 agents initialized today
          </div>
        </div>

        {/* Card 2: Conversations Today */}
        <div className="bg-[#121924] p-4 rounded-xl border border-slate-800 hover:border-indigo-500/50 transition-colors shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Conversations Today</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
              <MessageSquare className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-100 font-mono">
            42 <span className="text-xs text-slate-500 font-normal">Sessions</span>
          </div>
          <div className="mt-2 text-[11px] text-emerald-400 flex items-center gap-1 font-mono">
            <TrendingUp className="w-3 h-3" /> +18.4% volume vs yesterday
          </div>
        </div>

        {/* Card 3: Tools Executed */}
        <div className="bg-[#121924] p-4 rounded-xl border border-slate-800 hover:border-indigo-500/50 transition-colors shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Tools Executed</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center">
              <Wrench className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-100 font-mono">
            1,840 <span className="text-xs text-slate-500 font-normal">Calls</span>
          </div>
          <div className="mt-2 text-[11px] text-amber-400 flex items-center gap-1 font-mono">
            <Activity className="w-3 h-3" /> 0.02% error rate (3 retries)
          </div>
        </div>

        {/* Card 4: Avg Response Latency */}
        <div className="bg-[#121924] p-4 rounded-xl border border-slate-800 hover:border-indigo-500/50 transition-colors shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Avg Response Time</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-100 font-mono">
            245 <span className="text-xs text-slate-500 font-normal">ms / token</span>
          </div>
          <div className="mt-2 text-[11px] text-indigo-400 flex items-center gap-1 font-mono">
            <Zap className="w-3 h-3" /> Ollama Q4_K_M quant active
          </div>
        </div>
      </div>

      {/* GRAPH ROW 1: Token Usage Over Time & Agent Activity Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Token Usage Chart Visual */}
        <div className="lg:col-span-2 bg-[#121924] p-5 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-sm text-slate-100">Token Throughput Over Time (Last 24 Hours)</h3>
              <p className="text-xs text-slate-400">Total generated tokens processed across local agents.</p>
            </div>
            <span className="text-xs font-mono bg-slate-800 px-2 py-1 rounded text-indigo-400 border border-slate-700">
              Peak: 48,200 tok/hr
            </span>
          </div>

          {/* Simulated Bar Graph */}
          <div className="h-48 flex items-end justify-between gap-2 pt-6 pb-2 px-2 border-b border-slate-800 font-mono text-[10px] text-slate-400">
            {[20, 35, 42, 18, 55, 78, 92, 65, 84, 98, 70, 88, 60, 72, 90, 82].map((val, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1 h-full justify-end group">
                <div 
                  style={{ height: `${val}%` }} 
                  className="w-full bg-gradient-to-t from-indigo-700 to-indigo-400 rounded-t group-hover:from-indigo-500 group-hover:to-purple-400 transition-all relative"
                >
                  <span className="absolute -top-6 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 bg-slate-900 text-indigo-200 px-1 rounded border border-indigo-700 text-[9px] pointer-events-none">
                    {val * 420}
                  </span>
                </div>
                <span className="text-[9px] text-slate-500">{i * 2}:00</span>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between text-xs text-slate-400 font-mono pt-1">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-indigo-500"></span> Prompt Tokens: 124,800</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-purple-500"></span> Completion Tokens: 382,400</span>
            <span className="text-slate-200 font-bold">Total: 507,200</span>
          </div>
        </div>

        {/* Agent Activity Distribution */}
        <div className="bg-[#121924] p-5 rounded-xl border border-slate-800 space-y-4">
          <h3 className="font-bold text-sm text-slate-100">Agent Activity Breakdown</h3>

          <div className="space-y-3 font-mono text-xs">
            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span className="text-indigo-400">🔵 Sales Agent</span>
                <span>38%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-indigo-500 h-full w-[38%]"></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span className="text-emerald-400">🟢 IT Support Agent</span>
                <span>26%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full w-[26%]"></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span className="text-amber-400">🟠 Analytics Agent</span>
                <span>18%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-amber-500 h-full w-[18%]"></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span className="text-purple-400">🟣 Research Agent</span>
                <span>12%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-purple-500 h-full w-[12%]"></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span className="text-rose-400">🔴 Financial Agent</span>
                <span>6%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-rose-500 h-full w-[6%]"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* HARDWARE VRAM & SYSTEM HEALTH */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#121924] p-5 rounded-xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
              <Brain className="w-4 h-4 text-indigo-400" /> Local Ollama Model Memory Allocation
            </h3>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
              Loaded: glm4:9b
            </span>
          </div>

          <div className="p-3 bg-[#0c1118] rounded-lg border border-slate-800 space-y-2 font-mono text-xs">
            <div className="flex justify-between text-slate-300">
              <span>VRAM Used:</span>
              <span className="text-indigo-400 font-bold">{hardware.vramUsedGb} GB / {hardware.vramTotalGb} GB</span>
            </div>
            <div className="w-full bg-slate-800 h-3 rounded-full overflow-hidden p-0.5">
              <div className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full w-[30%]"></div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[11px] pt-2 border-t border-slate-800 text-slate-400">
              <div>Layers in VRAM: <strong className="text-slate-200">32/32 (100% GPU)</strong></div>
              <div>Context Buffer: <strong className="text-slate-200">4,096 tokens</strong></div>
            </div>
          </div>
        </div>

        <div className="bg-[#121924] p-5 rounded-xl border border-slate-800 space-y-3">
          <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
            <Server className="w-4 h-4 text-emerald-400" /> Enterprise Microservices Architecture
          </h3>

          <div className="space-y-2 font-mono text-xs">
            <div className="p-2 bg-[#0c1118] rounded border border-slate-800 flex items-center justify-between">
              <span className="flex items-center gap-2 text-slate-200">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Rust Core Execution Engine (Port 3000)
              </span>
              <span className="text-emerald-400">2ms latency</span>
            </div>

            <div className="p-2 bg-[#0c1118] rounded border border-slate-800 flex items-center justify-between">
              <span className="flex items-center gap-2 text-slate-200">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Python gRPC Worker (Port 50051)
              </span>
              <span className="text-emerald-400">4ms latency</span>
            </div>

            <div className="p-2 bg-[#0c1118] rounded border border-slate-800 flex items-center justify-between">
              <span className="flex items-center gap-2 text-slate-200">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Ollama Local LLM Server (Port 11434)
              </span>
              <span className="text-indigo-400">14ms latency</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
