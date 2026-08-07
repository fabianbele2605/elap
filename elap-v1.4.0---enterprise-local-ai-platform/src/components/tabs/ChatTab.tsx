import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Paperclip, 
  Mic, 
  Wrench, 
  Sliders, 
  RotateCcw, 
  MoreVertical, 
  Brain, 
  ChevronDown, 
  ChevronUp, 
  CheckCircle2, 
  Sparkles, 
  Clock, 
  Cpu, 
  Terminal, 
  Database, 
  BarChart2, 
  Copy, 
  Check, 
  Bot, 
  User, 
  Volume2, 
  Layers
} from 'lucide-react';
import { Agent, Message, Tool } from '../../types';

interface ChatTabProps {
  agent: Agent;
  messages: Message[];
  onSendMessage: (text: string, attachments?: any[]) => void;
  onNewConversation: () => void;
  isStreaming: boolean;
  tools: Tool[];
}

export const ChatTab: React.FC<ChatTabProps> = ({
  agent,
  messages,
  onSendMessage,
  onNewConversation,
  isStreaming,
  tools
}) => {
  const [inputText, setInputText] = useState('');
  const [openThoughts, setOpenThoughts] = useState<{ [msgId: string]: boolean }>({
    msg_2: true // expand first example thought by default
  });
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [showToolsDropdown, setShowToolsDropdown] = useState(false);
  const [showOptionsDropdown, setShowOptionsDropdown] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isStreaming) return;
    onSendMessage(inputText);
    setInputText('');
  };

  const toggleThoughts = (msgId: string) => {
    setOpenThoughts(prev => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const quickPrompts = [
    "Analyze Q3 sales performance & recommendations",
    "Check network connectivity & gRPC logs",
    "Run cohort retention matrix in Python",
    "Audit CapEx budget & quarterly EBITDA"
  ];

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0b0f15] text-slate-200 overflow-hidden relative">
      {/* CHAT TAB HEADER */}
      <div className="h-12 px-4 bg-[#0f141d] border-b border-[#1e293b] flex items-center justify-between shrink-0 z-10 select-none">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600/30 border border-indigo-500/50 flex items-center justify-center font-bold text-indigo-300 text-xs shadow">
            {agent.name.substring(0, 2).toUpperCase()}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-bold text-sm text-slate-100">{agent.name}</h2>
              <span className="text-[10px] bg-indigo-950/80 text-indigo-300 px-1.5 py-0.5 rounded border border-indigo-800 font-mono">
                {agent.role}
              </span>
              <span className="flex items-center gap-1 text-[11px] text-emerald-400 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Ready
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono">
              Model: <span className="text-slate-300">{agent.model}</span> • Context: {agent.contextLength} tokens
            </p>
          </div>
        </div>

        {/* Right Header Controls */}
        <div className="flex items-center gap-3">
          {/* Token Counter */}
          <div className="hidden sm:flex items-center gap-1.5 bg-[#17202d] px-2.5 py-1 rounded-md border border-slate-700/80 font-mono text-xs text-slate-300">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Tokens: <strong className="text-slate-100">523</strong> / 4000</span>
          </div>

          <button 
            onClick={onNewConversation}
            className="flex items-center gap-1 bg-[#1a2433] hover:bg-slate-700 text-slate-200 text-xs px-2.5 py-1.5 rounded-md border border-slate-700 transition-colors"
            title="Start new conversation session"
          >
            <RotateCcw className="w-3.5 h-3.5 text-indigo-400" />
            <span className="hidden md:inline">New Conversation</span>
          </button>

          <button 
            className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition-colors"
            title="Agent Menu Options"
          >
            <MoreVertical className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* CHAT MESSAGES SCROLLABLE AREA */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';

          return (
            <div key={msg.id} className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-4xl mx-auto space-y-1`}>
              {/* Message Header info */}
              <div className="flex items-center gap-2 text-[11px] text-slate-400 px-1 font-mono">
                {isUser ? (
                  <>
                    <span>You (Admin)</span>
                    <span>•</span>
                    <span>{msg.timestamp}</span>
                    <User className="w-3 h-3 text-slate-400" />
                  </>
                ) : (
                  <>
                    <Bot className="w-3.5 h-3.5 text-indigo-400" />
                    <span className="font-semibold text-slate-200">{msg.agentName || agent.name}</span>
                    <span className="text-slate-600">•</span>
                    <span>{msg.timestamp}</span>
                    {msg.tokens && (
                      <span className="bg-slate-900/90 text-slate-400 px-1.5 py-0.2 rounded border border-slate-800 text-[10px]">
                        {msg.tokens.total} tokens
                      </span>
                    )}
                  </>
                )}
              </div>

              {/* Message Bubble Box */}
              <div 
                className={`p-3.5 rounded-xl border text-sm leading-relaxed shadow-lg relative transition-all ${
                  isUser 
                    ? 'bg-indigo-600/90 text-white border-indigo-500 rounded-tr-none max-w-[85%]' 
                    : 'bg-[#121924] text-slate-200 border-[#1e293b] rounded-tl-none w-full'
                }`}
              >
                {/* ASSISTANT REASONING THOUGHTS STEP-BY-STEP */}
                {!isUser && msg.thoughts && msg.thoughts.length > 0 && (
                  <div className="mb-3 bg-[#0d131c] rounded-lg border border-slate-800 overflow-hidden text-xs">
                    <button 
                      onClick={() => toggleThoughts(msg.id)}
                      className="w-full px-3 py-2 bg-[#121a26] hover:bg-[#16202e] flex items-center justify-between text-slate-300 font-mono text-[11px] transition-colors"
                    >
                      <div className="flex items-center gap-2 text-indigo-300 font-semibold">
                        <Brain className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
                        <span>Sales Agent Thinking & Reasoning Process ({msg.thoughts.length} steps)</span>
                      </div>
                      {openThoughts[msg.id] ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>

                    {openThoughts[msg.id] && (
                      <div className="p-2.5 space-y-2 border-t border-slate-800/80 bg-[#0b0f16]">
                        {msg.thoughts.map((thought, idx) => (
                          <div key={idx} className="flex items-start gap-2 text-[11px] font-mono">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                            <div>
                              <div className="font-semibold text-slate-200">{thought.title}</div>
                              <div className="text-slate-400">{thought.content}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* TOOL INVOCATIONS LOGS INSIDE ASSISTANT BUBBLE */}
                {!isUser && msg.toolInvocations && msg.toolInvocations.length > 0 && (
                  <div className="mb-3 space-y-1.5 font-mono text-[11px]">
                    {msg.toolInvocations.map((tool, idx) => (
                      <div key={idx} className="bg-[#0e1520] p-2 rounded-md border border-slate-800/80">
                        <div className="flex items-center justify-between text-indigo-300 font-semibold mb-1">
                          <span className="flex items-center gap-1.5">
                            <Terminal className="w-3.5 h-3.5 text-amber-400" /> Tool Executed: {tool.toolName}
                          </span>
                          <span className="text-emerald-400 text-[10px] bg-emerald-950/60 px-1 rounded border border-emerald-800">
                            {tool.executionTimeMs}ms
                          </span>
                        </div>
                        <div className="text-slate-400 text-[10px] bg-[#070a0e] p-1.5 rounded border border-slate-900 truncate">
                          <span className="text-indigo-400">$ </span>{tool.input}
                        </div>
                        <div className="text-emerald-300/90 text-[10px] mt-1 pl-2 border-l-2 border-emerald-500">
                          {tool.output}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* MAIN MESSAGE CONTENT FORMATTED */}
                <div className="prose prose-invert max-w-none text-slate-200 text-sm space-y-2 leading-relaxed">
                  {msg.text.split('\n\n').map((paragraph, pIdx) => {
                    if (paragraph.startsWith('### ')) {
                      return <h3 key={pIdx} className="text-base font-bold text-indigo-300 mt-3 mb-1">{paragraph.replace('### ', '')}</h3>;
                    }
                    if (paragraph.startsWith('|')) {
                      // Basic table formatting helper
                      const rows = paragraph.trim().split('\n');
                      return (
                        <div key={pIdx} className="overflow-x-auto my-2 rounded border border-slate-800 bg-[#0d131c]">
                          <table className="w-full text-xs text-left border-collapse">
                            <tbody>
                              {rows.map((row, rIdx) => {
                                const cells = row.split('|').filter(c => c.trim().length > 0 || c === '');
                                if (rIdx === 1 && row.includes('---')) return null; // skip header separator
                                return (
                                  <tr key={rIdx} className={rIdx === 0 ? 'bg-slate-900/90 font-bold border-b border-slate-800 text-indigo-300' : 'border-b border-slate-800/60'}>
                                    {cells.map((cell, cIdx) => (
                                      <td key={cIdx} className="px-3 py-1.5">{cell.trim()}</td>
                                    ))}
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>
                        </div>
                      );
                    }
                    if (paragraph.startsWith('* ') || paragraph.startsWith('• ') || paragraph.startsWith('1. ')) {
                      return (
                        <ul key={pIdx} className="list-disc pl-5 space-y-1 text-slate-300">
                          {paragraph.split('\n').map((li, lIdx) => (
                            <li key={lIdx}>{li.replace(/^(\*|•|\d+\.)\s*/, '')}</li>
                          ))}
                        </ul>
                      );
                    }
                    return <p key={pIdx}>{paragraph}</p>;
                  })}
                </div>

                {/* COPY BUTTON FOR ASSISTANT */}
                {!isUser && (
                  <div className="mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
                    <span className="font-mono text-[10px]">Response generated locally in 1.2s</span>
                    <button 
                      onClick={() => copyToClipboard(msg.text, msg.id)}
                      className="flex items-center gap-1 hover:text-slate-300 transition-colors"
                      title="Copy response"
                    >
                      {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedId === msg.id ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* STREAMING ANIMATION INDICATOR */}
        {isStreaming && (
          <div className="flex flex-col items-start max-w-4xl mx-auto space-y-1 animate-fadeIn">
            <div className="flex items-center gap-2 text-[11px] text-indigo-400 px-1 font-mono">
              <Bot className="w-3.5 h-3.5 text-indigo-400 animate-spin" />
              <span>{agent.name} is thinking & streaming response...</span>
            </div>
            <div className="p-4 rounded-xl bg-[#121924] border border-indigo-500/50 w-full font-mono text-xs text-slate-300 space-y-2">
              <div className="flex items-center gap-2 text-indigo-400">
                <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping"></span>
                <span>Generating local LLM tokens (glm4:9b)...</span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 w-2/3 animate-pulse"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* QUICK SUGGESTIONS BAR */}
      <div className="px-4 py-1.5 bg-[#0e131b] border-t border-[#1e293b]/60 flex items-center gap-2 overflow-x-auto text-xs shrink-0 no-scrollbar">
        <span className="text-[10px] font-mono text-slate-500 uppercase font-bold shrink-0">Prompts:</span>
        {quickPrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => setInputText(prompt)}
            className="px-2.5 py-1 rounded-full bg-[#18212e] hover:bg-indigo-950/80 hover:text-indigo-200 border border-slate-800 text-[11px] text-slate-300 shrink-0 transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* INPUT AREA (BOTTOM) */}
      <div className="p-3 bg-[#0d1219] border-t border-[#1e293b] shrink-0">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-2">
          <div className="relative bg-[#141d28] border border-slate-700 focus-within:border-indigo-500 rounded-xl p-2 shadow-inner transition-colors">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
              rows={2}
              className="w-full bg-transparent text-slate-100 placeholder-slate-500 text-xs sm:text-sm focus:outline-none resize-none custom-scrollbar"
            />

            {/* Input Toolbar Buttons */}
            <div className="flex items-center justify-between pt-1 border-t border-slate-800/80">
              <div className="flex items-center gap-1.5 text-slate-400 text-xs">
                {/* Attach File Button */}
                <button 
                  type="button" 
                  className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition-colors flex items-center gap-1 text-[11px]"
                  title="Attach file or dataset"
                >
                  <Paperclip className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Attach</span>
                </button>

                {/* Tools Dropdown */}
                <div className="relative">
                  <button 
                    type="button" 
                    onClick={() => setShowToolsDropdown(!showToolsDropdown)}
                    className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition-colors flex items-center gap-1 text-[11px]"
                  >
                    <Wrench className="w-3.5 h-3.5 text-amber-400" />
                    <span className="hidden sm:inline">Tools ▼</span>
                  </button>

                  {showToolsDropdown && (
                    <div className="absolute bottom-full left-0 mb-2 w-52 bg-[#1e293b] border border-slate-700 rounded-lg shadow-2xl z-50 p-2 text-xs space-y-1">
                      <div className="font-semibold text-[10px] text-slate-400 uppercase tracking-wider mb-1">Active Tool Chain</div>
                      {tools.map(t => (
                        <div key={t.id} className="flex items-center justify-between p-1 hover:bg-slate-800 rounded">
                          <span className="text-slate-200 text-[11px]">{t.name}</span>
                          <span className="text-[9px] text-emerald-400 font-mono">Ready</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Options Button */}
                <button 
                  type="button" 
                  onClick={() => setShowOptionsDropdown(!showOptionsDropdown)}
                  className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition-colors flex items-center gap-1 text-[11px]"
                >
                  <Sliders className="w-3.5 h-3.5 text-indigo-400" />
                  <span className="hidden sm:inline">Options ⚙️</span>
                </button>
              </div>

              {/* Action Buttons: Send & Voice */}
              <div className="flex items-center gap-1.5">
                <button 
                  type="button" 
                  className="p-1.5 hover:bg-slate-800 text-slate-400 hover:text-slate-200 rounded transition-colors"
                  title="Voice input dictation"
                >
                  <Mic className="w-4 h-4" />
                </button>

                <button 
                  type="submit" 
                  disabled={!inputText.trim() || isStreaming}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium text-xs shadow-md transition-all ${
                    inputText.trim() && !isStreaming 
                      ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/30' 
                      : 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  }`}
                >
                  <span>Send</span>
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
