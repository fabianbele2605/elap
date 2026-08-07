"""
LangGraph graph construction.

Builds the execution graph with nodes for input processing,
tool selection, tool execution, and response generation.
"""

import json
from typing import Any, Literal
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, END

from .agent_state import AgentState


def build_agent_graph(config: dict[str, Any]):
    """
    Build LangGraph execution graph.

    Args:
        config: Agent configuration (id, name, role, system_prompt, etc.)

    Returns:
        Compiled graph ready for invocation
    """

    graph = StateGraph(AgentState)

    # ===== NODE: Process Input =====
    def process_input_node(state: AgentState) -> dict[str, Any]:
        """Process and validate user input."""
        # For now, just pass through
        # In future: input validation, entity extraction, etc.
        return {}

    # ===== NODE: Select Tool =====
    def tool_selector_node(state: AgentState) -> dict[str, Any]:
        """
        Decide whether to use a tool or generate response directly.

        Simple heuristic: if user mentions "read", "document", "file", "pdf"
        or "excel", route to tool execution. Otherwise respond directly.
        """
        last_message = state["messages"][-1]
        user_input = last_message.content.lower() if isinstance(last_message, HumanMessage) else ""

        tool_keywords = ["read", "document", "file", "pdf", "excel", "word", "csv",
                        "generate", "report", "chart", "graph", "analysis"]

        should_use_tool = any(keyword in user_input for keyword in tool_keywords)

        return {
            "current_tool": "document_processor" if should_use_tool else None
        }

    # ===== NODE: Execute Tool =====
    def tool_executor_node(state: AgentState) -> dict[str, Any]:
        """
        Execute selected tool.

        For now: placeholder. Will integrate with actual tools.
        """
        current_tool = state.get("current_tool")

        if current_tool == "document_processor":
            # Placeholder: return success
            result = {
                "status": "success",
                "data": "Document processed",
                "chunks": state.get("retrieved_context", [])
            }
        else:
            result = {}

        return {
            "tool_results": result
        }

    # ===== NODE: Generate Response =====
    def response_generator_node(state: AgentState) -> dict[str, Any]:
        """
        Generate agent response using LLM.

        For now: echo response. In production: call LLM API.
        """
        last_message = state["messages"][-1]
        user_input = last_message.content

        # Build context from company + retrieved docs
        empresa = state.get("empresa_contexto", {})
        empresa_nombre = empresa.get("nombre", "Empresa")
        contexto_docs = state.get("retrieved_context", [])

        # Construct prompt
        prompt_parts = [
            state.get("system_prompt", "You are a helpful assistant."),
            f"\n\nCompañía: {empresa_nombre}",
        ]

        if contexto_docs:
            prompt_parts.append(f"\n\nContexto de documentos:\n" + "\n".join(contexto_docs[:2]))

        tool_results = state.get("tool_results", {})
        if tool_results:
            prompt_parts.append(f"\n\nResultados de herramientas: {json.dumps(tool_results)}")

        prompt_parts.append(f"\n\nUsuario: {user_input}")

        full_prompt = "".join(prompt_parts)

        # TODO: Call actual LLM here
        # For now, return placeholder response
        response = f"[{state.get('agent_role', 'Agent')}] Respondiendo a: {user_input[:50]}..."

        return {
            "messages": [AIMessage(content=response)]
        }

    # ===== CONDITIONAL ROUTING =====
    def route_to_tool(state: AgentState) -> Literal["execute", "respond"]:
        """Route to tool execution or direct response generation."""
        if state.get("current_tool"):
            return "execute"
        return "respond"

    # ===== ADD NODES =====
    graph.add_node("process_input", process_input_node)
    graph.add_node("select_tool", tool_selector_node)
    graph.add_node("execute_tool", tool_executor_node)
    graph.add_node("generate_response", response_generator_node)

    # ===== ADD EDGES =====
    graph.add_edge("process_input", "select_tool")
    graph.add_conditional_edges(
        "select_tool",
        route_to_tool,
        {
            "execute": "execute_tool",
            "respond": "generate_response"
        }
    )
    graph.add_edge("execute_tool", "generate_response")
    graph.add_edge("generate_response", END)

    graph.set_entry_point("process_input")

    return graph.compile()
