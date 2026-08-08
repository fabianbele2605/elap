"""
Response handling para API REST.

Integra el framework de excepciones con aiohttp para conversiones
automáticas de ElapException a respuestas HTTP JSON.
"""

import json
from typing import Any, Dict, Optional, TypeVar
from aiohttp import web
from enum import Enum

from .errors import ElapException

T = TypeVar('T')


class ResponseType(str, Enum):
    """Tipos de respuesta."""
    SUCCESS = "success"
    ERROR = "error"
    CREATED = "created"
    ACCEPTED = "accepted"


class ApiResponse:
    """
    Respuesta estándar para API.

    Formato:
    {
        "code": "SUCCESS" | "AGENT_NOT_FOUND" | ...,
        "status": 200 | 404 | ...,
        "message": "Descripción",
        "data": {...} | null,
        "detail": "Contexto técnico (solo en desarrollo)"
    }
    """

    def __init__(
        self,
        code: str,
        status: int,
        message: str,
        data: Optional[Any] = None,
        detail: Optional[str] = None,
    ):
        self.code = code
        self.status = status
        self.message = message
        self.data = data
        self.detail = detail

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para JSON."""
        result = {
            "code": self.code,
            "status": self.status,
            "message": self.message,
        }

        if self.data is not None:
            result["data"] = self.data

        # Incluir detalles técnicos solo en desarrollo
        if self.detail is not None:
            result["detail"] = self.detail

        return result

    def to_aiohttp_response(self) -> web.Response:
        """Convertir a respuesta aiohttp."""
        return web.json_response(
            self.to_dict(),
            status=self.status,
        )


class SuccessResponse(ApiResponse):
    """Respuesta exitosa (200 OK, 201 Created, etc.)"""

    def __init__(
        self,
        data: Optional[Any] = None,
        message: str = "Success",
        status: int = 200,
    ):
        super().__init__(
            code="SUCCESS",
            status=status,
            message=message,
            data=data,
        )


class CreatedResponse(SuccessResponse):
    """Respuesta creada (201 Created)"""

    def __init__(self, data: Optional[Any] = None, message: str = "Created"):
        super().__init__(data=data, message=message, status=201)


class AcceptedResponse(SuccessResponse):
    """Respuesta aceptada (202 Accepted)"""

    def __init__(self, data: Optional[Any] = None, message: str = "Accepted"):
        super().__init__(data=data, message=message, status=202)


class ErrorResponse(ApiResponse):
    """Respuesta de error desde ElapException"""

    @staticmethod
    def from_exception(
        exc: ElapException,
        include_detail: bool = True,
    ) -> 'ErrorResponse':
        """
        Crear respuesta de error desde excepción.

        Args:
            exc: ElapException a convertir
            include_detail: Incluir detalles técnicos (solo en desarrollo)
        """
        code = exc.code
        status = exc.status_code
        message = exc.to_user_message()

        # Incluir detalles técnicos solo en desarrollo
        detail = None
        if include_detail:
            detail = exc.to_log_message()

        return ErrorResponse(
            code=code,
            status=status,
            message=message,
            detail=detail,
        )

    def __init__(
        self,
        code: str,
        status: int,
        message: str,
        detail: Optional[str] = None,
    ):
        super().__init__(
            code=code,
            status=status,
            message=message,
            data=None,
            detail=detail,
        )


# ============================================================================
# === Funciones auxiliares para handlers
# ============================================================================


def success_response(
    data: Optional[Any] = None,
    message: str = "Success",
    status: int = 200,
) -> web.Response:
    """Crear respuesta exitosa."""
    response = SuccessResponse(data=data, message=message, status=status)
    return response.to_aiohttp_response()


def created_response(
    data: Optional[Any] = None,
    message: str = "Created",
) -> web.Response:
    """Crear respuesta 201 Created."""
    response = CreatedResponse(data=data, message=message)
    return response.to_aiohttp_response()


def accepted_response(
    data: Optional[Any] = None,
    message: str = "Accepted",
) -> web.Response:
    """Crear respuesta 202 Accepted."""
    response = AcceptedResponse(data=data, message=message)
    return response.to_aiohttp_response()


def error_response(
    exc: ElapException,
    include_detail: bool = True,
) -> web.Response:
    """Crear respuesta de error desde excepción."""
    response = ErrorResponse.from_exception(exc, include_detail=include_detail)
    return response.to_aiohttp_response()


# ============================================================================
# === Decorador para manejo automático de errores
# ============================================================================


def handle_api_errors(include_detail: bool = True):
    """
    Decorador para handlers que maneja excepciones automáticamente.

    Ejemplo:
        @handle_api_errors()
        async def crear_agente(request):
            data = await request.json()

            # Validar entrada
            if not data.get('nombre'):
                raise ValidationError("Name is required")

            # Ejecutar
            agente = crear_agente_internal(data)

            # Retornar respuesta
            return created_response(data=agente)
    """

    def decorator(handler):
        async def wrapper(request: web.Request) -> web.Response:
            try:
                return await handler(request)
            except ElapException as e:
                return error_response(e, include_detail=include_detail)
            except Exception as e:
                # Convertir excepciones desconocidas a error genérico
                from .errors import wrap_exception
                elap_exc = wrap_exception(e)
                return error_response(
                    elap_exc,
                    include_detail=include_detail
                )

        return wrapper

    return decorator


# ============================================================================
# === Patrones de handlers
# ============================================================================

"""
PATRÓN 1: Validación de entrada

