import { API_BASE_URL } from '../../config/api';
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
import { Download } from 'lucide-react';
import { ConversationHistory, type ConversationHistoryProps } from '../ConversationHistory';
import { Conversation } from '../../hooks/useConversation';
import { AutoChart } from '../AutoChart';

interface ChatTabProps {
  agent: Agent;
  messages: Message[];
  onSendMessage: (text: string, attachments?: any[]) => void;
  onNewConversation: () => void;
  isStreaming: boolean;
  tools: Tool[];
  // Historial
  conversations?: Conversation[];
  currentConversationId?: string | null;
  onSelectConversation?: (convId: string) => void;
  onDeleteConversation?: (convId: string) => void;
  onCreateConversation?: () => void;
  conversationLoading?: boolean;
}

export const ChatTab: React.FC<ChatTabProps> = ({
  agent,
  messages,
  onSendMessage,
  onNewConversation,
  isStreaming,
  tools,
  conversations = [],
  currentConversationId,
  onSelectConversation,
  onDeleteConversation,
  onCreateConversation,
  conversationLoading = false
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

  if (!agent) {
    return (
      <div className="flex-1 flex flex-col h-full bg-white text-slate-700 overflow-hidden relative items-center justify-center">
        <div className="text-center">
          <div className="text-5xl mb-4">⏳</div>
          <p className="text-slate-700 font-medium">Cargando agentes...</p>
          <p className="text-slate-500 text-sm mt-2">Conectando con el backend</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-white text-slate-700 overflow-hidden relative">
      {/* CHAT TAB HEADER */}
      <div className="h-12 px-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between shrink-0 z-10 select-none">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600/30 border border-blue-600/50 flex items-center justify-center font-bold text-blue-600 text-xs shadow">
            {agent.name.substring(0, 2).toUpperCase()}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-bold text-sm text-slate-900">{agent.name}</h2>
              <span className="text-[12px] bg-slate-50/80 text-blue-600 px-1.5 py-0.5 rounded border border-blue-600-800 font-mono">
                {agent.role}
              </span>
              <span className="flex items-center gap-1 text-[13px] text-green-600 font-medium">
                <span className="w-2 h-2 rounded-full bg-green-600400 animate-pulse"></span> Listo
              </span>
            </div>
            <p className="text-[12px] text-slate-700 font-mono">
              Model: <span className="text-slate-700">{agent.model}</span> • Context: {agent.contextLength} tokens
            </p>
          </div>
        </div>

        {/* Right Header Controls */}
        <div className="flex items-center gap-3">
          {/* Token Counter */}
          <div className="hidden sm:flex items-center gap-1.5 bg-slate-100 px-2.5 py-1 rounded-md border border-slate-700/80 font-mono text-xs text-slate-700">
            <Sparkles className="w-3.5 h-3.5 text-amber-700" />
            <span>Tokens: <strong className="text-slate-900">523</strong> / 4000</span>
          </div>

          <button 
            onClick={onNewConversation}
            className="flex items-center gap-1 bg-slate-100 hover:bg-slate-100 text-slate-700 text-xs px-2.5 py-1.5 rounded-md border border-slate-700 transition-colors"
            title="Start new conversation session"
          >
            <RotateCcw className="w-3.5 h-3.5 text-blue-600" />
            <span className="hidden md:inline">Nueva Conversación</span>
          </button>

          <button 
            className="p-1.5 hover:bg-slate-100 rounded text-slate-700 hover:text-slate-700 transition-colors"
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
              <div className="flex items-center gap-2 text-[13px] text-slate-700 px-1 font-mono">
                {isUser ? (
                  <>
                    <span>You (Admin)</span>
                    <span>•</span>
                    <span>{msg.timestamp}</span>
                    <User className="w-3 h-3 text-slate-700" />
                  </>
                ) : (
                  <>
                    <Bot className="w-3.5 h-3.5 text-blue-600" />
                    <span className="font-semibold text-slate-700">{msg.agentName || agent.name}</span>
                    <span className="text-slate-600">•</span>
                    <span>{msg.timestamp}</span>
                    {msg.tokens && (
                      <span className="bg-white/90 text-slate-700 px-1.5 py-0.2 rounded border border-slate-300 text-[12px]">
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
                    ? 'bg-blue-600/90 text-white border-blue-600 rounded-tr-none max-w-[85%]' 
                    : 'bg-slate-50 text-slate-700 border-slate-200 rounded-tl-none w-full'
                }`}
              >
                {/* ASSISTANT REASONING THOUGHTS STEP-BY-STEP */}
                {!isUser && msg.thoughts && msg.thoughts.length > 0 && (
                  <div className="mb-3 bg-slate-50 rounded-lg border border-slate-300 overflow-hidden text-xs">
                    <button 
                      onClick={() => toggleThoughts(msg.id)}
                      className="w-full px-3 py-2 bg-slate-100 hover:bg-slate-100 flex items-center justify-between text-slate-700 font-mono text-[13px] transition-colors"
                    >
                      <div className="flex items-center gap-2 text-blue-600 font-semibold">
                        <Brain className="w-3.5 h-3.5 text-blue-600 animate-pulse" />
                        <span>Sales Agent Thinking & Reasoning Process ({msg.thoughts.length} steps)</span>
                      </div>
                      {openThoughts[msg.id] ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>

                    {openThoughts[msg.id] && (
                      <div className="p-2.5 space-y-2 border-t border-slate-300/80 bg-slate-100">
                        {msg.thoughts.map((thought, idx) => (
                          <div key={idx} className="flex items-start gap-2 text-[13px] font-mono">
                            <CheckCircle2 className="w-3.5 h-3.5 text-green-600 mt-0.5 shrink-0" />
                            <div>
                              <div className="font-semibold text-slate-700">{thought.title}</div>
                              <div className="text-slate-700">{thought.content}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* TOOL INVOCATIONS LOGS INSIDE ASSISTANT BUBBLE */}
                {!isUser && msg.toolInvocations && msg.toolInvocations.length > 0 && (
                  <div className="mb-3 space-y-1.5 font-mono text-[13px]">
                    {msg.toolInvocations.map((tool, idx) => (
                      <div key={idx} className="bg-slate-50 p-2 rounded-md border border-slate-300/80">
                        <div className="flex items-center justify-between text-blue-600 font-semibold mb-1">
                          <span className="flex items-center gap-1.5">
                            <Terminal className="w-3.5 h-3.5 text-amber-700" /> Tool Executed: {tool.toolName}
                          </span>
                          <span className="text-green-600 text-[12px] bg-green-600950/60 px-1 rounded border border-green-600">
                            {tool.executionTimeMs}ms
                          </span>
                        </div>
                        <div className="text-slate-700 text-[12px] bg-slate-50 p-1.5 rounded border border-slate-900 truncate">
                          <span className="text-blue-600">$ </span>{tool.input}
                        </div>
                        <div className="text-green-600/90 text-[12px] mt-1 pl-2 border-l-2 border-green-600-500">
                          {tool.output}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* MAIN MESSAGE CONTENT - MARKDOWN PROFESIONAL */}
                <div className="max-w-none text-slate-800 text-sm space-y-4 leading-relaxed">
                  {msg.text.split('\n\n').map((paragraph, pIdx) => {
                    const paragraphs = msg.text.split('\n\n');

                    // Detectar gráfico automático
                    if (paragraph.includes('[Gráfico automático:')) {
                      const match = paragraph.match(/\[Gráfico automático:\s*(.+?)\]/);
                      const chartTitle = match ? match[1].trim() : 'Gráfico';

                      // Buscar tabla anterior
                      let tableMarkdown = '';
                      for (let i = pIdx - 1; i >= 0; i--) {
                        if (paragraphs[i]?.startsWith('|')) {
                          tableMarkdown = paragraphs[i];
                          break;
                        }
                      }

                      return (
                        <div key={pIdx}>
                          <AutoChart title={chartTitle} tableMarkdown={tableMarkdown} />
                          <p className="text-slate-800 leading-relaxed text-sm mt-3">
                            {paragraph.replace(/\[Gráfico automático:.*?\]\s*/g, '').trim()}
                          </p>
                        </div>
                      );
                    }

                    // H1 (# Título)
                    if (paragraph.startsWith('# ') && !paragraph.startsWith('## ')) {
                      return (
                        <h1 key={pIdx} className="text-3xl font-bold text-indigo-700 mt-5 mb-3 pb-3 border-b-3 border-indigo-600">
                          {paragraph.replace(/^#+\s*/, '')}
                        </h1>
                      );
                    }
                    // H2 (## Subtítulo)
                    if (paragraph.startsWith('## ') && !paragraph.startsWith('### ')) {
                      return (
                        <h2 key={pIdx} className="text-2xl font-bold text-indigo-600 mt-4 mb-2 flex items-center gap-3">
                          <span className="w-1.5 h-7 bg-gradient-to-b from-indigo-600 to-blue-600 rounded-full"></span>
                          {paragraph.replace(/^#+\s*/, '')}
                        </h2>
                      );
                    }
                    // H3 (### Subencabezado)
                    if (paragraph.startsWith('### ')) {
                      return (
                        <h3 key={pIdx} className="text-lg font-bold text-indigo-700 mt-3 mb-2 flex items-center gap-2">
                          <span className="w-1 h-5 bg-indigo-600 rounded"></span>
                          {paragraph.replace(/^#+\s*/, '')}
                        </h3>
                      );
                    }
                    // Tablas
                    if (paragraph.startsWith('|')) {
                      const rows = paragraph.trim().split('\n');
                      return (
                        <div key={pIdx} className="overflow-x-auto my-4 rounded-lg border border-indigo-300 bg-gradient-to-br from-indigo-50 via-blue-50 to-slate-50 shadow-md">
                          <table className="w-full text-sm text-left border-collapse">
                            <tbody>
                              {rows.map((row, rIdx) => {
                                const cells = row.split('|').filter(c => c.trim().length > 0 || c === '');
                                if (rIdx === 1 && row.includes('---')) return null;
                                return (
                                  <tr key={rIdx} className={rIdx === 0 ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 font-bold border-b border-indigo-400 text-white' : rIdx % 2 === 0 ? 'bg-white border-b border-slate-200' : 'bg-indigo-50/40 border-b border-slate-200'}>
                                    {cells.map((cell, cIdx) => (
                                      <td key={cIdx} className="px-4 py-3 font-medium text-slate-800 whitespace-nowrap">{cell.trim()}</td>
                                    ))}
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>
                        </div>
                      );
                    }
                    // Listas
                    if (paragraph.startsWith('* ') || paragraph.startsWith('• ') || paragraph.startsWith('1. ')) {
                      return (
                        <div key={pIdx} className="my-3 pl-1 border-l-4 border-indigo-500 bg-indigo-50/60 py-3 px-4 rounded-r-lg">
                          <ul className="list-disc pl-5 space-y-2 text-slate-800">
                            {paragraph.split('\n').map((li, lIdx) => {
                              const text = li.replace(/^(\*|•|\d+\.)\s*/, '');
                              return <li key={lIdx} className="font-medium text-slate-800">{text}</li>;
                            })}
                          </ul>
                        </div>
                      );
                    }
                    // Párrafos normales
                    return (
                      <p key={pIdx} className="text-slate-800 leading-relaxed font-light">
                        {paragraph}
                      </p>
                    );
                  })}
                </div>

                {/* COPY & REPORT BUTTONS FOR ASSISTANT */}
                {!isUser && (
                  <div className="mt-2 pt-2 border-t border-slate-300/80 flex items-center justify-between text-[13px] text-slate-700">
                    <span className="font-mono text-[12px]">Response generated locally in 1.2s</span>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => copyToClipboard(msg.text, msg.id)}
                        className="flex items-center gap-1 hover:text-slate-700 transition-colors"
                        title="Copy response"
                      >
                        {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-green-600" /> : <Copy className="w-3.5 h-3.5" />}
                        <span>{copiedId === msg.id ? 'Copied' : 'Copy'}</span>
                      </button>

                      {/* Botones de descarga */}
                      <div className="flex items-center gap-1.5 border-l border-slate-300/80 pl-3">
                        <button
                          onClick={async () => {
                            try {
                              const response = await fetch(`${API_BASE_URL}/api/documents/pdf`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                  agent_name: agent.name,
                                  title: `Análisis - ${agent.name}`,
                                  content: msg.text
                                })
                              });
                              if (response.ok) {
                                const blob = await response.blob();
                                const url = window.URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = `${agent.name}_report.pdf`;
                                a.click();
                                window.URL.revokeObjectURL(url);
                              }
                            } catch (err) {
                              console.error('Error descargando PDF:', err);
                              alert('Error descargando PDF');
                            }
                          }}
                          className="flex items-center gap-1 hover:text-red-600 transition-colors text-[12px]"
                          title="Descargar como PDF"
                        >
                          <Download className="w-3.5 h-3.5" />
                          <span>PDF</span>
                        </button>
                        <button
                          onClick={async () => {
                            try {
                              const response = await fetch(`${API_BASE_URL}/api/documents/word`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                  agent_name: agent.name,
                                  title: `Análisis - ${agent.name}`,
                                  content: msg.text
                                })
                              });
                              if (response.ok) {
                                const blob = await response.blob();
                                const url = window.URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = `${agent.name}_report.docx`;
                                a.click();
                                window.URL.revokeObjectURL(url);
                              }
                            } catch (err) {
                              console.error('Error descargando Word:', err);
                              alert('Error descargando Word');
                            }
                          }}
                          className="flex items-center gap-1 hover:text-blue-600 transition-colors text-[12px]"
                          title="Descargar como Word"
                        >
                          <Download className="w-3.5 h-3.5" />
                          <span>Word</span>
                        </button>
                        <button
                          onClick={async () => {
                            try {
                              const response = await fetch(`${API_BASE_URL}/api/documents/excel`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                  agent_name: agent.name,
                                  title: `Análisis - ${agent.name}`,
                                  content: msg.text
                                })
                              });
                              if (response.ok) {
                                const blob = await response.blob();
                                const url = window.URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = `${agent.name}_report.xlsx`;
                                a.click();
                                window.URL.revokeObjectURL(url);
                              }
                            } catch (err) {
                              console.error('Error descargando Excel:', err);
                              alert('Error descargando Excel');
                            }
                          }}
                          className="flex items-center gap-1 hover:text-green-600 transition-colors text-[12px]"
                          title="Descargar como Excel"
                        >
                          <Download className="w-3.5 h-3.5" />
                          <span>Excel</span>
                        </button>
                        <button
                          onClick={() => {
                            const jsonData = {
                              agent: agent.name,
                              role: agent.role,
                              timestamp: new Date().toISOString(),
                              content: msg.text
                            };
                            const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `${agent.name}_report.json`;
                            a.click();
                            window.URL.revokeObjectURL(url);
                          }}
                          className="flex items-center gap-1 hover:text-amber-600 transition-colors text-[12px]"
                          title="Descargar como JSON"
                        >
                          <Download className="w-3.5 h-3.5" />
                          <span>JSON</span>
                        </button>
                        <button
                          onClick={() => {
                            const htmlContent = `
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reporte - ${agent.name}</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      line-height: 1.6;
      color: #334155;
      background: #f8fafc;
      padding: 40px;
      max-width: 900px;
      margin: 0 auto;
    }
    .header {
      background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
      color: white;
      padding: 30px;
      border-radius: 10px;
      margin-bottom: 30px;
    }
    .header h1 { margin: 0 0 10px 0; }
    .header p { margin: 0; opacity: 0.9; }
    .content {
      background: white;
      padding: 30px;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    h1, h2, h3 { color: #4f46e5; margin-top: 20px; }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
    }
    th {
      background: #4f46e5;
      color: white;
      padding: 12px;
      text-align: left;
    }
    td {
      padding: 12px;
      border-bottom: 1px solid #e2e8f0;
    }
    tr:nth-child(even) {
      background: #f8fafc;
    }
    ul, ol {
      margin: 15px 0;
      padding-left: 20px;
    }
    li {
      margin: 8px 0;
    }
    .timestamp {
      text-align: right;
      color: #94a3b8;
      font-size: 0.9em;
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #e2e8f0;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>${agent.name}</h1>
    <p>${agent.role}</p>
  </div>
  <div class="content">
    ${msg.text.replace(/\n/g, '<br>').replace(/^## /gm, '<h2>').replace(/^# /gm, '<h1>').replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')}
  </div>
  <div class="timestamp">
    Generado: ${new Date().toLocaleString('es-CO')}
  </div>
</body>
</html>
                            `;
                            const blob = new Blob([htmlContent], { type: 'text/html' });
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `${agent.name}_report.html`;
                            a.click();
                            window.URL.revokeObjectURL(url);
                          }}
                          className="flex items-center gap-1 hover:text-purple-600 transition-colors text-[12px]"
                          title="Descargar como HTML"
                        >
                          <Download className="w-3.5 h-3.5" />
                          <span>HTML</span>
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* STREAMING ANIMATION INDICATOR */}
        {isStreaming && (
          <div className="flex flex-col items-start max-w-4xl mx-auto space-y-1 animate-fadeIn">
            <div className="flex items-center gap-2 text-[13px] text-blue-600 px-1 font-mono">
              <Bot className="w-3.5 h-3.5 text-blue-600 animate-spin" />
              <span>{agent.name} is thinking & streaming response...</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-blue-600/50 w-full font-mono text-xs text-slate-700 space-y-2">
              <div className="flex items-center gap-2 text-blue-600">
                <span className="w-2 h-2 rounded-full bg-blue-600 animate-ping"></span>
                <span>Generating local LLM tokens (glm4:9b)...</span>
              </div>
              <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 w-2/3 animate-pulse"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* QUICK SUGGESTIONS BAR */}
      <div className="px-4 py-2 bg-gradient-to-r from-indigo-50 to-blue-50 border-t border-indigo-200 flex items-center gap-2 overflow-x-auto text-xs shrink-0 no-scrollbar">
        <span className="text-[11px] font-semibold text-indigo-700 uppercase tracking-wider shrink-0">💡 Sugerencias:</span>
        {quickPrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => setInputText(prompt)}
            className="px-3 py-1.5 rounded-full bg-white hover:bg-indigo-100 hover:text-indigo-700 border border-indigo-200 text-[12px] text-slate-700 shrink-0 transition-all hover:shadow-sm"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* INPUT AREA (BOTTOM) */}
      <div className="p-4 bg-gradient-to-t from-indigo-50 to-white border-t border-indigo-200 shrink-0">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-3">
          <div className="relative bg-white border-2 border-slate-300 focus-within:border-indigo-500 focus-within:shadow-lg rounded-xl p-3 transition-all duration-200">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="✍️  Escribe tu pregunta aquí... (Enter para enviar, Shift+Enter para nueva línea)"
              rows={2}
              className="w-full bg-transparent text-slate-900 placeholder-slate-500 text-sm focus:outline-none resize-none custom-scrollbar font-medium"
            />

            {/* Input Toolbar Buttons */}
            <div className="flex items-center justify-between pt-2 border-t border-indigo-200">
              <div className="flex items-center gap-2 text-slate-700 text-xs">
                {/* Attach File Button */}
                <button
                  type="button"
                  className="p-2 hover:bg-indigo-100 rounded-lg text-slate-700 hover:text-indigo-700 transition-colors flex items-center gap-1 text-[12px] font-medium"
                  title="Adjuntar archivo o dataset"
                >
                  <Paperclip className="w-4 h-4" />
                  <span className="hidden sm:inline">Adjuntar</span>
                </button>

                {/* Tools Dropdown */}
                <div className="relative">
                  <button
                    type="button"
                    onClick={() => setShowToolsDropdown(!showToolsDropdown)}
                    className="p-2 hover:bg-indigo-100 rounded-lg text-slate-700 hover:text-indigo-700 transition-colors flex items-center gap-1 text-[12px] font-medium"
                  >
                    <Wrench className="w-4 h-4 text-amber-600" />
                    <span className="hidden sm:inline">Herramientas</span>
                  </button>

                  {showToolsDropdown && (
                    <div className="absolute bottom-full left-0 mb-2 w-56 bg-white border border-indigo-300 rounded-lg shadow-lg z-50 p-2 text-xs space-y-1">
                      <div className="font-semibold text-[11px] text-indigo-700 uppercase tracking-wider mb-2">Cadena de Herramientas</div>
                      {tools.map(t => (
                        <div key={t.id} className="flex items-center justify-between p-2 hover:bg-indigo-50 rounded">
                          <span className="text-slate-700 text-[12px]">{t.name}</span>
                          <span className="text-[10px] text-green-600 font-bold">✓ Listo</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Options Button */}
                <button
                  type="button"
                  onClick={() => setShowOptionsDropdown(!showOptionsDropdown)}
                  className="p-2 hover:bg-indigo-100 rounded-lg text-slate-700 hover:text-indigo-700 transition-colors flex items-center gap-1 text-[12px] font-medium"
                >
                  <Sliders className="w-4 h-4 text-indigo-600" />
                  <span className="hidden sm:inline">Opciones</span>
                </button>
              </div>

              {/* Action Buttons: Send & Voice */}
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  className="p-2 hover:bg-indigo-100 text-slate-700 hover:text-indigo-700 rounded-lg transition-colors"
                  title="Entrada de voz"
                >
                  <Mic className="w-4 h-4" />
                </button>

                <button
                  type="submit"
                  disabled={!inputText.trim() || isStreaming}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold text-xs transition-all duration-200 ${
                    inputText.trim() && !isStreaming
                      ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white shadow-lg shadow-indigo-600/40'
                      : 'bg-slate-200 text-slate-500 cursor-not-allowed'
                  }`}
                >
                  <span>Enviar</span>
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
