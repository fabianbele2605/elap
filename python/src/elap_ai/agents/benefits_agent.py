"""Benefits Agent - Especializado en cálculo de prestaciones

Procesa queries sobre cesantías, prima, vacaciones, beneficios,
proveedores de salud, etc.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BenefitsAgent:
    """Agente especializado en prestaciones sociales y beneficios"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        self.smlmv_2026 = 1_613_000  # Salario mínimo 2026 Colombia
        logger.info(f"BenefitsAgent initialized with theme: {theme}")

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de beneficios

        Args:
            query: Consulta del usuario

        Returns:
            Dict con respuesta y metadata
        """
        logger.info(f"Processing benefits query: {query[:50]}...")

        response = await self._generate_benefits_response(query)

        return {
            "message": response,
            "intent": "benefits_management",
            "agent": "benefits_agent",
        }

    async def _generate_benefits_response(self, query: str) -> str:
        """Generar respuesta especializada en beneficios"""

        query_lower = query.lower()

        # Extrae números del query para cálculos
        meses = self._extract_months(query)
        salario = self._extract_salary(query)

        if ("cesantía" in query_lower or "severance" in query_lower) and meses and salario:
            return self._calculate_severance(salario, meses, query)
        elif ("prima" in query_lower or "bonus" in query_lower) and meses and salario:
            return self._calculate_bonus(salario, meses, query)
        elif "vacación" in query_lower or "vacation" in query_lower:
            return self._calculate_vacation(meses, query)
        elif "eps" in query_lower or "health" in query_lower or "proveedor" in query_lower:
            return self._health_providers(query)
        else:
            return await self._generic_benefits_response(query)

    def _extract_months(self, text: str) -> int:
        """Extrae número de meses del texto"""
        import re
        match = re.search(r'(\d+)\s*(?:meses?|months?)', text.lower())
        return int(match.group(1)) if match else None

    def _extract_salary(self, text: str) -> float:
        """Extrae salario del texto"""
        import re
        # Busca patrones como "3 millones", "3000000", "$3M"
        patterns = [
            r'(\d+)\s*millones?',  # 3 millones
            r'\$?\s*(\d+(?:,\d{3})*(?:\.\d+)?)',  # 3,000,000 o $3000000
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                num_str = match.group(1).replace(',', '')
                num = float(num_str)
                if num < 10:
                    num *= 1_000_000  # Asumir que son millones
                return num
        return None

    def _calculate_severance(self, salario: float, meses: int, query: str) -> str:
        """Calcular cesantías (Colombia)"""
        # Cesantías = Salario / 30 * 30 * (Meses / 12)
        cesantias = (salario / 30) * 30 * (meses / 12)

        return f"""🏛️ CÁLCULO DE CESANTÍAS

Datos:
- Salario: ${salario:,.0f}
- Meses trabajados: {meses}
- Período: {meses/12:.1f} años

Fórmula (Ley colombiana):
Cesantías = (Salario / 30) × 30 × (Meses / 12)

Desglose:
1. Salario diario: ${salario/30:,.0f}
2. Salario mensual equivalente: ${salario:,.0f}
3. Factor temporal: {meses}/12 = {meses/12:.4f} años

CESANTÍAS TOTALES: ${cesantias:,.0f}

Notas:
- Monto líquido sin intereses (se pagan al finalizar relación)
- Intereses sobre cesantías: {cesantias * 0.12:,.0f} (12% anual)
- Total con intereses: ${cesantias * 1.12:,.0f}

Regulación: Decreto 2351 de 1965 (Colombia)"""

    def _calculate_bonus(self, salario: float, meses: int, query: str) -> str:
        """Calcular prima de servicios (Colombia)"""
        # Prima = Salario promedio * (Meses trabajados en semestre / 6)
        prima = salario * (meses / 6)

        return f"""🎁 CÁLCULO DE PRIMA DE SERVICIOS

Datos:
- Salario: ${salario:,.0f}
- Meses trabajados: {meses}
- Período: {meses/12:.1f} años

Fórmula (Ley colombiana):
Prima = Salario × (Meses en semestre / 6)

Desglose:
1. Salario base: ${salario:,.0f}
2. Meses completados: {meses}
3. Semestres: {meses/6:.1f}

PRIMA TOTAL: ${prima:,.0f}

Distribución recomendada:
- Prima semestral (Jun): ${salario * (6/6):,.0f}
- Prima semestral (Dic): ${salario * (6/6):,.0f}

Regulación: Artículo 87 Código Sustantivo del Trabajo (Colombia)"""

    def _calculate_vacation(self, meses: int, query: str) -> str:
        """Calcular días de vacaciones (Colombia)"""
        # 15 días por cada año trabajado
        anos = meses / 12
        dias_vaca = int(anos * 15)
        dias_pendientes = ((meses % 12) / 12) * 15

        return f"""🏖️ CÁLCULO DE DÍAS DE VACACIONES

Datos:
- Meses trabajados: {meses}
- Período: {anos:.2f} años

Fórmula (Ley colombiana):
Vacaciones = 15 días por año completo

Desglose:
1. Años completos: {int(anos)} año(s)
2. Días por años completos: {int(anos)} × 15 = {int(anos)*15} días
3. Días por meses restantes: {meses % 12} meses × 1.25 = {dias_pendientes:.1f} días

TOTAL DE VACACIONES: {dias_vaca} días + {dias_pendientes:.1f} días = {dias_vaca + dias_pendientes:.1f} días

Status: {"Vacaciones completas" if dias_vaca >= 15 else "Vacaciones parciales"}

Regulación: Artículos 183-188 Código Sustantivo del Trabajo (Colombia)"""

    def _health_providers(self, query: str) -> str:
        """Información sobre proveedores de salud (EPS)"""
        return """🏥 PROVEEDORES DE SALUD - ANDINA FOODS

Afiliaciones Disponibles:

EPS (Seguro de Salud):
1. SANITAS - Plan Estándar/Premium
2. AXA COLSANITAS - Plan Básico/Plus
3. COOMEVA - Plan Salud/Completo
4. NUEVA EPS - Plan Clásico/Preferencial
5. SURA - Plan Esencial/Máximo

Fondo de Pensión (AFP):
1. PROTECCIÓN - Rentabilidad media
2. PORVENIR - Baja comisión
3. COLFONDOS - Amplia cobertura
4. PROFUTURO - Asesoría personalizada

Deducción Legal (2026):
- EPS: 4% del salario (empleado)
- AFP: 4% del salario (empleado)
- ARL: 0.5% - 3% del salario (empleador)

Cotización Empleador:
- Salud: 8.5% del salario
- Pensión: 12% del salario

Contacto Área de RRHH:
Teléfono: +57 (5) 330-2200 ext. 105
Email: beneficios@andina-foods.com.co"""

    async def _generic_benefits_response(self, query: str) -> str:
        """Respuesta genérica para queries de beneficios - usa Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("benefits_agent")

            prompt_ollama = f"""{system_prompt}

Pregunta del usuario: {query}

Responde de manera clara, con ejemplos y cálculos cuando sea relevante."""

            logger.info("💼 Llamando a Ollama para respuesta general de Benefits...")
            respuesta = await ollama.generar("glm4:9b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en Benefits: {e}")
            return """💼 ASISTENTE DE BENEFICIOS - ANDINA FOODS

Puedo ayudarte con cálculos de prestaciones (cesantías, prima, vacaciones),
información de EPS, análisis de beneficios y reportes.

¿Qué necesitas saber sobre beneficios?"""
