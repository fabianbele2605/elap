"""Tests for Tool Registry."""

import pytest
from elap_ai.tools.registry import ToolRegistry, Tool


@pytest.fixture
def tool_registry() -> ToolRegistry:
    """Create tool registry for testing."""
    return ToolRegistry()


def test_tool_registration(tool_registry: ToolRegistry) -> None:
    """Test registering a tool."""

    def add_numbers(a: int, b: int) -> int:
        return a + b

    tool_registry.register(
        name="add",
        description="Add two numbers",
        func=add_numbers,
        input_schema={"a": "int", "b": "int"},
        output_schema={"result": "int"},
    )

    assert len(tool_registry.tools) == 1
    assert "add" in tool_registry.tools


@pytest.mark.asyncio
async def test_tool_execution(tool_registry: ToolRegistry) -> None:
    """Test executing a registered tool."""

    def multiply(a: int, b: int) -> int:
        return a * b

    tool_registry.register(
        name="multiply",
        description="Multiply two numbers",
        func=multiply,
        input_schema={"a": "int", "b": "int"},
        output_schema={"result": "int"},
    )

    result = await tool_registry.execute("multiply", a=3, b=4)

    assert result == 12


@pytest.mark.asyncio
async def test_tool_execution_not_found(tool_registry: ToolRegistry) -> None:
    """Test executing non-existent tool."""
    with pytest.raises(ValueError):
        await tool_registry.execute("nonexistent", x=1)


def test_list_tools(tool_registry: ToolRegistry) -> None:
    """Test listing registered tools."""

    def dummy_tool() -> str:
        return "dummy"

    tool_registry.register(
        name="tool1",
        description="First tool",
        func=dummy_tool,
        input_schema={},
        output_schema={"result": "str"},
    )
    tool_registry.register(
        name="tool2",
        description="Second tool",
        func=dummy_tool,
        input_schema={},
        output_schema={"result": "str"},
    )

    tools = tool_registry.list_tools()

    assert len(tools) == 2
    assert tools[0]["name"] == "tool1"
    assert tools[1]["name"] == "tool2"


def test_get_tool(tool_registry: ToolRegistry) -> None:
    """Test getting a tool by name."""

    def sample_tool() -> None:
        pass

    tool_registry.register(
        name="sample",
        description="Sample tool",
        func=sample_tool,
        input_schema={},
        output_schema={},
    )

    tool = tool_registry.get_tool("sample")

    assert tool is not None
    assert tool.name == "sample"
    assert tool.description == "Sample tool"


def test_get_tool_not_found(tool_registry: ToolRegistry) -> None:
    """Test getting non-existent tool."""
    tool = tool_registry.get_tool("nonexistent")

    assert tool is None
