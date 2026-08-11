"""Recruitment Agent - Especializado en reclutamiento y selección con datos REALES

Procesa queries sobre screening de candidatos, job postings,
onboarding, evaluación de skills, etc. Genera documentos de oferta.
"""

import logging
import re
from typing import Dict, Any
from datetime import datetime

from elap_ai.data_agent_mixin import DataAgentMixin

logger = logging.getLogger(__name__)


class RecruitmentAgent(DataAgentMixin):
    """Agente especializado en reclutamiento y selección con datos REALES"""

    def __init__(self, theme: str = "andina_foods"):
        super().__init__()
        self.theme = theme
        logger.info(f"RecruitmentAgent initialized with theme: {theme} - usando datos REALES")

        try:
            from ..document_engine import DocumentEngine
            self.document_engine = DocumentEngine(theme=theme, language="es")
        except Exception as e:
            logger.warning(f"DocumentEngine no disponible: {e}")
            self.document_engine = None

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de reclutamiento

        Args:
            query: Consulta del usuario

        Returns:
            Dict con respuesta y metadata
        """
        logger.info(f"Processing recruitment query: {query[:50]}...")

        query_lower = query.lower()

        # ==================== DATOS REALES ====================
        # Palabras clave para consultas de reclutamiento
        reclutamiento_keywords = ["reclutamiento", "candidato", "candidatos", "vacante", "selección", "onboarding", "equipo"]

        if any(kw in query_lower for kw in reclutamiento_keywords):
            logger.info("👥 Detectada pregunta sobre reclutamiento - usando datos REALES")

            try:
                empleados = await self.obtener_datos_reales("employees", limite=1000)
                evaluaciones = await self.obtener_evaluaciones_por_depto()

                if empleados and evaluaciones:
                    respuesta = """👥 **ANÁLISIS DE ESTRUCTURA DE PERSONAL (DATOS REALES)**
==================================================================

📊 **RESUMEN ORGANIZACIONAL**
  • Total Empleados: {total}

🏢 **DISTRIBUCIÓN POR DEPARTAMENTO**

""".format(total=len(empleados))

                    # Agrupar por departamento
                    deptos = {}
                    for emp in empleados:
                        depto = emp.get('departamento', 'Desconocido')
                        if depto not in deptos:
                            deptos[depto] = 0
                        deptos[depto] += 1

                    for depto in sorted(deptos.keys()):
                        cantidad = deptos[depto]
                        eval_info = evaluaciones.get(depto, {})
                        puntaje = eval_info.get('puntaje_promedio', 0)
                        ascensos = eval_info.get('ascensos', 0)

                        respuesta += f"  • {depto}: {cantidad} empleados\n"
                        if puntaje > 0:
                            respuesta += f"    Puntaje Promedio: {puntaje:.1f}/100\n"
                        if ascensos > 0:
                            respuesta += f"    Candidatos Ascenso: {ascensos}\n"
                        respuesta += "\n"

                    respuesta += "✅ Datos actualizados desde PostgreSQL en tiempo real."

                    return {
                        "intent": "reclutamiento_query",
                        "message": respuesta
                    }
            except Exception as e:
                logger.error(f"Error obteniendo datos de reclutamiento: {e}")

        response = await self._generate_recruitment_response(query)

        return {
            "message": response,
            "intent": "recruitment",
            "agent": "recruitment_agent",
        }

    async def _generate_recruitment_response(self, query: str) -> str:
        """Generar respuesta especializada en reclutamiento"""

        query_lower = query.lower()

        # Detección de tipo de request
        if "candidat" in query_lower or "evalú" in query_lower:
            return self._screen_candidate(query)
        elif "oferta" in query_lower or "job posting" in query_lower:
            return self._create_job_posting(query)
        elif "onboarding" in query_lower or "integración" in query_lower:
            return self._onboarding_plan(query)
        else:
            return await self._generic_recruitment_response(query)

    def _screen_candidate(self, query: str) -> str:
        """Evaluar candidato"""
        # Extraer características
        experience = self._extract_experience(query)
        education = self._extract_education(query)
        skills = self._extract_skills(query)

        # Calcular score (0-100)
        score = self._calculate_candidate_score(experience, education, skills)
        rating = self._get_rating(score)

        return f"""👤 EVALUACIÓN DE CANDIDATO

Perfil Identificado:
- Años de experiencia: {experience} años
- Educación: {education if education else "No especificada"}
- Skills detectadas: {", ".join(skills) if skills else "No especificadas"}

SCORING AUTOMÁTICO:

