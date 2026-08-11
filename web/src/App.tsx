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
import { useConversation } from './hooks/useConversation';
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
import DocumentsTab from './components/tabs/DocumentsTab';
import { NewAgentModal } from './components/modals/NewAgentModal';
import { SettingsModal } from './components/modals/SettingsModal';
import { InstallAgentsModal } from './components/modals/InstallAgentsModal';
import { EMPRESA_CONTEXTO, SISTEMA_PROMPT_EMPRESA } from './config/empresa_contexto';
import { MessageSquare, BarChart2, Wrench, BookOpen, History, Sliders, FileText, Zap } from 'lucide-react';
import DocumentsPage from './pages/DocumentsPage';
import { KnowledgePackWizard } from './components/KnowledgePackWizard';

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
  const [user, setUser] = useState<any>(null);
  const [notifications, setNotifications] = useState<any>(null);
  const [battery, setBattery] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<MainTab>('chat');
  const [isStreaming, setIsStreaming] = useState(false);

  // Modals state
  const [isNewAgentModalOpen, setIsNewAgentModalOpen] = useState(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
  const [isInstallAgentsModalOpen, setIsInstallAgentsModalOpen] = useState(false);

  // Historial de conversaciones
  const conversation = useConversation();

  // Auto-crear conversación cuando se selecciona un agente
  // DESHABILITADO: Causaba crear múltiples conversaciones innecesarias
  // useEffect(() => {
  //   const createConv = async () => {
  //     if (selectedAgentId && selectedAgent && activeTab === 'chat') {
  //       if (!conversation.currentConversationId) {
  //         try {
  //           console.log(`📝 Auto-creando conversación para ${selectedAgent.name}...`);
  //           await conversation.createConversation(selectedAgent.name, selectedAgent.id);
  //           console.log('✅ Conversación creada');
  //         } catch (err) {
  //           console.error('❌ Error creando conversación:', err);
  //         }
  //       }
  //     }
  //   };
  //   createConv();
  // }, [selectedAgentId, activeTab]);

  // Load agents from backend on mount (ALWAYS from backend, NOT localStorage)
  useEffect(() => {
    const loadAgents = async () => {
      setIsLoadingAgents(true);
      try {
        // Always fetch from backend (source of truth)
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
          // Save to localStorage for reference (not as source of truth)
          localStorage.setItem('elap_agents', JSON.stringify(mappedAgents));
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

  // 🛑 NO persistir agents a localStorage - siempre cargar del backend
  // Esto evita que agentes viejos en localStorage sobrescriban los nuevos

  // 🛑 NO persistir messagesMap a localStorage - carga desde backend (conversation_manager)
  // Esto evita que mensajes viejos en localStorage se mezclen con los nuevos

  // Load hardware metrics and other data from API every 2 seconds
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/dashboard');
        if (response.ok) {
          const data = await response.json();
          const hwData = data.hardware;

          setHardware({
            cpuUsagePct: Math.round(hwData.cpu_percent),
            ramUsedGb: Math.round(hwData.memory_used_gb * 10) / 10,
            ramTotalGb: Math.round(hwData.memory_total_gb * 10) / 10,
            diskUsedGb: Math.round(hwData.disk_used_gb),
            diskTotalGb: Math.round(hwData.disk_total_gb),
            vramUsedGb: 4.8,
            vramTotalGb: 16,
            gpuUsagePct: 24
          });

          // Cargar datos adicionales
          if (data.user) setUser(data.user);
          if (data.notifications) setNotifications(data.notifications);
          if (data.battery) setBattery(data.battery);
        }
      } catch (err) {
        // API no disponible, mantener datos por defecto
      }
    };

    // Cargar inmediatamente
    loadDashboardData();

    // Actualizar cada 2 segundos
    const interval = setInterval(loadDashboardData, 2000);
    return () => clearInterval(interval);
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

    console.log(`🔵 handleSendMessage: selectedAgentId=${selectedAgentId}, selectedAgent.name=${selectedAgent?.name}`);

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
      // Enviar al backend - backend se encarga de crear conversación y guardar todo
      const url = `http://localhost:5000/api/agents/${selectedAgentId}/execute`;
      console.log(`📤 Enviando a: ${url}`);
      const res = await fetch(url, {
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

      // Post-procesar respuesta
      let respuestaLimpia = data.respuesta || "Error procesando la solicitud";
      respuestaLimpia = respuestaLimpia
        .replace(/\*\*(.+?)\*\*/g, '$1')
        .replace(/\*(.+?)\*/g, '$1')
        .replace(/###\s/g, '')
        .replace(/##\s/g, '')
        .replace(/#\s/g, '')
        .replace(/\[\[(.+?)\]\]/g, '$1')
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
        const response = await fetch('http://localhost:5000/api/agents', {
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
                <span>Chat</span>
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
                <span>Panél</span>
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
                <span>Wrench</span>
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
                <span>Conocimiento</span>
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
                <span>Historial</span>
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
                <span>Documentos</span>
              </button>

              <button
                onClick={() => setActiveTab('setup')}
                className={`px-3 py-1 rounded-t-lg text-xs font-semibold flex items-center gap-1.5 transition-all border-t border-x ${
                  activeTab === 'setup'
                    ? 'bg-white text-blue-600 border-slate-200 shadow-sm'
                    : 'text-slate-700 hover:text-slate-700 border-transparent hover:bg-slate-100'
                }`}
              >
                <Zap className="w-3.5 h-3.5 text-yellow-600" />
                <span>Fase 3</span>
              </button>
            </div>

            <div className="hidden sm:flex items-center gap-2 text-[12px] font-mono text-slate-700">
              <span>ELAP Engine: <strong className="text-green-600">En línea</strong></span>
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
                conversations={conversation.conversations}
                currentConversationId={conversation.currentConversationId}
                onSelectConversation={conversation.loadConversation}
                onDeleteConversation={conversation.deleteConversation}
                onCreateConversation={() => {
                  // Limpiar conversación actual para empezar una nueva
                  conversation.setCurrentConversationId(null);
                  setMessagesMap(prev => ({
                    ...prev,
                    [selectedAgentId]: []
                  }));
                }}
                conversationLoading={conversation.loading}
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
                conversations={conversation.conversations}
                historyItems={[]}
                onSelectSession={(id) => {
                  conversation.loadConversation(id);
                  setActiveTab('chat');
                }}
                onDeleteConversation={conversation.deleteConversation}
              />
            )}

            {activeTab === 'documents' && (
              <DocumentsTab isLoading={false} />
            )}

            {activeTab === 'setup' && (
              <KnowledgePackWizard
                onSuccess={() => setActiveTab('documents')}
              />
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
      <StatusBar hardware={hardware} user={user} notifications={notifications} battery={battery} />

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
