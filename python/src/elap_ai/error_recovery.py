"""
Error recovery con retry, circuit breaker y fallback.

Estrategias de recuperación automática para:
- Errores transitorios (timeout, conexión)
- Operaciones que pueden reintentarse
- Fallback a servicios alternativos
- Monitoreo de salud
"""

import asyncio
import time
from typing import Callable, Optional, TypeVar, Awaitable, List
from dataclasses import dataclass
from enum import Enum
import logging

from .errors import ElapException

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class RetryConfig:
    """Configuración de retry con backoff exponencial."""

    # Máximo número de intentos
    max_attempts: int = 3

    # Delay inicial en milisegundos
    initial_delay_ms: int = 100

    # Factor multiplicativo para backoff exponencial
    backoff_multiplier: float = 2.0

    # Máximo delay entre intentos en milisegundos
    max_delay_ms: int = 5000

    # Códigos de error que se deben reintentar
    retryable_errors: Optional[List[str]] = None

    def __post_init__(self):
        if self.retryable_errors is None:
            self.retryable_errors = [
                "AGENT_TIMEOUT",
                "TOOL_TIMEOUT",
                "GRPC_TIMEOUT",
                "CONNECTION_UNAVAILABLE",
                "CONNECTION_POOL_EXHAUSTED",
            ]

    def calculate_delay(self, attempt: int) -> float:
        """Calcular delay en segundos para este intento."""
        if attempt == 0:
            return self.initial_delay_ms / 1000.0

        delay = self.initial_delay_ms * (self.backoff_multiplier ** attempt)
        delay = min(delay, self.max_delay_ms)
        return delay / 1000.0

    def is_retryable(self, error: ElapException) -> bool:
        """Verificar si un error es reintentable."""
        return error.code in self.retryable_errors

    def with_retryable_error(self, code: str) -> "RetryConfig":
        """Agregar código de error reintentable."""
        if code not in self.retryable_errors:
            self.retryable_errors.append(code)
        return self


@dataclass
class CircuitBreakerConfig:
    """Configuración de circuit breaker."""

    # Número de fallos consecutivos antes de abrir
    failure_threshold: int = 5

    # Duración en segundos antes de intentar recovery
    timeout_sec: float = 30.0

    # Número de éxitos consecutivos para cerrar
    success_threshold: int = 2


class CircuitState(Enum):
    """Estados del circuit breaker."""
    CLOSED = "closed"  # Normal, operaciones permitidas
    OPEN = "open"  # Fallando, operaciones bloqueadas
    HALF_OPEN = "half_open"  # Recuperándose, pruebas limitadas


async def execute_with_retry(
    f: Callable[[], Awaitable[T]],
    config: Optional[RetryConfig] = None,
) -> T:
    """
    Ejecutar operación con retry automático.

    Args:
        f: Función async que retorna T o lanza ElapException
        config: Configuración de retry (default = RetryConfig())

    Returns:
        Resultado de la función

    Raises:
        ElapException: Si todos los intentos fallan
    """
    if config is None:
        config = RetryConfig()

    last_error = None

    for attempt in range(config.max_attempts):
        try:
            result = await f()
            if attempt > 0:
                logger.info(f"Operation succeeded after {attempt} retries")
            return result
        except ElapException as e:
            last_error = e

            # No reintentar si no es reintentable
            if not config.is_retryable(e):
                raise

            # No reintentar si es el último intento
            if attempt + 1 >= config.max_attempts:
                break

            # Calcular delay y reintentar
            delay = config.calculate_delay(attempt + 1)
            logger.warning(
                f"Retry attempt {attempt + 1}/{config.max_attempts} "
                f"after error {e.code}, waiting {delay:.1f}s"
            )
            await asyncio.sleep(delay)

    # Todos los intentos fallaron
    raise last_error or ElapException("All retry attempts failed")


async def execute_with_fallback(
    primary: Callable[[], Awaitable[T]],
    fallback: Callable[[], Awaitable[T]],
) -> T:
    """
    Ejecutar operación principal, fallback si falla.

    Args:
        primary: Función principal
        fallback: Función fallback

    Returns:
        Resultado de primary o fallback
    """
    try:
        result = await primary()
        logger.info("Primary operation succeeded")
        return result
    except ElapException as primary_error:
        logger.warning(
            f"Primary operation failed with {primary_error.code}, "
            "trying fallback"
        )

        try:
            result = await fallback()
            logger.info("Fallback operation succeeded")
            return result
        except ElapException as fallback_error:
            logger.error(
                f"Both primary ({primary_error.code}) and fallback "
                f"({fallback_error.code}) failed"
            )
            raise fallback_error


class CircuitBreaker:
    """Circuit breaker para evitar cascada de fallos."""

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None

    def is_open(self) -> bool:
        """¿El circuito está abierto?"""
        if self.state == CircuitState.OPEN:
            # Intentar recuperación si pasó el timeout
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.config.timeout_sec:
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    logger.info(
                        f"Circuit {self.name} changed to HALF_OPEN "
                        "after timeout"
                    )
                    return False
            return True
        return False

    def record_success(self):
        """Registrar operación exitosa."""
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                logger.info(f"Circuit {self.name} closed")

    def record_failure(self):
        """Registrar operación fallida."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit {self.name} opened after {self.failure_count} failures"
            )

    async def call(self, f: Callable[[], Awaitable[T]]) -> T:
        """
        Ejecutar función a través del circuit breaker.

        Args:
            f: Función async a ejecutar

        Returns:
            Resultado de f

        Raises:
            ElapException: Si el circuito está abierto o si f falla
        """
        if self.is_open():
            raise ElapException(
                f"Circuit {self.name} is open, request rejected"
            )

        try:
            result = await f()
            self.record_success()
            return result
        except ElapException as e:
            self.record_failure()
            raise


if __name__ == "__main__":
    import asyncio

    async def test():
        # Test 1: RetryConfig
        config = RetryConfig(max_attempts=3)
        delay0 = config.calculate_delay(0)
        delay1 = config.calculate_delay(1)
        print(f"✅ RetryConfig: delay0={delay0:.2f}s, delay1={delay1:.2f}s")

        # Test 2: execute_with_retry success
        async def success_op():
            return 42

        result = await execute_with_retry(success_op)
        assert result == 42
        print("✅ execute_with_retry (success)")

        # Test 3: execute_with_fallback
        async def fail_op():
            from .errors import AgentTimeout
            raise AgentTimeout("test")

        async def fallback_op():
            return 99

        result = await execute_with_fallback(fail_op, fallback_op)
        assert result == 99
        print("✅ execute_with_fallback")

        # Test 4: CircuitBreaker
        cb = CircuitBreaker("test_service")
        assert not cb.is_open()
        cb.record_success()
        print("✅ CircuitBreaker")

        print("\n✅ Error recovery framework en Python completamente funcional")

    asyncio.run(test())
