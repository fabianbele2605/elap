import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI } from "@google/genai";

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // Initialize Gemini AI Client
  const apiKey = process.env.GEMINI_API_KEY;
  let ai: GoogleGenAI | null = null;
  if (apiKey) {
    ai = new GoogleGenAI({
      apiKey,
      httpOptions: {
        headers: {
          'User-Agent': 'aistudio-build',
        }
      }
    });
  }

  // --- API ENDPOINTS ---

  // Health check endpoint
  app.get("/api/health", (req, res) => {
    res.json({
      status: "ok",
      version: "1.4.0",
      services: {
        rustCorePort: 3000,
        pythonGrpcPort: 50051,
        ollamaPort: 11434,
        geminiConfigured: !!apiKey,
      },
      timestamp: new Date().toISOString()
    });
  });

  // Local Ollama Models API
  app.get("/api/ollama/models", (req, res) => {
    res.json([
      { name: "glm4:9b", size: "5.2 GB", modified: "2026-08-01T10:00:00Z", parameterSize: "9B", quantization: "Q4_K_M" },
      { name: "llama3.3:70b", size: "39.5 GB", modified: "2026-08-02T14:30:00Z", parameterSize: "70B", quantization: "Q4_K_M" },
      { name: "qwen2.5-coder:32b", size: "18.2 GB", modified: "2026-08-03T09:15:00Z", parameterSize: "32B", quantization: "Q4_K_M" },
      { name: "deepseek-r1:14b", size: "8.9 GB", modified: "2026-08-04T16:20:00Z", parameterSize: "14B", quantization: "Q4_K_M" },
      { name: "mistral-nemo:12b", size: "7.1 GB", modified: "2026-08-05T11:45:00Z", parameterSize: "12B", quantization: "Q4_K_M" },
    ]);
  });

  // Execute Tool Endpoint
  app.post("/api/tools/execute", async (req, res) => {
    const { toolId, toolName, input } = req.body;
    const startTime = Date.now();

    // Simulate tool execution logic
    let result = "";
    if (toolId === "tool_db_query") {
      result = `SELECT region, COUNT(*), SUM(revenue) FROM deals WHERE status = 'won' AND query_params = '${input}';\n-- Returned 42 rows in 14ms. Total: $2,410,000.`;
    } else if (toolId === "tool_data_analysis") {
      result = `Calculated statistics for input payload:\nMean: 84.5 | StdDev: 12.3 | Growth Delta: +12.0% | Confidence Interval: 95%`;
    } else if (toolId === "tool_web_search") {
      result = `Top Search Results for '${input}':\n1. Enterprise AI Benchmarks 2026 - Q3 YoY Growth Analysis\n2. Regional Market Expansion Strategies in B2B SaaS`;
    } else {
      result = `Tool '${toolName}' executed successfully with input: "${input}". Process completed with zero exit code.`;
    }

    const latencyMs = Date.now() - startTime + Math.floor(Math.random() * 20) + 15;

    res.json({
      toolId,
      toolName,
      input,
      output: result,
      status: "success",
      executionTimeMs: latencyMs
    });
  });

  // Vector Search Knowledge Base Endpoint
  app.post("/api/knowledge/search", (req, res) => {
    const { query, sourceIds, topK = 3 } = req.body;
    res.json({
      query,
      topMatches: [
        {
          id: "chunk_891",
          sourceName: "Sales Database (Live)",
          content: `Q3 Closed Deals: West Coast region reached $1.1M in revenue with enterprise SaaS renewals. East Coast brought $750K.`,
          relevanceScore: 0.942,
        },
        {
          id: "chunk_412",
          sourceName: "Q3 Report (Indexed)",
          content: `Gross profit margin increased by 2.4% due to local LLM inference efficiency gains over cloud APIs.`,
          relevanceScore: 0.887,
        },
        {
          id: "chunk_105",
          sourceName: "Market Data (Cached)",
          content: `B2B SaaS benchmarks indicate 11-15% YoY growth across mid-market enterprise verticals in 2026.`,
          relevanceScore: 0.815,
        }
      ].slice(0, topK)
    });
  });

  // AI Chat Route using Gemini or local intelligent agent generator
  app.post("/api/chat", async (req, res) => {
    try {
      const { prompt, agentName, role, systemPrompt, model, history } = req.body;

      if (!prompt) {
        return res.status(400).json({ error: "Prompt is required" });
      }

      let generatedText = "";
      let promptTokens = Math.floor(prompt.length / 4) + 20;
      let completionTokens = 0;

      if (ai) {
        try {
          const fullPrompt = `${systemPrompt || 'You are an enterprise local AI agent named ' + agentName}.\nUser query: ${prompt}`;
          const response = await ai.models.generateContent({
            model: "gemini-3.6-flash",
            contents: fullPrompt,
            config: {
              temperature: 0.7,
              systemInstruction: `You are ELAP Enterprise AI Agent (${agentName} - Role: ${role || 'AI Specialist'}). Provide structured, authoritative markdown responses with bullet points, statistics, and clear execution steps when appropriate.`
            }
          });
          generatedText = response.text || "";
        } catch (geminiErr: any) {
          console.warn("Gemini API call failed, falling back to ELAP Local Agent synthesis:", geminiErr.message);
        }
      }

      // If Gemini wasn't available or returned empty, generate persona-specific response
      if (!generatedText) {
        if (role === 'IT Support' || agentName?.includes('IT')) {
          generatedText = `### 🛠️ IT Diagnostic Report\n\nI have scanned the local system logs and network sockets for your request: **"${prompt}"**.\n\n* **Status**: Network gateway stable on port 50051 (gRPC).\n* **Action Item**: Executed \`ipconfig /flushdns\` & reset active session cache.\n* **Resolution**: Service ping latency reduced to **2ms**.\n\nLet me know if you need automated script deployment.`;
        } else if (role === 'Analytics' || agentName?.includes('Analytics')) {
          generatedText = `### 📊 Analytics & Statistical Synthesis\n\nAnalyzed data request: **"${prompt}"**\n\n| Metric | Baseline | Current | Variance |\n| :--- | :--- | :--- | :--- |\n| **Data Throughput** | 1.2 GB/s | 1.8 GB/s | **+50.0%** |\n| **Query Latency** | 45ms | 18ms | **-60.0%** |\n| **Confidence Score** | 92% | 98.4% | **+6.4%** |\n\nAll data tables cross-referenced with local SQLite vector store.`;
        } else if (role === 'Financial' || agentName?.includes('Financial')) {
          generatedText = `### 💰 Financial Audit & Forecast\n\nRegarding **"${prompt}"**:\n\n1. **Quarterly CapEx Allocation**: $450,000 allocated for GPU cluster upgrades.\n2. **Estimated ROI Horizon**: 6.2 months based on local inference savings.\n3. **Compliance Rating**: **100% Passed** (SOX & ISO 27001 Local Data Privacy).`;
        } else {
          generatedText = `### ⚡ ELAP Agent Synthesis (${agentName || 'Sales Agent'})\n\nThank you for your prompt: **"${prompt}"**.\n\n* **Primary Strategy**: Optimized local workflow execution across connected agents.\n* **Key Finding**: Vector retrieval matched 3 enterprise knowledge documents with 94.2% relevance.\n* **Next Step**: Recommended continuous execution via the local Ollama LLM context buffer.`;
        }
      }

      completionTokens = Math.floor(generatedText.length / 4);

      // Return rich agent response with thoughts & tool logs
      res.json({
        text: generatedText,
        tokens: {
          prompt: promptTokens,
          completion: completionTokens,
          total: promptTokens + completionTokens
        },
        thoughts: [
          {
            title: `Context Retrieval via RAG (${agentName})`,
            content: `Indexed 3 local vector chunks from Knowledge Engine. Match precision: 0.942.`,
            status: 'completed',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
          },
          {
            title: `Executing Local Model Inference (${model || 'glm4:9b'})`,
            content: `Processed ${promptTokens} input tokens and generated ${completionTokens} completion tokens locally.`,
            status: 'completed',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
          }
        ],
        toolInvocations: [
          {
            toolId: 'tool_data_analysis',
            toolName: 'Local Execution Engine',
            input: prompt,
            output: 'Executed successfully with 0 exit code.',
            status: 'success',
            executionTimeMs: 24
          }
        ]
      });
    } catch (err: any) {
      console.error("Error in /api/chat:", err);
      res.status(500).json({ error: err.message || "Internal server error" });
    }
  });

  // Vite middleware for development vs Static serving for production
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`ELAP Server v1.4.0 running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
