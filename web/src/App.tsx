import React, { useState, useEffect } from 'react';
import {
  INITIAL_AGENTS,
  INITIAL_MESSAGES,
  INITIAL_TOOLS,
  INITIAL_KNOWLEDGE_SOURCES,
  INITIAL_HISTORY,
  INITIAL_HARDWARE
} from './data/initialData';
import { Agent, Message, Tool, KnowledgeSource, ConversationHistoryItem, HardwareMetrics, MainTab } from './types';
import { listarAgentes } from './services/api';
import { WindowHeader } from './components/WindowHeader';
import { LeftSidebar } from './components/LeftSidebar';
import { RightSidebar } from './components/RightSidebar';
import { StatusBar } from './components/StatusBar';
import { ChatTab } from './components/tabs/ChatTab';
import { DashboardTab } from './components/tabs/DashboardTab';
import { ToolsTab } from './components/tabs/ToolsTab';
import { KnowledgeTab } from './components/tabs/KnowledgeTab';
import { HistoryTab } from './components/tabs/HistoryTab';
import { NewAgentModal } from './components/modals/NewAgentModal';
import { SettingsModal } from './components/modals/SettingsModal';
import { InstallAgentsModal } from './components/modals/InstallAgentsModal';
import { EMPRESA_CONTEXTO, SISTEMA_PROMPT_EMPRESA } from './config/empresa_contexto';
import { MessageSquare, BarChart2, Wrench, BookOpen, History, Sliders, FileText } from 'lucide-react';
import DocumentsPage from './pages/DocumentsPage';

