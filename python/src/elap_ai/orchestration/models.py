"""Modelos para orchestration."""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
from datetime import datetime


class TaskStatus(str, Enum):
    """Estados de una tarea."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(str, Enum):
    """Prioridad de tarea."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Task:
    """Tarea para ejecutar."""

    id: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    required_role: Optional[str] = None
    input_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.now)
    assigned_agent_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING


@dataclass
class TaskResult:
    """Resultado de ejecución de tarea."""

    task_id: str
    agent_id: str
    status: TaskStatus
    output: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    completed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convertir a diccionario."""
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
        }


@dataclass
class AgentPool:
    """Pool de agentes disponibles."""

    agents: dict[str, Any] = field(default_factory=dict)
    busy_agents: set[str] = field(default_factory=set)

    def add_agent(self, agent_id: str, agent: Any) -> None:
        """Agregar agente al pool."""
        self.agents[agent_id] = agent

    def remove_agent(self, agent_id: str) -> None:
        """Remover agente del pool."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.busy_agents.discard(agent_id)

    def mark_busy(self, agent_id: str) -> None:
        """Marcar agente como ocupado."""
        if agent_id in self.agents:
            self.busy_agents.add(agent_id)

    def mark_free(self, agent_id: str) -> None:
        """Marcar agente como libre."""
        self.busy_agents.discard(agent_id)

    def get_available_agents(self) -> list[str]:
        """Obtener agentes disponibles."""
        return [aid for aid in self.agents if aid not in self.busy_agents]

    def get_agent(self, agent_id: str) -> Any:
        """Obtener agente por ID."""
        return self.agents.get(agent_id)

    def get_stats(self) -> dict[str, Any]:
        """Obtener estadísticas del pool."""
        return {
            "total_agents": len(self.agents),
            "busy_agents": len(self.busy_agents),
            "available_agents": len(self.get_available_agents()),
        }
