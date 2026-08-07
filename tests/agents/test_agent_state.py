"""Tests for AgentState."""

import pytest
from elap_ai.agents import AgentState
from langchain_core.messages import HumanMessage, AIMessage


def test_agent_state_creation():
    """Test creating an AgentState."""
    state: AgentState = {
        "messages": [HumanMessage(content="Hola")],
        "agent_id": "test_agent",
        "agent_name": "Test Agent",
        "agent_role": "Testing",
        "system_prompt": "You are a test agent",
        "empresa_contexto": {"nombre": "Test Company"},
        "uploaded_documents": [],
        "retrieved_context": [],
        "current_tool": None,
        "tool_results": {},
        "agent_memory": {},
    }

    assert state["agent_id"] == "test_agent"
    assert len(state["messages"]) == 1
    assert state["messages"][0].content == "Hola"


def test_agent_state_with_multiple_messages():
    """Test AgentState with conversation history."""
    state: AgentState = {
        "messages": [
            HumanMessage(content="¿Hola?"),
            AIMessage(content="¡Hola! ¿Cómo estás?"),
            HumanMessage(content="Bien, gracias"),
        ],
        "agent_id": "sales_agent",
        "agent_name": "Sales Assistant",
        "agent_role": "Ventas",
        "system_prompt": "You are a sales assistant",
        "empresa_contexto": {"nombre": "Andina Foods"},
        "uploaded_documents": [],
        "retrieved_context": [],
        "current_tool": None,
        "tool_results": {},
        "agent_memory": {},
    }

    assert len(state["messages"]) == 3
    assert state["messages"][1].content == "¡Hola! ¿Cómo estás?"


def test_agent_state_with_documents():
    """Test AgentState with uploaded documents."""
    state: AgentState = {
        "messages": [HumanMessage(content="Analiza este documento")],
        "agent_id": "document_agent",
        "agent_name": "Document Analyzer",
        "agent_role": "Análisis",
        "system_prompt": "Analyze documents",
        "empresa_contexto": {"nombre": "Company"},
        "uploaded_documents": ["/path/to/doc1.pdf", "/path/to/doc2.xlsx"],
        "retrieved_context": ["Chunk 1 from RAG", "Chunk 2 from RAG"],
        "current_tool": "read_pdf",
        "tool_results": {"status": "success"},
        "agent_memory": {"conversation_count": 5},
    }

    assert len(state["uploaded_documents"]) == 2
    assert len(state["retrieved_context"]) == 2
    assert state["current_tool"] == "read_pdf"
    assert state["agent_memory"]["conversation_count"] == 5


def test_agent_state_with_tool_execution():
    """Test AgentState during tool execution."""
    state: AgentState = {
        "messages": [HumanMessage(content="Lee el PDF")],
        "agent_id": "pdf_agent",
        "agent_name": "PDF Reader",
        "agent_role": "Lectura",
        "system_prompt": "Read PDFs",
        "empresa_contexto": {},
        "uploaded_documents": ["/path/to/file.pdf"],
        "retrieved_context": [],
        "current_tool": "read_pdf",
        "tool_results": {
            "text": "PDF content here...",
            "pages": 5,
            "tables": 2,
        },
        "agent_memory": {},
    }

    assert state["current_tool"] == "read_pdf"
    assert "text" in state["tool_results"]
    assert state["tool_results"]["pages"] == 5
