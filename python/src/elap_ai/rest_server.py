"""REST API server para exponer agentes Python

Este servidor REST permite que el Rust backend comunique con los agentes Python.
Es una solución temporal mientras el gRPC está siendo habilitado.
"""

import asyncio
import logging
from aiohttp import web
import json
from typing import Optional
from pathlib import Path
import os
from datetime import datetime

from .agents.hr_agent import HRAgent
from .agents.finance_agent import FinanceAgent

logger = logging.getLogger(__name__)

# Inicializar agentes globales
hr_agent = None
finance_agent = None


async def init_agents():
    """Inicializar agentes"""
    global hr_agent, finance_agent
    hr_agent = HRAgent(theme="andina_foods")
    finance_agent = FinanceAgent(theme="andina_foods")
    logger.info("✅ Agents initialized: HRAgent, FinanceAgent")


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
        agent_id = request.match_info.get('agent_id', 'hr')
        prompt = data.get('prompt', 'Hola')

        logger.info(f"Ejecutando agente {agent_id} con prompt: {prompt[:50]}...")

        # Mapear agent_id - si es UUID o desconocido, usar detección por contexto
        # Si contiene UUID, asumir HR (default)
        if agent_id == 'hr' or len(agent_id) > 20:  # UUID típicamente es más largo
            agent = hr_agent
            agent_id = 'hr'
        elif agent_id == 'finance':
            agent = finance_agent
        else:
            # Intentar detectar por contenido del prompt
            prompt_lower = prompt.lower()
            if any(word in prompt_lower for word in ['factura', 'invoice', 'reporte', 'report', 'finanza', 'finance']):
                agent = finance_agent
                agent_id = 'finance'
            else:
                agent = hr_agent
                agent_id = 'hr'

            logger.info(f"Detectado agente por contenido: {agent_id}")

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

        return web.json_response({
            'agente_id': agent_id,
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

        dashboard_info = {
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


async def add_cors_headers(request: web.Request, handler) -> web.Response:
    """Middleware para agregar headers CORS"""
    # Manejar OPTIONS requests (CORS preflight)
    if request.method == 'OPTIONS':
        return web.Response(
            status=200,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )

    # Procesar request normal
    response = await handler(request)

    # Agregar headers CORS a la respuesta
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

    return response


async def start_rest_server(host: str = '0.0.0.0', port: int = 5000):
    """Inicia el servidor REST para exponer agentes"""

    await init_agents()

    app = web.Application(middlewares=[
        web.middleware(add_cors_headers)
    ])

    # Rutas
    app.router.add_get('/api/health', health_check)
    app.router.add_post('/api/agents/{agent_id}/execute', ejecutar_agente)
    app.router.add_get('/api/documents', listar_documentos)
    app.router.add_get('/api/documents/{filename}', obtener_documento)
    app.router.add_delete('/api/documents/{filename}', eliminar_documento)
    app.router.add_get('/api/tools', listar_herramientas)
    app.router.add_get('/api/dashboard', obtener_dashboard_info)
    app.router.add_get('/api/history', obtener_historial)
    app.router.add_get('/api/knowledge-sources', obtener_fuentes_conocimiento)
    app.router.add_get('/api/menu-config', obtener_configuracion_menu)

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