@handle_api_errors()
async def crear_agente(request):
    data = await request.json()

    # ✅ Validar entrada
    if not data.get('nombre'):
        raise ValidationError("Name is required")
    if not data.get('rol'):
        raise ValidationError("Role is required")

    # ✅ Ejecutar
    agente = repo.create(data)

    # ✅ Retornar respuesta
    return created_response(data=agente)


PATRÓN 2: Verificar recurso existe

@handle_api_errors()
async def get_agente(request):
    agent_id = request.match_info['id']

    # ✅ Obtener recurso
    agente = repo.get(agent_id)
    if not agente:
        raise AgentNotFound(f"Agent {agent_id} not found")

    # ✅ Retornar respuesta
    return success_response(data=agente)


PATRÓN 3: Ejecutar operación con timeout

@handle_api_errors()
async def ejecutar_agente(request):
    data = await request.json()

    # ✅ Validar
    if not data.get('prompt'):
        raise ValidationError("Prompt is required")

    # ✅ Ejecutar con timeout
    try:
        timeout = data.get('timeout_ms', 30000) / 1000
        result = await asyncio.wait_for(
            agent.execute(data['prompt']),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        raise AgentTimeout(f"Execution timeout after {timeout}s")
    except Exception as e:
        raise AgentExecutionFailed(str(e))

    # ✅ Retornar respuesta
    return success_response(data={'resultado': result})


PATRÓN 4: Convertir errores externos

@handle_api_errors()
async def consultar_base_datos(request):
    try:
        resultados = await db.query("SELECT * FROM agents")
    except Exception as e:
        raise DatabaseError(f"Query failed: {e}")

    return success_response(data=resultados)


PATRÓN 5: Operación asíncrona (202 Accepted)

@handle_api_errors()
async def generar_documento(request):
    data = await request.json()

    # ✅ Validar
    if not data.get('template_id'):
        raise ValidationError("Template ID is required")

    # ✅ Enqueue (no esperar)
    job_id = await job_queue.enqueue(
        'generate_document',
        data
    )

    # ✅ Retornar 202 Accepted
    return accepted_response(data={
        'job_id': job_id,
        'status': 'queued'
    })
"""


# ============================================================================
# === Tests
# ============================================================================


if __name__ == "__main__":
    # Prueba básica
    from .errors import AgentNotFound, ValidationError

    # Test: SuccessResponse
    response = SuccessResponse(data={"id": "123"}, message="Agent created")
    print(f"✅ SuccessResponse: {response.to_dict()}")

    # Test: ErrorResponse from exception
    try:
        raise AgentNotFound("agent_xyz")
    except ElapException as e:
        error_resp = ErrorResponse.from_exception(e)
        print(f"✅ ErrorResponse: {error_resp.to_dict()}")

    # Test: CreatedResponse
    created = CreatedResponse(data={"id": "456"})
    print(f"✅ CreatedResponse: {created.to_dict()}")

    print("\n✅ API Response framework funcional")
