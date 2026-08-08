"""
Tests para el framework de error handling de ELAP.
"""

import pytest
from elap_ai.errors import (
    ElapException,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
    ConflictError,
    PermissionDenied,
    AuthenticationFailed,
    AgentNotFound,
    AgentExecutionFailed,
    InvalidAgentState,
    AgentTimeout,
    ToolNotFound,
    ToolExecutionFailed,
    ToolTimeout,
    ToolValidationFailed,
    DatabaseError,
    ConnectionPoolExhausted,
    TransactionFailed,
    DocumentGenerationFailed,
    TemplateNotFound,
    InvalidDocumentData,
    ConfigError,
    ConfigValidationFailed,
    GrpcError,
    GrpcTimeout,
    ConnectionUnavailable,
    NotImplementedError as NotImplementedErrorElap,
    get_error_code_from_exception,
    get_status_code_from_exception,
    get_user_message_from_exception,
    wrap_exception,
)


# ============================================================================
# === HTTP Status Codes
# ============================================================================


class TestHttpStatusCodes:
    """Verificar que los códigos HTTP sean correctos."""

    def test_4xx_client_errors(self):
        """Errores 4xx para errores del cliente."""
        errors_4xx = [
            UnauthorizedError("test"),
            ForbiddenError("test"),
            NotFoundError("test"),
            ValidationError("test"),
            ConflictError("test"),
            ToolValidationFailed("test"),
        ]

        for error in errors_4xx:
            assert 400 <= error.status_code < 500, f"{error.code} should be 4xx"

    def test_5xx_server_errors(self):
        """Errores 5xx para errores del servidor."""
        errors_5xx = [
            ElapException("test"),
            AgentExecutionFailed("test"),
            DatabaseError("test"),
            DocumentGenerationFailed("test"),
        ]

        for error in errors_5xx:
            assert 500 <= error.status_code < 600, f"{error.code} should be 5xx"

    def test_503_service_unavailable(self):
        """503 para errores de servicio no disponible."""
        unavailable_errors = [
            ConnectionPoolExhausted("test"),
            ConnectionUnavailable("test"),
        ]

        for error in unavailable_errors:
            assert error.status_code == 503

    def test_504_timeout(self):
        """504 para timeouts."""
        timeout_errors = [
            AgentTimeout("test"),
            ToolTimeout("test"),
            GrpcTimeout("test"),
        ]

        for error in timeout_errors:
            assert error.status_code == 504


# ============================================================================
# === Error Codes
# ============================================================================


class TestErrorCodes:
    """Verificar que los códigos de error sean correctos."""

    def test_error_code_uniqueness(self):
        """Todos los códigos de error deben ser únicos."""
        errors = [
            UnauthorizedError("test"),
            ForbiddenError("test"),
            NotFoundError("test"),
            AgentNotFound("test"),
            ToolNotFound("test"),
            DatabaseError("test"),
            GrpcError("test"),
        ]

        codes = [e.code for e in errors]
        assert len(codes) == len(set(codes)), "Duplicate error codes found"

    def test_error_code_format(self):
        """Códigos de error deben ser UPPER_SNAKE_CASE."""
        errors = [
            UnauthorizedError("test"),
            AgentExecutionFailed("test"),
            ToolValidationFailed("test"),
            DocumentGenerationFailed("test"),
        ]

        for error in errors:
            assert error.code == error.code.upper()
            assert "_" in error.code or len(error.code) > 5  # Debe tener formato


# ============================================================================
# === User Messages (no technical details)
# ============================================================================


class TestUserMessages:
    """Verificar que los mensajes de usuario sean seguros."""

    def test_user_message_no_technical_details(self):
        """Los mensajes para usuario NO deben contener detalles técnicos."""
        error = AgentTimeout("timeout after 30000ms in grpc call")
        user_msg = error.to_user_message()

        # No debe contener:
        assert "30000ms" not in user_msg
        assert "grpc" not in user_msg
        assert "localhost" not in user_msg
        assert "/path/to/file" not in user_msg

    def test_user_message_is_actionable(self):
        """Los mensajes para usuario deben sugerir una acción."""
        errors = [
            AgentTimeout("test"),
            DatabaseError("test"),
            ToolNotFound("test"),
        ]

        for error in errors:
            msg = error.to_user_message()
            # Debe contener alguna acción
            assert any(
                action in msg
                for action in ["Intenta", "Contacta", "Recarga", "disponible"]
            ), f"Not actionable: {msg}"

    def test_validation_error_includes_field(self):
        """ValidationError debe incluir el campo en el mensaje."""
        error = ValidationError("email is invalid")
        user_msg = error.to_user_message()

        assert "email is invalid" in user_msg
        assert "Datos inválidos" in user_msg


# ============================================================================
# === Log Messages (with technical details)
# ============================================================================


