//! Módulo de Sistema de Plugins
//!
//! Framework para cargar y ejecutar plugins de terceros
//! de forma segura con aislamiento y control de permisos.

pub mod plugin_trait;
pub mod metadata;
pub mod loader;
pub mod registry;
pub mod sandbox;
pub mod research_plugin;
pub mod payroll;
pub mod benefits;
pub mod recruitment;
pub mod discovery;
pub mod health;

pub use plugin_trait::Plugin;
pub use metadata::PluginMetadata;
pub use loader::PluginLoader;
pub use registry::RegistroPlugins;
pub use sandbox::{PluginSandbox, ConfiguracionSandbox, PoliticaEjecucion};
pub use research_plugin::ResearchPlugin;
pub use payroll::{PayrollPlugin, PayrollPluginConfig, SalaryAnalysis, BenefitCalculation, PayrollSummary};
pub use benefits::{BenefitsPlugin, BenefitsProvider, ProviderType, BenefitsPlan, SocialBenefits};
pub use recruitment::{RecruitmentPlugin, JobPosting, Candidate, ScreeningResult, OnboardingPlan};
pub use discovery::{PluginDiscoveryService, DiscoveredPlugin, DiscoveryStats};
pub use health::{PluginHealthMonitor, HealthStatus, ExecutionMetrics};
