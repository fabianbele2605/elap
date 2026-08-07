import React, { useState } from 'react';
import { X, Bot, Sparkles, Check, Wrench, BookOpen } from 'lucide-react';
import { Agent, AgentRole, Tool } from '../../types';

interface NewAgentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateAgent: (agent: Partial<Agent>) => void;
  availableTools: Tool[];
}

export const NewAgentModal: React.FC<NewAgentModalProps> = ({
  isOpen,
  onClose,
  onCreateAgent,
  availableTools
}) => {
  if (!isOpen) return null;

  const [name, setName] = useState('');
  const [role, setRole] = useState<AgentRole>('Sales');
  const [model, setModel] = useState('glm4:9b');
  const [systemPrompt, setSystemPrompt] = useState('You are a specialized Enterprise AI agent...');
  const [description, setDescription] = useState('Handles custom enterprise workflows.');
  const [selectedTools, setSelectedTools] = useState<string[]>(['tool_web_search', 'tool_data_analysis']);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    onCreateAgent({
      name,
      role,
      model,
      systemPrompt,
      description,
      status: 'online',
      avatarColor: role === 'Sales' ? 'indigo' : role === 'IT Support' ? 'emerald' : 'purple',
      lastActive: 'Just now',
      skillsCount: selectedTools.length,
      toolsEnabled: selectedTools,
      knowledgeAttached: ['ks_company_docs'],
      temperature: 0.7,
      topP: 0.9,
      contextLength: 4096,
      totalTokensUsed: 0
    });
    onClose();
  };

  const toggleToolSelection = (toolId: string) => {
    if (selectedTools.includes(toolId)) {
      setSelectedTools(selectedTools.filter(id => id !== toolId));
    } else {
      setSelectedTools([...selectedTools, toolId]);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-50 border border-slate-700 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl text-slate-700">
        <div className="px-5 py-3.5 bg-slate-50 border-b border-slate-300 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-blue-600/30 border border-blue-600/50 flex items-center justify-center text-blue-600">
              <Bot className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-sm text-slate-900">Create New ELAP AI Agent</h3>
          </div>
          <button onClick={onClose} className="text-slate-700 hover:text-slate-700 p-1">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4 text-xs font-sans">
          <div>
            <label className="block text-slate-700 font-semibold mb-1">Agent Name</label>
            <input 
              type="text" 
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Code Review Agent, Compliance Bot"
              className="w-full bg-white border border-slate-700 rounded-lg p-2 text-slate-900 focus:outline-none focus:border-blue-600 text-xs"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-700 font-semibold mb-1">Domain Role</label>
              <select 
                value={role}
                onChange={(e) => setRole(e.target.value as AgentRole)}
                className="w-full bg-white border border-slate-700 rounded-lg p-2 text-slate-900 focus:outline-none focus:border-blue-600 text-xs"
              >
                <option value="Sales">Sales</option>
                <option value="IT Support">IT Support</option>
                <option value="Analytics">Analytics</option>
                <option value="Research">Research</option>
                <option value="Financial">Financial</option>
                <option value="Developer">Developer</option>
                <option value="Custom">Custom</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1">Local Ollama Model</label>
              <select 
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full bg-white border border-slate-700 rounded-lg p-2 text-slate-900 focus:outline-none focus:border-blue-600 font-mono text-xs"
              >
                <option value="glm4:9b">glm4:9b (Fast & Balanced)</option>
                <option value="llama3.3:70b">llama3.3:70b (High Quality)</option>
                <option value="qwen2.5-coder:32b">qwen2.5-coder:32b (Code)</option>
                <option value="deepseek-r1:14b">deepseek-r1:14b (Reasoning)</option>
                <option value="mistral-nemo:12b">mistral-nemo:12b (Multilingual)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-slate-700 font-semibold mb-1">System Prompt / Instructions</label>
            <textarea 
              rows={3}
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              className="w-full bg-white border border-slate-700 rounded-lg p-2 text-slate-900 focus:outline-none focus:border-blue-600 font-mono text-xs"
            />
          </div>

          <div>
            <label className="block text-slate-700 font-semibold mb-1">Description</label>
            <input 
              type="text" 
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-white border border-slate-700 rounded-lg p-2 text-slate-900 focus:outline-none focus:border-blue-600 text-xs"
            />
          </div>

          <div>
            <label className="block text-slate-700 font-semibold mb-1">Tool Bindings</label>
            <div className="grid grid-cols-2 gap-1.5 max-h-32 overflow-y-auto p-2 bg-white rounded-lg border border-slate-300 custom-scrollbar">
              {availableTools.map(t => {
                const isSelected = selectedTools.includes(t.id);
                return (
                  <div 
                    key={t.id} 
                    onClick={() => toggleToolSelection(t.id)}
                    className={`p-1.5 rounded cursor-pointer flex items-center justify-between text-[13px] border transition-colors ${
                      isSelected ? 'bg-slate-50/80 border-blue-600-600 text-indigo-600' : 'bg-white border-slate-300 text-slate-700'
                    }`}
                  >
                    <span className="truncate">{t.name}</span>
                    {isSelected && <Check className="w-3 h-3 text-blue-600 shrink-0" />}
                  </div>
                );
              })}
            </div>
          </div>

          <div className="pt-2 border-t border-slate-300 flex items-center justify-end gap-2">
            <button 
              type="button" 
              onClick={onClose}
              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-100 text-slate-700 rounded-lg text-xs"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="px-4 py-1.5 bg-blue-600 hover:bg-blue-600 text-white font-medium rounded-lg text-xs shadow-md shadow-indigo-600/30"
            >
              Initialize Agent
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