class TestLogMessages:
    """Verificar que los mensajes de logs incluyan contexto técnico."""

    def test_log_message_includes_error_code(self):
        """El mensaje de log debe incluir el código de error."""
        error = ToolExecutionFailed("exit code 1")
        log_msg = error.to_log_message()

        assert "TOOL_EXECUTION_FAILED" in log_msg
        assert "exit code 1" in log_msg

    def test_log_message_with_context(self):
        """El mensaje de log debe incluir el contexto."""
        context = {"user_id": "user123", "request_id": "req-456"}
        error = PermissionDenied("read_sensitive_data", context=context)
        log_msg = error.to_log_message()

        assert "user_id=user123" in log_msg
        assert "request_id=req-456" in log_msg

    def test_log_message_with_original_error(self):
        """El mensaje de log debe incluir la excepción original."""
        original_exc = ValueError("invalid value")
        error = DatabaseError(
            "query failed",
            original_error=original_exc
        )
        log_msg = error.to_log_message()

        assert "ValueError" in log_msg
        assert "invalid value" in log_msg


# ============================================================================
# === Exception Hierarchy
# ============================================================================


class TestExceptionHierarchy:
    """Verificar la jerarquía de excepciones."""

    def test_all_errors_inherit_from_elap_exception(self):
        """Todas las excepciones deben heredar de ElapException."""
        errors = [
            UnauthorizedError("test"),
            AgentNotFound("test"),
            ToolExecutionFailed("test"),
            DatabaseError("test"),
            DocumentGenerationFailed("test"),
        ]

        for error in errors:
            assert isinstance(error, ElapException)
            assert isinstance(error, Exception)

    def test_error_is_catchable_as_exception(self):
        """Los errores deben poderse capturar como Exception."""
        with pytest.raises(Exception):
            raise AgentTimeout("test")

        with pytest.raises(ElapException):
            raise AgentTimeout("test")


# ============================================================================
# === API Errors (HTTP)
# ============================================================================


class TestApiErrors:
    """Errores relacionados con API HTTP."""

    def test_unauthorized_401(self):
        assert UnauthorizedError("test").status_code == 401

    def test_forbidden_403(self):
        assert ForbiddenError("test").status_code == 403

    def test_not_found_404(self):
        assert NotFoundError("test").status_code == 404

    def test_validation_error_400(self):
        assert ValidationError("test").status_code == 400

    def test_conflict_409(self):
        assert ConflictError("test").status_code == 409


# ============================================================================
# === Agent Errors
# ============================================================================


class TestAgentErrors:
    """Errores relacionados con agentes."""

    def test_agent_not_found(self):
        error = AgentNotFound("agent_xyz")
        assert error.code == "AGENT_NOT_FOUND"
        assert error.status_code == 404

    def test_agent_execution_failed(self):
        error = AgentExecutionFailed("eval failed")
        assert error.code == "AGENT_EXECUTION_FAILED"
        assert error.status_code == 500

    def test_invalid_agent_state(self):
        error = InvalidAgentState("zombie state")
        assert error.code == "INVALID_AGENT_STATE"

    def test_agent_timeout(self):
        error = AgentTimeout("60s limit")
        assert error.code == "AGENT_TIMEOUT"
        assert error.status_code == 504


# ============================================================================
# === Tool Errors
# ============================================================================


class TestToolErrors:
    """Errores relacionados con herramientas."""

    def test_tool_not_found(self):
        error = ToolNotFound("grep")
        assert error.code == "TOOL_NOT_FOUND"
        assert error.status_code == 404

    def test_tool_execution_failed(self):
        error = ToolExecutionFailed("exit code 1")
        assert error.code == "TOOL_EXECUTION_FAILED"

    def test_tool_timeout(self):
        error = ToolTimeout("60s")
        assert error.code == "TOOL_TIMEOUT"
        assert error.status_code == 504

    def test_tool_validation_failed(self):
        error = ToolValidationFailed("missing url param")
        assert error.code == "TOOL_VALIDATION_FAILED"
        assert error.status_code == 400


# ============================================================================
# === Database Errors
# ============================================================================


class TestDatabaseErrors:
    """Errores relacionados con base de datos."""

    def test_database_error(self):
        error = DatabaseError("connection refused")
        assert error.code == "DATABASE_ERROR"
        assert error.status_code == 500

    def test_connection_pool_exhausted(self):
        error = ConnectionPoolExhausted("no connections available")
        assert error.code == "CONNECTION_POOL_EXHAUSTED"
        assert error.status_code == 503

    def test_transaction_failed(self):
        error = TransactionFailed("rollback")
        assert error.code == "TRANSACTION_FAILED"


# ============================================================================
# === Document Errors
# ============================================================================


class TestDocumentErrors:
    """Errores relacionados con generación de documentos."""

    def test_document_generation_failed(self):
        error = DocumentGenerationFailed("template error")
        assert error.code == "DOCUMENT_GENERATION_FAILED"

    def test_template_not_found(self):
        error = TemplateNotFound("contract_xyz")
        assert error.code == "TEMPLATE_NOT_FOUND"
        assert error.status_code == 404

    def test_invalid_document_data(self):
        error = InvalidDocumentData("missing employee_name")
        assert error.code == "INVALID_DOCUMENT_DATA"
        assert error.status_code == 400


