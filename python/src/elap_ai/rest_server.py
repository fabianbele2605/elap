"""REST API server para exponer agentes Python

Este servidor REST permite que el Rust backend comunique con los agentes Python.
Es una solución temporal mientras el gRPC está siendo habilitado.
"""

import asyncio
import logging
from aiohttp import web
import aiohttp_cors
import json
from typing import Optional
from pathlib import Path
import os
from datetime import datetime
import psycopg2
import psycopg2.extras
from decimal import Decimal

# 🔧 Configurar logging INMEDIATAMENTE
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from .agents.hr_agent import HRAgent
from .agents.finance_agent import FinanceAgent
from .agents.payroll_agent import PayrollAgent
from .agents.benefits_agent import BenefitsAgent
from .agents.recruitment_agent import RecruitmentAgent
from .agents.ceo_assistant import CEOAssistant
from .agents.cfo_assistant import CFOAssistant
from .agents.cmo_assistant import CMOAssistant
from .agents.compras_agent import ComprasAgent
from .agents.ventas_agent import VentasAgent
from .agents.crm_agent import CRMAgent
from .agents.customer_service_agent import CustomerServiceAgent
from .agents.document_manager_agent import DocumentManagerAgent
from .agents.pdf_assistant_agent import PDFAssistantAgent
from .agents.system_supervisor import SystemSupervisor
from .agents.task_router import TaskRouter
from .agents.memory_manager import MemoryManager
from .orchestrator import get_orchestrator
from .document_generators import DocumentGenerator
from .conversation_manager_postgres import ConversationManagerPostgres

logger = logging.getLogger(__name__)
doc_generator = DocumentGenerator()

# Inicializar conversation_manager con manejo de errores
conversation_manager = None
try:
    conversation_manager = ConversationManagerPostgres(
        host="localhost",
        port=5432,
        database="elap_db",
        user="elap_user",
        password="elap_secure_pass_2026"
    )
    logger.info("✅ ConversationManager PostgreSQL inicializado")
except Exception as e:
    logger.error(f"❌ Error inicializando ConversationManager: {e}")
    conversation_manager = None

# Inicializar agentes globales - 15 agentes ELAP
# === Sistema (3) ===
system_supervisor = None
task_router = None
memory_manager = None

# === Administrativo (5) ===
hr_agent = None
finance_agent = None
payroll_agent = None
benefits_agent = None
recruitment_agent = None

# === Dirección (3) ===
ceo_assistant = None
cfo_assistant = None
cmo_assistant = None

# === Comercial (3) ===
compras_agent = None
ventas_agent = None
crm_agent = None
customer_service_agent = None

# === Documentación (2) ===
document_manager_agent = None
pdf_assistant_agent = None

orchestrator = None


def _detect_agent_type_from_prompt(prompt: str) -> str:
    """Detectar tipo de agente del system prompt - soporta 15 agentes ELAP"""
    prompt_lower = prompt.lower()

    # === CEO/Estrategia (Director Ejecutivo) ===
    if any(word in prompt_lower for word in ["director ejecutivo", "ceo", "estratég", "visión", "mercado", "expansión"]):
        return "ceo_assistant"

    # === CFO (Director Financiero) ===
    if any(word in prompt_lower for word in ["director financiero", "cfo", "presupuesto", "flujo de caja", "auditoría financiera"]):
        return "cfo_assistant"

    # === CMO (Director Marketing) ===
    if any(word in prompt_lower for word in ["director marketing", "cmo", "marketing", "campañas", "marca", "posicionamiento"]):
        return "cmo_assistant"

    # === RRHH (HR) ===
    if any(word in prompt_lower for word in ["rrhh", "recursos humanos", "contrat", "empleado", "selección", "salario promedio", "análisis salarial", "estructura salarial", "rango salarial"]):
        return "hr"

    # === Finanzas (Análista Financiero) ===
    if any(word in prompt_lower for word in ["analista financiero", "finanz", "utilidad", "margen", "reportes financiero", "ingresos", "gasto", "operacional", "proyecciones", "ahorro", "costo", "presupuesto", "rentabilidad", "flujo de caja", "análisis financiero", "inversión"]):
        return "finance"

    # === Contabilidad ===
    if any(word in prompt_lower for word in ["contabilidad", "contable", "normativo", "niif", "asiento"]):
        return "finance"

    # === Nómina/Payroll ===
    if any(word in prompt_lower for word in ["nómina", "payroll", "deducciones", "provisión", "cálculo de nómina"]):
        return "payroll"

    # === Prestaciones/Benefits ===
    if any(word in prompt_lower for word in ["prestación", "cesantía", "benefit", "pensión", "afiliación"]):
        return "benefits"

    # === Recruitment/Selección ===
    if any(word in prompt_lower for word in ["candidat", "reclutamiento", "hiring", "recruitment", "evaluación"]):
        return "recruitment"

    # === Compras/Procuramiento ===
    if any(word in prompt_lower for word in ["compra", "procuramiento", "proveedor", "compras", "cotización"]):
        return "compras_agent"

    # === Ventas ===
    if any(word in prompt_lower for word in ["venta", "prospecto", "pipeline", "propuesta comercial", "cierre"]):
        return "ventas_agent"

    # === CRM ===
    if any(word in prompt_lower for word in ["cliente", "crm", "relación cliente", "segmentación", "retención"]):
        return "crm_agent"

    # === Atención al Cliente ===
    if any(word in prompt_lower for word in ["consulta", "soporte", "atención", "problema", "queja", "escalamiento"]):
        return "customer_service_agent"

    # === Documentación ===
    if any(word in prompt_lower for word in ["documento", "clasificación", "retención", "archivo", "gestor documental"]):
        return "document_manager_agent"

    # === PDF Analysis ===
    if any(word in prompt_lower for word in ["pdf", "análisis pdf", "extracción", "resumen ejecutivo"]):
        return "pdf_assistant_agent"

    # Default
    return "asistente"