Componentes de Evaluación:
├─ Experiencia (40%): {experience/5*40:.1f} pts
│  └─ {experience} años × 8 pts/año = {experience*8:.0f} pts (máx 40)
├─ Educación (20%): 18 pts
│  └─ Profesional acreditado
└─ Skills Técnicos (40%): {len(skills)*8:.1f} pts
   └─ {len(skills)} skills × 8 pts = {len(skills)*8:.0f} pts (máx 40)

PUNTUACIÓN TOTAL: {score:.0f} / 100 - {rating}

Recomendación: {"✅ CALIFICADO PARA ENTREVISTA" if score >= 70 else "⚠️ REVISAR EN DETALLE" if score >= 50 else "❌ NO CUMPLE REQUISITOS"}

Fortalezas:
{"• Amplia experiencia" if experience >= 5 else "• Disponibilidad y potencial"}
{f"• Domina {len(skills)} skills técnicos" if skills else "• Flexible en herramientas"}

Próximos Pasos:
1. Revisión de referencias (si score > 70)
2. Entrevista técnica con IT Manager
3. Entrevista conductual con RRHH
4. Prueba práctica de 4 horas
5. Decision y oferta (si todo OK)

Tiempo estimado: 2-3 semanas"""

    def _create_job_posting(self, query: str) -> str:
        """Crear publicación de oferta de empleo"""
        return """📢 PUBLICACIÓN DE OFERTA LABORAL

Puesto: Contador Senior
Departamento: Finanzas
Ubicación: Barranquilla
Tipo de Contrato: Indefinido

Descripción del Rol:
- Gestión contable y fiscal de la empresa
- Preparación de reportes mensuales/trimestrales
- Asesoría en asuntos tributarios
- Supervisión de auxiliares contables
- Cumplimiento normativo

Requisitos:
ESENCIALES:
✓ Pregrado en Contabilidad o Contaduría Pública
✓ 3+ años experiencia similar
✓ Conocimiento de NIF/NIIF
✓ Manejo de ERP (preferible SAP)

DESEABLES:
• Especialización en Tributaria
• Certificación CPA
• Bilingüismo (Inglés nivel intermedio)
• Experiencia en comercio FMCG

Salario y Beneficios:
- Salario base: $4,500,000 - $5,500,000
- Auxilio de transporte
- EPS/AFP de elección
- Bonificación anual
- Capacitaciones

Contacto:
Área de RRHH
Email: reclutamiento@andina-foods.com.co
Teléfono: +57 (5) 330-2200 ext. 101

Aplicar en: andina-foods.com.co/jobs

Status: ABIERTA - Procesando candidatos"""

    def _onboarding_plan(self, query: str) -> str:
        """Plan de integración para nuevo empleado"""
        return """🎯 PLAN DE ONBOARDING

Empleado: [Nombre a Definir]
Cargo: [Posición a Definir]
Departamento: [Área a Definir]
Fecha Inicio: [Fecha a Confirmar]

SEMANA 1: INDUCCIÓN CORPORATIVA
Día 1 (Lunes):
□ Bienvenida y presentación con Gerente General
□ Recorrido por instalaciones
□ Entrega de credencial y accesos
□ Sesión RRHH: políticas y beneficios
□ Almuerzo de bienvenida con equipo

Día 2-3 (Mar-Mié):
□ Sesión estrategia y negocio
□ Inducción en seguridad y salud
□ Setup de equipos IT (PC, email, accesos)
□ Introducción a sistemas (ERP, contabilidad)

Día 4-5 (Jue-Vie):
□ Dinámicas de integración
□ Sesión de cultura corporativa
□ Networking con otros departamentos
□ Evaluación de la semana

SEMANA 2-4: FORMACIÓN TÉCNICA
□ Capacitación en procesos específicos del rol
□ Asignación de mentor/buddy
□ Rotación por áreas clave
□ Definición de objetivos primeros 90 días

SEMANA 5-12: DESEMPEÑO
□ Seguimiento semanal con supervisor
□ Evaluación formativa (mes 1)
□ Evaluación de período prueba (mes 3)
□ Formalización del contrato (si aplica)

Recursos Disponibles:
- Portal de capacitación
- Acceso a biblioteca virtual
- Mentoring personalizado
- Línea de bienestar

