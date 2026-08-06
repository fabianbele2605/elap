"""Tests para Multi-agent Orchestrator."""

import pytest
from elap_ai.orchestration.orchestrator import AgentOrchestrator
from elap_ai.orchestration.models import Task, TaskStatus, TaskPriority, AgentPool


@pytest.fixture
def orchestrator() -> AgentOrchestrator:
    """Crear orchestrator para tests."""
    return AgentOrchestrator(max_concurrent_tasks=5)


@pytest.fixture
def agent_pool() -> AgentPool:
    """Crear pool de agentes."""
    pool = AgentPool()
    pool.add_agent("agent_1", {"name": "Agent 1", "role": "processor"})
    pool.add_agent("agent_2", {"name": "Agent 2", "role": "analyzer"})
    pool.add_agent("agent_3", {"name": "Agent 3", "role": "validator"})
    return pool


def test_task_creation() -> None:
    """Test crear una tarea."""
    task = Task(
        id="task_1",
        description="Process data",
        priority=TaskPriority.HIGH,
    )

    assert task.id == "task_1"
    assert task.status == TaskStatus.PENDING
    assert task.priority == TaskPriority.HIGH


def test_agent_pool_add_agent(agent_pool: AgentPool) -> None:
    """Test agregar agente al pool."""
    agent_pool.add_agent("agent_4", {"name": "Agent 4"})

    assert len(agent_pool.agents) == 4
    assert agent_pool.get_agent("agent_4") is not None


def test_agent_pool_remove_agent(agent_pool: AgentPool) -> None:
    """Test remover agente del pool."""
    agent_pool.remove_agent("agent_1")

    assert len(agent_pool.agents) == 2
    assert agent_pool.get_agent("agent_1") is None


def test_agent_pool_busy_management(agent_pool: AgentPool) -> None:
    """Test marcar agentes como busy/free."""
    assert "agent_1" in agent_pool.get_available_agents()

    agent_pool.mark_busy("agent_1")
    assert "agent_1" not in agent_pool.get_available_agents()

    agent_pool.mark_free("agent_1")
    assert "agent_1" in agent_pool.get_available_agents()


def test_agent_pool_statistics(agent_pool: AgentPool) -> None:
    """Test estadísticas del pool."""
    agent_pool.mark_busy("agent_1")
    agent_pool.mark_busy("agent_2")

    stats = agent_pool.get_stats()

    assert stats["total_agents"] == 3
    assert stats["busy_agents"] == 2
    assert stats["available_agents"] == 1


def test_orchestrator_register_agent(orchestrator: AgentOrchestrator) -> None:
    """Test registrar agente."""
    orchestrator.register_agent("agent_1", {"name": "Agent 1"})

    assert orchestrator.pool.get_agent("agent_1") is not None


def test_orchestrator_submit_task(orchestrator: AgentOrchestrator) -> None:
    """Test enviar tarea."""
    task = Task(id="task_1", description="Test task")

    orchestrator.submit_task(task)

    assert len(orchestrator.task_queue) == 1
    assert orchestrator.task_queue[0].id == "task_1"


def test_orchestrator_task_priority_ordering(orchestrator: AgentOrchestrator) -> None:
    """Test ordenamiento de tareas por prioridad."""
    task_low = Task(id="task_1", description="Low", priority=TaskPriority.LOW)
    task_high = Task(id="task_2", description="High", priority=TaskPriority.HIGH)
    task_medium = Task(id="task_3", description="Medium", priority=TaskPriority.MEDIUM)

    orchestrator.submit_task(task_low)
    orchestrator.submit_task(task_high)
    orchestrator.submit_task(task_medium)

    # Debe estar ordenado por prioridad
    assert orchestrator.task_queue[0].priority == TaskPriority.HIGH
    assert orchestrator.task_queue[1].priority == TaskPriority.MEDIUM
    assert orchestrator.task_queue[2].priority == TaskPriority.LOW


@pytest.mark.asyncio
async def test_orchestrator_execute_tasks(orchestrator: AgentOrchestrator) -> None:
    """Test ejecutar tareas."""
    orchestrator.register_agent("agent_1", {})
    orchestrator.register_agent("agent_2", {})

    task1 = Task(id="task_1", description="Task 1")
    task2 = Task(id="task_2", description="Task 2")

    orchestrator.submit_task(task1)
    orchestrator.submit_task(task2)

    results = await orchestrator.execute_tasks()

    assert len(results) == 2
    assert all(r.status == TaskStatus.COMPLETED for r in results.values())


def test_orchestrator_statistics(orchestrator: AgentOrchestrator) -> None:
    """Test obtener estadísticas."""
    orchestrator.register_agent("agent_1", {})

    task = Task(id="task_1", description="Task")
    orchestrator.submit_task(task)

    stats = orchestrator.get_statistics()

    assert "pool_stats" in stats
    assert "pending_tasks" in stats
    assert stats["pending_tasks"] == 1


def test_orchestrator_clear_history(orchestrator: AgentOrchestrator) -> None:
    """Test limpiar historial."""
    from elap_ai.orchestration.models import TaskResult

    result = TaskResult(
        task_id="task_1",
        agent_id="agent_1",
        status=TaskStatus.COMPLETED,
    )

    orchestrator.task_history.append(result)
    assert len(orchestrator.task_history) == 1

    orchestrator.clear_history()
    assert len(orchestrator.task_history) == 0
