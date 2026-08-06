"""Agent with LangGraph StateGraph."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field, ConfigDict


class AgentStateEnum(str, Enum):
    """Agent states."""
    IDLE = "idle"
    THINKING = "thinking"
    PLANNING = "planning"
    EXECUTING = "executing"
    REFLECTING = "reflecting"
    COMPLETED = "completed"
    ERROR = "error"


class AgentState(BaseModel):
    """Agent state managed by LangGraph."""

    id: str = Field(..., description="Agent unique identifier")
    name: str = Field(..., description="Agent name")
    role: str = Field(..., description="Agent role (e.g., Sales, Support)")
    objective: str = Field(..., description="Agent objective")

    state: AgentStateEnum = Field(default=AgentStateEnum.IDLE)
    progress: float = Field(default=0.0, ge=0.0, le=1.0)

    current_step: int = Field(default=0, description="Current execution step")
    total_steps: int = Field(default=0, description="Total planned steps")

    plan: list[str] = Field(default_factory=list, description="Execution plan")
    history: list[dict[str, Any]] = Field(default_factory=list, description="Action history")
    reflections: list[str] = Field(default_factory=list, description="Agent reflections")

    error: Optional[str] = Field(default=None, description="Error message if any")

    model_config = ConfigDict(use_enum_values=False)


class Agent:
    """LangGraph-based Agent with state management."""

    def __init__(self, state: AgentState) -> None:
        """Initialize agent with initial state."""
        self.state = state
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build LangGraph StateGraph for agent lifecycle."""
        workflow = StateGraph(AgentState)

        # Add nodes (states and transitions)
        workflow.add_node("idle", self._node_idle)
        workflow.add_node("thinking", self._node_thinking)
        workflow.add_node("planning", self._node_planning)
        workflow.add_node("executing", self._node_executing)
        workflow.add_node("reflecting", self._node_reflecting)
        workflow.add_node("error_handler", self._node_error)

        # Add edges (transitions)
        workflow.add_edge("idle", "thinking")
        workflow.add_edge("thinking", "planning")
        workflow.add_edge("planning", "executing")
        workflow.add_edge("executing", END)
        workflow.add_edge("reflecting", "executing")
        workflow.add_edge("error_handler", END)

        # Set entry point
        workflow.set_entry_point("idle")

        return workflow.compile()

    async def _node_idle(self, state: AgentState) -> AgentState:
        """Idle state: Initialize and prepare."""
        state.state = AgentStateEnum.THINKING
        return state

    async def _node_thinking(self, state: AgentState) -> AgentState:
        """Thinking state: Analyze objective."""
        state.state = AgentStateEnum.PLANNING
        state.history.append({
            "step": "thinking",
            "description": f"Analyzing objective: {state.objective}"
        })
        return state

    async def _node_planning(self, state: AgentState) -> AgentState:
        """Planning state: Create execution plan."""
        state.plan = [
            "Step 1: Gather requirements",
            "Step 2: Validate inputs",
            "Step 3: Execute main task",
            "Step 4: Verify results",
        ]
        state.total_steps = len(state.plan)
        state.state = AgentStateEnum.EXECUTING
        state.history.append({
            "step": "planning",
            "plan_steps": len(state.plan)
        })
        return state

    async def _node_executing(self, state: AgentState) -> AgentState:
        """Executing state: Run plan steps."""
        # Execute all remaining steps
        while state.current_step < state.total_steps:
            state.current_step += 1
            state.progress = state.current_step / state.total_steps
            state.history.append({
                "step": state.current_step,
                "description": state.plan[state.current_step - 1]
            })
            # Add reflection at even steps
            if state.current_step % 2 == 0:
                state.reflections.append(
                    f"Completed step {state.current_step}/{state.total_steps}"
                )

        state.state = AgentStateEnum.COMPLETED
        state.progress = 1.0
        return state

    async def _node_reflecting(self, state: AgentState) -> AgentState:
        """Reflecting state: Analyze and learn."""
        reflection = f"Completed step {state.current_step}/{state.total_steps}"
        state.reflections.append(reflection)
        state.state = AgentStateEnum.EXECUTING
        return state

    async def _node_error(self, state: AgentState) -> AgentState:
        """Error handler state."""
        state.state = AgentStateEnum.ERROR
        return state

    @staticmethod
    def _should_reflect(state: AgentState) -> bool:
        """Determine if agent should reflect."""
        return state.current_step % 2 == 0 and state.current_step < state.total_steps

    async def execute(self) -> AgentState:
        """Execute agent workflow."""
        try:
            # Run graph from initial state
            output = await self.graph.ainvoke(self.state.model_dump())
            # Convert dict output back to AgentState
            return AgentState(**output)
        except Exception as e:
            self.state.error = str(e)
            self.state.state = AgentStateEnum.ERROR
            return self.state

    def get_state(self) -> AgentState:
        """Get current agent state."""
        return self.state

    def to_dict(self) -> dict[str, Any]:
        """Convert agent to dictionary."""
        return self.state.model_dump()
