"""Agente RRHH - Generación de documentos laborales"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import uuid

from elap_ai.agent_runtime.agent import Agent, AgentState
from elap_ai.document_engine import DocumentEngine

logger = logging.getLogger(__name__)


class HRAgent(Agent):
    """Agente especializado en Recursos Humanos

    Genera documentos laborales: contratos, políticas, certificados, etc.
    Integrado con Document Engine para crear documentos profesionales.
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
            objective="Generate HR documents: contracts, policies, certificates"
        )
        super().__init__(state=state)
        self.theme = theme
        self.document_engine = DocumentEngine(theme=theme, language="es")
        logger.info(f"HR Agent initialized with theme: {theme}")

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

        Interpreta intención y genera documentos si aplica
        """
        logger.info(f"Processing HR query: {query}")

        query_lower = query.lower()

        # Verificar si tiene datos de contrato (Empresa:, Empleado:, etc)
        has_employee_data = all(keyword in query for keyword in ["Empresa:", "Empleado:", "Cargo:", "Salario:"])

        # Si tiene datos, GENERAR el contrato
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

        # Si NO tiene datos pero pide contrato, solicitar datos
        elif any(word in query_lower for word in ["contrato", "contract", "empleado", "employee"]):
            return {
                "intent": "generate_contract",
                "message": """🧑‍💼 *Asistente RRHH* aquí.

Veo que necesitas generar un **contrato laboral**.

Para crearlo necesito:
• Nombre de la empresa
• Nombre del empleado
• Cargo
• Salario
• Fecha de inicio
• Beneficios (seguro, bonificación, etc)
• Responsabilidades principales

¿Proporcionas estos datos para generar el contrato?""",
                "required_fields": [
                    "empresa", "empleado", "cargo", "salario",
                    "fecha_inicio", "beneficios", "responsabilidades"
                ]
            }

        # Intención: generar política
        elif any(word in query_lower for word in ["política", "policy", "poliza", "protocolo"]):
            return {
                "intent": "generate_policy",
                "message": """🧑‍💼 *Asistente RRHH* aquí.

Veo que necesitas una **política corporativa**.

¿Qué tipo de política necesitas?

• **Ausencias** - control de inasistencias
• **Vacaciones** - días y procedimiento
• **Conducta** - código ético
• **Confidencialidad** - protección de datos

¿Cuál prefieres?""",
                "policy_types": ["ausencias", "vacaciones", "conducta", "confidencialidad"]
            }

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

                return {
                    "intent": "general_query",
                    "message": f"🧑‍💼 *Asistente de Recursos Humanos*\n\n{respuesta}",
                    "ley_consultada": ley_actualizada.get("fuente") if ley_actualizada else None,
                    "confianza_legal": ley_actualizada.get("confianza") if ley_actualizada else None
                }
            except Exception as e:
                logger.error(f"Ollama error en HR: {e}")
                return {
                    "intent": "general_query",
                    "message": """🧑‍💼 *Asistente de Recursos Humanos* a tu servicio.

Soy especialista en documentación laboral y legislación colombiana. Puedo ayudarte con:

📋 **Contratos** - Contratos de empleados, acuerdos, cartas de oferta
📜 **Políticas** - Ausencias, vacaciones, código de conducta
🏛️ **Legislación** - Derechos laborales, prestaciones, protección

¿Qué necesitas? Cuéntame más detalles."""
                }

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
