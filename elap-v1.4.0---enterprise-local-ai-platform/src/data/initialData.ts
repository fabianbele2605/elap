import { Agent, Tool, KnowledgeSource, ConversationHistoryItem, SystemServiceStatus, HardwareMetrics, Message } from '../types';

export const INITIAL_AGENTS: Agent[] = [
  {
    id: 'agent_sales_01',
    name: 'Sales Agent',
    role: 'Sales',
    avatarColor: 'indigo',
    status: 'online',
    model: 'glm4:9b',
    lastActive: '2 min ago',
    skillsCount: 5,
    description: 'Specialized in Q3/Q4 sales forecasting, pipeline analysis, competitor comparison, and customer CRM recommendations.',
    systemPrompt: 'You are an Enterprise Sales Strategy AI Agent. Analyze sales performance, regional revenue metrics, pipeline opportunities, and synthesize actionable Q4 growth recommendations.',
    temperature: 0.7,
    topP: 0.9,
    contextLength: 4096,
    toolsEnabled: ['tool_web_search', 'tool_data_analysis', 'tool_report_gen', 'tool_db_query'],
    knowledgeAttached: ['ks_sales_db', 'ks_q3_report', 'ks_market_data'],
    totalTokensUsed: 142500,
  },
  {
    id: 'agent_it_02',
    name: 'IT Support Agent',
    role: 'IT Support',
    avatarColor: 'emerald',
    status: 'online',
    model: 'llama3.3:70b',
    lastActive: '5 min ago',
    skillsCount: 8,
    description: 'Diagnoses network connectivity, automates active directory password resets, and inspects local log traces.',
    systemPrompt: 'You are an IT Support & Infrastructure AI Agent. Provide clear, step-by-step diagnostic procedures, script resolution options, and network troubleshooting steps.',
    temperature: 0.3,
    topP: 0.85,
    contextLength: 8192,
    toolsEnabled: ['tool_db_query', 'tool_custom_scripts', 'tool_file_ocr'],
    knowledgeAttached: ['ks_company_docs'],
    totalTokensUsed: 98200,
  },
  {
    id: 'agent_analytics_03',
    name: 'Analytics Agent',
    role: 'Analytics',
    avatarColor: 'amber',
    status: 'online',
    model: 'qwen2.5-coder:32b',
    lastActive: '12 min ago',
    skillsCount: 6,
    description: 'Executes Python pandas/numpy data transformations, cohort churn analysis, and visualization rendering.',
    systemPrompt: 'You are a Senior Data Analytics AI Agent. Synthesize structured data tables, calculate statistical metrics, and explain data trends with extreme numerical precision.',
    temperature: 0.2,
    topP: 0.95,
    contextLength: 16384,
    toolsEnabled: ['tool_data_analysis', 'tool_custom_scripts', 'tool_db_query'],
    knowledgeAttached: ['ks_sales_db', 'ks_market_data'],
    totalTokensUsed: 310400,
  },
  {
    id: 'agent_research_04',
    name: 'Research Agent',
    role: 'Research',
    avatarColor: 'purple',
    status: 'idle',
    model: 'deepseek-r1:14b',
    lastActive: '1 hr ago',
    skillsCount: 7,
    description: 'Deep RAG vector searches across internal PDF archives, patent filings, and industry benchmark reports.',
    systemPrompt: 'You are an Enterprise Research AI Agent. Cross-reference academic sources, internal vector databases, and technical whitepapers with cited references.',
    temperature: 0.5,
    topP: 0.9,
    contextLength: 8192,
    toolsEnabled: ['tool_web_search', 'tool_file_ocr', 'tool_report_gen'],
    knowledgeAttached: ['ks_company_docs', 'ks_q3_report'],
    totalTokensUsed: 215000,
  },
  {
    id: 'agent_financial_05',
    name: 'Financial Agent',
    role: 'Financial',
    avatarColor: 'rose',
    status: 'online',
    model: 'mistral-nemo:12b',
    lastActive: '30 min ago',
    skillsCount: 4,
    description: 'Conducts ROI forecasting, quarterly EBITDA calculations, budget allocation audits, and tax compliance checks.',
    systemPrompt: 'You are an Enterprise Financial Controller AI Agent. Review financial ledgers, perform balance audits, and calculate quarterly margin growth.',
    temperature: 0.1,
    topP: 0.8,
    contextLength: 4096,
    toolsEnabled: ['tool_data_analysis', 'tool_report_gen', 'tool_db_query'],
    knowledgeAttached: ['ks_q3_report', 'ks_sales_db'],
    totalTokensUsed: 189000,
  }
];