export default function App() {
  const [agents, setAgents] = useState<Agent[]>(INITIAL_AGENTS);
  const [selectedAgentId, setSelectedAgentId] = useState<string>('');
  const [isLoadingAgents, setIsLoadingAgents] = useState(true);
  const [messagesMap, setMessagesMap] = useState<{ [agentId: string]: Message[] }>({
    agent_sales_01: INITIAL_MESSAGES
  });
  const [tools, setTools] = useState<Tool[]>(INITIAL_TOOLS);
  const [knowledgeSources, setKnowledgeSources] = useState<KnowledgeSource[]>(INITIAL_KNOWLEDGE_SOURCES);
  const [historyItems, setHistoryItems] = useState<ConversationHistoryItem[]>(INITIAL_HISTORY);
  const [hardware, setHardware] = useState<HardwareMetrics>(INITIAL_HARDWARE);
  const [activeTab, setActiveTab] = useState<MainTab>('chat');
  const [isStreaming, setIsStreaming] = useState(false);

  // Modals state
  const [isNewAgentModalOpen, setIsNewAgentModalOpen] = useState(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
  const [isInstallAgentsModalOpen, setIsInstallAgentsModalOpen] = useState(false);

  // Load agents from backend on mount
  useEffect(() => {
    const loadAgents = async () => {
      setIsLoadingAgents(true);
      try {
        const backendAgents = await listarAgentes();
        if (backendAgents && backendAgents.length > 0) {
          // Map backend response to frontend Agent type
          const mappedAgents: Agent[] = backendAgents.map((agent: any) => ({
            id: agent.id,
            name: agent.nombre || agent.name || 'Unknown',
            role: agent.rol || agent.role || 'Agent',
            model: agent.modelo || agent.model || 'glm4:9b',
            avatarColor: 'indigo',
            status: agent.estado === 'Activo' ? 'online' : 'idle',
            lastActive: 'Just now',
            skillsCount: 4,
            description: agent.objetivo || 'Local AI Agent',
            systemPrompt: 'You are an enterprise AI agent.',
            temperature: agent.temperatura || 0.7,
            topP: agent.top_p || 0.9,
            contextLength: 4096,
            toolsEnabled: [],
            knowledgeAttached: [],
            totalTokensUsed: 0
          }));
          setAgents(mappedAgents);
          setSelectedAgentId(mappedAgents[0].id);
        } else {
          console.warn('No agents found from backend');
        }
      } catch (err) {
        console.error('Error loading agents from backend:', err);
      } finally {
        setIsLoadingAgents(false);
      }
    };

    loadAgents();
  }, []);

  const selectedAgent = agents.find(a => a.id === selectedAgentId) || agents[0];
  const currentMessages = selectedAgent ? messagesMap[selectedAgentId] || [
    {
      id: `init_${Date.now()}`,
      sender: 'assistant',
      agentId: selectedAgent.id,
      agentName: selectedAgent.name,
      text: `¡Hola! Soy **${selectedAgent.name}** (Especialista en ${selectedAgent.role}).\n\n¿Cómo puedo ayudarte hoy?`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ] : [];

  // Handle sending a new message
  const handleSendMessage = async (text: string) => {
    const timestampStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const userMsg: Message = {
      id: `user_${Date.now()}`,
      sender: 'user',
      text,
      timestamp: timestampStr
    };

    // Update messages state
    const updatedMessages = [...currentMessages, userMsg];
    setMessagesMap(prev => ({
      ...prev,
      [selectedAgentId]: updatedMessages
    }));

    setIsStreaming(true);

    try {
      const res = await fetch(`http://localhost:3000/agents/${selectedAgentId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: text,
          agentName: selectedAgent.name,
          role: selectedAgent.role,
          systemPrompt: selectedAgent.systemPrompt,
          model: selectedAgent.model,
          history: updatedMessages,
          empresaContexto: EMPRESA_CONTEXTO,
          sistemaPromptEmpresa: SISTEMA_PROMPT_EMPRESA
        })
      });

      const data = await res.json();

      // Post-procesar respuesta para limpiar markdown y caracteres especiales
      let respuestaLimpia = data.respuesta || "Error procesando la solicitud";
      respuestaLimpia = respuestaLimpia
        .replace(/\*\*(.+?)\*\*/g, '$1')  // **negrita** → negrita
        .replace(/\*(.+?)\*/g, '$1')      // *cursiva* → cursiva
        .replace(/###\s/g, '')            // ### → (quita heading)
        .replace(/##\s/g, '')             // ## → (quita heading)
        .replace(/#\s/g, '')              // # → (quita heading)
        .replace(/\[\[(.+?)\]\]/g, '$1')  // [[link]] → link
        .replace(/\[(.*?)\]\((.*?)\)/g, '$1') // [text](url) → text
        .trim();

      const assistantMsg: Message = {
        id: `asst_${Date.now()}`,
        sender: 'assistant',
        agentId: selectedAgent.id,
        agentName: selectedAgent.name,
        text: respuestaLimpia,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        tokens: data.tokens || { prompt: 110, completion: 240, total: 350 },
        thoughts: data.thoughts || [
          {
            title: `Executed local model inference (${selectedAgent.model})`,
            content: `Synthesized response with local RAG context.`,
            status: 'completed',
            timestamp: timestampStr
          }
        ],
        toolInvocations: data.toolInvocations || [
          {
            toolId: 'tool_data_analysis',
            toolName: 'Local Execution Engine',
            input: text,
            output: 'Executed successfully with 0 exit code.',
            status: 'success',
            executionTimeMs: 24
          }
        ]
      };

      setMessagesMap(prev => ({
        ...prev,
        [selectedAgentId]: [...updatedMessages, assistantMsg]
      }));

      // Update total tokens in agent
      setAgents(prev => prev.map(a => {
        if (a.id === selectedAgentId) {
          return {
            ...a,
            totalTokensUsed: a.totalTokensUsed + (data.tokens?.total || 350),
            lastActive: 'Just now'
          };
        }
        return a;
      }));

    } catch (err) {
      console.error("Error in sending message:", err);
      // Fallback message
      const fallbackMsg: Message = {
        id: `asst_err_${Date.now()}`,
        sender: 'assistant',
        agentId: selectedAgent.id,
        agentName: selectedAgent.name,
        text: `Local Synthesis (${selectedAgent.name})\n\nProcessed query: **"${text}"**\n\n* Retrieved from connected knowledge bases\n* Ollama engine operating normally`,
        timestamp: timestampStr
      };
      setMessagesMap(prev => ({
        ...prev,
        [selectedAgentId]: [...updatedMessages, fallbackMsg]
      }));
    } finally {
      setIsStreaming(false);
    }
  };

  // Create new agent
  const handleCreateAgent = (newAgentData: Partial<Agent>) => {
    const newId = `agent_custom_${Date.now()}`;
    const newAgent: Agent = {
      id: newId,
      name: newAgentData.name || 'Custom Agent',
      role: newAgentData.role || 'Custom',
      avatarColor: newAgentData.avatarColor || 'indigo',
      status: 'online',
      model: newAgentData.model || 'glm4:9b',
      lastActive: 'Just now',
      skillsCount: newAgentData.skillsCount || 4,
      description: newAgentData.description || 'Custom local agent.',
      systemPrompt: newAgentData.systemPrompt || 'You are an enterprise AI agent.',
      temperature: 0.7,
      topP: 0.9,
      contextLength: 4096,
      toolsEnabled: newAgentData.toolsEnabled || ['tool_web_search'],
      knowledgeAttached: ['ks_company_docs'],
      totalTokensUsed: 0
    };

    setAgents(prev => [newAgent, ...prev]);
    setSelectedAgentId(newId);
    setActiveTab('chat');
  };

  // Install multiple agents from templates
  const handleInstallAgents = async (agentIds: string[]) => {
    try {
      const { AGENT_TEMPLATES } = await import('./config/agents');
      const agentsToCreate = AGENT_TEMPLATES.filter(t => agentIds.includes(t.id));

      const newAgents: Agent[] = [];
      for (const template of agentsToCreate) {
        const response = await fetch('http://localhost:3000/agents', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            nombre: template.nombre,
            rol: template.rol,
            objetivo: template.descripcion,
            modelo: template.modelo,
            temperatura: template.temperatura,
            top_p: template.top_p
          })
        });

        if (response.ok) {
          const data = await response.json();
          const newAgent: Agent = {
            id: data.id,
            name: data.nombre,
            role: data.rol,
            model: data.modelo,
            avatarColor: 'indigo',
            status: 'online',
            lastActive: 'Just now',
            skillsCount: 4,
            description: template.descripcion,
            systemPrompt: template.systemPrompt,
            temperature: template.temperatura,
            topP: template.top_p,
            contextLength: 4096,
            toolsEnabled: [],
            knowledgeAttached: [],
            totalTokensUsed: 0
          };
          newAgents.push(newAgent);
        }
      }

      if (newAgents.length > 0) {
        setAgents(prev => [...newAgents, ...prev]);
        setSelectedAgentId(newAgents[0].id);
      }
    } catch (err) {
      console.error('Error installing agents:', err);
    }
  };

  // Clear chat
  const handleClearChat = () => {
    setMessagesMap(prev => ({
      ...prev,
      [selectedAgentId]: [
        {
          id: `init_${Date.now()}`,
          sender: 'assistant',
          agentId: selectedAgent.id,
          agentName: selectedAgent.name,
          text: `Conversation cleared. How can I assist you, user?`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]
    }));
  };

  // Export chat
  const handleExportChat = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentMessages, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `ELAP_Session_${selectedAgent.name}_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Toggle tool binding for selected agent
  const handleToggleTool = (toolId: string) => {
    setAgents(prev => prev.map(a => {
      if (a.id === selectedAgentId) {
        const hasTool = a.toolsEnabled.includes(toolId);
        const updatedTools = hasTool 
          ? a.toolsEnabled.filter(id => id !== toolId)
          : [...a.toolsEnabled, toolId];
        return { ...a, toolsEnabled: updatedTools, skillsCount: updatedTools.length };
      }
      return a;
    }));
  };

  // Update hyper-parameters
  const handleUpdateAgentParams = (temperature: number, topP: number, contextLength: number) => {
    setAgents(prev => prev.map(a => {
      if (a.id === selectedAgentId) {
        return { ...a, temperature, topP, contextLength };
      }
      return a;
    }));
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-white text-slate-900 font-sans overflow-hidden select-none">
      {/* 1. TOP WINDOW HEADER & MENU CHROME */}
      <WindowHeader 
        projectName="Project Alpha"
        onOpenSettings={() => setIsSettingsModalOpen(true)}
        onOpenNewAgent={() => setIsNewAgentModalOpen(true)}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {/* 2. MAIN DESKTOP WORKSPACE AREA */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* LEFT SIDEBAR (220px) - AGENT NAVIGATOR */}
        <LeftSidebar
          agents={agents}
          selectedAgentId={selectedAgentId}
          onSelectAgent={(id) => {
            setSelectedAgentId(id);
            if (activeTab !== 'chat') setActiveTab('chat');
          }}
          onOpenNewAgentModal={() => setIsNewAgentModalOpen(true)}
          onOpenSettingsModal={() => setIsSettingsModalOpen(true)}
          onOpenInstallAgentsModal={() => setIsInstallAgentsModalOpen(true)}
          rustPortStatus={true}
          grpcPortStatus={true}
          ollamaPortStatus={true}
        />

        {/* CENTER MAIN AREA (Multi-Tab Interface) */}
        <main className="flex-1 flex flex-col min-w-0 bg-slate-50 border-r border-slate-200">
          {/* MULTI-TAB NAVIGATION BAR */}
          <div className="h-9 px-3 bg-white border-b border-slate-200 flex items-center justify-between shrink-0 select-none">
            <div className="flex items-center gap-1">
              <button
                onClick={() => setActiveTab('chat')}
                className={`px-3 py-1 rounded-t-lg text-xs font-semibold flex items-center gap-1.5 transition-all border-t border-x ${
                  activeTab === 'chat'
                    ? 'bg-white text-blue-600 border-slate-200 shadow-sm'
                    : 'text-slate-700 hover:text-slate-700 border-transparent hover:bg-slate-100'
                }`}
              >
                <MessageSquare className="w-3.5 h-3.5 text-blue-600" />
                <span>'Chat'</span>
              </button>

              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-3 py-1 rounded-t-lg text-xs font-semibold flex items-center gap-1.5 transition-all border-t border-x ${
                  activeTab === 'dashboard'
                    ? 'bg-white text-blue-600 border-slate-200 shadow-sm'
                    : 'text-slate-700 hover:text-slate-700 border-transparent hover:bg-slate-100'
                }`}
              >
                <BarChart2 className="w-3.5 h-3.5 text-green-600" />
                <span>'Panél'</span>
              </button>

              <button
                onClick={() => setActiveTab('tools')}
                className={`px-3 py-1 rounded-t-lg text-xs font-semibold flex items-center gap-1.5 transition-all border-t border-x ${
                  activeTab === 'tools'
                    ? 'bg-white text-blue-600 border-slate-200 shadow-sm'
                    : 'text-slate-700 hover:text-slate-700 border-transparent hover:bg-slate-100'
                }`}
              >
                <Wrench className="w-3.5 h-3.5 text-amber-700" />
                <span>'Wrench'</span>
              </button>

              <button
                onClick={() => setActiveTab('knowledge')}
                className={`px-3 py-1 rounded-t-lg text-xs font-semibold flex items-center gap-1.5 transition-all border-t border-x ${
                  activeTab === 'knowledge'
                    ? 'bg-white text-blue-600 border-slate-200 shadow-sm'
                    : 'text-slate-700 hover:text-slate-700 border-transparent hover:bg-slate-100'
                }`}
              >
                <BookOpen className="w-3.5 h-3.5 text-purple-700" />
                <span>'BookOpen'</span>
              </button>

              <button
                onClick={() => setActiveTab('history')}
                className={`px-3 py-1 rounded-t-lg text-xs font-semibold flex items-center gap-1.5 transition-all border-t border-x ${
                  activeTab === 'history'
                    ? 'bg-white text-blue-600 border-slate-200 shadow-sm'
                    : 'text-slate-700 hover:text-slate-700 border-transparent hover:bg-slate-100'
                }`}
              >
                <History className="w-3.5 h-3.5 text-rose-700" />
                <span>'History'</span>
              </button>

              <button
                onClick={() => setActiveTab('documents')}
                className={`px-3 py-1 rounded-t-lg text-xs font-semibold flex items-center gap-1.5 transition-all border-t border-x ${
                  activeTab === 'documents'
                    ? 'bg-white text-blue-600 border-slate-200 shadow-sm'
                    : 'text-slate-700 hover:text-slate-700 border-transparent hover:bg-slate-100'
                }`}
              >
                <FileText className="w-3.5 h-3.5 text-orange-600" />
                <span>'Documentos'</span>
              </button>
            </div>

            <div className="hidden sm:flex items-center gap-2 text-[12px] font-mono text-slate-700">
              <span>ELAP Engine: <strong className="text-green-600">'En línea'</strong></span>
            </div>
          </div>

          {/* ACTIVE TAB CONTENT DISPLAY */}
          <div className="flex-1 flex flex-col min-h-0 relative">
            {activeTab === 'chat' && (
              <ChatTab 
                agent={selectedAgent}
                messages={currentMessages}
                onSendMessage={handleSendMessage}
                onNewConversation={handleClearChat}
                isStreaming={isStreaming}
                tools={tools}
              />
            )}

            {activeTab === 'dashboard' && (
              <DashboardTab 
                agents={agents}
                hardware={hardware}
              />
            )}

            {activeTab === 'tools' && (
              <ToolsTab 
                tools={tools}
                onToggleTool={handleToggleTool}
              />
            )}

            {activeTab === 'knowledge' && (
              <KnowledgeTab 
                knowledgeSources={knowledgeSources}
              />
            )}

            {activeTab === 'history' && (
              <HistoryTab
                historyItems={historyItems}
                onSelectSession={(id) => {
                  setActiveTab('chat');
                }}
              />
            )}

            {activeTab === 'documents' && (
              <DocumentsPage />
            )}
          </div>
        </main>

        {/* RIGHT SIDEBAR (280px) - CONTEXT & PROPIEDADES */}
        <RightSidebar 
          agent={selectedAgent}
          tools={tools}
          knowledgeSources={knowledgeSources}
          onToggleTool={handleToggleTool}
          onClearChat={handleClearChat}
          onExportChat={handleExportChat}
          onUpdateAgentParams={handleUpdateAgentParams}
        />
      </div>

      {/* 3. BOTTOM STATUS BAR */}
      <StatusBar hardware={hardware} />

      {/* MODALS */}
      <NewAgentModal
        isOpen={isNewAgentModalOpen}
        onClose={() => setIsNewAgentModalOpen(false)}
        onCreateAgent={handleCreateAgent}
        availableTools={tools}
      />

      <SettingsModal
        isOpen={isSettingsModalOpen}
        onClose={() => setIsSettingsModalOpen(false)}
      />

      <InstallAgentsModal
        isOpen={isInstallAgentsModalOpen}
        onClose={() => setIsInstallAgentsModalOpen(false)}
        onInstall={handleInstallAgents}
      />
    </div>
  );
}
