import { Agent, Tool, KnowledgeSource, ConversationHistoryItem, SystemServiceStatus, HardwareMetrics, Message } from '../types';

// Fallback empty agents — será reemplazado por datos del backend
export const INITIAL_AGENTS: Agent[] = [];

export const INITIAL_MESSAGES: Message[] = [];

export const INITIAL_TOOLS: Tool[] = [
  {
    id: 'tool_web_search',
    name: 'Web Search Engine',
    category: 'Search',
    description: 'Searches live internet sources and filters domain reputation for up-to-date market intel.',
    iconName: 'Globe',
    isEnabled: true,
    version: '1.2.0',
    author: 'ELAP Core',
    parameters: [
      { name: 'query', type: 'string', description: 'Search keywords', required: true },
      { name: 'num_results', type: 'number', description: 'Maximum results to fetch', required: false },
    ],
    executionCount: 1420,
    avgLatencyMs: 210,
  },
  {
    id: 'tool_data_analysis',
    name: 'Data Analysis Engine',
    category: 'Data',
    description: 'Performs statistical calculations, trendline fits, and matrix transformations.',
    iconName: 'BarChart2',
    isEnabled: true,
    version: '2.0.4',
    author: 'ELAP Core',
    parameters: [
      { name: 'data_json', type: 'string', description: 'JSON dataset array', required: true },
      { name: 'metrics', type: 'string', description: 'Aggregation functions', required: true },
    ],
    executionCount: 3890,
    avgLatencyMs: 35,
  },
  {
    id: 'tool_report_gen',
    name: 'Report Generator',
    category: 'Communication',
    description: 'Formats raw analysis into executive Markdown, PDF summaries, and slide decks.',
    iconName: 'ArchivoText',
    isEnabled: true,
    version: '1.1.0',
    author: 'ELAP Core',
    parameters: [
      { name: 'template', type: 'string', description: 'Executive summary or detail view', required: true },
      { name: 'content', type: 'string', description: 'Markdown body content', required: true },
    ],
    executionCount: 840,
    avgLatencyMs: 90,
  },
  {
    id: 'tool_db_query',
    name: 'Sales Database Query',
    category: 'Data',
    description: 'Executes read-only SQL queries against local SQLite and PostgreSQL enterprise data lakes.',
    iconName: 'Database',
    isEnabled: true,
    version: '1.4.2',
    author: 'ELAP Data Team',
    parameters: [
      { name: 'sql_query', type: 'string', description: 'Read-only SQL statement', required: true },
    ],
    executionCount: 5210,
    avgLatencyMs: 18,
  },
  {
    id: 'tool_custom_scripts',
    name: 'Python Script Runner',
    category: 'Code',
    description: 'Sandboxed Pyodide/Python interpreter for customized data manipulation and automation.',
    iconName: 'Terminal',
    isEnabled: true,
    version: '3.10.2',
    author: 'ELAP Dev',
    parameters: [
      { name: 'script_code', type: 'string', description: 'Python source code', required: true },
    ],
    executionCount: 950,
    avgLatencyMs: 145,
  },
  {
    id: 'tool_file_ocr',
    name: 'Document & PDF OCR',
    category: 'Data',
    description: 'Parses complex multi-page PDFs, scans table columns, and extracts key-value pairs.',
    iconName: 'ArchivoSearch',
    isEnabled: true,
    version: '2.1.0',
    author: 'ELAP Vision',
    parameters: [
      { name: 'file_path', type: 'string', description: 'Path to target PDF/Image', required: true },
    ],
    executionCount: 630,
    avgLatencyMs: 410,
  }
];

export const INITIAL_KNOWLEDGE_SOURCES: KnowledgeSource[] = [
  {
    id: 'ks_sales_db',
    name: 'Sales Database (Live)',
    type: 'Database',
    status: 'Indexed',
    vectorCount: 42800,
    fileSize: '1.2 GB',
    lastUpdated: 'Live Sync',
    description: 'Real-time sync with internal enterprise SQLite deal ledger and customer CRM accounts.',
  },
  {
    id: 'ks_q3_report',
    name: 'Q3 Report (Indexed)',
    type: 'Document',
    status: 'Indexed',
    vectorCount: 8450,
    fileSize: '48.2 MB',
    lastUpdated: '2 hours ago',
    description: 'Audited financial results, operational metrics, and executive board slide decks.',
  },
  {
    id: 'ks_market_data',
    name: 'Market Data (Cached)',
    type: 'Vector DB',
    status: 'Cached',
    vectorCount: 125000,
    fileSize: '3.4 GB',
    lastUpdated: '1 day ago',
    description: 'Industry benchmark reports, competitor pricing tables, and macroeconomic indices.',
  },
  {
    id: 'ks_company_docs',
    name: 'Company Docs (Vectorized)',
    type: 'Document',
    status: 'Indexed',
    vectorCount: 64200,
    fileSize: '890 MB',
    lastUpdated: '3 days ago',
    description: 'Internal HR handbooks, IT security guidelines, API schemas, and SLA procedures.',
  }
];

export const INITIAL_HISTORY: ConversationHistoryItem[] = [
  {
    id: 'conv_1',
    agentId: 'agent_sales_01',
    agentName: 'Sales Agent',
    title: 'Q3 Revenue & Q4 Growth Strategy',
    preview: 'Analyze the Q3 sales performance and provide recommendations for Q4.',
    timestamp: 'Today, 09:43 AM',
    messageCount: 2,
    tokensUsed: 523,
    isPinned: true,
    isFavorite: true,
  },
  {
    id: 'conv_2',
    agentId: 'agent_it_02',
    agentName: 'IT Support Agent',
    title: 'VPN Connection Timeout Investigation',
    preview: 'Users reporting error 800 on secondary gateways.',
    timestamp: 'Yesterday, 04:15 PM',
    messageCount: 8,
    tokensUsed: 2410,
    isPinned: false,
    isFavorite: true,
  },
  {
    id: 'conv_3',
    agentId: 'agent_analytics_03',
    agentName: 'Analytics Agent',
    title: 'Customer Churn Cohort Matrix Q2-Q3',
    preview: 'Calculate 90-day retention rates for enterprise subscribers.',
    timestamp: 'Aug 04, 2026',
    messageCount: 12,
    tokensUsed: 6840,
    isPinned: true,
    isFavorite: false,
  },
  {
    id: 'conv_4',
    agentId: 'agent_financial_05',
    agentName: 'Financial Agent',
    title: 'Operating Expense Audit & Cost Center Breakdown',
    preview: 'Verify hardware allocation against Q3 CapEx budget.',
    timestamp: 'Aug 02, 2026',
    messageCount: 5,
    tokensUsed: 1950,
    isPinned: false,
    isFavorite: false,
  }
];

export const SYSTEM_SERVICES: SystemServiceStatus[] = [
  { name: 'Rust Core Engine', port: 3000, status: 'healthy', latencyMs: 2, icon: 'Zap' },
  { name: 'Python gRPC Worker', port: 50051, status: 'healthy', latencyMs: 4, icon: 'Cpu' },
  { name: 'Ollama Local LLM', port: 11434, status: 'healthy', latencyMs: 14, icon: 'Brain' },
];

export const INITIAL_HARDWARE: HardwareMetrics = {
  cpuUsagePct: 45,
  ramUsedGb: 2.3,
  ramTotalGb: 8.0,
  gpuUsagePct: 24,
  vramUsedGb: 4.8,
  vramTotalGb: 16.0,
  diskUsedGb: 340,
  diskTotalGb: 1000,
  ollamaModelLoaded: 'glm4:9b (Q4_K_M)',
};
