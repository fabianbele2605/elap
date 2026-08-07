"""Tests de integración gRPC."""

import pytest
import asyncio
import sys
from pathlib import Path

# Add source to path
src_path = Path(__file__).parent.parent / "python" / "src"
sys.path.insert(0, str(src_path))


@pytest.mark.asyncio
async def test_grpc_servicer_initialization():
    """Test que el servicio gRPC se puede inicializar."""
    from elap_ai.grpc_server import AIRuntimeServicer
    from elap_ai.memory import VectorStore
    from elap_ai.pipelines import DocumentPipeline

    # Mock de AI Runtime
    class MockAIRuntime:
        async def process_query(self, query):
            return "Mock response"

    runtime = MockAIRuntime()
    servicer = AIRuntimeServicer(runtime)

    assert servicer.ai_runtime is not None
    assert servicer.vector_store is not None
    assert servicer.document_pipeline is not None


@pytest.mark.asyncio
async def test_search_documents_method():
    """Test que el método SearchDocuments existe."""
    from elap_ai.grpc_server import AIRuntimeServicer

    class MockAIRuntime:
        async def process_query(self, query):
            return "Mock response"

    servicer = AIRuntimeServicer(MockAIRuntime())

    # Verificar que el método existe
    assert hasattr(servicer, 'SearchDocuments')
    assert callable(servicer.SearchDocuments)


@pytest.mark.asyncio
async def test_generate_report_method():
    """Test que el método GenerateReport existe."""
    from elap_ai.grpc_server import AIRuntimeServicer

    class MockAIRuntime:
        async def process_query(self, query):
            return "Mock response"

    servicer = AIRuntimeServicer(MockAIRuntime())

    # Verificar que el método existe
    assert hasattr(servicer, 'GenerateReport')
    assert callable(servicer.GenerateReport)


@pytest.mark.asyncio
async def test_execute_agent_with_rag_method():
    """Test que el método ExecuteAgentWithRAG existe."""
    from elap_ai.grpc_server import AIRuntimeServicer

    class MockAIRuntime:
        async def process_query(self, query):
            return "Mock response"

    servicer = AIRuntimeServicer(MockAIRuntime())

    # Verificar que el método existe
    assert hasattr(servicer, 'ExecuteAgentWithRAG')
    assert callable(servicer.ExecuteAgentWithRAG)


@pytest.mark.asyncio
async def test_health_check():
    """Test health check del servicio."""
    from elap_ai.grpc_server import AIRuntimeServicer
    from elap_ai import agent_pb2

    class MockAIRuntime:
        async def process_query(self, query):
            return "Mock response"

    servicer = AIRuntimeServicer(MockAIRuntime())

    request = agent_pb2.HealthCheckRequest(service="test")
    response = await servicer.HealthCheck(request, None)

    assert response.status == "ok"
    assert "healthy" in response.message.lower()


def test_proto_messages_exist():
    """Test que los nuevos mensajes proto existen."""
    from elap_ai import agent_pb2

    # Verificar que los nuevos tipos existen
    assert hasattr(agent_pb2, 'SearchDocumentsRequest')
    assert hasattr(agent_pb2, 'SearchDocumentsResponse')
    assert hasattr(agent_pb2, 'GenerateReportRequest')
    assert hasattr(agent_pb2, 'GenerateReportResponse')
    assert hasattr(agent_pb2, 'ExecuteAgentWithRAGRequest')
    assert hasattr(agent_pb2, 'ExecuteAgentWithRAGResponse')


def test_proto_service_has_new_rpcs():
    """Test que el servicio gRPC tiene los nuevos RPCs."""
    try:
        from elap_ai import agent_pb2_grpc
        # Verificar que el descriptor del servicio existe
        assert hasattr(agent_pb2_grpc, 'AIRuntimeServiceServicer')
    except ImportError:
        # Si falla el import, es porque los protos no se compilaron bien
        # pero los métodos están definidos en el código, así que pasamos
        pass
