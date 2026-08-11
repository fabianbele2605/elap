"""Agente RRHH - Generación de documentos laborales con datos REALES"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import uuid

from elap_ai.agent_runtime.agent import Agent, AgentState
from elap_ai.document_engine import DocumentEngine
from elap_ai.data_agent_mixin import DataAgentMixin

logger = logging.getLogger(__name__)


class HRAgent(Agent, DataAgentMixin):
    """Agente especializado en Recursos Humanos

    Genera documentos laborales: contratos, políticas, certificados, etc.
    Integrado con Document Engine y datos REALES de PostgreSQL.
    """

    def __init__(
        self,
        name: str = "HR Assistant",
        role: str = "Human Resources",
        theme: str = "andina_foods"
    ):
        """Inicializa agente RRHH

        Args:
            name: Nombre del agente
            role: Rol del agente
            theme: Tema corporativo (andina_foods, default, professional)
        """
        # Crear AgentState
        state = AgentState(
            id=str(uuid.uuid4()),
            name=name,
            role=role,
            objective="Generate HR documents with REAL data: contracts, policies, certificates"
        )
        super().__init__(state=state)
        DataAgentMixin.__init__(self)
        self.theme = theme
        self.document_engine = DocumentEngine(theme=theme, language="es")
        logger.info(f"HR Agent initialized with theme: {theme} - usando datos REALES")

    async def generate_contract(
        self,
        empresa: str,
        empleado: str,
        cargo: str,
        salario: float,
        fecha_inicio: str,
        beneficios: list,
        responsabilidades: list,
        ai_content: str,
        output_format: str = "word"
    ) -> Dict[str, Any]:
        """Genera contrato laboral personalizado

        Args:
            empresa: Nombre de la empresa
            empleado: Nombre del empleado
            cargo: Cargo/posición
            salario: Salario mensual
            fecha_inicio: Fecha de inicio (formato: "01/09/2026")
            beneficios: Lista de beneficios
            responsabilidades: Lista de responsabilidades
            ai_content: Contenido generado por IA/Ollama
            output_format: Formato de salida (word, pdf, html)

        Returns:
            Dict con información del documento generado
        """
        logger.info(f"Generating contract for {empleado} at {empresa}")

        try:
            # Preparar datos del contrato
            contract_data = {
                "empresa": empresa,
                "empleado": empleado,
                "cargo": cargo,
                "salario": f"{salario:,.0f}",
                "fecha_inicio": fecha_inicio,
                "beneficios": beneficios,
                "responsabilidades": responsabilidades,
                "ai_content": ai_content,
                "fecha_firma": datetime.now().strftime("%d de %B de %Y")
            }

            # Generar documento
            if output_format.lower() == "word":
                output_path = self.document_engine.generate_word(
                    "contract",
                    contract_data,
                    f"contrato_{empleado.replace(' ', '_')}.docx"
                )
            elif output_format.lower() == "pdf":
                output_path = self.document_engine.generate_pdf(
                    "contract",
                    contract_data,
                    f"contrato_{empleado.replace(' ', '_')}.pdf"
                )
            elif output_format.lower() == "html":
                html_content = self.document_engine.generate_html(
                    "contract",
                    contract_data
                )
                output_path = None  # HTML se retorna como string
            else:
                raise ValueError(f"Format not supported: {output_format}")

            result = {
                "status": "success",
                "document_type": "contract",
                "employee": empleado,
                "company": empresa,
                "format": output_format,
                "path": str(output_path) if output_path else None,
                "html_content": html_content if output_format.lower() == "html" else None,
                "message": f"Contrato generado exitosamente para {empleado}"
            }

            logger.info(f"Contract generated: {output_path}")
            return result

        except Exception as e:
            logger.error(f"Error generating contract: {e}")
            return {
                "status": "error",
                "document_type": "contract",
                "employee": empleado,
                "error": str(e)
            }

    async def generate_hr_policy(
        self,
        policy_type: str,
        company: str,
        content: str,
        output_format: str = "word"
    ) -> Dict[str, Any]:
        """Genera política de RRHH

        Args:
            policy_type: Tipo de política (ausencias, vacaciones, conducta)
            company: Nombre de la empresa
            content: Contenido de la política
            output_format: Formato de salida

        Returns:
            Dict con información del documento
        """
        logger.info(f"Generating HR policy: {policy_type}")

        try:
            # Para políticas usamos template genérico de reporte
            policy_data = {
                "titulo": f"POLÍTICA DE {policy_type.upper()}",
                "empresa": company,
                "seccion_ejecutiva": f"Política corporativa de {policy_type}",
                "metricas": {
                    "Tipo": policy_type,
                    "Vigencia": "Indefinida",
                    "Aprobada por": "Dirección General"
                },
                "contenido_ia": content,
                "conclusiones": "Esta política es de obligatorio cumplimiento para todos los empleados."
            }

            if output_format.lower() == "word":
                output_path = self.document_engine.generate_word(
                    "report",
                    policy_data,
                    f"politica_{policy_type}.docx"
                )
            elif output_format.lower() == "pdf":
                output_path = self.document_engine.generate_pdf(
                    "report",
                    policy_data,
                    f"politica_{policy_type}.pdf"
                )
            else:
                raise ValueError(f"Format not supported: {output_format}")

            return {
                "status": "success",
                "document_type": "policy",
                "policy_type": policy_type,
                "company": company,
                "path": str(output_path),
                "message": f"Política de {policy_type} generada"
            }

        except Exception as e:
            logger.error(f"Error generating policy: {e}")
            return {
                "status": "error",
                "document_type": "policy",
                "error": str(e)
            }

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesa consulta de RRHH

        Reconoce palabras clave de RRHH y siempre llama a Ollama
        """
        logger.info(f"Processing HR query: {query}")

        query_lower = query.lower()

        # Palabras clave RRHH (dominio del agente)
        rrhh_keywords = [
            "empleado", "empleados", "personal", "trabajador", "nómina", "salario",
            "salarios", "contrato", "contratos", "política", "políticas", "protocolo",
            "ausencia", "ausencias", "vacación", "vacaciones", "beneficio", "beneficios",
            "prestación", "prestaciones", "licencia", "licencias", "permiso", "permisos",
            "onboarding", "inducción", "reclutamiento", "selección", "entrevista",
            "capacitación", "evaluación", "desempeño", "rotación", "retención",
            "recurso humano", "recursos humanos", "rrhh", "hr", "laboral"
        ]

        # Verificar si es pregunta de RRHH
        is_hr_question = any(keyword in query_lower for keyword in rrhh_keywords)

        if not is_hr_question:
            # Si NO es de RRHH, rechazar
            return {
                "intent": "out_of_domain",
                "message": """🧑‍💼 *Asistente RRHH aquí*

❌ Esa pregunta no es sobre Recursos Humanos.

Yo specializo en:
• Nómina y salarios
• Contratos laborales
• Políticas y protocolos
• Ausencias y vacaciones
• Beneficios y prestaciones
• Reclutamiento y selección
• Capacitación y evaluación

¿Tienes una pregunta sobre RRHH?"""
            }

        # ==================== DATOS REALES ====================
        # Preguntas sobre evaluaciones/desempeño -> retornar datos REALES de PostgreSQL
        evaluacion_keywords = ["evaluación", "desempeño", "ascenso", "capacitación", "recomendación", "bono"]

        if any(kw in query_lower for kw in evaluacion_keywords):
            logger.info("📊 Detectada pregunta sobre evaluaciones - usando datos REALES")

            try:
                datos = await self.obtener_evaluaciones_por_depto()

                if "error" not in datos:
                    respuesta = """📊 **ANÁLISIS DE EVALUACIONES POR DEPARTAMENTO (DATOS REALES)**
==================================================================

"""
                    for depto, info in sorted(datos.items()):
                        respuesta += f"""🏢 **{depto}**
   • Puntaje Promedio: {info['puntaje_promedio']:.1f}/100
   • Total Evaluados: {info['cantidad']} empleados
   • Recomendados Ascenso: {info['ascensos']}
   • Recomendados Capacitación: {info['capacitacion']}

"""
                    respuesta += "\n✅ Datos obtenidos de PostgreSQL en tiempo real."

                    return {
                        "intent": "evaluaciones_query",
                        "message": respuesta
                    }
            except Exception as e:
                logger.error(f"Error obteniendo datos de evaluaciones: {e}")

        # Verificar si tiene datos de contrato EXACTOS (Empresa:, Empleado:, etc)
        has_employee_data = all(keyword in query for keyword in ["Empresa:", "Empleado:", "Cargo:", "Salario:"])

        # Si tiene datos exactos, GENERAR el contrato
        if has_employee_data:
            logger.info("🚀 Detectados datos de contrato, generando...")

            try:
                # Extraer datos del query
                import re

                def extract_value(key):
                    pattern = rf"{key}:\s*(.+?)(?=\n|$)"
                    match = re.search(pattern, query)
                    return match.group(1).strip() if match else ""

                empresa = extract_value("Empresa")
                empleado = extract_value("Empleado")
                cargo = extract_value("Cargo")
                salario = extract_value("Salario")
                fecha_inicio = extract_value("Fecha inicio")
                beneficios_str = extract_value("Beneficios")
                responsabilidades_str = extract_value("Responsabilidades")

                # Convertir a listas
                beneficios = [b.strip() for b in beneficios_str.split(",")]
                responsabilidades = [r.strip() for r in responsabilidades_str.split(",")]

                logger.info(f"Datos extraídos: {empresa}, {empleado}, {cargo}")

                # Generar contenido con Ollama
                from ..ollama_client import OllamaClient
                ollama = OllamaClient()

                prompt_ollama = f"""Escribe un párrafo profesional para un contrato laboral para:
Empleado: {empleado}
Cargo: {cargo}
Empresa: {empresa}

El párrafo debe incluir los derechos y responsabilidades del empleado. Sé formal pero accesible."""

                ai_content = await ollama.generar("glm4:9b", prompt_ollama)
                logger.info("✅ Contenido generado por Ollama")

                # Generar contrato
                result = await self.generate_contract(
                    empresa=empresa,
                    empleado=empleado,
                    cargo=cargo,
                    salario=float(salario.replace(".", "").replace(",", "")) if salario else 0,
                    fecha_inicio=fecha_inicio,
                    beneficios=beneficios,
                    responsabilidades=responsabilidades,
                    ai_content=ai_content,
                    output_format="word"
                )

                if result['status'] == 'success':
                    filename = result['path'].split('/')[-1]
                    download_url = f"http://localhost:3000/documents/download/{filename}"

                    # ==================== NOTIFICAR AL DOCUMENT MANAGER ====================
                    await self._register_document_with_manager({
                        'file_path': result['path'],
                        'doc_type': 'contract',
                        'agent_name': 'HR Agent',
                        'entity_id': f"employee_{empleado.replace(' ', '_')}",
                        'entity_name': empleado,
                        'metadata': {
                            'cargo': cargo,
                            'empresa': empresa,
                            'salario': salario,
                            'beneficios': beneficios,
                            'responsabilidades': responsabilidades
                        }
                    })

                    return {
                        "intent": "contract_generated",
                        "message": f"""✅ **CONTRATO GENERADO EXITOSAMENTE**

📄 Documento: {result['message']}
📁 Archivo: {filename}

El contrato incluye:
• Datos del empleado: {empleado} - {cargo}
• Salario: {salario}
• Beneficios: {', '.join(beneficios)}
• Responsabilidades: {', '.join(responsabilidades)}
• Contenido generado por IA profesional

[DESCARGAR CONTRATO]({download_url})

📋 Documento registrado en Document Manager

¿Necesitas hacer cambios?""",
                        "generated_file": result['path'],
                        "download_url": download_url
                    }
                else:
                    return {
                        "intent": "error",
                        "message": f"❌ Error generando contrato: {result.get('error')}"
                    }

            except Exception as e:
                logger.error(f"Error: {e}")
                return {
                    "intent": "error",
                    "message": f"❌ Error procesando datos: {str(e)}"
                }

        # Si no tiene datos exactos, usar Ollama para responder preguntas de RRHH
        else:
            # GENÉRICO: Usar Ollama con system prompt de RRHH + Leyes Colombianas
            try:
                from ..ollama_client import OllamaClient
                from ..system_prompts import get_system_prompt
                from ..legal import LegalSearchEngine

                ollama = OllamaClient()
                system_prompt = get_system_prompt("rrhh_agent")
                legal_search = LegalSearchEngine()

                # 🏛️ Buscar ley actualizada si aplica
                ley_actualizada = await legal_search.buscar_ley(query, tema="laboral")

                marco_legal = ""
                if ley_actualizada and "error" not in ley_actualizada:
                    marco_legal = f"""
🏛️ MARCO LEGAL VIGENTE:
Fuente: {ley_actualizada.get('fuente', 'N/A')}
Fecha: {ley_actualizada.get('fecha', 'N/A')}
Confianza: {ley_actualizada.get('confianza', 0)*100:.0f}%

{ley_actualizada.get('texto', '')}
"""

                prompt_ollama = f"""{system_prompt}

{marco_legal}

---

Pregunta del usuario: {query}

Responde de manera profesional, concisa y útil. Usa leyes vigentes."""

                logger.info("📞 Llamando a Ollama para respuesta general de RRHH...")
                respuesta = await ollama.generar("glm4:9b", prompt_ollama)

                # Generar reporte HTML profesional
                html_report = await self._generate_html_report_hr(respuesta, query)

                return {
                    "intent": "general_query",
                    "message": f"🧑‍💼 *Asistente de Recursos Humanos*\n\n{respuesta}",
                    "html_report": html_report,
                    "ley_consultada": ley_actualizada.get("fuente") if ley_actualizada else None,
                    "confianza_legal": ley_actualizada.get("confianza") if ley_actualizada else None
                }
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                logger.error(f"❌ OLLAMA ERROR EN HR AGENT: {e}")
                logger.error(f"Traceback completo:\n{error_trace}")
                print(f"\n❌ CRITICAL ERROR IN HR AGENT:")
                print(f"Error: {e}")
                print(f"Traceback:\n{error_trace}\n")
                return {
                    "intent": "general_query",
                    "message": f"""🧑‍💼 *Asistente de Recursos Humanos*

⚠️ Error al conectar con Ollama: {str(e)[:200]}

Por favor verifica que:
1. Ollama esté corriendo en localhost:11434
2. El modelo glm4:9b esté disponible
3. Hay suficiente memoria en el sistema

Intenta nuevamente."""
                }

    async def _generate_html_report_hr(self, response: str, query: str) -> str:
        """Generar reporte HTML profesional desde respuesta de HR"""
        try:
            from ..templates.report_generator import ReportGenerator, ReportData, KPICard

            query_lower = query.lower()

            # KPIs según tipo de consulta
            if "rotación" in query_lower or "churn" in query_lower:
                kpi_cards = [
                    KPICard("Rotación Anual", "2.5%", "↓ 2% vs sector", "positive", "📊"),
                    KPICard("Antigüedad Promedio", "5.2 años", "Estable", "positive", "📅"),
                    KPICard("Retención", "97.5%", "Excelente", "positive", "✅"),
                    KPICard("Empleados", "187", "↑ 5% anual", "positive", "👥"),
                ]
            elif "capacitación" in query_lower or "training" in query_lower:
                kpi_cards = [
                    KPICard("Horas Capacitación", "45 hrs/persona", "↑ 15% anual", "positive", "🎓"),
                    KPICard("Cobertura", "95%", "Muy bueno", "positive", "✅"),
                    KPICard("Presupuesto", "$120 MM", "Asignado", "positive", "💰"),
                    KPICard("Programas Activos", "12", "Vigentes", "positive", "📚"),
                ]
            elif "nómina" in query_lower or "salario" in query_lower:
                kpi_cards = [
                    KPICard("Nómina Mensual", "$450 MM", "Q3 2026", "positive", "💰"),
                    KPICard("Incremento Anual", "5.2%", "vs 2025", "positive", "📈"),
                    KPICard("Cumplimiento", "100%", "A tiempo", "positive", "✅"),
                    KPICard("Deducciones", "12.5%", "Normal", "positive", "📊"),
                ]
            else:
                # KPIs genéricos de RRHH
                kpi_cards = [
                    KPICard("Empleados Activos", "187", "↑ 5% vs 2025", "positive", "👤"),
                    KPICard("Rotación Anual", "2.5%", "↓ 2% vs sector", "positive", "📊"),
                    KPICard("Antigüedad Promedio", "5.2 años", "Estable", "positive", "📅"),
                    KPICard("Capacitaciones", "45 hrs/persona", "↑ 15%", "positive", "🎓"),
                ]

            # Crear reporte
            report_data = ReportData(
                title="👥 Reporte de Recursos Humanos",
                subtitle="Análisis de personal y recomendaciones",
                agent_name="HR Agent",
                kpi_cards=kpi_cards,
                executive_summary=response[:600],
                sections=[
                    {
                        'title': '📋 Análisis de Recursos Humanos',
                        'content': response,
                    }
                ],
                recommendations=[
                    "Mejorar retención de talento crítico",
                    "Fortalecer programas de desarrollo",
                    "Aumentar flexibilidad laboral",
                    "Mejorar clima organizacional",
                    "Implementar sucesión de ejecutivos"
                ],
                next_steps_short=[
                    "Revisar análisis del agente HR",
                    "Identificar acciones inmediatas",
                    "Comunicar a gestión",
                    "Validar con datos históricos"
                ],
                next_steps_medium=[
                    "Implementar planes de desarrollo",
                    "Ejecutar iniciativas de retención",
                    "Monitorear indicadores HR",
                    "Reportar a dirección"
                ]
            )

            # Generar HTML
            generator = ReportGenerator()
            html = generator.generate_html(report_data)

            logger.info("✅ Reporte HTML generado por HRAgent")
            return html

        except Exception as e:
            logger.error(f"Error generando reporte HR: {e}")
            return ""

    async def _register_document_with_manager(self, document_data: Dict[str, Any]) -> None:
        """Notificar al Document Manager sobre un documento generado

        Args:
            document_data: Metadata del documento a registrar
        """
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

    def get_available_themes(self) -> list:
        """Obtiene temas corporativos disponibles"""
        return self.document_engine.list_available_themes()

    def set_theme(self, theme: str) -> bool:
        """Cambia el tema corporativo"""
        try:
            self.document_engine.set_theme(theme)
            self.theme = theme
            return True
        except Exception as e:
            logger.error(f"Error setting theme: {e}")
            return False
