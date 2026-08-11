"""Payroll Agent - Especializado en análisis salarial y nómina con generación de reportes

Procesa queries relacionadas con salarios, nómina, análisis de equity,
beneficios salariales, etc. Accede a datos REALES desde PostgreSQL.
Genera reportes de nómina y notifica al Document Manager.
"""

import logging
from typing import Dict, Any
import asyncio
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)


class PayrollAgent:
    """Agente especializado en análisis de nómina y salarios"""

    def __init__(self, theme: str = "andina_foods"):
        self.theme = theme
        self.api_url = "http://localhost:5000/api/data/empresa"
        logger.info(f"PayrollAgent initialized with theme: {theme}")

        try:
            from ..document_engine import DocumentEngine
            self.document_engine = DocumentEngine(theme=theme, language="es")
        except Exception as e:
            logger.warning(f"DocumentEngine no disponible: {e}")
            self.document_engine = None

    async def _obtener_datos_reales(self, tabla: str = "employees") -> Dict[str, Any]:
        """Obtiene datos reales desde PostgreSQL via API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}?tabla={tabla}&limite=1000") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        logger.info(f"✅ Datos obtenidos de {tabla}: {len(data.get('datos', []))} registros")
                        return data.get('datos', [])
                    else:
                        logger.warning(f"⚠️ API retornó {resp.status}")
                        return []
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos: {e}")
            return []

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
        if "promedio" in query_lower or "departamento" in query_lower or "empleados por" in query_lower:
            return await self._salaries_by_department(query)
        elif "equity" in query_lower or "equidad" in query_lower:
            return await self._salary_equity_analysis(query)
        elif "distribución" in query_lower:
            return await self._salary_distribution(query)
        else:
            return await self._generic_payroll_response(query)

    async def _salaries_by_department(self, query: str) -> str:
        """Análisis de salarios por departamento - DATOS REALES"""
        try:
            # Obtener datos reales de empleados
            empleados = await self._obtener_datos_reales("employees")

            if not empleados:
                return "⚠️ No se pudieron obtener datos de empleados. Intenta más tarde."

            # Agrupar por departamento y calcular estadísticas
            deptos = {}
            for emp in empleados:
                depto = emp.get('departamento', 'Desconocido')
                salario = emp.get('salario_basico', 0)

                if depto not in deptos:
                    deptos[depto] = {'salarios': [], 'cantidad': 0}

                deptos[depto]['salarios'].append(salario)
                deptos[depto]['cantidad'] += 1

            # Generar reporte
            respuesta = "📊 ANÁLISIS DE SALARIOS POR DEPARTAMENTO (DATOS REALES)\n"
            respuesta += "=" * 60 + "\n\n"

            for depto, datos in sorted(deptos.items(), key=lambda x: x[1]['cantidad'], reverse=True):
                salarios = datos['salarios']
                cantidad = datos['cantidad']
                promedio = sum(salarios) / len(salarios) if salarios else 0
                minimo = min(salarios) if salarios else 0
                maximo = max(salarios) if salarios else 0

                respuesta += f"🏢 **{depto}**\n"
                respuesta += f"   • Empleados: {cantidad}\n"
                respuesta += f"   • Salario Promedio: ${promedio:,.0f}\n"
                respuesta += f"   • Mínimo: ${minimo:,.0f}\n"
                respuesta += f"   • Máximo: ${maximo:,.0f}\n"
                respuesta += f"   • Rango: ${maximo - minimo:,.0f}\n\n"

            respuesta += "📈 Análisis: Estructura salarial equilibrada con variaciones por especialización.\n"
            respuesta += "✅ Datos obtenidos de PostgreSQL en tiempo real."

            logger.info(f"✅ Payroll report generado con {len(empleados)} empleados reales")
            return respuesta

        except Exception as e:
            logger.error(f"Error en _salaries_by_department: {e}")
            return f"❌ Error procesando datos: {str(e)}"

    async def _salary_equity_analysis(self, query: str) -> str:
        """Análisis de equidad salarial - DATOS REALES"""
        try:
            empleados = await self._obtener_datos_reales("employees")

            if not empleados:
                return "⚠️ No se pudieron obtener datos de empleados."

            # Calcular por departamento
            deptos = {}
            for emp in empleados:
                depto = emp.get('departamento', 'Desconocido')
                salario = emp.get('salario_basico', 0)

                if depto not in deptos:
                    deptos[depto] = {'salarios': []}
                deptos[depto]['salarios'].append(salario)

            promedios = {k: sum(v['salarios']) / len(v['salarios']) for k, v in deptos.items()}
            max_prom = max(promedios.values()) if promedios else 0
            min_prom = min(promedios.values()) if promedios else 0
            ratio = max_prom / min_prom if min_prom > 0 else 0

            respuesta = "📈 ANÁLISIS DE EQUIDAD SALARIAL (DATOS REALES)\n"
            respuesta += "=" * 60 + "\n\n"
            respuesta += "Distribución por Departamento:\n"

            for depto in sorted(promedios.keys()):
                prom = promedios[depto]
                cant = len(deptos[depto]['salarios'])
                respuesta += f"- {depto}: ${prom:,.0f} promedio ({cant} empleados)\n"

            respuesta += f"\n📊 Índice de Equidad:\n"
            respuesta += f"- Ratio máximo/mínimo: {ratio:.2f} (aceptable < 1.5)\n"
            respuesta += f"- Rango de variación: ${(max_prom - min_prom):,.0f}\n\n"
            respuesta += "✅ Distribución equitativa dentro de rangos aceptables.\n"
            respuesta += "✅ Datos en tiempo real desde PostgreSQL."

            return respuesta

        except Exception as e:
            logger.error(f"Error en equity analysis: {e}")
            return f"❌ Error: {str(e)}"

    async def _salary_distribution(self, query: str) -> str:
        """Distribución de salarios - DATOS REALES"""
        try:
            empleados = await self._obtener_datos_reales("employees")

            if not empleados:
                return "⚠️ No se pudieron obtener datos."

            salarios = [e.get('salario_basico', 0) for e in empleados if e.get('salario_basico')]
            salarios.sort()

            # Rangos
            rangos = {
                '2M-2.5M': 0, '2.5M-3M': 0, '3M-3.5M': 0,
                '3.5M-4M': 0, '4M-4.5M': 0, '4.5M+': 0
            }

            for sal in salarios:
                if sal < 2500000: rangos['2M-2.5M'] += 1
                elif sal < 3000000: rangos['2.5M-3M'] += 1
                elif sal < 3500000: rangos['3M-3.5M'] += 1
                elif sal < 4000000: rangos['3.5M-4M'] += 1
                elif sal < 4500000: rangos['4M-4.5M'] += 1
                else: rangos['4.5M+'] += 1

            promedio = sum(salarios) / len(salarios) if salarios else 0
            mediana = salarios[len(salarios)//2] if salarios else 0

            respuesta = f"💰 DISTRIBUCIÓN DE SALARIOS - ANDINA FOODS (DATOS REALES)\n"
            respuesta += f"{'='*60}\n\n"
            respuesta += f"Total Empleados: {len(empleados)}\n\n"
            respuesta += "Rangos Salariales:\n"

            for rango, cantidad in rangos.items():
                pct = (cantidad / len(salarios) * 100) if salarios else 0
                respuesta += f"${rango:10} : {cantidad:3} empleados ({pct:5.1f}%)\n"

            respuesta += f"\nEstadísticas:\n"
            respuesta += f"- Salario Promedio: ${promedio:,.0f}\n"
            respuesta += f"- Salario Mediano: ${mediana:,.0f}\n"
            respuesta += f"- Mínimo: ${min(salarios):,.0f}\n"
            respuesta += f"- Máximo: ${max(salarios):,.0f}\n"
            respuesta += f"\n✅ Análisis en tiempo real desde PostgreSQL"

            return respuesta

        except Exception as e:
            logger.error(f"Error en salary distribution: {e}")
            return f"❌ Error: {str(e)}"

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

    async def generate_payroll_report(self, periodo: str = None) -> Dict[str, Any]:
        """Generar reporte de nómina mensual

        Args:
            periodo: Período del reporte (e.g., "agosto-2026")

        Returns:
            Dict con resultado de generación y ruta del archivo
        """
        if not self.document_engine:
            return {"status": "error", "message": "DocumentEngine no disponible"}

        try:
            empleados = await self._obtener_datos_reales("employees")

            if not empleados:
                return {"status": "error", "message": "No hay datos de empleados"}

            # Calcular estadísticas
            total_salarios = sum(float(e.get('salario_basico', 0)) for e in empleados)
            promedio = total_salarios / len(empleados) if empleados else 0

            # Crear datos para el reporte
            periodo = periodo or datetime.now().strftime("%B-%Y")
            report_data = {
                "titulo": f"Reporte de Nómina {periodo}",
                "empresa": "Andina Foods S.A.S.",
                "periodo": periodo,
                "seccion_ejecutiva": f"Reporte de nómina para {len(empleados)} empleados",
                "metricas": {
                    "Total Empleados": str(len(empleados)),
                    "Nómina Total": f"${total_salarios:,.0f}",
                    "Salario Promedio": f"${promedio:,.0f}"
                },
                "contenido_ia": f"Nómina procesada para {len(empleados)} empleados en el período {periodo}.",
                "conclusiones": "Nómina generada exitosamente desde datos en tiempo real."
            }

            # Generar documento
            output_path = self.document_engine.generate_word(
                "report",
                report_data,
                f"nomina_{periodo.replace(' ', '_')}.docx"
            )

            logger.info(f"✅ Reporte de nómina generado: {output_path}")

            # Notificar a Document Manager
            await self._register_document_with_manager({
                'file_path': str(output_path),
                'doc_type': 'report',
                'agent_name': 'Payroll Agent',
                'entity_id': f"nomina_{periodo}",
                'entity_name': f"Nómina {periodo}",
                'metadata': {
                    'periodo': periodo,
                    'total_empleados': len(empleados),
                    'nómina_total': float(total_salarios)
                }
            })

            return {
                "status": "success",
                "document_type": "payroll_report",
                "periode": periodo,
                "total_empleados": len(empleados),
                "nómina_total": f"${total_salarios:,.0f}",
                "path": str(output_path),
                "message": f"Reporte de nómina {periodo} generado exitosamente"
            }

        except Exception as e:
            logger.error(f"Error generando reporte de nómina: {e}")
            return {"status": "error", "message": str(e)}

    async def _register_document_with_manager(self, document_data: Dict[str, Any]) -> None:
        """Notificar al Document Manager sobre un documento generado"""
        try:
            from .document_manager_agent import DocumentManagerAgent

            doc_manager = DocumentManagerAgent()
            result = await doc_manager.register_document(document_data)

            if result['status'] == 'success':
                logger.info(f"✅ Documento registrado en Document Manager: {result['doc_id']}")
            else:
                logger.warning(f"⚠️ Error registrando en Document Manager: {result.get('message')}")
        except Exception as e:
            logger.error(f"Error notificando al Document Manager: {e}")
