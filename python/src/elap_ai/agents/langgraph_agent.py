"""
LangGraph-based agent implementation.

Provides structured agent execution with persistent state,
automatic tool selection, and response generation.
"""

import asyncio
from typing import Any, Optional
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

from .agent_state import AgentState
from .graph_builder import build_agent_graph


class LangGraphAgent:
    """Orchestrates agent execution using LangGraph."""

    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        agent_role: str,
        system_prompt: str,
        empresa_contexto: dict[str, Any],
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
    ):
        """
        Initialize LangGraph agent.

        Args:
            agent_id: Unique identifier
            agent_name: Display name
            agent_role: Role (e.g., "Sales", "RRHH")
            system_prompt: System instructions
            empresa_contexto: Company context for injection
            model_name: Model to use for inference
            temperature: Sampling temperature
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.system_prompt = system_prompt
        self.empresa_contexto = empresa_contexto
        self.model_name = model_name
        self.temperature = temperature

        # Graph will be built lazily
        self._graph = None
        self._conversation_state: Optional[AgentState] = None

    def build_graph(self) -> None:
        """Build the agent's execution graph."""
        if self._graph is None:
            config = {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "agent_role": self.agent_role,
                "system_prompt": self.system_prompt,
                "empresa_contexto": self.empresa_contexto,
                "model_name": self.model_name,
                "temperature": self.temperature,
            }
            self._graph = build_agent_graph(config)

    async def execute(
        self,
        user_input: str,
        conversation_history: Optional[list[dict]] = None,
        context_docs: Optional[list[str]] = None,
    ) -> str:
        """
        Execute agent with user input and optional context.

        Args:
            user_input: User's message
            conversation_history: Prior messages (list of dicts with role/content)
            context_docs: Document chunks to inject as context

        Returns:
            Agent's response
        """
        self.build_graph()

        # Initialize or update conversation state
        if self._conversation_state is None:
            self._conversation_state = {
                "messages": [HumanMessage(content=user_input)],
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "agent_role": self.agent_role,
                "system_prompt": self.system_prompt,
                "empresa_contexto": self.empresa_contexto,
                "uploaded_documents": [],
                "retrieved_context": context_docs or [],
                "current_tool": None,
                "tool_results": {},
                "agent_memory": {},
            }
        else:
            self._conversation_state["messages"].append(HumanMessage(content=user_input))
            self._conversation_state["retrieved_context"] = context_docs or []

        # Execute graph
        output_state = self._graph.invoke(self._conversation_state)

        # Extract response from last message
        last_message = output_state["messages"][-1]
        response = last_message.content if hasattr(last_message, "content") else str(last_message)

        # Update state for next execution
        self._conversation_state = output_state

        return response

    def reset_conversation(self) -> None:
        """Clear conversation history."""
        self._conversation_state = None

    def get_memory(self) -> dict[str, Any]:
        """Get agent's persistent memory."""
        if self._conversation_state:
            return self._conversation_state.get("agent_memory", {})
        return {}

    def set_memory(self, memory: dict[str, Any]) -> None:
        """Update agent's persistent memory."""
        if self._conversation_state:
            self._conversation_state["agent_memory"] = memory
