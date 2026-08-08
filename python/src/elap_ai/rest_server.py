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

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host, port)
    await site.start()

    logger.info(f"🚀 REST API server iniciado en http://{host}:{port}")
    logger.info(f"   POST /api/agents/{{agent_id}}/execute - Ejecutar agente")
    logger.info(f"   GET /api/health - Health check")
    logger.info(f"   GET /api/documents - Listar documentos")
    logger.info(f"   GET /api/documents/{{filename}} - Obtener documento")
    logger.info(f"   DELETE /api/documents/{{filename}} - Eliminar documento")

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