export const INITIAL_MESSAGES: Message[] = [
  {
    id: 'msg_1',
    sender: 'user',
    text: 'Analyze the Q3 sales performance and provide recommendations for Q4.',
    timestamp: '09:42 AM',
  },
  {
    id: 'msg_2',
    sender: 'assistant',
    agentId: 'agent_sales_01',
    agentName: 'Sales Agent',
    timestamp: '09:43 AM',
    isStreaming: false,
    tokens: {
      prompt: 142,
      completion: 381,
      total: 523,
    },
    thoughts: [
      {
        title: 'Querying vector index ks_sales_db & ks_q3_report',
        content: 'Retrieved 4 high-relevance chunks from Q3 financial ledger and regional breakdown tables. Top match score: 0.94.',
        status: 'completed',
        timestamp: '09:42:15',
      },
      {
        title: 'Running Tool: tool_data_analysis',
        content: 'Aggregated regional revenue: West Coast ($1.1M), East Coast ($750K), EMEA ($350K), APAC ($200K). Total = $2.4M.',
        status: 'completed',
        timestamp: '09:42:30',
      },
      {
        title: 'Generating Q4 Strategic Recommendations',
        content: 'Synthesizing recommendations based on enterprise expansion in West Coast & targeted upsell for EMEA accounts.',
        status: 'completed',
        timestamp: '09:42:45',
      }
    ],
    toolInvocations: [
      {
        toolId: 'tool_db_query',
        toolName: 'Sales Database Query',
        input: 'SELECT region, SUM(amount) FROM q3_deals WHERE status = "closed_won" GROUP BY region;',
        output: '{"West Coast": 1100000, "East Coast": 750000, "EMEA": 350000, "APAC": 200000}',
        status: 'success',
        executionTimeMs: 42,
      },
      {
        toolId: 'tool_data_analysis',
        toolName: 'Data Analysis Engine',
        input: 'calc_yoy_growth(q3_2025=2400000, q3_2024=2142857)',
        output: '+12.00% YoY Growth Rate',
        status: 'success',
        executionTimeMs: 18,
      }
    ],
    text: `Based on the Q3 data analysis retrieved from the internal **Sales Database (Live)** and indexed **Q3 Performance Report**:

### 📈 Executive Performance Summary
* **Total Revenue**: **$2.4M** (*+12% YoY* vs $2.14M in Q3 2024)
* **Top Performing Region**: **West Coast** ($1.1M, representing 45.8% of total volume)
* **Average Deal Size**: **$84,500** (*+8.5% QoQ*)
* **Pipeline Conversion Rate**: **28.4%** (Target was 25.0%)

### 📊 Regional Breakdown
| Region | Q3 Revenue | Growth vs Q2 | Win Rate | Key Growth Driver |
| :--- | :--- | :--- | :--- | :--- |
| **West Coast** | $1,100,000 | +18.2% | 34% | Enterprise SaaS Tier Expansions |
| **East Coast** | $750,000 | +8.4% | 27% | Financial Services Verticals |
| **EMEA** | $350,000 | +14.1% | 22% | Local Channel Partners |
| **APAC** | $200,000 | -2.5% | 19% | Currency Fluctuations & Lengthened Cycles |

### 🚀 Strategic Recommendations for Q4
1. **West Coast Account Expansion**: Allocate 2 additional Senior SDRs to the West Coast territory to capitalize on high enterprise renewal momentum.
2. **EMEA Channel Accelerator**: Standardize localization playbooks to shorten the 45-day deal cycle down to sub-30 days.
3. **Product Bundling for APAC**: Introduce a streamlined mid-market tier to re-engage stalled APAC pipeline opportunities.`,
  }
];

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
    iconName: 'FileText',
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
    iconName: 'FileSearch',
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
