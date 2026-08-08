"""
Error handling framework para ELAP.

Jerarquía de excepciones empresariales con:
- Códigos de error internos
- Status HTTP automático
- Mensajes para usuario (sin detalles técnicos)
- Contexto técnico para logging

Ejemplo:
    try:
        agent = get_agent("unknown_agent")
    except ElapException as e:
        logger.error(e.to_log_message())  # Con detalles
        user.show_message(e.user_message)  # Sin detalles
"""

from typing import Optional, Dict, Any
import traceback


class ElapException(Exception):
    """
    Excepción base para ELAP.

    Todos los errores en el sistema heredan de esta clase.
    Proporciona:
    - Código de error interno
    - Status HTTP automático
    - Mensaje para usuario (sin detalles técnicos)
    - Contexto técnico para logs
    """

    code: str = "INTERNAL_ERROR"
    status_code: int = 500
    user_message: str = "Error interno del sistema. El equipo técnico ha sido notificado."

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        Inicializar excepción ELAP.

        Args:
            message: Mensaje técnico detallado (para logs)
            context: Contexto adicional (user_id, request_id, etc.)
            original_error: Excepción original que causó este error
        """
        self.message = message
        self.context = context or {}
        self.original_error = original_error
        super().__init__(message)

    def to_user_message(self) -> str:
        """Mensaje para usuario (SIN detalles técnicos, seguro)."""
        return self.user_message

    def to_log_message(self) -> str:
        """Mensaje para logs (CON contexto técnico completo)."""
        context_str = ""
        if self.context:
            context_items = [f"{k}={v}" for k, v in self.context.items()]
            context_str = f" | Context: {', '.join(context_items)}"

        original_str = ""
        if self.original_error:
            original_str = f" | Original: {type(self.original_error).__name__}: {self.original_error}"

        return f"[{self.code}] {self.message}{context_str}{original_str}"

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code}, message={self.message})"


# ============================================================================
# === API / HTTP ERRORS (4xx, 5xx)
# ============================================================================


class UnauthorizedError(ElapException):
    """401 - Autenticación requerida."""

    code = "UNAUTHORIZED"
    status_code = 401
    user_message = "Necesitas iniciar sesión para continuar."


class ForbiddenError(ElapException):
    """403 - Permiso denegado."""

    code = "FORBIDDEN"
    status_code = 403
    user_message = "No tienes permiso para realizar esta acción."


class NotFoundError(ElapException):
    """404 - Recurso no encontrado."""

    code = "NOT_FOUND"
    status_code = 404
    user_message = "El recurso solicitado no existe."


class ValidationError(ElapException):
    """400 - Datos de entrada inválidos."""

    code = "VALIDATION_ERROR"
    status_code = 400

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, original_error: Optional[Exception] = None):
        super().__init__(message, context, original_error)
        self.user_message = f"Datos inválidos: {message}. Revisa el formato."


class ConflictError(ElapException):
    """409 - Conflicto (recurso existe, estado inconsistente)."""

    code = "CONFLICT"
    status_code = 409
    user_message = "La operación conflictúa con el estado actual. Intenta de nuevo."


class PermissionDenied(ElapException):
    """403 - Permiso denegado (RBAC)."""

    code = "PERMISSION_DENIED"
    status_code = 403
    user_message = "No tienes permisos suficientes."


class AuthenticationFailed(ElapException):
    """401 - Autenticación falló."""

    code = "AUTHENTICATION_FAILED"
    status_code = 401
    user_message = "La autenticación falló. Intenta de nuevo."


# ============================================================================
# === AGENT ERRORS
# ============================================================================


class AgentError(ElapException):
    """Error relacionado con agentes."""

    code = "AGENT_ERROR"
    status_code = 500
    user_message = "Error en el procesamiento del agente. Intenta de nuevo."


class AgentNotFound(ElapException):
    """Agente no encontrado."""

    code = "AGENT_NOT_FOUND"
    status_code = 404
    user_message = "El agente solicitado no está disponible."


class AgentExecutionFailed(ElapException):
    """Ejecución de agente falló."""

    code = "AGENT_EXECUTION_FAILED"
    status_code = 500
    user_message = "El procesamiento falló. Intenta con una solicitud más simple."


class InvalidAgentState(ElapException):
    """Estado inválido del agente."""

    code = "INVALID_AGENT_STATE"
    status_code = 500
    user_message = "El agente está en un estado inconsistente. Recarga la página."


class AgentTimeout(ElapException):
    """Timeout en ejecución de agente."""

    code = "AGENT_TIMEOUT"
    status_code = 504
    user_message = "El procesamiento tardó demasiado. Intenta de nuevo."


# ============================================================================
# === TOOL ERRORS
# ============================================================================


class ToolError(ElapException):
    """Error relacionado con herramientas."""

    code = "TOOL_ERROR"
    status_code = 500
    user_message = "Error en la herramienta. Intenta de nuevo."


class ToolNotFound(ElapException):
    """Herramienta no registrada."""

    code = "TOOL_NOT_FOUND"
    status_code = 404
    user_message = "La herramienta solicitada no está disponible. Intenta con otra herramienta."


class ToolExecutionFailed(ElapException):
    """Ejecución de herramienta falló."""

    code = "TOOL_EXECUTION_FAILED"
    status_code = 500
    user_message = "La herramienta no pudo completarse. Intenta de nuevo."


class ToolTimeout(ElapException):
    """Timeout en herramienta."""

    code = "TOOL_TIMEOUT"
    status_code = 504
    user_message = "La herramienta tardó demasiado. Intenta con parámetros más simples."


class ToolValidationFailed(ElapException):
    """Parámetros inválidos para herramienta."""

    code = "TOOL_VALIDATION_FAILED"
    status_code = 400
    user_message = "Los parámetros de la herramienta son inválidos."


# ============================================================================
# === DATABASE ERRORS
# ============================================================================


class DatabaseError(ElapException):
    """Error de base de datos."""

    code = "DATABASE_ERROR"
    status_code = 500
    user_message = "Error temporal en el sistema. Recargando..."


class ConnectionPoolExhausted(ElapException):
    """Pool de conexiones exhausto."""

    code = "CONNECTION_POOL_EXHAUSTED"
    status_code = 503
    user_message = "El sistema está sobrecargado. Intenta en unos segundos."


class TransactionFailed(ElapException):
    """Transacción falló."""

    code = "TRANSACTION_FAILED"
    status_code = 500
    user_message = "La operación no se pudo completar. Intenta de nuevo."


# ============================================================================
# === DOCUMENT GENERATION ERRORS
# ============================================================================


class DocumentError(ElapException):
    """Error en generación de documentos."""

    code = "DOCUMENT_ERROR"
    status_code = 500
    user_message = "Error en la generación de documentos. Intenta de nuevo."


class DocumentGenerationFailed(ElapException):
    """Generación de documento falló."""

    code = "DOCUMENT_GENERATION_FAILED"
    status_code = 500
    user_message = "No se pudo generar el documento. Intenta con datos diferentes."


class TemplateNotFound(ElapException):
    """Plantilla no encontrada."""

    code = "TEMPLATE_NOT_FOUND"
    status_code = 404
    user_message = "La plantilla solicitada no existe."


class InvalidDocumentData(ElapException):
    """Datos inválidos para documento."""

    code = "INVALID_DOCUMENT_DATA"
    status_code = 400
    user_message = "Los datos del documento son inválidos. Revisa el formato."


# ============================================================================
# === CONFIGURATION ERRORS
# ============================================================================


class ConfigError(ElapException):
    """Error de configuración."""

    code = "CONFIG_ERROR"
    status_code = 500
    user_message = "Error de configuración del sistema. Contacta soporte."


class ConfigValidationFailed(ElapException):
    """Validación de configuración falló."""

    code = "CONFIG_VALIDATION_FAILED"
    status_code = 500
    user_message = "Configuración inválida. Contacta soporte."


# ============================================================================
# === COMMUNICATION ERRORS (gRPC, IPC)
# ============================================================================


class CommunicationError(ElapException):
    """Error en comunicación IPC/gRPC."""

    code = "COMMUNICATION_ERROR"
    status_code = 503
    user_message = "Error en comunicación del sistema. Intenta de nuevo."


class GrpcError(ElapException):
    """Error en llamada gRPC."""

    code = "GRPC_ERROR"
    status_code = 503
    user_message = "Error en comunicación del sistema. Intenta de nuevo."


class GrpcTimeout(ElapException):
    """Timeout en gRPC."""

    code = "GRPC_TIMEOUT"
    status_code = 504
    user_message = "La comunicación tardó demasiado. Intenta de nuevo."


class ConnectionUnavailable(ElapException):
    """Conexión no disponible."""

    code = "CONNECTION_UNAVAILABLE"
    status_code = 503
    user_message = "Servicio no disponible. Intenta en unos segundos."


# ============================================================================
# === SYSTEM ERRORS
# ============================================================================


class NotImplementedError(ElapException):
    """Funcionalidad no implementada."""

    code = "NOT_IMPLEMENTED"
    status_code = 501
    user_message = "Esta funcionalidad aún no está disponible."


# ============================================================================
# === HELPER FUNCTIONS
# ============================================================================


def get_error_code_from_exception(exc: Exception) -> str:
    """Obtener código de error de una excepción."""
    if isinstance(exc, ElapException):
        return exc.code
    return "UNKNOWN_ERROR"


def get_status_code_from_exception(exc: Exception) -> int:
    """Obtener status HTTP de una excepción."""
    if isinstance(exc, ElapException):
        return exc.status_code
    return 500


def get_user_message_from_exception(exc: Exception) -> str:
    """Obtener mensaje seguro para usuario."""
    if isinstance(exc, ElapException):
        return exc.to_user_message()
    return "Algo salió mal. Intenta de nuevo."


def wrap_exception(
    exc: Exception,
    error_class: type = ElapException,
    message: str = None,
    context: Dict[str, Any] = None,
) -> ElapException:
    """
    Envolver una excepción desconocida como ElapException.

    Útil para convertir excepciones de librerías externas.

    Args:
        exc: Excepción original
        error_class: Clase de ElapException a usar
        message: Mensaje personalizado (si no, usa str(exc))
        context: Contexto adicional

    Returns:
        ElapException con info de exc como original_error
    """
    msg = message or str(exc)
    return error_class(msg, context=context, original_error=exc)