# ============================================================================
# === Helper Functions
# ============================================================================


class TestHelperFunctions:
    """Funciones auxiliares para manejo de errores."""

    def test_get_error_code_from_elap_exception(self):
        error = AgentTimeout("test")
        code = get_error_code_from_exception(error)
        assert code == "AGENT_TIMEOUT"

    def test_get_error_code_from_unknown_exception(self):
        exc = ValueError("test")
        code = get_error_code_from_exception(exc)
        assert code == "UNKNOWN_ERROR"

    def test_get_status_code_from_exception(self):
        errors = [
            (NotFoundError("test"), 404),
            (AgentTimeout("test"), 504),
            (DatabaseError("test"), 500),
        ]

        for error, expected_code in errors:
            assert get_status_code_from_exception(error) == expected_code

    def test_get_status_code_from_unknown_exception(self):
        exc = ValueError("test")
        code = get_status_code_from_exception(exc)
        assert code == 500  # Default to 500

    def test_get_user_message_from_exception(self):
        error = ToolNotFound("grep")
        msg = get_user_message_from_exception(error)
        assert msg == error.to_user_message()
        assert "grep" not in msg  # No debe incluir detalles

    def test_wrap_exception(self):
        original = ValueError("invalid data")
        wrapped = wrap_exception(
            original,
            error_class=ValidationError,
            message="custom message",
            context={"field": "email"}
        )

        assert isinstance(wrapped, ValidationError)
        assert wrapped.message == "custom message"
        assert wrapped.context == {"field": "email"}
        assert wrapped.original_error is original

    def test_wrap_exception_preserves_message(self):
        original = RuntimeError("something went wrong")
        wrapped = wrap_exception(
            original,
            error_class=DatabaseError,
        )

        assert wrapped.message == "something went wrong"


# ============================================================================
# === Exception String Representations
# ============================================================================


class TestStringRepresentations:
    """Verificar las representaciones en string de excepciones."""

    def test_str_representation(self):
        error = ToolExecutionFailed("exit code 1")
        str_repr = str(error)

        assert "TOOL_EXECUTION_FAILED" in str_repr
        assert "exit code 1" in str_repr

    def test_repr_representation(self):
        error = AgentNotFound("agent_123")
        repr_str = repr(error)

        assert "AgentNotFound" in repr_str
        assert "AGENT_NOT_FOUND" in repr_str


# ============================================================================
# === Error Creation Patterns
# ============================================================================


class TestErrorCreationPatterns:
    """Patrones comunes de creación de errores."""

    def test_error_with_message_only(self):
        error = ToolNotFound("my_tool")
        assert error.message == "my_tool"
        assert error.context == {}
        assert error.original_error is None

    def test_error_with_context(self):
        context = {"user_id": "user123", "tool_id": "grep"}
        error = ToolNotFound("grep", context=context)
        assert error.context == context

    def test_error_with_original_exception(self):
        original = FileNotFoundError("file.txt")
        error = DocumentGenerationFailed(
            "failed to load template",
            original_error=original
        )
        assert error.original_error is original
        assert isinstance(error.original_error, FileNotFoundError)

    def test_error_inheritance_in_except_clause(self):
        """Los errores deben ser catcheables por tipo."""
        try:
            raise AgentTimeout("test")
        except AgentTimeout as e:
            assert e.code == "AGENT_TIMEOUT"
        except Exception:
            pytest.fail("Should be caught as AgentTimeout")


# ============================================================================
# === Permission and Security Errors
# ============================================================================


class TestSecurityErrors:
    """Errores relacionados con seguridad."""

    def test_permission_denied(self):
        error = PermissionDenied("read_sensitive_data")
        assert error.code == "PERMISSION_DENIED"
        assert error.status_code == 403

    def test_authentication_failed(self):
        error = AuthenticationFailed("invalid token")
        assert error.code == "AUTHENTICATION_FAILED"
        assert error.status_code == 401

    def test_unauthorized_error(self):
        error = UnauthorizedError("login required")
        assert error.code == "UNAUTHORIZED"
        assert error.status_code == 401


# ============================================================================
# === Communication Errors
# ============================================================================


class TestCommunicationErrors:
    """Errores de comunicación (gRPC, IPC)."""

    def test_grpc_error(self):
        error = GrpcError("connection refused")
        assert error.code == "GRPC_ERROR"
        assert error.status_code == 503

    def test_grpc_timeout(self):
        error = GrpcTimeout("30s")
        assert error.code == "GRPC_TIMEOUT"
        assert error.status_code == 504

    def test_connection_unavailable(self):
        error = ConnectionUnavailable("service down")
        assert error.code == "CONNECTION_UNAVAILABLE"
        assert error.status_code == 503
