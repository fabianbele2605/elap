"""gRPC Server para AI Runtime"""

import asyncio
import json
import logging
from typing import Optional

import grpc
from grpc import aio

# Importar los tipos generados desde proto
# Nota: primero ejecutar: python -m grpc_tools.protoc -I./src/elap_ai --python_out=./src/elap_ai --grpc_python_out=./src/elap_ai ./src/elap_ai/agent.proto

from .agents import LangGraphAgent
from .memory import VectorStore
from .pipelines import DocumentPipeline
from .tools.documents import DocumentReader, DocumentGenerator
from .document_generation_service import DocumentGenerationService

logger = logging.getLogger(__name__)


class AIRuntimeServicer:
    """Implementación del servicio gRPC de AI Runtime"""

    def __init__(self, ai_runtime):
        self.ai_runtime = ai_runtime
        self.vector_store = VectorStore(db_path="./data/chromadb")
        self.document_pipeline = DocumentPipeline(self.vector_store)
        self.document_generation_service = DocumentGenerationService(self.vector_store)
        self.agents: dict = {}  # Cache de agentes
        logger.info("AIRuntimeServicer initialized with RAG support and Document Generation")

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

    async def SearchDocuments(self, request, context):
        """Buscar documentos en RAG

        Args:
            request: SearchDocumentsRequest con collection y query
            context: gRPC context

        Returns:
            SearchDocumentsResponse con chunks recuperados
        """
        try:
            logger.info(f"SearchDocuments: collection={request.collection}, query={request.query[:50]}...")

            # Buscar en RAG
            chunks = self.document_pipeline.search(
                collection_name=request.collection,
                query=request.query,
                top_k=request.top_k or 5
            )

            from . import agent_pb2
            return agent_pb2.SearchDocumentsResponse(
                status="success",
                chunks=chunks,
                count=len(chunks),
                error=""
            )
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            from . import agent_pb2
            return agent_pb2.SearchDocumentsResponse(
                status="error",
                chunks=[],
                count=0,
                error=str(e)
            )

    async def GenerateReport(self, request, context):
        """Generar reporte en PDF o Excel

        Args:
            request: GenerateReportRequest con titulo, sections, formato
            context: gRPC context

        Returns:
            GenerateReportResponse con archivo binario
        """
        try:
            logger.info(f"GenerateReport: title={request.title}, format={request.format}")

            # Parsear secciones del JSON
            sections = json.loads(request.sections_json)

            # Generar según formato
            if request.format.lower() == "pdf":
                report_bytes = DocumentGenerator.generate_pdf_report(
                    title=request.title,
                    sections=sections,
                    company_name=request.company_name or "Empresa"
                )
            elif request.format.lower() == "excel":
                import pandas as pd
                # Convertir secciones a DataFrames
                data = {}
                for section in sections:
                    data[section.get("title", "Sheet")] = pd.DataFrame(section.get("data", []))
                report_bytes = DocumentGenerator.generate_excel_report(
                    data=data,
                    title=request.title
                )
            else:
                raise ValueError(f"Unsupported format: {request.format}")

            from . import agent_pb2
            return agent_pb2.GenerateReportResponse(
                status="success",
                file_bytes=report_bytes,
                filename=f"{request.title}.{request.format.lower()}",
                error=""
            )
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            from . import agent_pb2
            return agent_pb2.GenerateReportResponse(
                status="error",
                file_bytes=b"",
                filename="",
                error=str(e)
            )

    async def ExecuteAgentWithRAG(self, request, context):
        """Ejecutar agente con contexto de RAG

        Args:
            request: ExecuteAgentWithRAGRequest
            context: gRPC context

        Returns:
            ExecuteAgentResponse con resultado enriquecido
        """
        try:
            logger.info(f"ExecuteAgentWithRAG: agent_id={request.agent_id}, query={request.query[:50]}...")

            # Buscar documentos relevantes si se proporciona colección
            context_docs = []
            if request.rag_collection:
                context_docs = self.document_pipeline.search(
                    collection_name=request.rag_collection,
                    query=request.query,
                    top_k=3
                )

            # Ejecutar agente (mantener compatibilidad con Ollama por ahora)
            # TODO: Integrar con LangGraphAgent cuando esté completamente funcional
            result = await self.ai_runtime.process_query(request.query)

            from . import agent_pb2
            return agent_pb2.ExecuteAgentWithRAGResponse(
                agent_id=request.agent_id,
                status="completed",
                result=result,
                context_chunks=context_docs,
                context_count=len(context_docs),
                error=""
            )
        except Exception as e:
            logger.error(f"Error executing agent with RAG: {str(e)}")
            from . import agent_pb2
            return agent_pb2.ExecuteAgentWithRAGResponse(
                agent_id=request.agent_id,
                status="error",
                result="",
                context_chunks=[],
                context_count=0,
                error=str(e)
            )

    async def GenerateDocuments(self, request, context):
        """Generar 15 documentos personalizados basados en configuración de empresa

        Args:
            request: GenerateDocumentsRequest con CompanyConfig
            context: gRPC context

        Returns:
            GenerateDocumentsResponse con documentos generados
        """
        try:
            logger.info(f"GenerateDocuments: company={request.config.nombreEmpresa}")

            # Convertir protobuf config a dict
            company_config = {
                "nombreEmpresa": request.config.nombreEmpresa,
                "sector": request.config.sector,
                "ubicacion": request.config.ubicacion,
                "anoFundacion": request.config.anoFundacion,
                "website": request.config.website or "",
                "numEmpleados": request.config.numEmpleados,
                "departamentos": list(request.config.departamentos),
                "ceo": request.config.ceo or "",
                "contactoRRHH": request.config.contactoRRHH or "",
                "productos": list(request.config.productos),
                "servicios": list(request.config.servicios),
                "clientesPrincipales": request.config.clientesPrincipales or "",
                "salarioPromedio": request.config.salarioPromedio,
                "presupuestoAnual": request.config.presupuestoAnual or 0,
                "crecimientoEsperado": request.config.crecimientoEsperado or "15-20%",
            }

            # Generar documentos (usa simulación por ahora, pero es asyncio-compatible)
            template_names = list(request.template_names) if request.template_names else None
            result = await self.document_generation_service.generate_documents(
                company_config, template_names
            )

            logger.info(f"Generated {result.get('total_documents')} documents successfully")

            # Nota: Aquí necesitaríamos convertir a protobuf cuando esté compilado
            # Por ahora, retornamos un dict que será serializado
            return {
                "status": "success",
                "company_id": result.get("company_id"),
                "total_documents": result.get("total_documents"),
                "documents_indexed": result.get("documents_indexed"),
                "overall_status": result.get("overall_status"),
            }

        except Exception as e:
            logger.error(f"Error generating documents: {str(e)}")
            return {
                "status": "error",
                "company_id": "",
                "total_documents": 0,
                "documents_indexed": 0,
                "overall_status": "error",
                "error": str(e),
            }

    async def GetGenerationStatus(self, request, context):
        """Obtener estado de generación de documentos

        Args:
            request: GetGenerationStatusRequest con company_id
            context: gRPC context

        Returns:
            GetGenerationStatusResponse con estado actual
        """
        try:
            logger.info(f"GetGenerationStatus: company_id={request.company_id}")

            result = self.document_generation_service.get_generation_status(
                request.company_id
            )

            logger.info(f"Generation status: {result.get('overall_status')}")

            # Retornar resultado
            return result

        except Exception as e:
            logger.error(f"Error getting generation status: {str(e)}")
            return {
                "company_id": request.company_id,
                "overall_status": "error",
                "error": str(e),
            }


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
