"""Multi-agent Orchestrator."""

import asyncio
from typing import Any, Optional, Callable
from collections import defaultdict

from elap_ai.orchestration.models import Task, TaskResult, TaskStatus, TaskPriority, AgentPool


class AgentOrchestrator:
    """Orquesta múltiples agentes para ejecutar tareas."""

    def __init__(self, max_concurrent_tasks: int = 10) -> None:
        """Inicializar orchestrator.

        Args:
            max_concurrent_tasks: Máximo de tareas concurrentes
        """
        self.pool = AgentPool()
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_queue: list[Task] = []
        self.results: dict[str, TaskResult] = {}
        self.task_history: list[TaskResult] = []

    def register_agent(self, agent_id: str, agent: Any) -> None:
        """Registrar un agente."""
        self.pool.add_agent(agent_id, agent)

    def unregister_agent(self, agent_id: str) -> None:
        """Desregistrar un agente."""
        self.pool.remove_agent(agent_id)

    def submit_task(self, task: Task) -> None:
        """Enviar una tarea para ejecución."""
        self.task_queue.append(task)
        # Ordenar por prioridad
        self.task_queue.sort(key=lambda t: self._priority_value(t.priority), reverse=True)

    async def execute_tasks(self) -> dict[str, TaskResult]:
        """Ejecutar todas las tareas encoladas."""
        results = {}
        available_agents = self.pool.get_available_agents()

        # Ejecutar tareas con agentes disponibles
        tasks_to_run = self.task_queue[: min(len(available_agents), self.max_concurrent_tasks)]

        for i, task in enumerate(tasks_to_run):
            if i < len(available_agents):
                agent_id = available_agents[i]
                self.pool.mark_busy(agent_id)
                result = await self._execute_task(agent_id, task)
                results[task.id] = result
                self.results[task.id] = result
                self.task_history.append(result)
                self.pool.mark_free(agent_id)

        # Limpiar tareas ejecutadas
        self.task_queue = self.task_queue[len(tasks_to_run):]

        return results

    async def _execute_task(self, agent_id: str, task: Task) -> TaskResult:
        """Ejecutar una tarea con un agente."""
        task.status = TaskStatus.RUNNING
        task.assigned_agent_id = agent_id

        try:
            import time
            start_time = time.time()

            # Simular ejecución (en producción, llamaría el método del agente)
            output = await self._simulate_execution(task)

            end_time = time.time()

            return TaskResult(
                task_id=task.id,
                agent_id=agent_id,
                status=TaskStatus.COMPLETED,
                output=output,
                execution_time=end_time - start_time,
            )
        except Exception as e:
            return TaskResult(
                task_id=task.id,
                agent_id=agent_id,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    def _get_best_task(self, agent_id: str) -> Optional[Task]:
        """Obtener mejor tarea para un agente."""
        agent = self.pool.get_agent(agent_id)
        if not agent:
            return None

        # Filtrar por rol si es necesario
        for task in self.task_queue:
            if task.required_role is None or task.required_role == agent_id:
                self.task_queue.remove(task)
                return task

        return None

    @staticmethod
    async def _simulate_execution(task: Task) -> dict[str, Any]:
        """Simular ejecución de tarea."""
        await asyncio.sleep(0.1)  # Simular trabajo
        return {
            "task_id": task.id,
            "description": f"Completed: {task.description}",
            "input_processed": task.input_data,
        }

    @staticmethod
    def _priority_value(priority: TaskPriority) -> int:
        """Convertir prioridad a valor numérico."""
        values = {
            TaskPriority.CRITICAL: 4,
            TaskPriority.HIGH: 3,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 1,
        }
        return values.get(priority, 0)

    def get_statistics(self) -> dict[str, Any]:
        """Obtener estadísticas."""
        completed = sum(1 for r in self.task_history if r.status == TaskStatus.COMPLETED)
        failed = sum(1 for r in self.task_history if r.status == TaskStatus.FAILED)
        avg_time = sum(r.execution_time for r in self.task_history) / len(self.task_history) if self.task_history else 0

        return {
            "pool_stats": self.pool.get_stats(),
            "pending_tasks": len(self.task_queue),
            "completed_tasks": completed,
            "failed_tasks": failed,
            "total_tasks": len(self.task_history),
            "average_execution_time": avg_time,
        }

    def clear_history(self) -> None:
        """Limpiar historial de tareas."""
        self.task_history.clear()
        self.results.clear()
