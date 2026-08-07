"""gRPC Server para AI Runtime"""

import asyncio
import logging
from typing import Optional

import grpc
from grpc import aio

# Importar los tipos generados desde proto
# Nota: primero ejecutar: python -m grpc_tools.protoc -I./src/elap_ai --python_out=./src/elap_ai --grpc_python_out=./src/elap_ai ./src/elap_ai/agent.proto

logger = logging.getLogger(__name__)


class AIRuntimeServicer:
    """Implementación del servicio gRPC de AI Runtime"""

    def __init__(self, ai_runtime):
        self.ai_runtime = ai_runtime
        logger.info("AIRuntimeServicer initialized")

    async def ExecuteAgent(self, request, context):
        """Ejecutar un agente

        Args:
            request: ExecuteAgentRequest con agent_id y query
            context: gRPC context

        Returns:
            ExecuteAgentResponse con resultado de ejecución
        """
        try:
            logger.info(f"ExecuteAgent: agent_id={request.agent_id}, query={request.query[:50]}...")

            # Procesar la query con el AI Runtime
            result = await self.ai_runtime.process_query(request.query)

            # Retornar respuesta exitosa
            from . import agent_pb2
            return agent_pb2.ExecuteAgentResponse(
                agent_id=request.agent_id,
                status="completed",
                result=result,
                progress=1.0,
                error=""
            )
        except Exception as e:
            logger.error(f"Error executing agent: {str(e)}")
            from . import agent_pb2
            return agent_pb2.ExecuteAgentResponse(
                agent_id=request.agent_id,
                status="error",
                result="",
                progress=0.0,
                error=str(e)
            )

    async def ExecuteAgentStreaming(self, request, context):
        """Ejecutar un agente con streaming de respuesta

        Args:
            request: ExecuteAgentRequest con agent_id y query
            context: gRPC context

        Yields:
            ExecuteAgentChunk con tokens individuales
        """
        try:
            logger.info(f"ExecuteAgentStreaming: agent_id={request.agent_id}, query={request.query[:50]}...")

            from . import agent_pb2

            # Obtener modelo correspondiente al agente
            modelo = "glm4:9b"  # Default, podría venir del request

            # Streaming desde Ollama
            chunk_index = 0
            async for token in self.ai_runtime.ollama_client.generar_streaming(modelo, request.query):
                chunk_index += 1

                # Enviar chunk
                yield agent_pb2.ExecuteAgentChunk(
                    agent_id=request.agent_id,
                    chunk=token,
                    progress=min(0.95 + (chunk_index * 0.001), 0.99),  # Progreso simulado
                    is_final=False,
                    error=""
                )

            # Enviar chunk final
            yield agent_pb2.ExecuteAgentChunk(
                agent_id=request.agent_id,
                chunk="",
                progress=1.0,
                is_final=True,
                error=""
            )

        except Exception as e:
            logger.error(f"Error executing agent stream: {str(e)}")
            from . import agent_pb2
            yield agent_pb2.ExecuteAgentChunk(
                agent_id=request.agent_id,
                chunk="",
                progress=0.0,
                is_final=True,
                error=str(e)
            )

    async def HealthCheck(self, request, context):
        """Health check

        Args:
            request: HealthCheckRequest
            context: gRPC context

        Returns:
            HealthCheckResponse
        """
        logger.info(f"HealthCheck: service={request.service}")

        from . import agent_pb2
        return agent_pb2.HealthCheckResponse(
            status="ok",
            message="AI Runtime is healthy"
        )


async def serve(ai_runtime, port: int = 50051):
    """Iniciar servidor gRPC

    Args:
        ai_runtime: Instancia de AIRuntime
        port: Puerto donde escuchar
    """
    # Crear servidor
    server = aio.server()

    # Registrar servicio
    from . import agent_pb2_grpc
    agent_pb2_grpc.add_AIRuntimeServiceServicer_to_server(
        AIRuntimeServicer(ai_runtime), server
    )

    # Escuchar en puerto
    listen_addr = f"127.0.0.1:{port}"
    server.add_insecure_port(listen_addr)

    logger.info(f"🚀 gRPC server listening on {listen_addr}")

    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Import AIRuntime
    from .main import AIRuntime

    # Crear instancia
    runtime = AIRuntime()

    # Ejecutar servidor
    asyncio.run(serve(runtime))
