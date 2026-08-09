"""Agent Orchestrator - Intent detection y routing inteligente

Espeja la lógica del Rust plugin_orchestrator para hacer routing automático
de queries a los agentes/plugins especializados.
"""

import logging
from enum import Enum
from typing import Tuple
import re

logger = logging.getLogger(__name__)


class Intent(Enum):
    """Tipos de intent detectables"""
    DOCUMENT_GENERATION = "document_generation"
    PAYROLL_ANALYSIS = "payroll_analysis"
    BENEFITS_MANAGEMENT = "benefits_management"
    RECRUITMENT = "recruitment"
    GENERAL_QUERY = "general_query"


class AgentOrchestrator:
    """Orquestador de agentes - routing automático por intent"""

    def __init__(self):
        """Inicializar orchestrator"""
        self.intent_keywords = {
            Intent.DOCUMENT_GENERATION: [
                "contrat", "oferta", "generar", "crear", "documento",
                "acuerdo", "carta", "policy", "política", "código conducta",
                "confidencialidad", "nda", "documento legal"
            ],
            Intent.PAYROLL_ANALYSIS: [
                "salario", "nómina", "sueldo", "payroll", "desglosa",
                "análisis", "promedio", "departamento", "equity",
                "comparación", "distribución", "cálculo"
            ],
            Intent.BENEFITS_MANAGEMENT: [
                "cesantía", "prima", "vacacion", "benefici", "prestación",
                "eps", "afiliación", "seguro", "pensión", "proveedor",
                "salud", "cálculo de beneficio", "deducción"
            ],
            Intent.RECRUITMENT: [
                "candidat", "oferta empleo", "job", "posición", "puesto",
                "experiencia", "skill", "screening", "onboarding",
                "entrevista", "hiring", "reclutamient", "selection"
            ],
        }

    def detect_intent(self, query: str) -> Intent:
        """Detectar intent de una query automáticamente

        Análisis de keywords en español e inglés.

        Args:
            query: Query del usuario

        Returns:
            Intent detectado
        """
        query_lower = query.lower()

        # Scoring por intent
        scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(
                len(re.findall(rf'\b{kw}\w*', query_lower))
                for kw in keywords
            )
            scores[intent] = score

        # Retornar intent con mayor score, sino GENERAL
        max_intent = max(scores.items(), key=lambda x: x[1])
        if max_intent[1] > 0:
            logger.info(f"Intent detected: {max_intent[0].value} (score: {max_intent[1]})")
            return max_intent[0]

        return Intent.GENERAL_QUERY

    def route_to_agent(self, intent: Intent) -> str:
        """Mapear intent a agent/plugin

        Args:
            intent: Intent detectado

        Returns:
            agent_id para usar
        """
        routing_map = {
            Intent.DOCUMENT_GENERATION: "hr_agent",
            Intent.PAYROLL_ANALYSIS: "payroll_plugin",
            Intent.BENEFITS_MANAGEMENT: "benefits_plugin",
            Intent.RECRUITMENT: "recruitment_plugin",
            Intent.GENERAL_QUERY: "asistente",
        }

        agent_id = routing_map.get(intent, "hr_agent")
        logger.info(f"Routing to: {agent_id}")
        return agent_id

    def process_query(self, query: str) -> Tuple[str, Intent]:
        """Procesar query: detectar intent y retornar agent_id

        Args:
            query: Query del usuario

        Returns:
            Tupla (agent_id, intent)
        """
        intent = self.detect_intent(query)
        agent_id = self.route_to_agent(intent)
        return agent_id, intent


# Singleton global
_orchestrator = None


def get_orchestrator() -> AgentOrchestrator:
    """Obtener instancia global del orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
