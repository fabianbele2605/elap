"""
Ejemplos de handlers REST usando el framework de error handling.

Estos ejemplos muestran los patrones recomendados para:
1. Validación de entrada
2. Verificación de recursos
3. Manejo de errores externos
4. Operaciones asíncronas con timeout
5. Respuestas HTTP estándar
"""

import asyncio
from aiohttp import web
from typing import Dict, Any, Optional

from .api_response import (
    handle_api_errors,
    success_response,
    created_response,
    accepted_response,
    error_response,
)
from .errors import (
    ValidationError,
    AgentNotFound,
    AgentTimeout,
    AgentExecutionFailed,
    DatabaseError,
    ElapException,
)


# ============================================================================
# === Ejemplo 1: Validación de entrada
# ============================================================================

@handle_api_errors()
async def crear_agente_handler(request: web.Request) -> web.Response:
    """
    POST /api/agents

    Patrón: Validación de entrada

    Antes:
        async def crear_agente(request):
            data = await request.json()
            try:
                agente = crear_agente_internal(data)
                return web.json_response({"agente": agente}, status=201)
            except Exception as e:
                return web.json_response(
                    {"error": str(e)},
                    status=400
                )

    Después:
        @handle_api_errors()
        async def crear_agente(request):
            data = await request.json()

            # ✅ Validar
            if not data.get('nombre'):
                raise ValidationError("Name is required")
            if not data.get('rol'):
                raise ValidationError("Role is required")
            if len(data['nombre']) > 256:
                raise ValidationError("Name too long (max 256 chars)")

            # ✅ Crear
            agente = crear_agente_internal(data)

            # ✅ Retornar
            return created_response(data=agente)
    """
    data = await request.json()

    # ✅ Validar entrada
    if not data.get('nombre'):
        raise ValidationError("Name is required")
    if not data.get('rol'):
        raise ValidationError("Role is required")
    if len(data['nombre']) > 256:
        raise ValidationError("Name too long (max 256 chars)")

    # ✅ Crear agente (simulado)
    agente = {
        'id': 'agent_123',
        'nombre': data['nombre'],
        'rol': data['rol'],
        'estado': 'creado',
    }

    # ✅ Retornar respuesta
    return created_response(
        data=agente,
        message=f"Agent {data['nombre']} created successfully"
    )


# ============================================================================
# === Ejemplo 2: Verificar recurso existe
# ============================================================================

@handle_api_errors()
async def get_agente_handler(request: web.Request) -> web.Response:
    """
    GET /api/agents/{agent_id}

    Patrón: Verificar que recurso existe

    Antes:
        async def get_agente(request):
            agent_id = request.match_info['agent_id']
            agente = repo.get(agent_id)
            if not agente:
                return web.json_response({"error": "Not found"}, status=404)
            return web.json_response(agente)

    Después:
        @handle_api_errors()
        async def get_agente(request):
            agent_id = request.match_info['agent_id']

            # ✅ Obtener
            agente = repo.get(agent_id)
            if not agente:
                raise AgentNotFound(f"Agent {agent_id} not found")

            # ✅ Retornar
            return success_response(data=agente)
    """
    agent_id = request.match_info.get('agent_id')

    # ✅ Validar parámetro
    if not agent_id:
        raise ValidationError("Agent ID is required")

    # ✅ Obtener recurso (simulado)
    if agent_id == 'valid_agent':
        agente = {
            'id': agent_id,
            'nombre': 'Test Agent',
            'rol': 'sales',
            'estado': 'activo',
        }
    else:
        raise AgentNotFound(f"Agent {agent_id} not found")

    # ✅ Retornar respuesta
    return success_response(data=agente)


# ============================================================================
# === Ejemplo 3: Ejecutar operación con timeout
# ============================================================================

@handle_api_errors()
async def ejecutar_agente_handler(request: web.Request) -> web.Response:
    """
    POST /api/agents/{agent_id}/execute

    Patrón: Ejecutar operación con timeout

    Antes:
        async def ejecutar_agente(request):
            try:
                data = await request.json()
                agent_id = request.match_info['agent_id']
                result = await agent.execute(data['prompt'])
                return web.json_response({"resultado": result})
            except asyncio.TimeoutError:
                return web.json_response({"error": "timeout"}, status=504)
            except Exception as e:
                return web.json_response({"error": str(e)}, status=500)

    Después:
        @handle_api_errors()
        async def ejecutar_agente(request):
            data = await request.json()
            agent_id = request.match_info['agent_id']

            # ✅ Validar
            if not data.get('prompt'):
                raise ValidationError("Prompt is required")

            # ✅ Obtener agente
            agente = repo.get(agent_id)
            if not agente:
                raise AgentNotFound(f"Agent {agent_id} not found")

            # ✅ Ejecutar con timeout
            try:
                timeout = data.get('timeout_ms', 30000) / 1000
                result = await asyncio.wait_for(
                    agente.execute(data['prompt']),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                raise AgentTimeout(f"Execution timeout after {timeout}s")
            except Exception as e:
                raise AgentExecutionFailed(str(e))

            # ✅ Retornar respuesta
            return success_response(data={
                'agent_id': agent_id,
                'resultado': result,
                'duracion_ms': 1500,
            })
    """
    data = await request.json()
    agent_id = request.match_info.get('agent_id', 'default')

    # ✅ Validar entrada
    if not data.get('prompt'):
        raise ValidationError("Prompt is required")

    # ✅ Validar timeout
    timeout_ms = data.get('timeout_ms', 30000)
    if timeout_ms < 1000:
        raise ValidationError("Timeout must be at least 1000ms")

    # ✅ Obtener agente (simulado)
    if agent_id not in ['hr', 'finance']:
        raise AgentNotFound(f"Agent {agent_id} not found")

    # ✅ Ejecutar con timeout
    try:
        timeout = timeout_ms / 1000
        # Simular ejecución del agente
        await asyncio.sleep(0.1)
        resultado = f"Resultado para: {data['prompt'][:50]}..."
    except asyncio.TimeoutError:
        raise AgentTimeout(f"Execution timeout after {timeout}s")
    except Exception as e:
        raise AgentExecutionFailed(f"Agent execution failed: {e}")

    # ✅ Retornar respuesta
    return success_response(
        data={
            'agent_id': agent_id,
            'resultado': resultado,
            'duracion_ms': 150,
        },
        message="Execution completed successfully"
    )


