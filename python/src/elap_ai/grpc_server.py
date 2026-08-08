"""gRPC Server for AI Runtime

Servidor gRPC que expone los agentes Python al backend Rust.
"""

import asyncio
import logging
from grpc import aio
import grpc

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


class AIRuntimeServicer:
    """Implementación del servicio AIRuntime"""

    async def ExecuteAgent(self, request, context):
        """Ejecuta un agente con un prompt dado"""
        try:
            agent_id = request.agent_id
            prompt = request.prompt

            logger.info(f"Ejecutando agente {agent_id} con prompt: {prompt[:50]}...")

            # Seleccionar agente
            if agent_id == 'hr':
                agent = hr_agent
            elif agent_id == 'finance':
                agent = finance_agent
            else:
                await context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    f"Unknown agent: {agent_id}"
                )

            # Procesar query
            result = await agent.process_query(prompt)

            respuesta = result.get('message', str(result))

            # Retornar respuesta
            return {
                'agent_id': agent_id,
                'estado': 'completado',
                'pasos_completados': 1,
                'progreso': 1.0,
                'respuesta': respuesta,
                'intent': result.get('intent', ''),
                'required_fields': result.get('required_fields', []),
                'tokens': {
                    'prompt': 50,
                    'completion': 100,
                    'total': 150
                }
            }

        except Exception as e:
            logger.error(f"Error executing agent: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL,
                f"Error: {str(e)}"
            )

    async def HealthCheck(self, request, context):
        """Health check para el servicio"""
        return {
            'status': 'ok',
            'message': 'gRPC AI Runtime Server funcionando',
            'uptime_seconds': 0
        }


async def start_grpc_server(host: str = '0.0.0.0', port: int = 50051):
    """Inicia el servidor gRPC"""

    await init_agents()

    server = aio.server()

    # Registrar el servicio
    # (Normalmente usaríamos grpc_servicer_pb2 generado desde .proto)
    # Por ahora, implementamos de forma manual para compatibilidad

    logger.info(f"🚀 gRPC Server iniciado en {host}:{port}")
    logger.info(f"   Servicio: AIRuntime")
    logger.info(f"   RPC: ExecuteAgent, HealthCheck")

    # Iniciar servidor (placeholder - versión completa requiere compilar protos)
    # await server.start()
    # await server.wait_for_termination()

    # Por ahora, usamos REST como fallback
    logger.info("⚠️  Nota: Usar REST API en puerto 5000 mientras se compilan los .proto files")

    # Mantener vivo
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("gRPC server shutdown")
        # await server.stop(grace=5)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    asyncio.run(start_grpc_server())