async def init_agents():
    """Inicializar todos los 15 agentes ELAP"""
    global system_supervisor, task_router, memory_manager
    global hr_agent, finance_agent, payroll_agent, benefits_agent, recruitment_agent
    global ceo_assistant, cfo_assistant, cmo_assistant
    global compras_agent, ventas_agent, crm_agent, customer_service_agent
    global document_manager_agent, pdf_assistant_agent, orchestrator

    # === Sistema (3) ===
    system_supervisor = SystemSupervisor(theme="andina_foods")
    task_router = TaskRouter(theme="andina_foods")
    memory_manager = MemoryManager(theme="andina_foods")

    # === Administrativo (5) ===
    hr_agent = HRAgent(theme="andina_foods")
    finance_agent = FinanceAgent(theme="andina_foods")
    payroll_agent = PayrollAgent(theme="andina_foods")
    benefits_agent = BenefitsAgent(theme="andina_foods")
    recruitment_agent = RecruitmentAgent(theme="andina_foods")

    # === Dirección (3) ===
    ceo_assistant = CEOAssistant(theme="andina_foods")
    cfo_assistant = CFOAssistant(theme="andina_foods")
    cmo_assistant = CMOAssistant(theme="andina_foods")

    # === Comercial (4) ===
    compras_agent = ComprasAgent(theme="andina_foods")
    ventas_agent = VentasAgent(theme="andina_foods")
    crm_agent = CRMAgent(theme="andina_foods")
    customer_service_agent = CustomerServiceAgent(theme="andina_foods")

    # === Documentación (2) ===
    document_manager_agent = DocumentManagerAgent(theme="andina_foods")
    pdf_assistant_agent = PDFAssistantAgent(theme="andina_foods")

    orchestrator = get_orchestrator()

    logger.info("✅ Sistema Agents (3): Supervisor, TaskRouter, Memory")
    logger.info("✅ Administrativo Agents (5): HR, Finance, Payroll, Benefits, Recruitment")
    logger.info("✅ Dirección Agents (3): CEO, CFO, CMO")
    logger.info("✅ Comercial Agents (4): Compras, Ventas, CRM, CustomerService")
    logger.info("✅ Documentación Agents (2): DocumentManager, PDFAssistant")
    logger.info("✅ Agent Orchestrator initialized (Fase 6)")
    logger.info("🚀 TOTAL: 15 agentes listos")


