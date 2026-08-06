"""Tests for Agent with LangGraph."""

import pytest
from elap_ai.agent_runtime.agent import Agent, AgentState, AgentStateEnum


@pytest.fixture
def sample_agent_state() -> AgentState:
    """Create sample agent state for testing."""
    return AgentState(
        id="agent_123",
        name="Test Agent",
        role="Testing",
        objective="Complete test task",
    )


@pytest.fixture
def sample_agent(sample_agent_state: AgentState) -> Agent:
    """Create sample agent for testing."""
    return Agent(sample_agent_state)


def test_agent_creation(sample_agent: Agent) -> None:
    """Test agent initialization."""
    assert sample_agent.state.name == "Test Agent"
    assert sample_agent.state.state == AgentStateEnum.IDLE
    assert sample_agent.state.progress == 0.0


def test_agent_state_to_dict(sample_agent: Agent) -> None:
    """Test converting agent state to dictionary."""
    state_dict = sample_agent.to_dict()

    assert state_dict["name"] == "Test Agent"
    assert state_dict["role"] == "Testing"
    assert state_dict["objective"] == "Complete test task"
    assert state_dict["state"] == AgentStateEnum.IDLE.value


@pytest.mark.asyncio
async def test_agent_execution(sample_agent: Agent) -> None:
    """Test agent execution workflow."""
    result = await sample_agent.execute()

    assert result.state == AgentStateEnum.COMPLETED
    assert result.progress == 1.0
    assert result.current_step == result.total_steps
    assert len(result.plan) > 0
    assert len(result.history) > 0


@pytest.mark.asyncio
async def test_agent_reflections(sample_agent: Agent) -> None:
    """Test agent reflections during execution."""
    result = await sample_agent.execute()

    # Agent should have reflections at even steps
    assert len(result.reflections) > 0


def test_agent_state_validation() -> None:
    """Test agent state validation."""
    # Valid state
    state = AgentState(
        id="test",
        name="Test",
        role="Testing",
        objective="Test objective",
    )
    assert state.state == AgentStateEnum.IDLE

    # Progress bounds
    state.progress = 0.0
    assert state.progress == 0.0

    state.progress = 1.0
    assert state.progress == 1.0


def test_agent_graph_structure(sample_agent: Agent) -> None:
    """Test LangGraph structure."""
    # Verify graph is compiled
    assert sample_agent.graph is not None

    # Verify initial state
    assert sample_agent.state.state == AgentStateEnum.IDLE
