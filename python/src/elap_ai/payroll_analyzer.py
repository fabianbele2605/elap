"""PayrollAnalyzer - Análisis avanzado de nómina con Ollama

Analiza datos de nómina, calcula impuestos y beneficios,
y genera insights sobre estructura salarial de la empresa.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json

from elap_ai.ollama_client import OllamaClient
from elap_ai.errors import ElapException

logger = logging.getLogger(__name__)


@dataclass
class SalaryData:
    """Datos de un empleado en nómina"""
    employee_id: str
    name: str
    department: str
    position: str
    gross_salary: float
    hire_date: str


class PayrollAnalyzer:
    """Analizador avanzado de nómina

    Capacidades:
    - Análisis de salarios por departamento
    - Cálculos de impuestos y beneficios
    - Proyecciones de costos
    - Análisis de equidad salarial
    - Generación de reportes
    """

    def __init__(self, theme: str = "andina_foods", model: str = "glm4:9b"):
        """Inicializar analizador

        Args:
            theme: Tema corporativo (para contexto)
            model: Modelo Ollama a usar
        """
        self.theme = theme
        self.model = model
        self.ollama = OllamaClient()
        logger.info(f"PayrollAnalyzer inicializado con modelo: {model}")

    async def analyze_salary_distribution(
        self,
        employees: List[SalaryData]
    ) -> Dict[str, Any]:
        """Analizar distribución de salarios

        Args:
            employees: Lista de empleados con datos salariales

        Returns:
            Dict con análisis completo
        """
        if not employees:
            raise ElapException("No hay empleados para analizar")

        # Agrupar por departamento
        by_department = {}
        for emp in employees:
            if emp.department not in by_department:
                by_department[emp.department] = []
            by_department[emp.department].append(emp.gross_salary)

        # Calcular estadísticas
        analysis = {
            "total_employees": len(employees),
            "total_payroll": sum(e.gross_salary for e in employees),
            "average_salary": sum(e.gross_salary for e in employees) / len(employees),
            "by_department": {}
        }

        for dept, salaries in by_department.items():
            analysis["by_department"][dept] = {
                "count": len(salaries),
                "total": sum(salaries),
                "average": sum(salaries) / len(salaries),
                "min": min(salaries),
                "max": max(salaries),
                "range": max(salaries) - min(salaries)
            }

        logger.info(f"Análisis salarial completado: {len(employees)} empleados")
        return analysis

    async def calculate_benefits(
        self,
        gross_salary: float
    ) -> Dict[str, float]:
        """Calcular beneficios y deducciones (normativa colombiana)

        Args:
            gross_salary: Salario bruto

        Returns:
            Dict con detalles de beneficios
        """
        # Constantes según normativa colombiana 2026
        TRANSPORT_ALLOWANCE = 117_346.0
        HEALTH_RATE = 0.04  # 4% empleado
        PENSION_RATE = 0.04  # 4% empleado
        EMPLOYER_HEALTH = 0.085  # 8.5%
        EMPLOYER_PENSION = 0.12  # 12%
        SEVERANCE_RATE = 0.0833  # 8.33% mensual
        BONUS_RATE = 0.0833  # 8.33% mensual
        VACATION_RATE = 0.0417  # 4.17% mensual

        deductions = {
            "gross_salary": gross_salary,
            "transport_allowance": TRANSPORT_ALLOWANCE,
            "health_deduction": gross_salary * HEALTH_RATE,
            "pension_deduction": gross_salary * PENSION_RATE,
            "total_deductions": gross_salary * (HEALTH_RATE + PENSION_RATE),
            "net_salary": gross_salary + TRANSPORT_ALLOWANCE - (gross_salary * (HEALTH_RATE + PENSION_RATE)),
            "employer_contributions": {
                "health": gross_salary * EMPLOYER_HEALTH,
                "pension": gross_salary * EMPLOYER_PENSION,
                "severance": gross_salary * SEVERANCE_RATE,
                "bonus": gross_salary * BONUS_RATE,
                "vacation": gross_salary * VACATION_RATE,
                "total": gross_salary * (EMPLOYER_HEALTH + EMPLOYER_PENSION + SEVERANCE_RATE + BONUS_RATE + VACATION_RATE)
            }
        }

        return deductions

    async def analyze_salary_equity(
        self,
        employees: List[SalaryData]
    ) -> Dict[str, Any]:
        """Analizar equidad salarial entre departamentos

        Args:
            employees: Lista de empleados

        Returns:
            Dict con análisis de equidad
        """
        if not employees:
            raise ElapException("No hay empleados para analizar")

        # Agrupar por departamento y posición
        by_dept_pos = {}
        for emp in employees:
            key = f"{emp.department}:{emp.position}"
            if key not in by_dept_pos:
                by_dept_pos[key] = []
            by_dept_pos[key].append(emp.gross_salary)

        # Calcular varianza por grupo
        equity = {
            "total_employees": len(employees),
            "groups": {}
        }

        for group, salaries in by_dept_pos.items():
            avg = sum(salaries) / len(salaries)
            variance = sum((s - avg) ** 2 for s in salaries) / len(salaries)
            std_dev = variance ** 0.5

            equity["groups"][group] = {
                "count": len(salaries),
                "average": avg,
                "std_deviation": std_dev,
                "range": max(salaries) - min(salaries),
                "equity_score": 1.0 - (std_dev / avg) if avg > 0 else 0.0
            }

        logger.info("Análisis de equidad salarial completado")
        return equity

    async def generate_salary_insights(
        self,
        analysis: Dict[str, Any]
    ) -> str:
        """Generar insights con Ollama

        Args:
            analysis: Análisis previo de nómina

        Returns:
            Insights en formato texto
        """
        prompt = f"""Analiza la siguiente estructura salarial de la empresa Andina Foods
        y proporciona insights ejecutivos en máximo 3 párrafos.