async def ejecutar_agente(request: web.Request) -> web.Response:
    """POST /api/agents/:agent_id/execute

    Ejecuta un agente con un prompt dado.

    Body esperado:
    {
        "prompt": "...",
        "agent_id": "hr" | "finance" | uuid (mapea a hr por defecto),
        "model": "glm4:9b",
        "history": [],
        ...
    }
    """
    try:
        data = await request.json()
        agent_id = request.match_info.get('agent_id', 'asistente')
        prompt = data.get('prompt', data.get('query', 'Hola'))

        logger.info(f"🔴 EXECUTE ENDPOINT - agent_id desde URL: '{agent_id}'")
        logger.info(f"Solicitud: {prompt[:50]}... [Agent: {agent_id}]")

        # 🧠 AGENT ORCHESTRATOR - Intent detection automático
        # Lógica: si viene agent_id específico, respetarlo; sino, detectar por intent
        if agent_id in ['hr', 'finance', 'payroll', 'benefits', 'recruitment']:
            # Agent específico por nombre - respetarlo
            intent_val = "specific_agent"
            logger.info(f"Agent específico por nombre: {agent_id}")
        elif agent_id != 'asistente' and len(agent_id) > 8:
            # Es probablemente un UUID del dashboard - detectar tipo de agente del prompt
            detected_agent_type = _detect_agent_type_from_prompt(prompt)
            agent_id = detected_agent_type
            intent_val = "dashboard_agent"
            logger.info(f"Agent detectado del dashboard: {agent_id}")
        else:
            # "asistente" o desconocido - usar Orchestrator para detectar
            detected_agent, intent = orchestrator.process_query(prompt)
            agent_id = detected_agent
            intent_val = intent.value
            logger.info(f"Intent detectado: {intent_val} → Agent: {agent_id}")

        # Mapear a agente Python especializado - 15 agentes
        agent_mapping = {
            # === Sistema ===
            'system_supervisor': system_supervisor,
            'task_router': task_router,
            'memory_manager': memory_manager,

            # === Administrativo ===
            'hr': hr_agent,
            'hr_agent': hr_agent,
            'rrhh': hr_agent,
            'finance': finance_agent,
            'finance_agent': finance_agent,
            'finanza': finance_agent,
            'payroll': payroll_agent,
            'payroll_agent': payroll_agent,
            'payroll_plugin': payroll_agent,
            'nómina': payroll_agent,
            'benefits': benefits_agent,
            'benefits_agent': benefits_agent,
            'benefits_plugin': benefits_agent,
            'prestaciones': benefits_agent,
            'recruitment': recruitment_agent,
            'recruitment_agent': recruitment_agent,
            'recruitment_plugin': recruitment_agent,
            'reclutamiento': recruitment_agent,

            # === Dirección ===
            'ceo_assistant': ceo_assistant,
            'ceo': ceo_assistant,
            'director_ejecutivo': ceo_assistant,
            'cfo_assistant': cfo_assistant,
            'cfo': cfo_assistant,
            'director_financiero': cfo_assistant,
            'cmo_assistant': cmo_assistant,
            'cmo': cmo_assistant,
            'director_marketing': cmo_assistant,

            # === Comercial ===
            'compras_agent': compras_agent,
            'compras': compras_agent,
            'procuramiento': compras_agent,
            'ventas_agent': ventas_agent,
            'ventas': ventas_agent,
            'crm_agent': crm_agent,
            'crm': crm_agent,
            'gestión_clientes': crm_agent,
            'customer_service_agent': customer_service_agent,
            'atención_cliente': customer_service_agent,
            'servicio_cliente': customer_service_agent,

            # === Documentación ===
            'document_manager_agent': document_manager_agent,
            'gestor_documental': document_manager_agent,
            'documentos': document_manager_agent,
            'pdf_assistant_agent': pdf_assistant_agent,
            'asistente_pdf': pdf_assistant_agent,
            'análisis_pdf': pdf_assistant_agent,

            # === Default ===
            'asistente': hr_agent,
            'asistente_general': hr_agent,
        }

        # Intentar mapear el agent_id
        agent = agent_mapping.get(agent_id.lower())

        if agent is None:
            # Si no se encuentra, intentar detectar del prompt
            detected_type = _detect_agent_type_from_prompt(prompt)
            agent = agent_mapping.get(detected_type.lower(), hr_agent)
            logger.info(f"Agent no encontrado '{agent_id}', detectado: {detected_type}")

        # Validar que agent no sea None
        if agent is None:
            agent = hr_agent
            logger.warning(f"Fallback a HR Agent para agent_id: {agent_id}")

        # 🏷️ Mapear agent_id a nombre legible ANTES de procesar
        print(f"🟡 ANTES DE PROCESAR - agent_id='{agent_id}'")
        agent_names = {
            'hr': 'HR Agent', 'finance': 'Finance Agent', 'payroll': 'Payroll Agent',
            'benefits': 'Benefits Agent', 'recruitment': 'Recruitment Agent',
            'ceo_assistant': 'CEO Assistant', 'cfo_assistant': 'CFO Assistant', 'cmo_assistant': 'CMO Assistant',
            'compras': 'Compras Agent', 'ventas': 'Ventas Agent', 'crm': 'CRM Agent',
            'customer_service': 'Customer Service Agent', 'document_manager': 'Document Manager',
            'pdf_assistant': 'PDF Assistant', 'system_supervisor': 'System Supervisor',
            'task_router': 'Task Router', 'memory_manager': 'Memory Manager'
        }
        agent_display_name = agent_names.get(agent_id, agent_id)
        print(f"✅ agent_display_name='{agent_display_name}', conversation_manager is None? {conversation_manager is None}")

        # Procesar query con el agente
        result = await agent.process_query(prompt)

        # Retornar respuesta en formato que espera Rust
        respuesta = result.get('message', str(result))

        # DEBUG: Log de la respuesta completa
        logger.info(f"RESPUESTA DEL AGENTE: {respuesta[:200]}...")
        if "[DESCARGAR" in respuesta:
            logger.info("✅ MARKDOWN LINK PRESENTE EN RESPUESTA")
        else:
            logger.warning("❌ MARKDOWN LINK NO ENCONTRADO EN RESPUESTA")

        print(f"🔵 COMPLETADO: agent_display_name='{agent_display_name}', conversation_manager is None? {conversation_manager is None}")

        # 💾 AUTO-CREAR Y GUARDAR EN HISTORIAL
        conversation_id = data.get('conversation_id')
        print(f"💾 conversation_manager is None? {conversation_manager is None}")
        if not conversation_id:
            # Crear conversación automáticamente con el nombre correcto del agente
            if conversation_manager is None:
                logger.error("❌ ConversationManager NO INICIALIZADO - no se puede guardar historial")
            else:
                try:
                    conversation_id = conversation_manager.create_conversation(
                        agent_id, agent_display_name,
                        title=f"Chat con {agent_display_name}"
                    )
                    logger.info(f"✅ Conversación creada automáticamente: {conversation_id} ({agent_display_name})")
                except Exception as e:
                    logger.error(f"❌ Error creando conversación: {e}")

        # Guardar mensajes en conversación
        if conversation_id and conversation_manager is not None:
            try:
                # Guardar mensaje del usuario
                conversation_manager.add_message(
                    conversation_id, 'user', prompt,
                    agent_name=agent_display_name
                )
                # Guardar respuesta del asistente
                conversation_manager.add_message(
                    conversation_id, 'assistant', respuesta,
                    agent_name=agent_display_name,
                    metadata={'intent': result.get('intent')}
                )
                logger.info(f"💾 Mensajes guardados en conversación: {conversation_id}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo guardar mensajes: {e}")

        return web.json_response({
            'agente_id': agent_id,
            'agent_name': agent_display_name,
            'estado': 'completado',
            'pasos_completados': 1,
            'progreso': 100.0,
            'respuesta': respuesta,
            'intent': result.get('intent'),
            'required_fields': result.get('required_fields'),
            'tokens': {
                'prompt': 50,
                'completion': 100,
                'total': 150
            },
            'thoughts': [
                {
                    'title': f'Agente {agent_id} procesó la solicitud',
                    'content': f'Intent: {result.get("intent", "general")}'
                }
            ]
        })

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return web.json_response({
            'error': 'Invalid JSON',
            'respuesta': 'Error: JSON inválido'
        }, status=400)
    except Exception as e:
        logger.error(f"Error executing agent: {e}")
        return web.json_response({
            'error': str(e),
            'respuesta': f'Error: {str(e)}'
        }, status=500)


async def health_check(request: web.Request) -> web.Response:
    """GET /api/health - Health check"""
    return web.json_response({
        'status': 'ok',
        'agents': ['hr', 'finance'],
        'message': 'Python REST API para agentes funcionando'
    })