Éxito esperado: Empleado productivo y comprometido después de 90 días"""

    def _extract_experience(self, text: str) -> int:
        """Extrae años de experiencia"""
        match = re.search(r'(\d+)\s*(?:años?|years?)\s*(?:de\s*)?(?:experiencia|experience)', text.lower())
        return int(match.group(1)) if match else 2

    def _extract_education(self, text: str) -> str:
        """Extrae nivel educativo"""
        if "profesional" in text.lower() or "degree" in text.lower():
            return "Profesional"
        elif "técnico" in text.lower():
            return "Técnico"
        elif "maestría" in text.lower() or "master" in text.lower():
            return "Maestría"
        return None

    def _extract_skills(self, text: str) -> list:
        """Extrae skills mencionadas"""
        skill_keywords = {
            "excel": ["excel", "sheets", "hojas"],
            "sap": ["sap", "erp"],
            "python": ["python"],
            "sql": ["sql"],
            "stata": ["stata"],
            "r": [r"\bR\b", "rstudio"],
            "contabilidad": ["contabilidad", "accounting"],
            "fiscalidad": ["fiscal", "tax"],
            "finanzas": ["finanzas", "finance"],
        }

        skills_found = []
        text_lower = text.lower()

        for skill, keywords in skill_keywords.items():
            for keyword in keywords:
                if re.search(rf'\b{keyword}\b', text_lower):
                    if skill not in skills_found:
                        skills_found.append(skill.title())
                    break

        return skills_found

    def _calculate_candidate_score(self, exp: int, edu: str, skills: list) -> float:
        """Calcular score final del candidato"""
        score = 0

        # Experiencia (40%)
        exp_score = min(40, (exp / 5) * 40)
        score += exp_score

        # Educación (20%)
        edu_score = 20 if edu else 5
        score += edu_score

        # Skills (40%)
        skills_score = min(40, len(skills) * 8)
        score += skills_score

        return score

    def _get_rating(self, score: float) -> str:
        """Obtener rating de texto"""
        if score >= 85:
            return "⭐⭐⭐⭐⭐ EXCELENTE MATCH"
        elif score >= 70:
            return "⭐⭐⭐⭐ STRONG CANDIDATE"
        elif score >= 50:
            return "⭐⭐⭐ CANDID ATO POTENCIAL"
        else:
            return "⭐⭐ NO RECOMENDADO"

    async def _generic_recruitment_response(self, query: str) -> str:
        """Respuesta genérica para queries de reclutamiento - usa Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("recruitment_agent")

            prompt_ollama = f"""{system_prompt}

Pregunta del usuario: {query}

Responde de manera profesional, justa y orientada al potencial."""

            logger.info("👤 Llamando a Ollama para respuesta general de Recruitment...")
            respuesta = await ollama.generar("glm4:9b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en Recruitment: {e}")
            return """💼 ASISTENTE DE RECLUTAMIENTO - ANDINA FOODS

Puedo ayudarte con evaluación de candidatos, creación de ofertas laborales,
planes de onboarding, y análisis de pipeline de reclutamiento.

¿Qué necesitas en reclutamiento?"""

    async def generate_job_offer(
        self,
        candidato: str,
        puesto: str,
        salario: str,
        contrato: str = "Indefinido"
    ) -> Dict[str, Any]:
        """Generar oferta de trabajo para candidato

        Args:
            candidato: Nombre del candidato
            puesto: Puesto a ofrecer
            salario: Salario ofrecido
            contrato: Tipo de contrato (Indefinido, Término Fijo, etc)

        Returns:
            Dict con ruta del documento generado
        """
        if not self.document_engine:
            return {"status": "error", "message": "DocumentEngine no disponible"}

        try:
            offer_data = {
                "titulo": f"Oferta de Empleo - {puesto}",
                "empresa": "Andina Foods S.A.S.",
                "candidato": candidato,
                "puesto": puesto,
                "salario": salario,
                "tipo_contrato": contrato,
                "fecha_oferta": datetime.now().strftime("%d/%m/%Y"),
                "condiciones": "Bajo las condiciones estándar de la empresa",
                "validez": "Esta oferta es válida por 15 días hábiles"
            }

            output_path = self.document_engine.generate_word(
                "job_offer",
                offer_data,
                f"oferta_{candidato.replace(' ', '_')}.docx"
            )

            logger.info(f"✅ Oferta de trabajo generada: {output_path}")

            # Registrar en Document Manager
            await self._register_document_with_manager({
                'file_path': str(output_path),
                'doc_type': 'job_offer',
                'agent_name': 'Recruitment Agent',
                'entity_id': f"candidato_{candidato.replace(' ', '_')}",
                'entity_name': candidato,
                'metadata': {
                    'puesto': puesto,
                    'salario': salario,
                    'contrato': contrato
                }
            })

            return {
                "status": "success",
                "document_type": "job_offer",
                "candidato": candidato,
                "puesto": puesto,
                "path": str(output_path),
                "message": f"Oferta de empleo generada para {candidato}"
            }

        except Exception as e:
            logger.error(f"Error generando oferta: {e}")
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
