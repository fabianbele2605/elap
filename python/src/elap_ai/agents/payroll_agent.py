"""Payroll Agent - Especializado en análisis salarial y nómina

Procesa queries relacionadas con salarios, nómina, análisis de equity,
beneficios salariales, etc.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PayrollAgent:
    """Agente especializado en análisis de nómina y salarios"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        logger.info(f"PayrollAgent initialized with theme: {theme}")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de nómina

        Args:
            query: Consulta del usuario

        Returns:
            Dict con respuesta y metadata
        """
        logger.info(f"Processing payroll query: {query[:50]}...")

        response = await self._generate_payroll_response(query)

        return {
            "message": response,
            "intent": "payroll_analysis",
            "agent": "payroll_agent",
        }

    async def _generate_payroll_response(self, query: str) -> str:
        """Generar respuesta especializada en nómina"""

        query_lower = query.lower()

        # Detección simple para diferentes tipos de queries
        if "promedio" in query_lower or "average" in query_lower:
            return self._salaries_by_department(query)
        elif "equity" in query_lower or "equidad" in query_lower:
            return self._salary_equity_analysis(query)
        elif "distribución" in query_lower:
            return self._salary_distribution(query)
        else:
            return await self._generic_payroll_response(query)

    def _salaries_by_department(self, query: str) -> str:
        """Análisis de salarios por departamento"""
        return """📊 ANÁLISIS DE SALARIOS POR DEPARTAMENTO

Departamento: Operaciones y Logística
Salario Promedio: $3,500,000
  • Mínimo: $2,800,000
  • Máximo: $4,200,000
  • Empleados: 45

Desglose:
- Gerente Operaciones: $4,200,000
- Coordinadores: $3,800,000
- Auxiliares: $2,800,000

Análisis:
- Rango salarial: $1,400,000 (50% variación)
- Desviación estándar: $385,000
- Percentil 75: $3,900,000

Comparación con otras áreas:
- Comercial: $3,800,000 (+8.6%)
- Administración: $3,200,000 (-8.6%)
- IT: $4,100,000 (+17.1%)

Recomendación: Estructura salarial equilibrada dentro del mercado regional."""

    def _salary_equity_analysis(self, query: str) -> str:
        """Análisis de equidad salarial"""
        return """📈 ANÁLISIS DE EQUIDAD SALARIAL

Distribución Actual por Departamento:
- Comercial: $3,800,000 promedio (48 empleados)
- Operaciones: $3,500,000 promedio (45 empleados)
- Administración: $3,200,000 promedio (34 empleados)
- IT: $4,100,000 promedio (28 empleados)
- RRHH: $3,400,000 promedio (12 empleados)

Índice de Equidad:
- Ratio máximo/mínimo: 1.28 (dentro de rango aceptable 1.3)
- Coeficiente de Gini: 0.22 (buena distribución)
- Dispersión: Baja a media

Hallazgos:
✓ Distribución equitativa entre niveles
✓ Premios por especialización (IT +17%)
✓ Consistencia con mercado regional

Recomendación: Mantener estructura actual con revisión anual."""

    def _salary_distribution(self, query: str) -> str:
        """Distribución de salarios"""
        return """💰 DISTRIBUCIÓN DE SALARIOS - ANDINA FOODS

Total Empleados: 187

Rangos Salariales:
$2M - $2.5M:  12 empleados (6.4%) - Auxiliares
$2.5M - $3M:  34 empleados (18.2%) - Coordinadores
$3M - $3.5M:  56 empleados (29.9%) - Especialistas
$3.5M - $4M:  52 empleados (27.8%) - Supervisores
$4M - $4.5M:  23 empleados (12.3%) - Gerentes
$4.5M +:       10 empleados (5.3%) - Directivos

Estadísticas:
- Salario Promedio: $3,450,000
- Salario Mediano: $3,380,000
- Desviación: $485,000
- Rango: $2,000,000 - $5,200,000

Distribución Normal: ✓ Levemente concentrada en media"""

    async def _generic_payroll_response(self, query: str) -> str:
        """Respuesta genérica para queries de nómina - usa Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("payroll_agent")

            prompt_ollama = f"""{system_prompt}

Pregunta del usuario: {query}

Responde de manera técnica, precisa y con ejemplos de cálculos cuando sea posible."""

            logger.info("💼 Llamando a Ollama para respuesta general de Payroll...")
            respuesta = await ollama.generar("glm4:9b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en Payroll: {e}")
            return """💼 ASISTENTE DE NÓMINA - ANDINA FOODS

Puedo ayudarte con:
📊 Análisis de salarios por departamento, equity salarial
💰 Cálculos de nómina, deducciones, provisiones
📈 Reportes de nómina, análisis comparativo, proyecciones

¿Qué información necesitas sobre nómina?"""
