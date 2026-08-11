"""Orquestador de Flujos de Trabajo - Encadena múltiples agentes automáticamente"""

import logging
from typing import Dict, List, Any, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Estados de un flujo de trabajo"""
    PENDING = "⏳ Pendiente"
    RUNNING = "▶️ Ejecutando"
    COMPLETED = "✅ Completado"
    FAILED = "❌ Fallido"
    PAUSED = "⏸️ Pausado"


class WorkflowStep:
    """Un paso en el flujo de trabajo"""

    def __init__(
        self,
        step_id: str,
        agent_id: str,
        agent_name: str,
        description: str,
        executor: Callable,
        input_mapping: Dict[str, str] = None
    ):
        self.step_id = step_id
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.description = description
        self.executor = executor
        self.input_mapping = input_mapping or {}
        self.status = WorkflowStatus.PENDING
        self.result = None
        self.error = None
        self.timestamp_start = None
        self.timestamp_end = None

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta el paso"""
        try:
            self.status = WorkflowStatus.RUNNING
            self.timestamp_start = datetime.now()

            # Mapear inputs del contexto
            inputs = {}
            for param, source in self.input_mapping.items():
                if source in context:
                    inputs[param] = context[source]
                else:
                    logger.warning(f"⚠️ Input {source} no encontrado en contexto")

            # Ejecutar agente
            logger.info(f"▶️ Ejecutando paso: {self.step_id} ({self.agent_name})")
            result = await self.executor(**inputs) if inputs else await self.executor()

            self.result = result
            self.status = WorkflowStatus.COMPLETED
            self.timestamp_end = datetime.now()

            logger.info(f"✅ Paso completado: {self.step_id}")
            return result

        except Exception as e:
            logger.error(f"❌ Error en paso {self.step_id}: {e}")
            self.status = WorkflowStatus.FAILED
            self.error = str(e)
            self.timestamp_end = datetime.now()
            raise

    def to_dict(self) -> Dict[str, Any]:
        duration = None
        if self.timestamp_start and self.timestamp_end:
            duration = (self.timestamp_end - self.timestamp_start).total_seconds()

        return {
            "step_id": self.step_id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "description": self.description,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "duration_seconds": duration
        }


class Workflow:
    """Define un flujo de trabajo con múltiples pasos"""

    def __init__(self, workflow_id: str, name: str, description: str):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.steps: List[WorkflowStep] = []
        self.status = WorkflowStatus.PENDING
        self.context: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.completed_at = None

    def add_step(self, step: WorkflowStep) -> "Workflow":
        """Agrega un paso al flujo"""
        self.steps.append(step)
        return self

    async def execute(self) -> Dict[str, Any]:
        """Ejecuta todos los pasos del flujo"""
        try:
            self.status = WorkflowStatus.RUNNING
            logger.info(f"🚀 Iniciando flujo de trabajo: {self.name}")

            for step in self.steps:
                try:
                    # Ejecutar paso
                    result = await step.execute(self.context)

                    # Almacenar resultado en contexto para próximos pasos
                    self.context[f"step_{step.step_id}"] = result
                    self.context[f"agent_{step.agent_id}"] = result

                except Exception as e:
                    logger.error(f"❌ Flujo fallido en paso {step.step_id}: {e}")
                    self.status = WorkflowStatus.FAILED
                    raise

            self.status = WorkflowStatus.COMPLETED
            self.completed_at = datetime.now()
            logger.info(f"✅ Flujo completado: {self.name}")

            return self.get_summary()

        except Exception as e:
            logger.error(f"❌ Error ejecutando flujo: {e}")
            self.status = WorkflowStatus.FAILED
            raise

    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumen del flujo"""
        duration = None
        if self.completed_at:
            duration = (self.completed_at - self.created_at).total_seconds()

        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "status": self.status.value,
            "steps": [step.to_dict() for step in self.steps],
            "context": self.context,
            "duration_seconds": duration,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class WorkflowTemplates:
    """Plantillas predefinidas de flujos de trabajo"""

    @staticmethod
    def presupuesto_workflow() -> Dict[str, Any]:
        """Flujo: Solicitud de Presupuesto
        1. CEO solicita presupuesto
        2. CFO analiza factibilidad
        3. Finance calcula números
        4. Document Manager genera documento
        """
        return {
            "id": "presupuesto",
            "name": "Solicitud de Presupuesto",
            "description": "Procesa solicitud de presupuesto con análisis ejecutivo",
            "steps": [
                {
                    "id": "ceo_review",
                    "agent": "ceo_assistant",
                    "description": "CEO revisa necesidad estratégica"
                },
                {
                    "id": "cfo_analysis",
                    "agent": "cfo_assistant",
                    "description": "CFO analiza factibilidad financiera"
                },
                {
                    "id": "finance_calc",
                    "agent": "finance_agent",
                    "description": "Finance calcula detalles presupuestales"
                },
                {
                    "id": "doc_generation",
                    "agent": "document_manager",
                    "description": "Document Manager genera documento final"
                }
            ]
        }

    @staticmethod
    def analisis_venta_workflow() -> Dict[str, Any]:
        """Flujo: Análisis de Venta
        1. CMO analiza oportunidad de mercado
        2. Finance proyecta ingresos
        3. CFO valida viabilidad
        """
        return {
            "id": "venta",
            "name": "Análisis de Venta",
            "description": "Análisis completo de oportunidad de venta",
            "steps": [
                {
                    "id": "cmo_market",
                    "agent": "cmo_assistant",
                    "description": "CMO analiza mercado objetivo"
                },
                {
                    "id": "finance_projection",
                    "agent": "finance_agent",
                    "description": "Finance proyecta ingresos"
                },
                {
                    "id": "cfo_validation",
                    "agent": "cfo_assistant",
                    "description": "CFO valida viabilidad financiera"
                }
            ]
        }

    @staticmethod
    def alerta_critica_workflow() -> Dict[str, Any]:
        """Flujo: Respuesta a Alerta Crítica
        1. Detectar alerta (cartera vencida, etc)
        2. CEO analiza impacto
        3. CFO propone acciones
        4. Documentar decisión
        """
        return {
            "id": "alerta",
            "name": "Respuesta a Alerta Crítica",
            "description": "Respuesta estructurada a alertas del sistema",
            "steps": [
                {
                    "id": "ceo_impact",
                    "agent": "ceo_assistant",
                    "description": "CEO analiza impacto estratégico"
                },
                {
                    "id": "cfo_action",
                    "agent": "cfo_assistant",
                    "description": "CFO propone plan de acción"
                },
                {
                    "id": "doc_save",
                    "agent": "document_manager",
                    "description": "Documentar decisión"
                }
            ]
        }