Datos:
- Total empleados: {analysis.get('total_employees', 0)}
- Nómina total: ${analysis.get('total_payroll', 0):,.0f}
- Salario promedio: ${analysis.get('average_salary', 0):,.0f}

Por departamento:
{json.dumps(analysis.get('by_department', {}), indent=2, ensure_ascii=False)}

Proporciona:
1. Resumen de la estructura salarial
2. Áreas de atención (si las hay)
3. Recomendaciones ejecutivas

Sé conciso y profesional."""

        try:
            insights = await self.ollama.generar(self.model, prompt)
            logger.info("Insights generados por Ollama")
            return insights
        except Exception as e:
            logger.error(f"Error generando insights: {e}")
            raise ElapException(f"No se pudo generar análisis: {str(e)}")

    async def process_payroll_query(
        self,
        query: str,
        employees: List[SalaryData]
    ) -> str:
        """Procesar consulta sobre nómina

        Args:
            query: Pregunta del usuario
            employees: Datos de empleados

        Returns:
            Respuesta analizada por Ollama
        """
        # Análisis previo
        analysis = await self.analyze_salary_distribution(employees)

        # Preparar prompt para Ollama
        prompt = f"""Como analista de nómina de Andina Foods, responde esta pregunta:

Pregunta: {query}

Contexto de la nómina:
- Total empleados: {analysis['total_employees']}
- Nómina total: ${analysis['total_payroll']:,.0f}
- Salario promedio: ${analysis['average_salary']:,.0f}

Distribución por departamento:
{json.dumps(analysis['by_department'], indent=2, ensure_ascii=False)}

Responde de forma clara, concisa y basada en los datos.
Sin markdown, solo texto plano profesional."""

        try:
            response = await self.ollama.generar(self.model, prompt)
            logger.info(f"Consulta procesada: {query[:50]}...")
            return response
        except Exception as e:
            logger.error(f"Error procesando consulta: {e}")
            raise ElapException(f"No se pudo responder: {str(e)}")

    async def forecast_payroll_growth(
        self,
        current_payroll: float,
        growth_rate: float,
        employees_to_hire: int,
        avg_new_salary: float
    ) -> Dict[str, Any]:
        """Proyectar crecimiento de nómina

        Args:
            current_payroll: Nómina actual
            growth_rate: Tasa de crecimiento esperado (ej: 0.05 = 5%)
            employees_to_hire: Empleados nuevos a contratar
            avg_new_salary: Salario promedio de nuevos empleados

        Returns:
            Proyecciones
        """
        new_payroll = current_payroll * (1 + growth_rate)
        added_payroll = employees_to_hire * avg_new_salary
        total_projected = new_payroll + added_payroll

        return {
            "current_payroll": current_payroll,
            "growth_rate": growth_rate,
            "projected_payroll": new_payroll,
            "employees_to_hire": employees_to_hire,
            "new_payroll": added_payroll,
            "total_projected": total_projected,
            "increase_percentage": ((total_projected - current_payroll) / current_payroll) * 100
        }


if __name__ == "__main__":
    import asyncio

    async def test():
        analyzer = PayrollAnalyzer()

        # Test: crear datos de prueba
        employees = [
            SalaryData(
                employee_id="EMP001",
                name="Juan Pérez",
                department="Ventas",
                position="Gerente",
                gross_salary=3_000_000.0,
                hire_date="2020-01-15"
            ),
            SalaryData(
                employee_id="EMP002",
                name="María García",
                department="Operaciones",
                position="Coordinadora",
                gross_salary=2_500_000.0,
                hire_date="2021-06-20"
            ),
        ]

        # Test: análisis
        analysis = await analyzer.analyze_salary_distribution(employees)
        print("✅ Análisis salarial:")
        print(json.dumps(analysis, indent=2, ensure_ascii=False))

        # Test: beneficios
        benefits = await analyzer.calculate_benefits(3_000_000.0)
        print("\n✅ Beneficios calculados:")
        print(json.dumps(benefits, indent=2, ensure_ascii=False))

        print("\n✅ PayrollAnalyzer funcional")

    asyncio.run(test())
