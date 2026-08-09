# Fase 6: Multi-Agent Plugin Runtime Architecture

**Estado**: 🚀 Iniciada (2026-08-09)  
**Duración**: 1 semana  
**Entrega**: 2026-08-16  
**Objetivo**: Sistema de plugins con agentes especializados

---

## 🎯 Visión

Transformar ELAP de **un monolito de agentes** a una **arquitectura modular multi-agent**:

```
┌──────────────────────────────────────┐
│   Agent Orchestrator (Orquestador)   │
├──────────────────────────────────────┤
│                                      │
│  ┌────────────────┐ ┌────────────┐  │
│  │   HR Agent     │ │ Payroll    │  │
│  │ (Documentos)   │ │ Plugin     │  │
│  │                │ │(Análisis)  │  │
│  └────────────────┘ └────────────┘  │
│                                      │
│  ┌────────────────┐ ┌────────────┐  │
│  │   Benefits     │ │ Recruit    │  │
│  │   Plugin       │ │ Plugin     │  │
│  │                │ │            │  │
│  └────────────────┘ └────────────┘  │
│                                      │
└──────────────────────────────────────┘
         |              |
      Tools        RAG Data
      Ollama        Knowledge
```

**Beneficios**:
- ✅ Cada agent especializado en su dominio
- ✅ Tools reutilizables y separadas
- ✅ RAG específico por agent
- ✅ Escalable: agregar agents sin tocar existentes
- ✅ Mantenible: responsabilidades claras
- ✅ Seguro: plugins aislados con permisos granulares

---

## 📐 Arquitectura

### Agent Orchestrator (Coordinador Central)

```rust
pub struct AgentOrchestrator {
    agents: HashMap<String, Box<dyn Agent>>,
    payroll_plugin: Option<PayrollPlugin>,
    benefits_plugin: Option<BenefitsPlugin>,
    recruitment_plugin: Option<RecruitmentPlugin>,
}

impl AgentOrchestrator {
    pub async fn execute(&self, query: &str) -> Result<Response>;
    pub async fn load_plugin(&mut self, plugin: Plugin) -> Result<()>;
    pub async fn route_to_agent(&self, intent: Intent) -> Result<Response>;
}
```

### Agent Traits & Implementations

```rust
// Base trait (ya existe)
pub trait Agent {
    fn name(&self) -> &str;
    fn role(&self) -> &str;
    async fn process(&mut self, query: &str) -> Result<Response>;
}

// Implementaciones especializadas
impl Agent for HRAgent { /* contrato, políticas */ }
impl Agent for PayrollAgent { /* salarios, impuestos */ }
impl Agent for BenefitsAgent { /* seguros, pensión */ }
impl Agent for RecruitmentAgent { /* hiring, onboarding */ }
```

### Plugin System

```rust
pub struct PluginManifest {
    pub name: String,
    pub version: String,
    pub api_version: String,
    pub permissions: Vec<Permission>,
    pub tools: Vec<PluginTool>,
}

pub enum Permission {
    Database { tables: Vec<String> },
    FileSystem { paths: Vec<PathBuf> },
    Network { domains: Vec<String> },
    RAG { collections: Vec<String> },
    Ollama { models: Vec<String> },
}
```

---

## 📋 Implementación (5 días)

### Día 1: Agent Orchestrator Base

**Archivos**:
- `crates/elap-core/src/agent_orchestrator.rs` (mejorado)
- `crates/elap-core/src/agent_traits.rs` (refactor)

**Tasks**:
- [ ] Crear trait `Agent` base con métodos comunes
- [ ] Implementar `AgentOrchestrator` con registry
- [ ] Método `route_to_agent()` basado en intent
- [ ] Tests de orquestación (8 tests)

**LOC estimado**: ~200

---

### Día 2: Payroll Plugin

**Archivos**:
- `crates/elap-core/src/plugins/payroll.rs` (nuevo)
- `python/src/elap_ai/payroll_analyzer.py` (nuevo)

**Tasks**:
- [ ] PayrollPlugin Rust (manifest, loader)
- [ ] PayrollAnalyzer Python (Ollama + análisis)
- [ ] Integrar datos nómina al RAG
- [ ] Tests: salary calc, benefits, taxes (12 tests)

**LOC estimado**: ~400

---

### Día 3: Benefits & Recruitment Plugins

**Archivos**:
- `crates/elap-core/src/plugins/benefits.rs` (nuevo)
- `crates/elap-core/src/plugins/recruitment.rs` (nuevo)

**Tasks**:
- [ ] BenefitsPlugin: EPS, pensión, cesantías
- [ ] RecruitmentPlugin: CV parsing, job posting
- [ ] Integration con Ollama para asesoría
- [ ] Tests (10 tests)

