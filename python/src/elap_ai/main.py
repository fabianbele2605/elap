"""Main AI Runtime module for ELAP"""

import asyncio
import logging
from typing import Optional

from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class AIRuntime:
    """AI Runtime manager for ELAP

    Manages AI inference, agents, and model orchestration.
    """

    def __init__(self, name: str = "ELAP-AI-Runtime", version: str = "0.1.0") -> None:
        """Initialize AI Runtime

        Args:
            name: Runtime name
            version: Runtime version
        """
        self.name = name
        self.version = version
        self.is_running = False
        self.ollama_client = OllamaClient()
        logger.info(f"Initialized {name} v{version}")

    async def start(self) -> None:
        """Start the AI Runtime"""
        if self.is_running:
            logger.warning("Runtime already running")
            return

        logger.info(f"Starting {self.name}")
        self.is_running = True
        logger.info(f"{self.name} started successfully")

    async def stop(self) -> None:
        """Stop the AI Runtime"""
        if not self.is_running:
            logger.warning("Runtime not running")
            return

        logger.info(f"Stopping {self.name}")
        self.is_running = False
        logger.info(f"{self.name} stopped")

    async def health_check(self) -> bool:
        """Check if runtime is healthy

        Returns:
            True if healthy, False otherwise
        """
        return self.is_running

    async def process_query(self, query: str, modelo: str = "glm4:9b") -> str:
        """Process a user query usando Ollama

        Args:
            query: User query string
            modelo: Modelo a usar (default: glm4:9b)

        Returns:
            Response string desde el modelo
        """
        if not self.is_running:
            raise RuntimeError("Runtime not running")

        logger.info(f"Processing query with {modelo}: {query[:50]}...")

        try:
            # Llamar a Ollama real
            respuesta = await self.ollama_client.generar(modelo, query)
            logger.info(f"Query processed successfully")
            return respuesta
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            # Fallback a respuesta mock si Ollama falla
            return f"Error: {str(e)}"


async def main() -> None:
    """Main entry point for AI Runtime"""
    runtime = AIRuntime()
    await runtime.start()

    # Iniciar servidor REST para exponer agentes
    from .rest_server import start_rest_server

    # Crear tarea asincrónica para el servidor REST
    rest_server_task = asyncio.create_task(start_rest_server(host='0.0.0.0', port=5000))

    logger.info("AI Runtime ready (gRPC server disabled - use REST API instead)")

    # Mantener el proceso corriendo
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        rest_server_task.cancel()
    finally:
        await runtime.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(main())
