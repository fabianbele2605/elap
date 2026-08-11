"""Ejecutor de Workflows Real - Conecta agentes verdaderos"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """Ejecuta workflows usando agentes reales"""

    def __init__(self, agents_dict: Dict[str, Any]):
        """
        Args:
            agents_dict: Dict con agentes inicializados
                {
                    'ceo_assistant': CEOAssistant(),
                    'cfo_assistant': CFOAssistant(),
                    ...
                }
        """
        self.agents = agents_dict
        logger.info(f"✅ WorkflowExecutor inicializado con {len(agents_dict)} agentes")

    async def execute_agent(self, agent_id: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Ejecuta un agente real con una query

        Args:
            agent_id: ID del agente (ej: 'ceo_assistant', 'finance_agent')
            query: Pregunta/prompt para el agente
            context: Contexto previo del workflow

        Returns:
            Respuesta del agente
        """
        if agent_id not in self.agents:
            return {
                "error": f"Agente {agent_id} no encontrado",
                "agent": agent_id
            }

        agent = self.agents[agent_id]

        try:
            logger.info(f"▶️ Ejecutando {agent_id}: {query[:50]}...")

            # Ejecutar según tipo de agente
            if hasattr(agent, 'process_query'):
                # Agentes con process_query (CEOAssistant, CFOAssistant, etc)
                result = await agent.process_query(query)

            elif hasattr(agent, 'ejecutar'):
                # Agentes con método ejecutar
                result = await agent.ejecutar(query)

            else:
                result = {
                    "error": f"Agente {agent_id} no tiene método de ejecución válido",
                    "agent": agent_id
                }

            logger.info(f"✅ {agent_id} completado")
            return result

        except Exception as e:
            logger.error(f"❌ Error ejecutando {agent_id}: {e}")
            return {
                "error": str(e),
                "agent": agent_id,
                "status": "fallido"
            }

    async def execute_presupuesto_workflow(self, monto: float, descripcion: str = "") -> Dict[str, Any]:
        """Flujo real: Solicitud de Presupuesto

        CEO → CFO → Finance → DocumentManager
        """
        logger.info(f"🚀 Iniciando workflow presupuesto: ${monto:,.0f}")

        context = {
            "monto": monto,
            "descripcion": descripcion
        }

        try:
            # 1. CEO revisa necesidad estratégica
            query_ceo = f"""Evalúa la solicitud de presupuesto de ${monto:,.0f} para: {descripcion}
Considera:
- Alineación estratégica
- ROI esperado
- Riesgos principales"""

            result_ceo = await self.execute_agent("ceo_assistant", query_ceo, context)
            context["ceo_analysis"] = result_ceo
            logger.info("✅ CEO completó análisis")

            # 2. CFO analiza factibilidad
            query_cfo = f"""Analiza la factibilidad financiera de presupuesto ${monto:,.0f}
Contexto del CEO: {result_ceo.get('message', '')[:200]}
Proporciona:
- Análisis de flujo de caja
- Impacto en márgenes
- Recomendación de aprobación"""

            result_cfo = await self.execute_agent("cfo_assistant", query_cfo, context)
            context["cfo_analysis"] = result_cfo
            logger.info("✅ CFO completó análisis")

            # 3. Finance calcula detalles
            query_finance = f"""Calcula detalles del presupuesto de ${monto:,.0f}
Análisis CFO: {result_cfo.get('message', '')[:200]}
Proporciona:
- Desglose por componentes
- Calendario de desembolsos
- Impacto en indicadores financieros"""

            result_finance = await self.execute_agent("finance_agent", query_finance, context)
            context["finance_analysis"] = result_finance
            logger.info("✅ Finance completó cálculos")

            return {
                "workflow": "presupuesto",
                "status": "✅ Completado",
                "monto": monto,
                "steps": {
                    "ceo": result_ceo,
                    "cfo": result_cfo,
                    "finance": result_finance
                },
                "context": context
            }

        except Exception as e:
            logger.error(f"❌ Error en workflow presupuesto: {e}")
            return {
                "workflow": "presupuesto",
                "status": "❌ Fallido",
                "error": str(e)
            }

    async def execute_venta_workflow(self, producto: str, mercado: str) -> Dict[str, Any]:
        """Flujo real: Análisis de Venta

        CMO → Finance → CFO
        """
        logger.info(f"🚀 Iniciando workflow venta: {producto} en {mercado}")

        context = {
            "producto": producto,
            "mercado": mercado
        }

        try:
            # 1. CMO analiza mercado
            query_cmo = f"""Analiza la oportunidad de venta:
Producto: {producto}
Mercado: {mercado}

Proporciona:
- Tamaño de mercado
- Competencia
- Estrategia de posicionamiento
- Proyección de ventas"""

            result_cmo = await self.execute_agent("cmo_assistant", query_cmo, context)
            context["cmo_analysis"] = result_cmo
            logger.info("✅ CMO completó análisis")

            # 2. Finance proyecta ingresos
            query_finance = f"""Proyecta ingresos para: {producto} en {mercado}
Análisis CMO: {result_cmo.get('message', '')[:200]}

Proporciona:
- Proyección de ingresos (3 años)
- Margen esperado
- Punto de equilibrio"""

            result_finance = await self.execute_agent("finance_agent", query_finance, context)
            context["finance_analysis"] = result_finance
            logger.info("✅ Finance completó proyecciones")

            # 3. CFO valida viabilidad
            query_cfo = f"""Valida viabilidad financiera de: {producto} en {mercado}
Análisis CMO: {result_cmo.get('message', '')[:100]}
Proyecciones Finance: {result_finance.get('message', '')[:100]}

Proporciona:
- Recomendación de viabilidad
- Riesgos financieros
- Condiciones para proceder"""

            result_cfo = await self.execute_agent("cfo_assistant", query_cfo, context)
            context["cfo_analysis"] = result_cfo
            logger.info("✅ CFO completó validación")

            return {
                "workflow": "venta",
                "status": "✅ Completado",
                "producto": producto,
                "mercado": mercado,
                "steps": {
                    "cmo": result_cmo,
                    "finance": result_finance,
                    "cfo": result_cfo
                },
                "context": context
            }

        except Exception as e:
            logger.error(f"❌ Error en workflow venta: {e}")
            return {
                "workflow": "venta",
                "status": "❌ Fallido",
                "error": str(e)
            }

    async def execute_alerta_workflow(self, alerta_tipo: str, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Flujo real: Respuesta a Alerta Crítica

        CEO → CFO → (documentar)
        """
        logger.info(f"🚀 Iniciando workflow alerta: {alerta_tipo}")

        context = {
            "alerta": alerta_tipo,
            "datos": datos
        }

        try:
            # 1. CEO analiza impacto
            query_ceo = f"""Analiza el impacto estratégico de la alerta: {alerta_tipo}
Datos: {str(datos)[:200]}

Proporciona:
- Impacto en objetivos estratégicos
- Escenarios posibles
- Recomendaciones ejecutivas"""

            result_ceo = await self.execute_agent("ceo_assistant", query_ceo, context)
            context["ceo_analysis"] = result_ceo
            logger.info("✅ CEO completó análisis")

            # 2. CFO propone acciones
            query_cfo = f"""Propone plan de acción para alerta: {alerta_tipo}
Impacto CEO: {result_ceo.get('message', '')[:200]}

Proporciona:
- Plan de acción inmediato
- Recursos necesarios
- Métricas de seguimiento"""

            result_cfo = await self.execute_agent("cfo_assistant", query_cfo, context)
            context["cfo_analysis"] = result_cfo
            logger.info("✅ CFO completó propuesta")

            return {
                "workflow": "alerta",
                "status": "✅ Completado",
                "alerta_tipo": alerta_tipo,
                "steps": {
                    "ceo": result_ceo,
                    "cfo": result_cfo
                },
                "context": context
            }

        except Exception as e:
            logger.error(f"❌ Error en workflow alerta: {e}")
            return {
                "workflow": "alerta",
                "status": "❌ Fallido",
                "error": str(e)
            }