**LOC estimado**: ~300

---

### Día 4: Plugin Discovery & Health Monitoring

**Archivos**:
- `crates/elap-core/src/plugin/discovery.rs` (mejorado)
- `crates/elap-core/src/plugin/health.rs` (mejorado)

**Tasks**:
- [ ] Auto-discover plugins en `/plugins/`
- [ ] Plugin health scores y metrics
- [ ] Auto-disable unhealthy plugins
- [ ] Tests (8 tests)

**LOC estimado**: ~250

---

### Día 5: Integration & Documentation

**Archivos**:
- `docs/06-Plugin-Runtime/IMPLEMENTATION.md` (nuevo)
- `docs/06-Plugin-Runtime/API_GUIDE.md` (nuevo)
- Libro 06 para NotebookLM

**Tasks**:
- [ ] Integración REST API de plugins
- [ ] CLI commands: `elap plugin list/load/execute`
- [ ] Documentación técnica completa
- [ ] Libro para NotebookLM (5 capítulos)
- [ ] CHANGELOG.md + TREE.md actualizado

**LOC estimado**: ~200

---

## 📊 Agentes & Plugins

| Agent/Plugin | Responsabilidad | Tools | RAG | Ollama |
|---|---|---|---|---|
| **HRAgent** | Contratos, políticas | ContractGen, PolicyLib | Leyes laborales | Redacción |
| **PayrollPlugin** | Salarios, nómina, impuestos | SalaryCal, TaxCal, BenefitsCal | Datos nómina | Análisis |
| **BenefitsPlugin** | Seguro, pensión, cesantías | EPSManager, PensionCalc | Tablas beneficios | Asesoría |
| **RecruitmentPlugin** | Hiring, onboarding | JobPostTpl, CVParser | Candidatos | Screening |

---

## 🔌 Plugin Manifest Example

```toml
[metadata]
name = "payroll-analyzer"
version = "1.0.0"
api_version = "1.5.0"
description = "Análisis avanzado de nómina y cálculos de impuestos"
author = "ELAP Team"

[requirements]
min_api_version = "1.5.0"
dependencies = []

[permissions]
required = ["database:nomina", "rag:payroll_data", "ollama:glm4"]
optional = ["network:external_tax_api"]

[safety]
timeout_ms = 30000
max_memory_mb = 512
max_file_size_mb = 100

[tools]
[[tools.item]]
name = "calculate_salary"
input_schema = { employee_id = "string", date = "string" }
output_schema = { gross = "number", deductions = "number", net = "number" }
```

---

## 🧪 Tests

- **Unit tests**: 40+ tests (agents, plugins, tools)
- **Integration tests**: 12+ tests (orquestación, RAG, Ollama)
- **E2E tests**: 5+ tests (flujos completos)
- **Cobertura**: >85%

---

## 📈 Métricas de Éxito

- ✅ 4 agentes especializados funcionales
- ✅ 3 plugins operacionales (Payroll, Benefits, Recruitment)
- ✅ Agent Orchestrator enruta correctamente
- ✅ RAG específico por agent
- ✅ Health monitoring activo
- ✅ Latencia overhead < 100ms
- ✅ >80% test coverage
- ✅ Documentación técnica completa

---

## 🏗️ Estructura de Archivos

```
crates/elap-core/src/
├── agent_orchestrator.rs (mejorado)
├── agent_traits.rs (refactor)
├── plugins/
│   ├── payroll.rs (nuevo)
│   ├── benefits.rs (nuevo)
│   ├── recruitment.rs (nuevo)
│   ├── manifest.rs (mejorado)
│   ├── discovery.rs (mejorado)
│   └── health.rs (mejorado)
├── tools/
│   ├── salary_calculator.rs (nuevo)
│   ├── tax_calculator.rs (nuevo)
│   ├── benefit_manager.rs (nuevo)
│   └── job_parser.rs (nuevo)
└── tests/
    └── plugin_integration_tests.rs (nuevo)

python/src/elap_ai/
├── payroll_analyzer.py (nuevo)
├── benefits_advisor.py (nuevo)
├── recruitment_ai.py (nuevo)
└── tests/
    └── test_plugins.py (nuevo)

docs/06-Plugin-Runtime/
├── IMPLEMENTATION.md (nuevo)
├── API_GUIDE.md (nuevo)
├── PLUGIN_MANIFEST.md (mejorado)
└── EXAMPLES.md (nuevo)

notebook/
└── Libro_06_MultiAgent_Plugins.md (nuevo)
```

---

## 🚀 Próximo Paso

**Día 1**: Implementar Agent Orchestrator base

¿Comenzamos? 🔥
