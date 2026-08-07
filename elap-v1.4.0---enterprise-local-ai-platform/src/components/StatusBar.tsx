import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, 
  Brain, 
  Cpu, 
  HardDrive, 
  UserCheck, 
  Bell, 
  Battery, 
  Clock, 
  Zap,
  Activity,
  Layers
} from 'lucide-react';
import { HardwareMetrics } from '../types';

interface StatusBarProps {
  hardware: HardwareMetrics;
  onOpenNotifications?: () => void;
}

export const StatusBar: React.FC<StatusBarProps> = ({ hardware }) => {
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <footer className="h-6 bg-[#0b0e12] border-t border-[#1a2332] text-slate-400 font-mono text-[11px] px-3 flex items-center justify-between select-none z-30 shrink-0">
      {/* Left side: Services Connectivity */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1 text-emerald-400">
          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
          <span>Rust Core (3000)</span>
        </div>
        <span className="text-slate-700">|</span>
        <div className="flex items-center gap-1 text-emerald-400">
          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
          <span>Python gRPC (50051)</span>
        </div>
        <span className="text-slate-700">|</span>
        <div className="flex items-center gap-1 text-indigo-400">
          <Brain className="w-3 h-3 text-indigo-400" />
          <span>Ollama (11434)</span>
        </div>
      </div>

      {/* Center: Hardware Resource Monitor */}
      <div className="hidden lg:flex items-center gap-4 text-slate-300">
        <div className="flex items-center gap-1.5" title="CPU Load">
          <Cpu className="w-3 h-3 text-amber-400" />
          <span>CPU:</span>
          <span className="text-amber-400 font-bold">{hardware.cpuUsagePct}%</span>
        </div>
        <span className="text-slate-800">•</span>
        <div className="flex items-center gap-1.5" title="RAM Usage">
          <Layers className="w-3 h-3 text-indigo-400" />
          <span>RAM:</span>
          <span className="text-indigo-300">{hardware.ramUsedGb}GB / {hardware.ramTotalGb}GB</span>
        </div>
        <span className="text-slate-800">•</span>
        <div className="flex items-center gap-1.5" title="Local GPU VRAM Allocation">
          <Zap className="w-3 h-3 text-purple-400" />
          <span>GPU VRAM:</span>
          <span className="text-purple-300 font-bold">{hardware.vramUsedGb}GB / {hardware.vramTotalGb}GB ({hardware.gpuUsagePct}%)</span>
        </div>
        <span className="text-slate-800">•</span>
        <div className="flex items-center gap-1.5" title="NVMe Storage">
          <HardDrive className="w-3 h-3 text-slate-400" />
          <span>Disk:</span>
          <span className="text-slate-400">{hardware.diskUsedGb}GB / {hardware.diskTotalGb}GB</span>
        </div>
      </div>

      {/* Right side: User & System Time */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1 text-slate-300">
          <UserCheck className="w-3 h-3 text-indigo-400" />
          <span>Admin User</span>
        </div>
        <span className="text-slate-700">|</span>
        <div className="flex items-center gap-1 text-amber-300 cursor-pointer hover:text-amber-200">
          <Bell className="w-3 h-3 text-amber-400" />
          <span>2 notifications</span>
        </div>
        <span className="text-slate-700">|</span>
        <div className="flex items-center gap-1 text-slate-200 font-semibold">
          <Clock className="w-3 h-3 text-slate-400" />
          <span>{timeStr || '09:45 AM'}</span>
        </div>
        <span className="text-slate-700">|</span>
        <div className="flex items-center gap-1 text-emerald-400" title="Battery Status">
          <Battery className="w-3.5 h-3.5 text-emerald-400 fill-emerald-400/20" />
          <span>92%</span>
        </div>
      </div>
    </footer>
  );
};