# ============================================================================
# === Ejemplo 4: Consultar base de datos
# ============================================================================

@handle_api_errors()
async def consultar_base_datos_handler(request: web.Request) -> web.Response:
    """
    GET /api/database/query

    Patrón: Convertir errores de base de datos
    """
    query = request.rel_url.query.get('q', 'SELECT * FROM agents')

    # ✅ Validar query
    if not query:
        raise ValidationError("Query parameter 'q' is required")
    if len(query) > 1000:
        raise ValidationError("Query too long (max 1000 chars)")

    # ✅ Ejecutar query (simulado)
    try:
        # Simular error de BD
        if 'INVALID' in query:
            raise RuntimeError("SQL Syntax Error: INVALID keyword")

        resultados = [
            {'id': '1', 'nombre': 'Agent 1'},
            {'id': '2', 'nombre': 'Agent 2'},
        ]
    except RuntimeError as e:
        raise DatabaseError(f"Database query failed: {e}")

    # ✅ Retornar respuesta
    return success_response(
        data=resultados,
        message=f"Query executed: {len(resultados)} rows"
    )


# ============================================================================
# === Ejemplo 5: Operación asíncrona (202 Accepted)
# ============================================================================

@handle_api_errors()
async def generar_documento_handler(request: web.Request) -> web.Response:
    """
    POST /api/documents/generate

    Patrón: Operación asíncrona (enqueue, no esperar)

    Respuesta: 202 Accepted (en lugar de 201/200)
    """
    data = await request.json()

    # ✅ Validar entrada
    if not data.get('template_id'):
        raise ValidationError("Template ID is required")
    if not data.get('employee_name'):
        raise ValidationError("Employee name is required")

    # ✅ Enqueue job (no esperar)
    # En una aplicación real, esto iría a una cola de trabajos
    job_id = f"job_{hash(str(data)) % 10000}"

    # ✅ Retornar 202 Accepted
    return accepted_response(
        data={
            'job_id': job_id,
            'status': 'queued',
            'template_id': data['template_id'],
        },
        message="Document generation queued"
    )


# ============================================================================
# === Resumen de patrones
# ============================================================================

"""
TABLA DE PATRONES EN PYTHON:

┌──────────────────┬────────────────────────────────────┬───────────┐
│ Situación        │ Patrón                             │ Error     │
├──────────────────┼────────────────────────────────────┼───────────┤
│ Entrada inválida │ raise ValidationError("...")       │ 400       │
│ Recurso existe   │ raise AgentNotFound("...")         │ 404       │
│ Sin permiso      │ raise PermissionDenied("...")      │ 403       │
│ Timeout          │ raise AgentTimeout("...")          │ 504       │
│ Ejecución falla  │ raise AgentExecutionFailed("...")  │ 500       │
│ Error de BD      │ raise DatabaseError("...")         │ 500       │
│ Operación async  │ return accepted_response(...)      │ 202       │
└──────────────────┴────────────────────────────────────┴───────────┘

DECORADOR @handle_api_errors():

✅ Captura ElapException automáticamente
✅ Convierte a respuesta HTTP JSON
✅ Incluye status codes correctos
✅ Captura excepciones desconocidas
✅ Mensajes seguros para usuario

ESTRUCTURA DE HANDLER:

@handle_api_errors()
async def handler(request: web.Request) -> web.Response:
    # 1. Extraer datos
    data = await request.json()
    id = request.match_info.get('id')

    # 2. Validar entrada
    if not data.get('campo'):
        raise ValidationError("Field is required")

    # 3. Verificar recurso
    recurso = repo.get(id)
    if not recurso:
        raise AgentNotFound(f"Resource {id} not found")

    # 4. Ejecutar lógica
    try:
        resultado = await operacion(data)
    except TimeoutError:
        raise AgentTimeout("Operation took too long")
    except Exception as e:
        raise AgentExecutionFailed(str(e))

    # 5. Retornar respuesta
    return success_response(data=resultado)
"""
