export type AgentRole = 'Sales' | 'IT Support' | 'Analytics' | 'Research' | 'Financial' | 'Developer' | 'Executive' | 'Custom';

export type AgentStatus = 'online' | 'busy' | 'idle' | 'offline';

export interface Agent {
  id: string;
  name: string;
  role: AgentRole;
  avatarColor: string; // Tailwind color class or hex
  status: AgentStatus;
  model: string;
  lastActive: string;
  skillsCount: number;
  systemPrompt: string;
  temperature: number;
  topP: number;
  contextLength: number;
  description: string;
  toolsEnabled: string[];
  knowledgeAttached: string[];
  totalTokensUsed: number;
}

export interface ThoughtStep {
  title: string;
  content: string;
  status: 'pending' | 'in_progress' | 'completed';
  timestamp?: string;
}

export interface ToolInvocation {
  toolId: string;
  toolName: string;
  input: string;
  output: string;
  status: 'running' | 'success' | 'failed';
  executionTimeMs: number;
}

export interface Message {
  id: string;
  sender: 'user' | 'assistant' | 'system';
  agentId?: string;
  agentName?: string;
  text: string;
  timestamp: string;
  isStreaming?: boolean;
  thoughts?: ThoughtStep[];
  toolInvocations?: ToolInvocation[];
  tokens?: {
    prompt: number;
    completion: number;
    total: number;
  };
  attachments?: {
    name: string;
    size: string;
    type: string;
  }[];
}

export interface Tool {
  id: string;
  name: string;
  category: 'Data' | 'Search' | 'Code' | 'Communication' | 'System';
  description: string;
  iconName: string;
  isEnabled: boolean;
  version: string;
  author: string;
  parameters: {
    name: string;
    type: string;
    description: string;
    required: boolean;
  }[];
  executionCount: number;
  avgLatencyMs: number;
}

export interface KnowledgeSource {
  id: string;
  name: string;
  type: 'Database' | 'Document' | 'Vector DB' | 'API Stream' | 'Web Scraping';
  status: 'Indexed' | 'Syncing' | 'Cached' | 'Error';
  vectorCount: number;
  fileSize: string;
  lastUpdated: string;
  relevanceScore?: number;
  description: string;
}

export interface ConversationHistoryItem {
  id: string;
  agentId: string;
  agentName: string;
  title: string;
  preview: string;
  timestamp: string;
  messageCount: number;
  tokensUsed: number;
  isPinned?: boolean;
  isFavorite?: boolean;
}

export interface SystemServiceStatus {
  name: string;
  port: number;
  status: 'healthy' | 'degraded' | 'offline';
  latencyMs: number;
  icon: string;
}

export interface HardwareMetrics {
  cpuUsagePct: number;
  ramUsedGb: number;
  ramTotalGb: number;
  gpuUsagePct: number;
  vramUsedGb: number;
  vramTotalGb: number;
  diskUsedGb: number;
  diskTotalGb: number;
  ollamaModelLoaded: string;
}

export type MainTab = 'chat' | 'dashboard' | 'tools' | 'knowledge' | 'history' | 'documents' | 'setup' | 'settings';
