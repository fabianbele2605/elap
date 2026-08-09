"""
Error logging con contexto estructurado.

Integra el framework de excepciones con logging para capturar:
- Código de error (UNAUTHORIZED, AGENT_NOT_FOUND, etc.)
- Status HTTP (401, 404, 500, etc.)
- Contexto (user_id, request_id, agent_id, etc.)
- Información de retry
- Duración de operaciones
"""

import logging
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from .errors import ElapException

logger = logging.getLogger(__name__)


@dataclass
class ErrorContext:
    """Contexto estructurado para logging de errores."""

    # IDs de seguimiento
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    tool_id: Optional[str] = None

    # Información adicional
    extra: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.extra is None:
            self.extra = {}

    def add_extra(self, key: str, value: Any) -> "ErrorContext":
        """Agregar campo personalizado."""
        self.extra[key] = str(value)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para logging."""
        result = {}

        if self.request_id:
            result["request_id"] = self.request_id
        if self.user_id:
            result["user_id"] = self.user_id
        if self.agent_id:
            result["agent_id"] = self.agent_id
        if self.tool_id:
            result["tool_id"] = self.tool_id

        if self.extra:
            result.update(self.extra)

        return result

    def to_string(self) -> str:
        """Convertir a string para logging."""
        items = []
        for key, value in self.to_dict().items():
            items.append(f"{key}={value}")
        return " | ".join(items)


def log_error(
    error: ElapException,
    context: Optional[ErrorContext] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Loguear error con contexto estructurado.

    Args:
        error: Excepción a loguear
        context: Contexto de error (user_id, request_id, etc.)
        extra: Campos adicionales para logging
    """
    code = error.code
    status = error.status_code
    message = error.to_log_message()

    # Construir campos estructurados
    fields = {
        "code": code,
        "status": status,
        "message": message,
    }

    if context:
        fields.update(context.to_dict())

    if extra:
        fields.update(extra)

    # Loguear según severidad
    if 400 <= status < 500:
        # Cliente (WARN)
        logger.warning(
            json.dumps(fields),
            extra={
                "code": code,
                "status": status,
            }
        )
    elif status >= 500:
        # Servidor (ERROR)
        logger.error(
            json.dumps(fields),
            extra={
                "code": code,
                "status": status,
            }
        )
    else:
        # Otros (INFO)
        logger.info(
            json.dumps(fields),
            extra={
                "code": code,
                "status": status,
            }
        )


def log_recoverable_error(
    error: ElapException,
    retry_attempt: int,
    max_retries: int,
    context: Optional[ErrorContext] = None,
) -> None:
    """
    Loguear error recuperable con información de retry.

    Args:
        error: Excepción a loguear
        retry_attempt: Número de intento actual
        max_retries: Máximo de intentos
        context: Contexto de error
    """
    code = error.code
    message = error.to_log_message()

    fields = {
        "code": code,
        "message": message,
        "retry_attempt": retry_attempt,
        "max_retries": max_retries,
        "retry_info": f"attempt {retry_attempt}/{max_retries}",
    }

    if context:
        fields.update(context.to_dict())

    logger.warning(
        json.dumps(fields),
        extra={
            "code": code,
            "retry_attempt": retry_attempt,
        }
    )


def log_success_after_retry(
    attempt: int,
    duration_ms: float,
    context: Optional[ErrorContext] = None,
) -> None:
    """
    Loguear operación exitosa después de retry.

    Args:
        attempt: Número de intento en que tuvo éxito
        duration_ms: Duración total en milisegundos
        context: Contexto de error
    """
    fields = {
        "status": "success_after_retry",
        "attempt": attempt,
        "duration_ms": round(duration_ms, 2),
    }

    if context:
        fields.update(context.to_dict())

    logger.info(json.dumps(fields))


def log_handler(
    method: str,
    path: str,
    status: int,
    duration_ms: float,
    context: Optional[ErrorContext] = None,
    error: Optional[Exception] = None,
) -> None:
    """
    Loguear request/response de handler.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status: HTTP status code
        duration_ms: Duración en milisegundos
        context: Contexto de error
        error: Excepción si aplica
    """
    fields = {
        "method": method,
        "path": path,
        "status": status,
        "duration_ms": round(duration_ms, 2),
        "request": f"{method} {path}",
    }

    if context:
        fields.update(context.to_dict())

    if error:
        if isinstance(error, ElapException):
            fields["error_code"] = error.code
            fields["error_message"] = error.to_log_message()
        else:
            fields["error"] = str(error)

    # Loguear según severidad
    if 200 <= status < 300:
        logger.info(json.dumps(fields))
    elif 400 <= status < 500:
        logger.warning(json.dumps(fields))
    elif status >= 500:
        logger.error(json.dumps(fields))
    else:
        logger.info(json.dumps(fields))


def log_operation(
    operation: str,
    duration_ms: float,
    success: bool = True,
    context: Optional[ErrorContext] = None,
    error: Optional[Exception] = None,
) -> None:
    """
    Loguear operación general.

    Args:
        operation: Nombre de la operación
        duration_ms: Duración en milisegundos
        success: Si tuvo éxito
        context: Contexto de error
        error: Excepción si aplica
    """
    fields = {
        "operation": operation,
        "duration_ms": round(duration_ms, 2),
        "success": success,
    }

    if context:
        fields.update(context.to_dict())

    if error:
        if isinstance(error, ElapException):
            fields["error_code"] = error.code
            fields["error_message"] = error.message
        else:
            fields["error"] = str(error)

    log_level = "info" if success else "error"
    if log_level == "info":
        logger.info(json.dumps(fields))
    else:
        logger.error(json.dumps(fields))


if __name__ == "__main__":
    # Configurar logging para prueba
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    # Test 1: ErrorContext
    context = ErrorContext(request_id="req-123", user_id="user-456")
    context.add_extra("operation", "create_agent")
    print(f"✅ ErrorContext: {context.to_string()}")

    # Test 2: log_error desde excepciones
    from .errors import AgentNotFound, ValidationError

    try:
        raise AgentNotFound("agent_xyz")
    except ElapException as e:
        log_error(e, context=context)
        print("✅ log_error funcional")

    # Test 3: log_recoverable_error
    try:
        raise ValidationError("invalid input")
    except ElapException as e:
        log_recoverable_error(e, retry_attempt=1, max_retries=3, context=context)
        print("✅ log_recoverable_error funcional")

    # Test 4: log_handler
    log_handler(
        "POST",
        "/api/agents",
        201,
        150.5,
        context=context,
    )
    print("✅ log_handler funcional")

    print("\n✅ Error logging framework en Python completamente funcional")
