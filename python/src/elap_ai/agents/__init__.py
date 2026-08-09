"""
LangGraph-based agent orchestration.

Provides structured agent execution with state management,
tool selection, and persistent memory.

15 ELAP Agents:
- Sistema (3): SystemSupervisor, TaskRouter, MemoryManager
- Administrativo (5): HRAgent, FinanceAgent, PayrollAgent, BenefitsAgent, RecruitmentAgent
- Dirección (3): CEOAssistant, CFOAssistant, CMOAssistant
- Comercial (4): ComprasAgent, VentasAgent, CRMAgent, CustomerServiceAgent
- Documentación (2): DocumentManagerAgent, PDFAssistantAgent
"""

from .langgraph_agent import LangGraphAgent
from .agent_state import AgentState

# === Administrativo ===
from .hr_agent import HRAgent
from .finance_agent import FinanceAgent
from .payroll_agent import PayrollAgent
from .benefits_agent import BenefitsAgent
from .recruitment_agent import RecruitmentAgent

# === Dirección ===
from .ceo_assistant import CEOAssistant
from .cfo_assistant import CFOAssistant
from .cmo_assistant import CMOAssistant

# === Comercial ===
from .compras_agent import ComprasAgent
from .ventas_agent import VentasAgent
from .crm_agent import CRMAgent
from .customer_service_agent import CustomerServiceAgent

# === Documentación ===
from .document_manager_agent import DocumentManagerAgent
from .pdf_assistant_agent import PDFAssistantAgent

# === Sistema ===
from .system_supervisor import SystemSupervisor
from .task_router import TaskRouter
from .memory_manager import MemoryManager

__all__ = [
    # Core
    "LangGraphAgent",
    "AgentState",

    # Administrativo
    "HRAgent",
    "FinanceAgent",
    "PayrollAgent",
    "BenefitsAgent",
    "RecruitmentAgent",

    # Dirección
    "CEOAssistant",
    "CFOAssistant",
    "CMOAssistant",

    # Comercial
    "ComprasAgent",
    "VentasAgent",
    "CRMAgent",
    "CustomerServiceAgent",

    # Documentación
    "DocumentManagerAgent",
    "PDFAssistantAgent",

    # Sistema
    "SystemSupervisor",
    "TaskRouter",
    "MemoryManager",
]
