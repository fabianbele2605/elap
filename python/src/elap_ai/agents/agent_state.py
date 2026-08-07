"""
Agent state definition for LangGraph execution.

Tracks conversation history, context, documents, and tool execution state.
"""

from typing import Annotated, Any, TypedDict, Optional
from langchain_core.messages import BaseMessage, AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Represents the complete state of a running agent.

    Fields:
        messages: Conversation history with add_messages reducer
        agent_id: Unique agent identifier
        agent_name: Human-readable agent name
        agent_role: Agent's organizational role
        system_prompt: Agent's system prompt
        empresa_contexto: Company context dict (name, structure, etc.)
        uploaded_documents: List of document file paths
        retrieved_context: Document chunks from RAG search
        current_tool: Currently executing tool name
        tool_results: Results from tool execution
        agent_memory: Persistent agent-specific memory
    """

    # Conversation
    messages: Annotated[list[AnyMessage], add_messages]

    # Context
    agent_id: str
    agent_name: str
    agent_role: str
    system_prompt: str
    empresa_contexto: dict[str, Any]

    # Documents
    uploaded_documents: list[str]  # file paths
    retrieved_context: list[str]   # chunks from RAG

    # Tool execution
    current_tool: Optional[str]
    tool_results: dict[str, Any]
    agent_memory: dict[str, Any]