async def listar_documentos(request: web.Request) -> web.Response:
    """GET /api/documents - Listar documentos generados"""
    try:
        docs_dir = Path('/tmp/elap_documents')

        if not docs_dir.exists():
            return web.json_response([])

        documentos = []
        for file_path in docs_dir.glob('*'):
            if file_path.is_file():
                stat = file_path.stat()

                # Detectar tipo por extensión
                ext = file_path.suffix.lower()
                if 'contrato' in file_path.name.lower():
                    doc_type = 'contract'
                elif 'factura' in file_path.name.lower():
                    doc_type = 'invoice'
                elif 'reporte' in file_path.name.lower():
                    doc_type = 'report'
                else:
                    doc_type = 'other'

                # Extraer nombre del empleado del filename
                # Ej: contrato_Juan_Pérez.docx → Juan Pérez
                name_without_ext = file_path.stem
                if '_' in name_without_ext:
                    employee = name_without_ext.split('_', 1)[1].replace('_', ' ')
                else:
                    employee = None

                documentos.append({
                    'filename': file_path.name,
                    'size': stat.st_size,
                    'createdAt': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'type': doc_type,
                    'employee': employee
                })

        logger.info(f"📁 Listados {len(documentos)} documentos")
        return web.json_response(documentos)

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def eliminar_documento(request: web.Request) -> web.Response:
    """DELETE /api/documents/{filename} - Eliminar documento"""
    try:
        filename = request.match_info.get('filename')

        # Validación: prevenir path traversal
        if '..' in filename or '/' in filename:
            return web.json_response({'error': 'Invalid filename'}, status=400)

        doc_path = Path('/tmp/elap_documents') / filename

        if not doc_path.exists():
            return web.json_response({'error': 'Document not found'}, status=404)

        # Eliminar archivo
        doc_path.unlink()
        logger.info(f"🗑️ Eliminado: {filename}")

        return web.json_response({'status': 'deleted', 'filename': filename})

    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def obtener_configuracion_menu(request: web.Request) -> web.Response:
    """GET /api/menu-config - Obtener configuración dinámica del menú"""
    try:
        menu_config = {
            'file': {
                'label': 'File',
                'items': [
                    {'label': 'Nuevo Agente...', 'action': 'openNewAgent', 'shortcut': '⌘N'},
                    {'label': 'Abrir Registros', 'action': 'setActiveTab:history', 'shortcut': '⌘H'},
                    {'divider': True},
                    {'label': 'Preferencias / Settings', 'action': 'openSettings', 'shortcut': '⌘,'}
                ]
            },
            'edit': {
                'label': 'Editar',
                'items': [
                    {'label': 'Limpiar Sesión Activa', 'action': 'clearSession'},
                    {'label': 'Reset Model Context', 'action': 'resetContext'},
                    {'label': 'Exportar Conversación', 'action': 'exportConversation'}
                ]
            },
            'view': {
                'label': 'Ver',
                'items': [
                    {'label': 'Chat', 'action': 'setActiveTab:chat', 'icon': 'MessageSquare'},
                    {'label': 'Panél', 'action': 'setActiveTab:dashboard', 'icon': 'BarChart2'},
                    {'label': 'Herramientas', 'action': 'setActiveTab:tools', 'icon': 'Wrench'},
                    {'label': 'Base de Conocimiento', 'action': 'setActiveTab:knowledge', 'icon': 'BookOpen'},
                    {'label': 'Documentos', 'action': 'setActiveTab:documents', 'icon': 'FileText'},
                    {'label': 'Historial', 'action': 'setActiveTab:history', 'icon': 'History'}
                ]
            },
            'agents': {
                'label': 'Agentes',
                'items': [
                    {'label': 'Crear Agente', 'action': 'openNewAgent'},
                    {'label': 'Reload Profiles', 'action': 'reloadProfiles'},
                    {'label': 'Model Manager', 'action': 'openModelManager'}
                ]
            },
            'tools': {
                'label': 'Tools',
                'items': [
                    {'label': 'Mercado de Herramientas', 'action': 'setActiveTab:tools'},
                    {'label': 'Visual Chain Builder', 'action': 'openChainBuilder'}
                ]
            },
            'help': {
                'label': 'Ayuda',
                'items': [
                    {'label': 'Documentación ELAP', 'action': 'openDocs'},
                    {'label': 'Test Ollama', 'action': 'testOllama'},
                    {'label': 'Acerca de ELAP v1.5.0', 'action': 'aboutDialog'}
                ]
            }
        }

        logger.info("📋 Configuración del menú obtenida")
        return web.json_response(menu_config)

    except Exception as e:
        logger.error(f"Error getting menu config: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def obtener_fuentes_conocimiento(request: web.Request) -> web.Response:
    """GET /api/knowledge-sources - Obtener fuentes de conocimiento RAG"""
    try:
        sources = [
            {
                'id': '1',
                'name': 'Política de Recursos Humanos',
                'type': 'Document',
                'status': 'Active',
                'vector_count': 2850,
                'file_size': '4.2 MB',
                'last_updated': '2026-08-06T14:30:00Z',
                'description': 'Manual de políticas HR con 50+ documentos'
            },
            {
                'id': '2',
                'name': 'Base Histórica de Contratos',
                'type': 'Database',
                'status': 'Active',
                'vector_count': 1560,
                'file_size': '8.7 MB',
                'last_updated': '2026-08-07T10:15:00Z',
                'description': 'Histórico de 200+ contratos anteriores'
            },
            {
                'id': '3',
                'name': 'Qdrant Vector Store',
                'type': 'Vector DB',
                'status': 'Active',
                'vector_count': 4200,
                'file_size': '22.5 MB',
                'last_updated': '2026-08-08T09:00:00Z',
                'description': 'Vector embeddings de todos los documentos'
            }
        ]

        logger.info(f"📚 Fuentes de conocimiento obtenidas: {len(sources)}")
        return web.json_response(sources)

    except Exception as e:
        logger.error(f"Error getting knowledge sources: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def obtener_historial(request: web.Request) -> web.Response:
    """GET /api/history - Obtener historial de conversaciones"""
    try:
        from datetime import datetime, timedelta

        # Generar historial simulado basado en agentes reales
        history = [
            {
                'id': '1',
                'agent_id': 'hr',
                'agent_name': 'HR Agent',
                'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
                'type': 'contract',
                'user_message': 'Empresa: Andina Foods / Empleado: Juan Pérez / Cargo: Gerente de Ventas / Salario: 5.000.000',
                'agent_response': '✅ Contrato generado para Juan Pérez',
                'status': 'completed',
                'icon': '📄'
            },
            {
                'id': '2',
                'agent_id': 'finance',
                'agent_name': 'Finance Agent',
                'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
                'type': 'query',
                'user_message': '¿Cuál es el estado de las facturas pendientes?',
                'agent_response': 'Se encontraron 3 facturas pendientes por valor total de $15.000.000',
                'status': 'completed',
                'icon': '💬'
            },
            {
                'id': '3',
                'agent_id': 'hr',
                'agent_name': 'HR Agent',
                'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
                'type': 'contract',
                'user_message': 'Empresa: Andina Foods / Empleado: María García / Cargo: Analista / Salario: 3.500.000',
                'agent_response': '✅ Contrato generado para María García',
                'status': 'completed',
                'icon': '📄'
            },
            {
                'id': '4',
                'agent_id': 'finance',
                'agent_name': 'Finance Agent',
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'type': 'report',
                'user_message': 'Genera un reporte mensual de ventas',
                'agent_response': '📊 Reporte generado: Q3 2026 Sales Summary',
                'status': 'completed',
                'icon': '📊'
            },
            {
                'id': '5',
                'agent_id': 'hr',
                'agent_name': 'HR Agent',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'type': 'contract',
                'user_message': 'Empresa: Andina Foods / Empleado: Carlos López / Cargo: Ingeniero / Salario: 4.000.000',
                'agent_response': '✅ Contrato generado para Carlos López',
                'status': 'completed',
                'icon': '📄'
            }
        ]

        logger.info(f"📜 Historial obtenido: {len(history)} items")
        return web.json_response(history)

    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def obtener_dashboard_info(request: web.Request) -> web.Response:
    """GET /api/dashboard - Obtener información del dashboard"""
    try:
        import psutil
        import platform

        # Info del sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Obtener estado de batería
        try:
            battery = psutil.sensors_battery()
            if battery:
                battery_percent = int(battery.percent)
                battery_charging = battery.power_plugged
                battery_status = 'Charging' if battery_charging else 'Discharging'
            else:
                # Si no hay batería, asumir que es AC
                battery_percent = 100
                battery_charging = True
                battery_status = 'AC Power'
        except (AttributeError, TypeError):
            battery_percent = 100
            battery_charging = True
            battery_status = 'AC Power'

        dashboard_info = {
            'user': {
                'username': 'fabian',
                'role': 'Admin',
                'display_name': 'Fabian Robles'
            },
            'notifications': {
                'count': 3,
                'items': [
                    {'id': '1', 'title': 'HRAgent completó contrato', 'timestamp': '5 min ago'},
                    {'id': '2', 'title': 'FinanceAgent procesó factura', 'timestamp': '12 min ago'},
                    {'id': '3', 'title': 'Ollama modelo cargado', 'timestamp': '1 hora ago'}
                ]
            },
            'battery': {
                'percent': battery_percent,
                'charging': battery_charging,
                'status': battery_status
            },
            'agents': [
                {
                    'id': 'hr',
                    'name': 'HR Agent',
                    'role': 'Recursos Humanos',
                    'status': 'online',
                    'icon': '👨‍💼',
                    'tasks_completed': 24,
                    'documents_generated': 6
                },
                {
                    'id': 'finance',
                    'name': 'Finance Agent',
                    'role': 'Finanzas',
                    'status': 'online',
                    'icon': '💰',
                    'tasks_completed': 12,
                    'documents_generated': 0
                }
            ],
            'hardware': {
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'memory_used_gb': round(memory.used / (1024**3), 2),
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'disk_percent': round(disk.percent, 1),
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'platform': platform.system(),
                'processor': platform.processor()
            },
            'runtime': {
                'version': 'v0.1.0',
                'uptime_seconds': 3600,
                'documents_directory': '/tmp/elap_documents',
                'api_port': 5000
            }
        }

        logger.info("📊 Dashboard info obtenida")
        return web.json_response(dashboard_info)

    except Exception as e:
        logger.error(f"Error getting dashboard info: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def listar_herramientas(request: web.Request) -> web.Response:
    """GET /api/tools - Listar herramientas disponibles"""
    try:
        herramientas = [
            {
                'id': 'generate_contract',
                'name': 'Generar Contrato',
                'description': 'Generar contratos laborales con IA',
                'category': 'Recursos Humanos',
                'enabled': True,
                'icon': '📄',
                'parameters': [
                    {'name': 'Nombre del empleado', 'type': 'string', 'required': True},
                    {'name': 'Cargo', 'type': 'string', 'required': True},
                    {'name': 'Salario', 'type': 'number', 'required': True}
                ]
            },
            {
                'id': 'generate_report',
                'name': 'Generar Reporte',
                'description': 'Generar reportes financieros profesionales',
                'category': 'Finanzas',
                'enabled': True,
                'icon': '📊',
                'parameters': [
                    {'name': 'Período', 'type': 'string', 'required': True},
                    {'name': 'Tipo de reporte', 'type': 'string', 'required': True}
                ]
            },
            {
                'id': 'generate_invoice',
                'name': 'Generar Factura',
                'description': 'Generar facturas profesionales',
                'category': 'Finanzas',
                'enabled': True,
                'icon': '🧾',
                'parameters': [
                    {'name': 'Número de factura', 'type': 'string', 'required': True},
                    {'name': 'Cliente', 'type': 'string', 'required': True}
                ]
            },
            {
                'id': 'search_documents',
                'name': 'Buscar Documentos',
                'description': 'Buscar en el repositorio de documentos',
                'category': 'Búsqueda',
                'enabled': True,
                'icon': '🔍',
                'parameters': [
                    {'name': 'Términos de búsqueda', 'type': 'string', 'required': True}
                ]
            },
            {
                'id': 'rag_query',
                'name': 'Consultar Base de Conocimiento',
                'description': 'Consultar la base de conocimiento empresarial',
                'category': 'Conocimiento',
                'enabled': True,
                'icon': '🧠',
                'parameters': [
                    {'name': 'Pregunta', 'type': 'string', 'required': True}
                ]
            }
        ]

        logger.info(f"🛠️ Listadas {len(herramientas)} herramientas")
        return web.json_response(herramientas)

    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def obtener_documento(request: web.Request) -> web.Response:
    """GET /api/documents/{filename} - Obtener metadatos de documento"""
    try:
        filename = request.match_info.get('filename')

        # Validación
        if '..' in filename or '/' in filename:
            return web.json_response({'error': 'Invalid filename'}, status=400)

        doc_path = Path('/tmp/elap_documents') / filename

        if not doc_path.exists():
            return web.json_response({'error': 'Document not found'}, status=404)

        stat = doc_path.stat()

        return web.json_response({
            'filename': filename,
            'size': stat.st_size,
            'createdAt': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modifiedAt': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'url': f'/documents/download/{filename}'
        })

    except Exception as e:
        logger.error(f"Error getting document: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def generar_reporte_html(request: web.Request) -> web.Response:
    """POST /api/reports/{agent_id} - Generar reporte HTML profesional

    Body esperado:
    {
        "title": "Reporte Financiero",
        "subtitle": "Análisis Q3 2026",
        "executive_summary": "Texto del resumen ejecutivo",
        "kpi_data": [
            {"label": "Ingresos", "value": "$21.2M", "change": "↑ 12%", "status": "positive"}
        ],
        "sections": [
            {
                "title": "Análisis Detallado",
                "content": "Contenido aquí",
                "table": {"headers": [...], "rows": [...]}
            }
        ],
        "recommendations": ["Rec 1", "Rec 2"],
        "next_steps_short": ["Paso 1"],
        "next_steps_medium": ["Paso 2"]
    }
    """
    try:
        from .templates.report_generator import ReportGenerator, ReportData, KPICard

        agent_id = request.match_info.get('agent_id', 'asistente')
        data = await request.json()

        # Construir KPI cards
        kpi_cards = []
        for kpi in data.get('kpi_data', []):
            kpi_cards.append(KPICard(
                label=kpi.get('label', 'Métrica'),
                value=kpi.get('value', '-'),
                change=kpi.get('change', '→'),
                status=kpi.get('status', 'positive'),
                icon=kpi.get('icon', '📊')
            ))

        # Construir report data
        report_data = ReportData(
            title=data.get('title', 'Reporte Ejecutivo'),
            subtitle=data.get('subtitle', 'Análisis profesional'),
            agent_name=agent_id,
            kpi_cards=kpi_cards,
            executive_summary=data.get('executive_summary', 'Resumen pendiente'),
            sections=data.get('sections', []),
            recommendations=data.get('recommendations', []),
            next_steps_short=data.get('next_steps_short', []),
            next_steps_medium=data.get('next_steps_medium', []),
        )

        # Generar HTML
        generator = ReportGenerator()
        html = generator.generate_html(report_data)

        # Guardar temporalmente
        import hashlib
        report_id = hashlib.md5(f"{agent_id}{datetime.now()}".encode()).hexdigest()[:8]
        report_filename = f"reporte_{agent_id}_{report_id}.html"
        report_path = Path('/tmp/elap_reports') / report_filename

        # Crear directorio si no existe
        report_path.parent.mkdir(parents=True, exist_ok=True)

        # Guardar archivo
        generator.save_html(html, str(report_path))

        logger.info(f"✅ Reporte HTML generado: {report_filename}")

        return web.json_response({
            'status': 'success',
            'report_id': report_id,
            'filename': report_filename,
            'filepath': str(report_path),
            'html': html,
            'url': f'/api/reports/download/{report_filename}'
        })

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return web.json_response({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


async def descargar_reporte(request: web.Request) -> web.FileResponse:
    """GET /api/reports/download/{filename} - Descargar reporte HTML"""
    try:
        filename = request.match_info.get('filename')

        if '..' in filename or '/' in filename:
            return web.json_response({'error': 'Invalid filename'}, status=400)

        report_path = Path('/tmp/elap_reports') / filename

        if not report_path.exists():
            return web.json_response({'error': 'Report not found'}, status=404)

        logger.info(f"📥 Descargando reporte: {filename}")

        return web.FileResponse(
            report_path,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )

    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        return web.json_response({'error': str(e)}, status=500)


@web.middleware
async def add_cors_headers(request: web.Request, handler) -> web.Response:
    """Middleware para agregar headers CORS"""
    # Manejar OPTIONS requests (CORS preflight)
    if request.method == 'OPTIONS':
        return web.Response(
            status=200,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS, PATCH, PUT',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Max-Age': '3600'
            }
        )

    # Procesar request normal
    response = await handler(request)

    # Agregar headers CORS a la respuesta
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS, PATCH, PUT'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

    return response


# === GENERADORES DE DOCUMENTOS ===

async def generar_documento_pdf(request: web.Request) -> web.Response:
    """Genera PDF desde respuesta de agente"""
    try:
        data = await request.json()
        agent_name = data.get('agent_name', 'Unknown')
        title = data.get('title', 'Reporte')
        content = data.get('content', '')

        filepath = doc_generator.generate_pdf(agent_name, title, content)

        with open(filepath, 'rb') as f:
            pdf_data = f.read()

        return web.Response(
            body=pdf_data,
            content_type='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{agent_name}_report.pdf"'
            }
        )
    except Exception as e:
        logger.error(f"❌ Error generando PDF: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def generar_documento_word(request: web.Request) -> web.Response:
    """Genera Word desde respuesta de agente"""
    try:
        data = await request.json()
        agent_name = data.get('agent_name', 'Unknown')
        title = data.get('title', 'Reporte')
        content = data.get('content', '')

        filepath = doc_generator.generate_word(agent_name, title, content)

        with open(filepath, 'rb') as f:
            word_data = f.read()

        return web.Response(
            body=word_data,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            headers={
                'Content-Disposition': f'attachment; filename="{agent_name}_report.docx"'
            }
        )
    except Exception as e:
        logger.error(f"❌ Error generando Word: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def listar_conversaciones(request: web.Request) -> web.Response:
    """Lista conversaciones recientes"""
    try:
        convs = conversation_manager.get_recent_conversations(limit=20)
        logger.info(f"📋 {len(convs)} conversaciones listadas")
        return web.json_response({"conversations": convs})
    except Exception as e:
        logger.error(f"Error listando conversaciones: {e}")
        return web.json_response({"error": str(e)}, status=500)


async def obtener_conversacion(request: web.Request) -> web.Response:
    """Obtiene una conversación completa con mensajes"""
    try:
        conv_id = request.match_info.get('conversation_id')
        conv = conversation_manager.get_conversation(conv_id)

        if not conv:
            return web.json_response({"error": "Conversación no encontrada"}, status=404)

        logger.info(f"📖 Conversación cargada: {conv_id}")
        return web.json_response(conv)
    except Exception as e:
        logger.error(f"Error obteniendo conversación: {e}")
        return web.json_response({"error": str(e)}, status=500)


async def crear_conversacion(request: web.Request) -> web.Response:
    """Crea nueva conversación"""
    try:
        data = await request.json()
        agent_id = data.get('agent_id', 'unknown')
        agent_name = data.get('agent_name', 'Asistente')
        title = data.get('title')

        conv_id = conversation_manager.create_conversation(agent_id, agent_name, title)
        logger.info(f"✅ Nueva conversación: {conv_id}")

        return web.json_response({
            "id": conv_id,
            "title": title or f"Chat con {agent_name}",
            "agent_name": agent_name
        })
    except Exception as e:
        logger.error(f"Error creando conversación: {e}")
        return web.json_response({"error": str(e)}, status=500)


async def agregar_mensaje(request: web.Request) -> web.Response:
    """Agrega mensaje a conversación"""
    try:
        conv_id = request.match_info.get('conversation_id')
        data = await request.json()

        role = data.get('role', 'user')  # 'user' o 'assistant'
        content = data.get('content', '')
        agent_name = data.get('agent_name')
        metadata = data.get('metadata')

        msg_id = conversation_manager.add_message(
            conv_id, role, content, agent_name, metadata
        )

        logger.info(f"💬 Mensaje agregado: {msg_id}")
        return web.json_response({"id": msg_id, "success": True})
    except Exception as e:
        logger.error(f"Error agregando mensaje: {e}")
        return web.json_response({"error": str(e)}, status=500)


async def eliminar_conversacion(request: web.Request) -> web.Response:
    """Elimina una conversación"""
    try:
        conv_id = request.match_info.get('conversation_id')
        conversation_manager.delete_conversation(conv_id)
        logger.info(f"🗑️ Conversación eliminada: {conv_id}")
        return web.json_response({"success": True})
    except Exception as e:
        logger.error(f"Error eliminando conversación: {e}")
        return web.json_response({"error": str(e)}, status=500)


async def estadisticas_conversaciones(request: web.Request) -> web.Response:
    """Obtiene estadísticas de conversaciones"""
    try:
        stats = conversation_manager.get_stats()
        logger.info("📊 Estadísticas de conversaciones obtenidas")
        return web.json_response(stats)
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return web.json_response({"error": str(e)}, status=500)


async def generar_documento_excel(request: web.Request) -> web.Response:
    """Genera Excel desde respuesta de agente"""
    try:
        data = await request.json()
        agent_name = data.get('agent_name', 'Unknown')
        title = data.get('title', 'Reporte')
        content = data.get('content', '')

        filepath = doc_generator.generate_excel(agent_name, title, content)

        with open(filepath, 'rb') as f:
            excel_data = f.read()

        return web.Response(
            body=excel_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename="{agent_name}_report.xlsx"'
            }
        )
    except Exception as e:
        logger.error(f"❌ Error generando Excel: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def listar_agentes(request: web.Request) -> web.Response:
    """Lista todos los 15 agentes ELAP disponibles"""
    try:
        agents = [
            # === Sistema ===
            {'id': 'system_supervisor', 'nombre': 'System Supervisor', 'rol': 'Sistema', 'estado': 'Activo', 'modelo': 'qwen3:8b'},
            {'id': 'task_router', 'nombre': 'Task Router', 'rol': 'Sistema', 'estado': 'Activo', 'modelo': 'qwen3:8b'},
            {'id': 'memory_manager', 'nombre': 'Memory Manager', 'rol': 'Sistema', 'estado': 'Activo', 'modelo': 'qwen3:8b'},

            # === Administrativo ===
            {'id': 'hr', 'nombre': 'HR Agent', 'rol': 'Recursos Humanos', 'estado': 'Activo', 'modelo': 'glm4:9b'},
            {'id': 'finance', 'nombre': 'Finance Agent', 'rol': 'Finanzas', 'estado': 'Activo', 'modelo': 'glm4:9b'},
            {'id': 'payroll', 'nombre': 'Payroll Agent', 'rol': 'Nómina', 'estado': 'Activo', 'modelo': 'glm4:9b'},
            {'id': 'benefits', 'nombre': 'Benefits Agent', 'rol': 'Prestaciones', 'estado': 'Activo', 'modelo': 'glm4:9b'},
            {'id': 'recruitment', 'nombre': 'Recruitment Agent', 'rol': 'Reclutamiento', 'estado': 'Activo', 'modelo': 'glm4:9b'},

            # === Dirección ===
            {'id': 'ceo_assistant', 'nombre': 'CEO Assistant', 'rol': 'Dirección Ejecutiva', 'estado': 'Activo', 'modelo': 'glm4:9b'},
            {'id': 'cfo_assistant', 'nombre': 'CFO Assistant', 'rol': 'Dirección Financiera', 'estado': 'Activo', 'modelo': 'glm4:9b'},
            {'id': 'cmo_assistant', 'nombre': 'CMO Assistant', 'rol': 'Dirección Marketing', 'estado': 'Activo', 'modelo': 'glm4:9b'},

            # === Comercial ===
            {'id': 'compras', 'nombre': 'Compras Agent', 'rol': 'Procuramiento', 'estado': 'Activo', 'modelo': 'glm4:9b'},
            {'id': 'ventas', 'nombre': 'Ventas Agent', 'rol': 'Ventas', 'estado': 'Activo', 'modelo': 'glm4:9b'},
            {'id': 'crm', 'nombre': 'CRM Agent', 'rol': 'Gestión de Clientes', 'estado': 'Activo', 'modelo': 'glm4:9b'},
            {'id': 'customer_service', 'nombre': 'Customer Service Agent', 'rol': 'Servicio al Cliente', 'estado': 'Activo', 'modelo': 'glm4:9b'},

            # === Documentación ===
            {'id': 'document_manager', 'nombre': 'Document Manager', 'rol': 'Gestión Documental', 'estado': 'Activo', 'modelo': 'glm4:9b'},
            {'id': 'pdf_assistant', 'nombre': 'PDF Assistant', 'rol': 'Análisis PDF', 'estado': 'Activo', 'modelo': 'glm4:9b'},
        ]

        logger.info(f"📋 {len(agents)} agentes listados")
        return web.json_response({'agentes': agents, 'total': len(agents)})
    except Exception as e:
        logger.error(f"Error listando agentes: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def obtener_datos_empresa(request: web.Request) -> web.Response:
    """Obtiene datos de la empresa desde PostgreSQL para agentes

    Query params:
    - tabla: employees, clients, products, transactions, evaluations, projects
    - filtro: JSON con filtros opcionales
    - limite: máximo de registros (default 100)
    """
    try:
        tabla = request.query.get('tabla', 'employees')
        limite = int(request.query.get('limite', 100))

        # Conectar a PostgreSQL
        import psycopg2
        conn = psycopg2.connect(
            host="localhost", port=5432, database="elap_db",
            user="elap_user", password="elap_secure_pass_2026"
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Queries seguras por tabla
        queries = {
            'employees': f"SELECT * FROM employees LIMIT {limite}",
            'clients': f"SELECT * FROM clients ORDER BY ventas_2024 DESC LIMIT {limite}",
            'products': f"SELECT * FROM products ORDER BY stock_actual ASC LIMIT {limite}",
            'transactions': f"SELECT * FROM transactions ORDER BY fecha DESC LIMIT {limite}",
            'evaluations': f"SELECT * FROM evaluations ORDER BY puntaje DESC LIMIT {limite}",
            'projects': f"SELECT * FROM projects ORDER BY avance_pct DESC LIMIT {limite}",
            'resumen': """
                SELECT
                    (SELECT COUNT(*) FROM employees) as total_empleados,
                    (SELECT COUNT(*) FROM clients) as total_clientes,
                    (SELECT COUNT(*) FROM products) as total_productos,
                    (SELECT COUNT(*) FROM transactions) as total_transacciones,
                    (SELECT SUM(valor_total) FROM transactions) as ingresos_totales,
                    (SELECT AVG(puntaje) FROM evaluations)::INT as puntaje_promedio_evaluaciones
            """
        }

        if tabla not in queries:
            return web.json_response({'error': f'Tabla no soportada: {tabla}'}, status=400)

        cursor.execute(queries[tabla])

        # Convertir resultados
        if tabla == 'resumen':
            resultado = dict(cursor.fetchone())
        else:
            filas = cursor.fetchall()
            resultado = [dict(fila) for fila in filas]

        # Convertir tipos no serializables
        import json
        from decimal import Decimal
        from datetime import date

        def convertir_tipos(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, date):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convertir_tipos(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convertir_tipos(item) for item in obj]
            return obj

        resultado = convertir_tipos(resultado)

        cursor.close()
        conn.close()

        logger.info(f"📊 Datos de {tabla} enviados ({len(resultado) if isinstance(resultado, list) else 1} registros)")
        return web.json_response({'tabla': tabla, 'datos': resultado})

    except Exception as e:
        logger.error(f"Error obteniendo datos: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def start_rest_server(host: str = '0.0.0.0', port: int = 5000):
    """Inicia el servidor REST para exponer agentes"""

    await init_agents()

    app = web.Application(middlewares=[add_cors_headers])

    # Rutas
    app.router.add_get('/api/health', health_check)
    app.router.add_get('/api/agents', listar_agentes)
    app.router.add_post('/api/agents/{agent_id}/execute', ejecutar_agente)
    app.router.add_get('/api/documents', listar_documentos)
    app.router.add_get('/api/documents/{filename}', obtener_documento)
    app.router.add_delete('/api/documents/{filename}', eliminar_documento)
    app.router.add_get('/api/tools', listar_herramientas)
    app.router.add_get('/api/dashboard', obtener_dashboard_info)
    app.router.add_get('/api/history', obtener_historial)
    app.router.add_get('/api/knowledge-sources', obtener_fuentes_conocimiento)
    app.router.add_get('/api/menu-config', obtener_configuracion_menu)

    # === Nuevas rutas para reportes profesionales ===
    app.router.add_post('/api/reports/{agent_id}', generar_reporte_html)
    app.router.add_get('/api/reports/download/{filename}', descargar_reporte)

    # === Generadores de documentos (PDF, Word, Excel) ===
    app.router.add_post('/api/documents/pdf', generar_documento_pdf)
    app.router.add_post('/api/documents/word', generar_documento_word)
    app.router.add_post('/api/documents/excel', generar_documento_excel)

    # === Historial de conversaciones (NUEVO) ===
    app.router.add_get('/api/conversations', listar_conversaciones)
    app.router.add_post('/api/conversations', crear_conversacion)
    app.router.add_get('/api/conversations/{conversation_id}', obtener_conversacion)
    app.router.add_post('/api/conversations/{conversation_id}/messages', agregar_mensaje)
    app.router.add_delete('/api/conversations/{conversation_id}', eliminar_conversacion)
    app.router.add_get('/api/conversations/stats', estadisticas_conversaciones)

    # === Datos de empresa (PostgreSQL) ===
    app.router.add_get('/api/data/empresa', obtener_datos_empresa)

    # === CORS manejado por middleware ===
    # (El middleware add_cors_headers agrega headers CORS a todas las respuestas)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host, port)
    await site.start()

    logger.info(f"🚀 REST API server iniciado en http://{host}:{port}")
    logger.info(f"   POST /api/agents/{{agent_id}}/execute - Ejecutar agente")
    logger.info(f"   GET /api/health - Health check")
    logger.info(f"   GET /api/dashboard - Info del dashboard")
    logger.info(f"   GET /api/documents - Listar documentos")
    logger.info(f"   GET /api/documents/{{filename}} - Obtener documento")
    logger.info(f"   DELETE /api/documents/{{filename}} - Eliminar documento")
    logger.info(f"   GET /api/tools - Listar herramientas")
    logger.info(f"   GET /api/history - Historial de conversaciones")
    logger.info(f"   GET /api/knowledge-sources - Fuentes de conocimiento")
    logger.info(f"   GET /api/menu-config - Configuración del menú")
    logger.info(f"   POST /api/reports/{{agent_id}} - Generar reporte HTML profesional")
    logger.info(f"   GET /api/reports/download/{{filename}} - Descargar reporte HTML")
    logger.info(f"   GET /api/conversations - Listar conversaciones")
    logger.info(f"   POST /api/conversations - Crear nueva conversación")
    logger.info(f"   GET /api/conversations/{{conversation_id}} - Obtener conversación")
    logger.info(f"   POST /api/conversations/{{conversation_id}}/messages - Agregar mensaje")
    logger.info(f"   DELETE /api/conversations/{{conversation_id}} - Eliminar conversación")
    logger.info(f"   GET /api/data/empresa?tabla=<tabla>&limite=<n> - Obtener datos de empresa")

    # Mantener el servidor corriendo
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("REST server shutdown")
    finally:
        await runner.cleanup()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    asyncio.run(start_rest_server())
